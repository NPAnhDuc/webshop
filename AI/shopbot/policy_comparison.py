"""Read-only, typed numeric comparison against an explicitly sourced policy cap.

This operation never approves a discount, infers a margin or changes a price.
The conservative adapter supports one current, unqualified discount cap only.
"""
import re
from datetime import date
from decimal import Decimal
from .retrieval import normalize


def compare_policy_percentage(requested, cap):
    left, right = Decimal(requested), Decimal(cap)
    if not all(x.is_finite() and 0 <= x <= 100 for x in (left, right)):
        raise ValueError('Percentage must be finite and between zero and 100')
    delta = left - right
    return dict(operation='compare_policy_percentage', metric='discount_rate',
                requested_percent=str(left), cap_percent=str(right),
                relation='above' if delta > 0 else 'equal' if delta == 0 else 'below',
                absolute_difference_percentage_points=str(abs(delta)),
                approval_granted=False, mutation_allowed=False)


def current_discount_comparison(question, role, scope, fragments, today):
    """Bind literal user operand and current source field; abstain on ambiguity."""
    q = normalize(question)
    if role != 'admin' or scope.get('months') or scope.get('quarters'):
        return None
    if not re.search(r'\b(?:tran|muc toi da|doi chieu)\b', q):
        return None
    if re.search(r'\b(?:gop|cong don|loi nhuan|lai|bien gop|gia ban sau|nhom|sku|laptop|gaming|neu|khi)\b', q):
        return None
    rates = re.findall(r'(-?\d+(?:[.,]\d+)?)\s*%', q)
    if not re.search(r'\bgiam(?=\s|[-\d,])', q) or len(rates) != 1:
        return None
    requested = rates[0].replace(',', '.')
    candidates = []
    for identifier, fragment in fragments.items():
        source = fragment['source']
        if (source.get('doc_type') != 'policy' or source.get('status') != 'approved'
                or source.get('audience') != 'admin'
                or source.get('authority') not in ('shop_document', 'shop_policy', 'synthetic_shop_document')):
            continue
        try:
            start = date.fromisoformat(source['effective_from'])
            end = date.fromisoformat(source['effective_to']) if source.get('effective_to') else None
        except (KeyError, TypeError, ValueError):
            continue
        if start > today or (end is not None and end < today):
            continue
        # A quarterly/monthly policy is not a universal present cap merely
        # because its effective_to metadata was left open.
        label = normalize(source.get('title', '') + ' ' + source.get('heading_path', ''))
        if re.search(r'\b(?:q[1-4]|quy\s*[1-4]|thang\s*\d)\b', label):
            continue
        match = re.fullmatch(r'muc giam toi da\s+(\d+(?:[.,]\d+)?)\s*%\s*[.;]?(?:\s*khong cong don[.]?)?',
                             normalize(fragment['text']).strip())
        if match:
            candidates.append((identifier, match[1].replace(',', '.'), fragment))
    if not candidates or len({Decimal(item[1]) for item in candidates}) != 1:
        return None
    identifier, cap, fragment = candidates[0]
    try:
        result = compare_policy_percentage(requested, cap)
    except ValueError:
        return None
    return dict(result, evidence_id=identifier, source=fragment['source'], quote=fragment['text'],
                reference_date=today.isoformat())


def covered_comparison_parts(parts, calculation):
    if not calculation:
        return set()
    covered = set()
    for key, part in parts.items():
        text = normalize(part)
        if re.search(r'\b(?:duyet|phe duyet|loi nhuan|bien|gia ban|dieu kien|hop le|duoc phep)\b', text):
            continue
        if re.search(r'\b(?:tran|muc toi da)\b', text) or re.search(r'\bgiam\s*\d+(?:[.,]\d+)?\s*%', text):
            covered.add(key)
    return covered


def render_comparison(calculation):
    def number(value):
        return format(Decimal(value).normalize(), 'f').replace('.', ',')
    requested, cap = (number(calculation[k]) for k in ('requested_percent', 'cap_percent'))
    difference = number(calculation['absolute_difference_percentage_points'])
    relation = calculation['relation']
    detail = (f'cao hơn trần {cap}% là {difference} điểm phần trăm' if relation == 'above'
              else f'bằng trần {cap}%' if relation == 'equal'
              else f'thấp hơn trần {cap}% là {difference} điểm phần trăm')
    return f'Đối chiếu bằng phép tính: mức đề nghị {requested}% {detail}. Kết quả này chỉ đối chiếu trần, chưa xác nhận phê duyệt hoặc biên lợi nhuận sau giảm.'
