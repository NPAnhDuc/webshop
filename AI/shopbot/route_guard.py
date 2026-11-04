"""Conservative rules for clear authorization and routing boundaries."""

import re
from functools import lru_cache
from pathlib import Path

from .retrieval import normalize


def _has(text, phrases):
    return any(re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text) for phrase in phrases)


def _known_product_mentioned(text, known_products):
    for product in known_products:
        name = normalize(str(product)).strip()
        if name and re.search(r"(?<!\w)" + re.escape(name) + r"(?!\w)", text):
            return True
    return False


@lru_cache(maxsize=1)
def corpus_words():
    """Every word in the shop's documents; a brand outside them cannot be something we sell."""
    data = Path(__file__).resolve().parents[1] / "data"
    words = set()
    for folder in (data / "unstructured/managed", data / "business_sql/scenario_v1/documents"):
        for path in folder.rglob("*.md"):
            words.update(re.findall(r"[a-z]+", normalize(path.read_text(encoding="utf-8"))))
    return frozenset(words)


def _unseen_model(text, known_products, vocabulary):
    """A word no document contains, followed by a model number: "qirava vento 14", "tavrix 15g"."""
    if not vocabulary or _known_product_mentioned(text, known_products):
        return False
    pattern = r"(?<!\w)([a-z]{4,})(?: [a-z]{2,})? [a-z]*\d[a-z0-9]*(?!\w)"
    return any(found[1] not in vocabulary for found in re.finditer(pattern, text))


def _has_period(text):
    return bool(re.search(r"\b(?:thang|quy)\s*(?:[1-9]|1[0-2]|[1-4])\b|\b20\d{2}\b", text))


def _clear_private_customer_request(text):
    private_fields = ("dia chi", "so dien thoai", "thong tin lien he", "lich su mua", "don hang", "email")
    third_party = ("khach khac", "nguoi khac", "khach vua mua", "khach vua dat", "khach mua", "nguoi vua mua", "cua khach", "cua nguoi")
    return _has(text, private_fields) and _has(text, third_party)


def _asks_for_internal_finance(text):
    # "biên lai" alone is a receipt; only "biên lãi trên / gộp" is a margin.
    return _has(text, (
        "gia nhap", "gia von", "loi nhuan", "lai lo", "bao cao loi lo",
        "doanh thu cua shop", "doanh thu shop", "chi phi cua shop",
        "bien lai tren", "bien lai gop",
    ))


def _asks_for_internal_people(text):
    """Staff pay, someone else's password, the shop's best customers, the shop's own spending."""
    staff_pay = re.search(r"\bluong (?:cua )?(?:tung |cac |moi )?(?:nhan vien|nguoi ban|quan ly|ky thuat vien)\b", text)
    password = _has(text, ("mat khau",)) and _has(text, ("khach", "nguoi khac", "nhan vien", "doanh nghiep", "quan tri"))
    top_buyers = re.search(r"\bkhach (?:hang )?(?:mua|chi) (?:nhieu|tieu nhieu) nhat\b|\bai la khach\b", text)
    shop_spend = re.search(r"\b(?:shop|cua hang) (?:chi|tieu|dau tu) (?:bao nhieu|bn|het)\b", text) and _has(text, ("quang cao", "marketing"))
    return bool(staff_pay or password or top_buyers or shop_spend)


def _asks_for_staff(text):
    """A request to be put through to a person, not a question about how staff work."""
    staff = _has(text, ("nhan vien", "ky thuat vien", "tu van vien", "nguoi that", "nguoi cua shop", "nguoi ban that", "quan ly cua hang"))
    contact = re.search(r"\b(?:gap|noi chuyen|ket noi|noi may|goi lai|goi cho (?:minh|toi))\b|\bchuyen (?:giup )?(?:minh |toi )?(?:qua|sang)\b", text)
    return bool(staff and contact) and not _has(text, ("the nao", "bao lau", "quy trinh", "chinh sach", "co phai"))


def _places_order(text):
    """Ordering, a deposit or a payment made through the chat; the shop takes orders on its product pages."""
    order = re.search(
        r"\bdat (?:mua )?(?:giup|ho)\b|\b(?:gui|chuyen) (?:tien )?coc\b|\b(?:da|vua) chuyen khoan\b"
        r"|\bchuyen khoan (?:roi|sau)\b|\bmai (?:minh |toi )?chuyen khoan\b|\b(?:chot|len|xac nhan) don\b", text)
    return bool(order) and not _has(text, ("the nao", "lam sao", "cach", "quy trinh", "huong dan", "bao lau", "khi nao", "chinh sach"))


# A product the user points at without naming it: "con màu đen đó", "chiếc nhỏ hơn", "cái ấy".
POINTED = re.compile(
    r"\b(?:cai|con|chiec|may|mau|san pham) ay\b"
    r"|\b(?:con|chiec|cai|ban) mau \w+ (?:do|kia|ay)\b"
    r"|\b(?:con|chiec|cai) (?:nho|lon|re|dat|nhe|nang) hon\b(?! \d)")
# Something shown earlier or outside the chat: "cái link mình vừa gửi", "con lúc nãy mình hỏi".
EARLIER = re.compile(
    r"\b(?:con|cai|chiec|mau|may|san pham|laptop|card|vga|man hinh)(?: \w+){0,4}? (?:luc truoc|luc nay|hoi nay|vua noi|vua nhac|vua hoi|dang xem)\b"
    r"|\b(?:gui|dan) (?:cai )?link\b|\blink(?: \w+){0,2}? (?:vua |da )?gui\b")
# An admin pointing at a report or target without naming it: "báo cáo ấy", "chỉ tiêu kia".
ADMIN_POINTED = re.compile(r"\b(?:bao cao|chi tieu|so lieu|con so|ke hoach|tai lieu|muc) (?:ay|kia)\b")


def _names_a_model(text):
    """"Máy vừa nói là Laptop Z710": a model code in the question names the product itself."""
    codes = re.findall(r"(?<!\w)(?=[a-z0-9-]*[a-z])(?=[a-z0-9-]*\d)[a-z0-9-]{3,}(?!\w)", text)
    units = re.compile(r"\d+(?:gb|tb|mb|hz|mhz|ghz|wh|w|fps|mah|inch|k)|ddr\d+|usb\d+|wifi\d+|pcie\d+")
    return any(not units.fullmatch(code) for code in codes)


def _unknown_brand(question, text, known_products, vocabulary):
    """"Hãng Zenvor", "Novatek Rook": a brand no document mentions, asked about a product attribute."""
    if not vocabulary or _known_product_mentioned(text, known_products):
        return False
    if not _has(text, ("ram", "pin", "man hinh", "cpu", "chip", "nang", "bao hanh", "cau hinh", "thong so", "ssd", "card", "vga")):
        return False
    names = [m[1] for m in re.finditer(r"(?i)\bhãng\s+([a-z]{3,})\b", question)]
    names += [w for pair in re.findall(r"\b([A-Z][a-z]{2,}) ([A-Z][a-z]{2,})\b", question) for w in pair]
    return any(normalize(name) not in vocabulary for name in names)


def _is_specific_unknown_product(text, known_products):
    if _known_product_mentioned(text, known_products):
        return False
    if not _has(text, (
        "shop co ban", "shop co mau", "shop co dong", "shop ban",
        "co ban mau", "co ban dong", "shop co san pham",
    )):
        return False

    known_tokens = {
        token
        for name in known_products
        for token in re.findall(r"[a-z0-9-]+", normalize(str(name)))
    }
    candidates = re.findall(r"(?<!\w)[a-z][a-z0-9-]*\d[a-z0-9-]*(?!\w)", text)
    common_specs = re.compile(
        r"^(?:i[3579]|[1-9]\d?(?:gb|tb|hz|w|mah)|20\d{2}|2k|4k|fhd|uhd|qhd)$"
    )
    for candidate in candidates:
        if len(candidate) < 3 or common_specs.fullmatch(candidate):
            continue
        if candidate in known_tokens:
            continue
        if re.fullmatch(r"(?:rtx|gtx|rx|ryzen|core|ultra|arc)\d+", candidate):
            continue
        return True
    return False


def _admin_requests_calculation(text):
    explicit_math = _has(text, (
        "tinh toan", "tinh giup", "tinh tong", "tinh chenhlech",
        "chenh lech bao nhieu", "xep hang", "tinh phan tram",
    ))
    compare_periods = (
        _has(text, ("so voi",))
        and _has(text, ("thang", "quy", "nam"))
        and _has(text, ("phan tram", "tang", "giam", "chenh lech"))
    )
    # "Doanh thu được tính thế nào?" asks for the method, which a document can answer.
    calculation_word = (
        _has(text, ("tinh",))
        and _has(text, ("loi nhuan", "gia von", "doanh thu", "chenh lech", "phan tram"))
        and not _has(text, ("tinh hinh", "tinh nang", "tinh the nao", "tinh ra sao", "tinh sao", "cach tinh", "duoc tinh", "cong thuc"))
    )
    cost_delta = (
        _has(text, ("chenh lech",))
        and _has(text, ("gia von", "gia nhap", "loi nhuan"))
        and _has(text, ("thang", "quy", "nam"))
    )
    return explicit_math or compare_periods or calculation_word or cost_delta


def _admin_requests_write(text):
    send_message = (
        _has(text, ("gui email", "gui tin nhan", "gui thong bao"))
        or (_has(text, ("gui",)) and _has(text, ("toan bo khach", "nhom quan ly")))
    )
    write_data = _has(text, (
        "ghi vao he thong", "ghi vao database", "cap nhat du lieu",
        "them vao database", "xoa du lieu", "sua du lieu", "nhap lieu vao",
        "danh dau don hang", "huy don hang", "xuat don hang",
    ))
    return send_message or write_data


def _needs_admin_clarification(text):
    if _has_period(text) or _has(text, ("chinh sach", "quy dinh", "tai lieu")):
        return False
    # "Tháng nào doanh thu cao nhất?" names what it asks about.
    if _has(text, ("doanh thu", "loi nhuan", "lai", "chi phi", "gia von", "cao nhat", "thap nhat", "nhieu nhat", "it nhat")):
        return False
    words = text.split()
    if len(words) > 6:
        return False
    return _has(text, (
        "bao cao thang nao", "bao cao quy nao", "thang nao", "quy nao",
        "cai nao", "muc nao", "con muc nao", "con so nao", "so nao",
    )) or (
        _has(text, ("cai",)) and _has(text, ("so",)) and len(words) <= 6
    ) or (
        _has(text, ("con so",)) and _has(text, ("tang", "giam")) and len(words) <= 7
    ) or (
        _has(text, ("bao cao",)) and _has(text, ("ay",)) and len(words) <= 8
    ) or (
        _has(text, ("so day",)) and len(words) <= 6
    ) or (
        _has(text, ("thang kia",)) and _has(text, ("nao",)) and len(words) <= 5
    )


def guard(question, role, has_history=False, known_products=(), vocabulary=(), has_subject=None):
    """Return a guard action only when the request clearly crosses a boundary.

    has_subject: a product is bound from an earlier turn. A turn about a policy is history
    but names no product, so "chiếc máy vừa nói" after it still needs a name.
    """
    text = normalize(str(question or ""))
    if not text:
        return None
    if has_subject is None:
        has_subject = has_history

    if role == "customer":
        # A personal history or a store address is ordinary customer support.
        personal = _has(text, ("cua minh", "cua toi", "lich su mua hang cua minh", "lich su mua hang cua toi"))
        # "giá nhập khẩu" is about imported goods, not the shop's cost.
        if _has(text.replace("gia nhap khau", " "), ("gia nhap", "gia von")):
            return "denied"
        if not personal and (
            (_asks_for_internal_finance(text) and _has(text, ("bao nhieu", "xem", "cho toi", "bao cao", "cua shop")))
            or _clear_private_customer_request(text)
            or (_has(text, ("shop",)) and _has(text, ("nhap", "lai", "loi")) and _has(text, ("bao nhieu",)) and not _has(text, ("lai suat", "tra gop")))
            or _asks_for_internal_people(text)
        ):
            return "denied"

        if _places_order(text):
            return "live_product"
        if _asks_for_staff(text):
            return "handoff"

        hold_request = (
            (
                _has(text, ("giu hang", "giu lai hang", "giu san pham", "giu chiec", "dat cho truoc", "giu cho toi", "giu cho minh", "giu giup", "giu ho", "giu toi", "khoa gia"))
                or (_has(text, ("giu lai",)) and _has(text, ("san pham", "hang", "chiec")))
                or (_has(text, ("dat coc",)) and _has(text, ("giup", "qua chat", "cho minh", "cho toi")))
            )
            and not _has(text, ("tu van", "nen mua", "goi y"))
        )
        if hold_request:
            return "live_product"

        deictic = _has(text, (
            "cai nay", "cai do", "con nay", "con do", "mau nay", "mau do",
            "san pham nay", "san pham do", "may nay", "may do", "no kia",
            "mau kia", "con kia", "cai kia", "san pham kia", "may luc nay",
        )) or re.match(r"(?:con )?no\b", text) or POINTED.search(text)
        if not _known_product_mentioned(text, known_products) and (
            (not has_history and deictic) or (not has_subject and EARLIER.search(text) and not _names_a_model(text))
        ):
            return "clarify"

        if (_is_specific_unknown_product(text, known_products) or _unseen_model(text, known_products, vocabulary)
                or _unknown_brand(question, text, known_products, vocabulary)):
            return "unknown_product"

    if role == "admin":
        if _admin_requests_calculation(text) and not _has(text, ("chi doc", "khong tinh", "khong can tinh", "doc so lieu")):
            return "deferred"
        if _admin_requests_write(text):
            return "deferred"
        if not has_history and (_needs_admin_clarification(text) or (ADMIN_POINTED.search(text) and not _has_period(text))):
            return "clarify"

    return None
