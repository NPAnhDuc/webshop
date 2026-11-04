"""Small, guarded calculations for unambiguous admin questions.

All accounting totals come from business_analysis.analyze_business. Extra SQL is
limited to its documented order/category/channel joins and always binds values.
"""
from __future__ import annotations

import re
import sqlite3
from datetime import date
from pathlib import Path

from .rag_metrics import METRICS
from .retrieval import normalize

DATA_START = date(2025, 10, 1)
DATA_END = date(2026, 10, 1)  # exclusive
RANK_PATTERN = re.compile(r"\b(?:cao nhat|lon nhat|nhieu nhat|thap nhat|it nhat|(?:nhieu|it) don nhat|top|xep hang)\b")
MENTION = re.compile(
    r"\b(?:quy|q)\s*[1-4]\b(?:\s*(?:/|nam)\s*20\d{2})?"
    r"|\b(?:thang\s*)?20\d{2}-(?:0?[1-9]|1[0-2])\b"
    r"|\bthang\s*\d{1,2}(?!\d)(?:\s*(?:/|nam)\s*20\d{2})?"
    r"|\bt\s*\d{1,2}(?:\s*/\s*20\d{2})?\b"
    r"|(?<![\d/])(?:0?[1-9]|1[0-2])\s*/\s*20\d{2}\b"
)
METRIC_WORDS = re.compile("|".join(pattern for _, pattern, *_ in METRICS) + r"|\bdt\b|\blg\b|\b(?:nhieu|it) don\b|\bsan pham hoan(?: tra)?\b|\btien hoan\b")
COURTESY = re.compile(r"\blam tron\s+(?:2|hai)(?:\s+chu so)?(?:\s+thap phan)?\b|\btu\s+(?:cao|nhieu|lon)\s+xuong\s+(?:thap|it|nho)\b")
COUNT_WORDS = re.compile(r"\btop\s*[1-5]\b|\b(?:[1-5]|mot|hai|ba)\s+(?=thang|kenh|danh muc|nhom)")

# A calculation question is taken only when every word in it is understood: a word
# outside these lists can change what is asked ("tai nghe", "Dell", "trước hoàn",
# "mỗi ngày", "nếu"), and the answer would be a right number for another question.
COMMON_WORDS = frozenset("la bao nhieu duoc cua trong thi vay the nhi a nhe oi shop minh toi ta cho hoi biet xem giup tinh tien dong tong co va so voi mang lai".split())
_FILTER = "kenh danh muc nhom qua tai o tu"
_CHANGE = f"chenh lech nhau tang giam hay thay doi cao thap nhieu it lon nho hon {_FILTER}"
OPERATION_WORDS = {
    "difference": frozenset(_CHANGE.split()),
    "pct_change": frozenset((_CHANGE + " phan tram truong").split()),
    "ratio": frozenset("ty le phan tram theo bien binh quan trung moi tren chia don luot hoan tra hang san pham da ban tong luong chiem quy doi ra may".split()),
    "rank": frozenset(f"top xep cao lon nhieu thap it nhat thang nao {_FILTER}".split()),
    "filter": frozenset(_FILTER.split()),
    "total": frozenset("gop tong cong so con".split()),
    "target_difference": frozenset("thuc hien cao hay thap hon ke hoach".split()),
}

# Category values are a closed mapping to the product dimension in shop.sqlite.
CATEGORY_ALIASES = {
    "laptop": "laptop", "may tinh xach tay": "laptop", "lap top": "laptop",
    "cpu": "cpu", "bo vi xu ly": "cpu", "ram": "memory", "memory": "memory", "bo nho": "memory",
    "ssd": "internal-hard-drive", "o cung": "internal-hard-drive", "o cung trong": "internal-hard-drive",
    "man hinh": "monitor", "monitor": "monitor", "chuot": "mouse", "mouse": "mouse",
    "mainboard": "motherboard", "bo mach chu": "motherboard", "motherboard": "motherboard",
    "card man hinh": "video-card", "video card": "video-card", "gpu": "video-card",
    "nguon": "power-supply", "power supply": "power-supply", "case": "case",
}
# A bare "cửa hàng" usually means the whole shop, so the store channel needs a preposition.
CHANNEL_ALIASES = {
    "website": "website", "web": "website",
    "qua cua hang": "store", "tai cua hang": "store", "o cua hang": "store", "kenh cua hang": "store",
    "store": "store", "offline": "store",
    "mang xa hoi": "social", "social": "social", "kenh xa hoi": "social",
}
FILTER_LABELS = {
    "laptop": "laptop", "cpu": "CPU", "memory": "RAM", "internal-hard-drive": "ổ cứng", "monitor": "màn hình",
    "mouse": "chuột", "motherboard": "mainboard", "video-card": "card màn hình", "power-supply": "nguồn", "case": "vỏ case",
    "website": "website", "store": "cửa hàng", "social": "mạng xã hội",
}

FIELD_BY_METRIC = {
    "revenue": ("totals", "revenue", "Doanh thu thuần", "đ"),
    "gross_profit": ("totals", "gross_profit", "Lãi gộp", "đ"),
    "cost": ("totals", "cost", "Giá vốn", "đ"),
    "operating_profit": ("financial", "operating_profit_before_interest_tax", "Lợi nhuận hoạt động trước lãi vay và thuế", "đ"),
    "expenses": ("financial", "operating_expenses", "Chi phí vận hành", "đ"),
    "orders": ("financial", "orders", "Số đơn hàng", "đơn"),
    "refunds": ("financial", "refunds", "Tiền hoàn cho khách", "đ"),
    "return_units": ("financial", "return_units", "Sản phẩm hoàn trả", "sản phẩm"),
}


def _month_bounds(month: str) -> tuple[date, date]:
    year, number = map(int, month.split("-"))
    return date(year, number, 1), date(year + (number == 12), number % 12 + 1, 1)


def _quarter_months(quarter: str) -> list[str]:
    year, q = int(quarter[:4]), int(quarter[-1])
    first = 3 * (q - 1) + 1
    return [f"{year:04}-{m:02}" for m in range(first, first + 3)]


def _parse_mentions(question: str, scope: dict) -> list[str]:
    """Keep textual order for A-vs-B math; scope remains authoritative for years."""
    q = normalize(question)
    ref = date.fromisoformat(scope.get("reference_date", date.today().isoformat()))
    years = [int(x) for x in re.findall(r"\b20\d{2}\b", q)]
    default_year = years[-1] if years else ref.year
    found: list[tuple[int, str]] = []
    occupied: list[tuple[int, int]] = []

    def inside(start: int) -> bool:
        return any(a <= start < b for a, b in occupied)

    quarter_pattern = re.compile(r"\b(?:quy\s*|q\s*)([1-4])\b(?:\s*(?:/|nam)\s*(20\d{2}))?")
    for m in quarter_pattern.finditer(q):
        year = int(m[2]) if m[2] else default_year
        found.append((m.start(), f"{year:04}-Q{m[1]}"))
        occupied.append(m.span())

    month_patterns = (
        (re.compile(r"\bthang\s*(\d{1,2})(?:\s*(?:/|nam)\s*(20\d{2}))?"), "named"),
        (re.compile(r"\bt\s*(\d{1,2})(?:\s*/\s*(20\d{2}))?\b"), "short"),
        (re.compile(r"(?<![\d/])(20\d{2})-(0?[1-9]|1[0-2])\b"), "iso"),
        (re.compile(r"(?<![\d/])(0?[1-9]|1[0-2])\s*/\s*(20\d{2})\b"), "slash"),
    )
    for pattern, style in month_patterns:
        for m in pattern.finditer(q):
            if inside(m.start()):
                continue
            prefix = q[max(0, m.start() - 8):m.start()]
            if style == "slash" and re.search(r"(?:q|quy|thang)\s*$", prefix):
                continue
            if style == "iso":
                year, month = int(m[1]), int(m[2])
            elif style == "slash":
                month, year = int(m[1]), int(m[2])
            else:
                month = int(m[1])
                year = int(m[2]) if m[2] else default_year
            if 1 <= month <= 12:
                found.append((m.start(), f"{year:04}-{month:02}"))
                occupied.append(m.span())

    if found:
        return [period for _, period in sorted(found)]
    months = list(scope.get("months", []))
    quarters = list(scope.get("quarters", []))
    return months + quarters


def _range(period: str) -> tuple[date, date, list[str]]:
    if "-Q" in period:
        months = _quarter_months(period)
        start = _month_bounds(months[0])[0]
        end = _month_bounds(months[-1])[1]
    else:
        start, end = _month_bounds(period)
        months = [period]
    return start, end, months


def _validated_period(period: str, reference: date) -> bool:
    try:
        start, end, _ = _range(period)
    except (ValueError, IndexError):
        return False
    return DATA_START <= start < end <= DATA_END and end <= reference


def _metric(q: str) -> str | None:
    matches = [key for key, pattern, *_ in METRICS if re.search(pattern, q)]
    if re.search(r"\bdt\b", q):
        matches.append("revenue")
    if re.search(r"\b(?:nhieu don|it don|don hang|so don)\b", q):
        matches.append("orders")
    if re.search(r"\blg\b", q):
        matches.append("gross_profit")
    matches = list(dict.fromkeys(matches))
    return matches[0] if len(matches) == 1 and matches[0] in FIELD_BY_METRIC else None


def _claim_filters(q: str) -> tuple[set[str], set[str], str]:
    """Longest alias first, so "card màn hình" is not read as "màn hình"."""
    categories: set[str] = set()
    channels: set[str] = set()
    rest = q
    for aliases, found in ((CHANNEL_ALIASES, channels), (CATEGORY_ALIASES, categories)):
        for alias in sorted(aliases, key=len, reverse=True):
            rest, hits = re.subn(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", " ", rest)
            if hits:
                found.add(aliases[alias])
    return categories, channels, rest


def _base_named_first(q: str) -> tuple[bool, bool]:
    """Return (base first, says "từ A đến B"): "so với A, B" and "từ A đến B" start from the base."""
    first = MENTION.search(q)
    if not first:
        return False, False
    before = q[:first.start()]
    from_to = bool(re.search(r"\btu\s*$", before) and re.match(r"\s*(?:den|sang)\b", q[first.end():]))
    return from_to or bool(re.search(r"\bso voi\s*$", before)), from_to


def _understood(rest: str, operation: str, from_to: bool, allow_return_adjustment: bool = False) -> bool:
    # "giữa A và B" is between two periods; "giữa tháng 8" alone is the middle of a month.
    rest = re.sub(r"\btinh theo (?:ledger|so cai|so sach)\b", " ", rest)
    if allow_return_adjustment:
        rest = re.sub(r"\b(?:da )?(?:tinh ca|tru(?: ca)?)\s+(?:(?:cac|dong)\s+)?hoan(?: hang)?\b", " ", rest)
    rest = re.sub(rf"\bgiua\s+(?=(?:{MENTION.pattern})\s+va\b)", " ", rest)
    rest = METRIC_WORDS.sub(" ", MENTION.sub(" ", re.sub(r"\b(?:nhom|xep) hang\b", " ", rest)))
    rest = COUNT_WORDS.sub(" ", re.sub(r"\b(?:nam\s+)?20\d{2}\b", " ", rest))
    rest = re.sub(r"\bmay\s*(?:phan tram|%)", " phan tram ", COURTESY.sub(" ", rest))
    if from_to:
        rest = re.sub(r"\b(?:den|sang)\b", " ", rest)
    return not set(re.findall(r"\w+", rest)) - COMMON_WORDS - OPERATION_WORDS[operation]


def _operation(q: str, filtered: bool) -> tuple[str | None, str | None]:
    # Return rates need an explicit denominator; otherwise "tỷ lệ hoàn" is ambiguous.
    if re.search(r"\b(?:bien lai gop|bien loi nhuan gop)\b", q):
        return "ratio", "gross_margin"
    if re.search(r"\b(?:lai gop|loi nhuan gop|lg)\b", q) and re.search(r"\b(?:binh quan|trung binh)\b.*\b(?:moi don|tren moi don|don hang)\b", q):
        return "ratio", "gross_profit_per_order"
    if re.search(r"\b(?:binh quan|trung binh)\b.*\b(?:moi )?don\b", q) and re.search(r"\bdoanh thu(?: thuan)?\b", q):
        return "ratio", "revenue_per_order"
    if re.search(r"\b(?:ty le|phan tram)\b.*\bsan pham hoan\b", q):
        if re.search(r"\b(?:tren|chia cho)\s+(?:tong\s+)?(?:luong|so luong|san pham|hang)(?:\s+da)?\s+ban\b", q):
            return "ratio", "returns_per_sold_unit"
        return None, None
    if re.search(r"\b(?:ty le|phan tram)\s+(?:(?:luot|san pham|hang)\s+)?(?:hoan|tra hang)\b", q):
        if re.search(r"\b(?:tren|chia cho)\s+(?:so )?don\b", q):
            return "ratio", "returns_per_order"
        if re.search(r"\b(?:tren|chia cho)\s+(?:tong )?(?:so )?(?:san pham|hang) da ban\b", q):
            return "ratio", "returns_per_sold_unit"
        return None, None

    if re.search(r"\btien hoan\b", q) and re.search(r"\bchiem\b", q) and re.search(r"\bdoanh thu thuan\b", q):
        return "ratio", "refund_share_of_revenue"

    if (re.search(r"\bthuc hien\b", q) and re.search(r"\bke hoach\b", q)
            and re.search(r"\b(?:cao|thap) hon\b", q) and re.search(r"\bbao nhieu\b", q)):
        return "target_difference", None

    comparison_terms = r"(?:chenh(?:\s+(?:lech|nhau))?|lech|tang|giam|thay doi)"
    if ((re.search(r"\btong\b", q) or re.search(r"\bgop\s+chi phi\b", q))
            and len(list(MENTION.finditer(q))) >= 2
            and not re.search(rf"\b{comparison_terms}\b", q)):
        return "total", None

    if re.search(rf"\b{comparison_terms}\b", q) and re.search(r"%|phan tram", q):
        return "pct_change", None
    if re.search(rf"\b(?:chenh(?:\s+(?:lech|nhau))?|lech|tang bao nhieu|giam bao nhieu|thay doi bao nhieu)\b", q):
        return "difference", None
    if re.search(r"\b(?:cao|thap|nhieu|it|lon|nho) hon\b", q) and re.search(r"\bbao nhieu\b", q):
        return "difference", None

    if len(list(MENTION.finditer(q))) == 2 and re.search(r"\bhon\b", q) and re.search(r"\bbao nhieu\b", q):
        return "difference", None

    if RANK_PATTERN.search(q):
        return "rank", None
    if filtered and re.search(r"\b(?:doanh thu|dt|lai gop|loi nhuan gop|lg)\b", q):
        return "filter", None
    return None, None


def _ranking_months(q: str, scope: dict, reference: date) -> list[str] | None:
    if re.search(r"\b(?:nua dau|nua sau|nua cuoi)\b", q):
        return None
    quarters = list(scope.get("quarters", []))
    if len(quarters) == 1 and not scope.get("months"):
        candidates = _quarter_months(quarters[0])
    else:
        years = [int(x) for x in re.findall(r"\b20\d{2}\b", q)]
        if not years:
            return None
        year = years[-1]
        candidates = [f"{year:04}-{m:02}" for m in range(1, 13)]
    return [m for m in candidates if _validated_period(m, reference)]


def calc_request(question, role, scope) -> dict | None:
    """Return a small allow-listed request, or None when interpretation is uncertain."""
    if role != "admin" or not isinstance(scope, dict):
        return None
    q = re.sub(r"\bbn\b", "bao nhieu", normalize(question))
    categories, channels, rest = _claim_filters(q)
    if len(categories) > 1 or len(channels) > 1:
        return None
    category, channel = next(iter(categories), None), next(iter(channels), None)
    operation, ratio_kind = _operation(q, bool(category or channel))
    if operation is None:
        return None
    base_first, from_to = _base_named_first(q)
    metric_hint = _metric(q)
    allow_return_adjustment = metric_hint == "revenue" or ratio_kind in {"refund_share_of_revenue", "revenue_per_order"}
    if not _understood(rest, operation, from_to, allow_return_adjustment):
        return None
    reference = date.fromisoformat(scope.get("reference_date", date.today().isoformat()))
    mentions = _parse_mentions(question, scope)

    if operation in {"difference", "pct_change"}:
        if len(mentions) != 2 or any(not _validated_period(p, reference) for p in mentions):
            return None
        if ("-Q" in mentions[0]) != ("-Q" in mentions[1]):
            return None
        metric = _metric(q)
        if metric is None or ((category or channel) and metric not in {"revenue", "gross_profit"}):
            return None
        periods = mentions[::-1] if base_first else mentions
        return {"operation": operation, "metric": metric, "periods": periods, "category": category,
                "channel": channel, "reference_date": reference.isoformat()}

    if operation == "target_difference":
        metric = _metric(q)
        if (len(mentions) != 1 or "-Q" in mentions[0] or not _validated_period(mentions[0], reference)
                or category or channel or metric not in {None, "revenue"}):
            return None
        return {"operation": operation, "metric": "revenue", "periods": mentions, "reference_date": reference.isoformat()}

    if operation == "total":
        metric = _metric(q)
        if (metric is None or not mentions or len(mentions) > 12
                or any(not _validated_period(p, reference) for p in mentions)):
            return None
        if any(("-Q" in p) != ("-Q" in mentions[0]) for p in mentions):
            return None
        return {"operation": "total", "metric": metric, "periods": mentions, "reference_date": reference.isoformat()}

    if operation == "ratio":
        if len(mentions) != 1 or not _validated_period(mentions[0], reference) or category or channel:
            return None
        return {"operation": "ratio", "ratio": ratio_kind, "periods": mentions, "reference_date": reference.isoformat()}

    metric = _metric(q)
    if operation == "filter":
        if metric not in {"revenue", "gross_profit"} or len(mentions) != 1 or not _validated_period(mentions[0], reference):
            return None
        if re.search(r"\bkenh\b", q) and channel is None:
            return None
        return {"operation": "filter", "metric": metric, "periods": mentions, "category": category,
                "channel": channel, "reference_date": reference.isoformat()}

    if metric is None:
        return None
    high = re.search(r"\b(?:cao nhat|lon nhat|nhieu nhat|nhieu don nhat)\b", q)
    low = re.search(r"\b(?:thap nhat|it nhat|it don nhat)\b", q)
    if high and low:
        return None
    direction = "asc" if low else "desc"
    count_match = re.search(r"\btop\s*([1-5])\b|\b([1-5])\s+(?:thang|kenh|danh muc|nhom)\b", q)
    count_words = re.search(r"\b(mot|hai|ba)\s+(?:thang|kenh|danh muc|nhom)\b", q)
    count = int(count_match[1] or count_match[2]) if count_match else {"mot": 1, "hai": 2, "ba": 3}[count_words[1]] if count_words else 1
    if re.search(r"\bthang\s+(?:nao|cao nhat|thap nhat)\b|\b(?:\d+|mot|hai|ba)\s+thang\b", q):
        entity = "month"
    elif re.search(r"\b(?:danh muc|nhom hang)\b", q):
        entity = "category"
    elif re.search(r"\bkenh\b", q):
        entity = "channel"
    else:
        return None
    if entity == "month":
        quarter_only = len(mentions) == 1 and "-Q" in mentions[0]
        candidates = _ranking_months(q, scope, reference) if quarter_only or not mentions else None
        if not candidates or metric not in {"revenue", "gross_profit", "cost", "expenses", "orders", "refunds"}:
            return None
        if (category or channel) and metric not in {"revenue", "gross_profit"}:
            return None
        return {"operation": "rank", "metric": metric, "entity": entity, "periods": candidates,
                "category": category, "channel": channel, "whole_year": not quarter_only,
                "direction": direction, "limit": count, "reference_date": reference.isoformat()}
    if category or channel or metric not in {"revenue", "gross_profit"} or count > 3:
        return None
    if len(mentions) != 1 or not _validated_period(mentions[0], reference):
        return None
    return {"operation": "rank", "metric": metric, "entity": entity, "periods": mentions,
            "direction": direction, "limit": count, "reference_date": reference.isoformat()}


def _label(period: str) -> str:
    if "-Q" in period:
        year, q = period.split("-Q")
        return f"quý {q}/{year}"
    year, month = period.split("-")
    return f"tháng {int(month)}/{year}"


def _filter_label(request: dict) -> str:
    category, channel = request.get("category"), request.get("channel")
    return " ".join(x for x in (FILTER_LABELS.get(category), f"qua {FILTER_LABELS[channel]}" if channel else None) if x)


def _format(value, unit: str, decimals: int = 0) -> str:
    if decimals:
        shown = f"{value:,.{decimals}f}".replace(",", "_").replace(".", ",").replace("_", ".")
        return shown + ("%" if unit == "%" else f" {unit}")
    shown = f"{int(value):,}".replace(",", ".")
    return shown + (f" {unit}" if unit else "")


def _analyze(db_path, period: str) -> dict:
    from .business_analysis import analyze_business

    start, end, months = _range(period)
    report = analyze_business(str(db_path), start.isoformat(), end.isoformat())
    present = {r["month"] for r in report["monthly"]}
    if not report["quality"]["source_rows"] or any(month not in present for month in months):
        raise ValueError("Kỳ thiếu giao dịch hoặc chưa đủ dữ liệu tháng.")
    return report


def _value(report: dict, metric: str):
    section, field, _, unit = FIELD_BY_METRIC[metric]
    return (report.get(section) or {}).get(field), unit


def _source(period: str, metric: str) -> dict:
    return {"source": "financial_ledger (SQL)", "period": period, "metric": metric}


def _category_value(report: dict, category: str, metric: str):
    key = "revenue" if metric == "revenue" else "gross_profit"
    return sum(row[key] for row in report["products"] if row.get("category") == category)


def _group_value(db_path, report: dict, period: str, category: str | None, channel: str | None, metric: str):
    key = "net_revenue" if metric == "revenue" else "gross_profit"
    if category and channel:
        start, end, _ = _range(period)
        query = """SELECT COALESCE(SUM(l.revenue),0) AS net_revenue,
                    COALESCE(SUM(l.revenue-l.cost),0) AS gross_profit
                 FROM financial_ledger l
                 LEFT JOIN returns r ON l.kind='return' AND r.id=l.id
                 JOIN order_items i ON i.id=CASE WHEN l.kind='sale' THEN l.id ELSE r.item_id END
                 JOIN orders o ON o.id=i.order_id JOIN products p ON p.sku=l.sku
                 WHERE l.day>=? AND l.day<? AND p.category=? AND o.channel=?"""
        uri = Path(db_path).resolve().as_uri() + "?mode=ro"
        with sqlite3.connect(uri, uri=True) as con:
            row = con.execute(query, (start.isoformat(), end.isoformat(), category, channel)).fetchone()
        return row[0 if metric == "revenue" else 1]
    if channel:
        item = next((x for x in (report.get("financial") or {}).get("channels", []) if x["channel"] == channel), None)
        return item[key] if item else 0
    return _category_value(report, category, metric)


def _calculate(db_path, request: dict):
    op = request["operation"]
    rows: list[dict] = []
    sources: list[dict] = []
    if op == "target_difference":
        period = request["periods"][0]
        report = _analyze(db_path, period)
        actual = _value(report, "revenue")[0]
        uri = Path(db_path).resolve().as_uri() + "?mode=ro"
        with sqlite3.connect(uri, uri=True) as con:
            target = con.execute("SELECT revenue FROM monthly_targets WHERE month=?", (period,)).fetchone()
        if target is None or target[0] is None:
            raise ValueError("Monthly target is unavailable")
        planned = target[0]
        delta = actual - planned
        label = _label(period)
        direction = "cao hơn" if delta > 0 else "thấp hơn" if delta < 0 else "bằng"
        text = (f"Doanh thu thuần {label}: thực hiện {_format(actual, 'đ')}; "
                f"kế hoạch {_format(planned, 'đ')}; chênh lệch (thực hiện trừ kế hoạch): "
                f"{_format(delta, 'đ')} ({direction}).")
        rows = [{"period": period, "actual": actual, "target": planned, "value": delta, "unit": "đ"}]
        sources = [{"source": "financial_ledger + monthly_targets (SQL)", "period": period, "metric": "revenue_vs_target"}]
        return text, rows, sources

    if op == "total":
        periods = request["periods"]
        reports = [_analyze(db_path, period) for period in periods]
        values = [_value(report, request["metric"])[0] for report in reports]
        if any(value is None for value in values):
            raise ValueError("Metric unavailable for requested period")
        total = sum(values)
        name = FIELD_BY_METRIC[request["metric"]][2]
        period_names = ", ".join(_label(period) for period in periods)
        text = f"Tổng {name[:1].lower() + name[1:]} gộp {period_names}: {_format(total, FIELD_BY_METRIC[request['metric']][3])}."
        rows = [{"period": period, "value": value, "unit": FIELD_BY_METRIC[request["metric"]][3]} for period, value in zip(periods, values)]
        rows.append({"period": "total", "value": total, "unit": FIELD_BY_METRIC[request["metric"]][3]})
        sources = [_source(period, request["metric"]) for period in periods]
        return text, rows, sources

    if op in {"difference", "pct_change"}:
        periods = request["periods"]
        if periods[0] == periods[1]:
            return "Hai kỳ được hỏi giống nhau nên không thể tính chênh lệch.", rows, sources
        reports = [_analyze(db_path, p) for p in periods]
        filtered = request.get("category") or request.get("channel")
        values = [_group_value(db_path, report, period, request.get("category"), request.get("channel"), request["metric"]) if filtered
                  else _value(report, request["metric"])[0] for report, period in zip(reports, periods)]
        unit = _value(reports[0], request["metric"])[1]
        name = " ".join(x for x in (FIELD_BY_METRIC[request["metric"]][2], _filter_label(request)) if x)
        if op == "pct_change":
            if values[1] == 0:
                return "Mẫu số của kỳ so sánh bằng 0 nên không thể tính phần trăm thay đổi.", rows, sources
            result = (values[0] - values[1]) / values[1] * 100
            rows = [{"period": p, "value": v, "unit": unit} for p, v in zip(periods, values)]
            rows.append({"period": "thay đổi", "value": round(result, 2), "unit": "%"})
            first, second = _label(periods[0]), _label(periods[1])
            text = f"{name} {first}: {_format(values[0], unit)}; {second}: {_format(values[1], unit)}; thay đổi so với {second}: {_format(result, '%', 2)} ({'tăng' if result > 0 else 'giảm' if result < 0 else 'không đổi'})."
        else:
            result = values[0] - values[1]
            rows = [{"period": p, "value": v, "unit": unit} for p, v in zip(periods, values)]
            rows.append({"period": "chênh lệch", "value": result, "unit": unit})
            first, second = _label(periods[0]), _label(periods[1])
            text = f"{name} {first}: {_format(values[0], unit)}; {second}: {_format(values[1], unit)}; chênh lệch ({first} trừ {second}): {_format(result, unit)} ({first} {'cao hơn' if result > 0 else 'thấp hơn' if result < 0 else 'bằng'})."
        sources = [_source(period, request["metric"]) for period in periods]
        return text, rows, sources

    if op == "ratio":
        period = request["periods"][0]
        report = _analyze(db_path, period)
        financial = report.get("financial") or {}
        ratio = request["ratio"]
        if ratio == "gross_margin":
            numerator, denominator = report["totals"]["gross_profit"], report["totals"]["revenue"]
            formula = "lãi gộp / doanh thu thuần"
        elif ratio == "revenue_per_order":
            numerator, denominator = report["totals"]["revenue"], financial.get("orders", 0)
            formula = "doanh thu thuần / số đơn"
        elif ratio == "refund_share_of_revenue":
            numerator, denominator = financial.get("refunds", 0), report["totals"]["revenue"]
            formula = "tiền hoàn / doanh thu thuần"
        elif ratio == "gross_profit_per_order":
            numerator, denominator = report["totals"]["gross_profit"], financial.get("orders", 0)
            formula = "lãi gộp / số đơn"
        elif ratio == "returns_per_order":
            numerator, denominator = financial.get("return_units", 0), financial.get("orders", 0)
            formula = "sản phẩm hoàn trả / số đơn"
        else:
            start, end, _ = _range(period)
            numerator = financial.get("return_units", 0)
            query = "SELECT COALESCE(SUM(quantity),0) FROM financial_ledger WHERE kind='sale' AND day>=? AND day<?"
            with sqlite3.connect(Path(db_path).resolve().as_uri() + "?mode=ro", uri=True) as con:
                denominator = con.execute(query, (start.isoformat(), end.isoformat())).fetchone()[0]
            formula = "sản phẩm hoàn trả / tổng sản phẩm đã bán"
        if denominator == 0:
            return f"Mẫu số của {formula} trong {_label(period)} bằng 0 nên không thể tính tỷ lệ.", [], []
        if ratio in {"gross_profit_per_order", "revenue_per_order"}:
            result = numerator / denominator
            rows = [{"period": period, "numerator": numerator, "denominator": denominator, "value": round(result) if ratio == "revenue_per_order" else round(result, 2), "unit": "đ/đơn"}]
            label = "Lãi gộp" if ratio == "gross_profit_per_order" else "Doanh thu thuần"
            text = f"{label} bình quân mỗi đơn {_label(period)}: {_format(result, 'đ/đơn', 0 if ratio == 'revenue_per_order' else 2)} ({label.lower()} {_format(numerator, 'đ')} / {denominator} đơn)."
        else:
            result = numerator / denominator * 100
            rows = [{"period": period, "numerator": numerator, "denominator": denominator, "value": round(result, 2), "unit": "%"}]
            unit = "đ" if ratio in {"gross_margin", "refund_share_of_revenue"} else ""
            text = f"Tỷ lệ {formula} {_label(period)}: {_format(numerator, unit)} / {_format(denominator, unit)} = {_format(result, '%', 2)}."
        return text, rows, [_source(period, ratio)]

    if op == "filter":
        period = request["periods"][0]
        report = _analyze(db_path, period)
        value = _group_value(db_path, report, period, request.get("category"), request.get("channel"), request["metric"])
        name = FIELD_BY_METRIC[request["metric"]][2]
        rows = [{"period": period, "category": request.get("category"), "channel": request.get("channel"), "value": value, "unit": "đ"}]
        text = f"{name} {_filter_label(request)} {_label(period)}: {_format(value, 'đ')} (đã tính theo sổ cái, gồm cả dòng hoàn trả)."
        return text, rows, [_source(period, request["metric"])]

    if op == "rank":
        metric, entity = request["metric"], request["entity"]
        periods = request["periods"]
        ranked: list[tuple[str, float]] = []
        if entity == "month":
            for period in periods:
                report = _analyze(db_path, period)
                if request.get("category") or request.get("channel"):
                    value = _group_value(db_path, report, period, request.get("category"), request.get("channel"), metric)
                else:
                    value = _value(report, metric)[0]
                ranked.append((period, value))
        else:
            period = periods[0]
            report = _analyze(db_path, period)
            if entity == "channel":
                key = "net_revenue" if metric == "revenue" else "gross_profit"
                ranked = [(x["channel"], x[key]) for x in (report.get("financial") or {}).get("channels", [])]
            else:
                key = "revenue" if metric == "revenue" else "gross_profit"
                grouped: dict[str, float] = {}
                for product in report["products"]:
                    category = product.get("category")
                    grouped[category] = grouped.get(category, 0) + product[key]
                ranked = list(grouped.items())
        reverse = request["direction"] == "desc"
        ranked.sort(key=lambda pair: ((-pair[1]) if reverse else pair[1], pair[0]))
        if not ranked:
            raise ValueError("Không có nhóm dữ liệu để xếp hạng.")
        count = min(request["limit"], len(ranked))
        selected = ranked[:count]
        selected_values = {value for _, value in selected}
        tied_values = {value for value in selected_values if sum(1 for _, v in ranked if v == value) > 1}
        tied = [item for item in ranked if item[1] in tied_values]
        selected = [item for item in ranked if item in selected or item in tied]
        rows = [{"label": label, "value": value, "unit": FIELD_BY_METRIC[metric][3]} for label, value in selected]
        period_label = "" if entity == "month" else f" trong {_label(periods[0])}"
        ordering = "cao xuống thấp" if reverse else "thấp lên cao"
        name = " ".join(x for x in (FIELD_BY_METRIC[metric][2], _filter_label(request)) if x)
        text = f"Xếp hạng {name}{period_label}, từ {ordering}: " + "; ".join(
            f"{_label(label) if entity == 'month' else FILTER_LABELS.get(label, label)}: {_format(value, FIELD_BY_METRIC[metric][3])}" for label, value in selected
        ) + "."
        if request.get("whole_year") and len(periods) < 12:
            text += f" Dữ liệu năm {periods[0][:4]} chỉ có từ {_label(periods[0])} đến {_label(periods[-1])}."
        if tied_values:
            text += " Có mục đồng hạng ở vị trí được hỏi; đã liệt kê toàn bộ mục đồng hạng."
        sources = [_source(period, metric) for period in periods]
        return text, rows, sources

    raise ValueError("Dạng tính chưa được hỗ trợ.")


def answer_calc(db_path, request) -> dict:
    """Compute only a request produced by calc_request and return cited SQL evidence."""
    if not isinstance(request, dict):
        return {"text": "Chưa đủ thông tin để tính.", "rows": [], "sources": []}
    try:
        text, rows, sources = _calculate(db_path, request)
    except (KeyError, TypeError, ValueError, sqlite3.Error, OSError):
        return {"text": "Dữ liệu kỳ này không đầy đủ hoặc chưa thể tính chắc chắn.", "rows": [], "sources": []}
    return {"text": text, "rows": rows, "sources": sources}
