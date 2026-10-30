"""Conservative lexical preflight for explicit unsupported admin actions.

This is a baseline, not a general Vietnamese intent parser. It prevents a
known action from being replaced by source inspection. It grants no authority
and never executes a tool. Unmatched input still uses the semantic planner.
"""
import re
from .catalog_planner import plain

_TRANSFORM=re.compile(r'\b(?:lam sach|clean|chuan hoa|xoa|ghi de|thay doi|loai bo|nhap|doc|sua|gop|tach)\b')
_DATA=re.compile(r'\b(?:excel|file|bang|du lieu|dong|ban sao)\b')
_READ_FILE=re.compile(r'\b(?:file|excel)\b|\bbang excel\b')
_EXPLAIN=re.compile(r'^\s*(?:giai thich|dinh nghia|thuat ngu|the nao la)\b')


def unsupported_capability(question):
    """Return an explicit unsupported capability, or None (no override).

    Negation carries across coordinated verbs ("không xóa hay sửa") until a
    contrast/restriction marker or sentence boundary. A negated write clause
    never cancels an earlier affirmative clean-copy request.
    """
    text=plain(question)
    if _EXPLAIN.search(text):return None
    # Keep separators so negation scope cannot leak across "nhưng/chỉ".
    parts=re.split(r'([,;.!?]|\b(?:nhung|chi|roi|va|hay|hoac)\b)',text)
    negative=False
    for part in parts:
        if part in ('nhung','chi','roi','.', ';','!','?'):
            negative=False
            continue
        if part in (',','va','hay','hoac'):continue
        for action in _TRANSFORM.finditer(part):
            prefix=part[:action.start()]
            negations=list(re.finditer(r'\b(?:khong|dung|chua can)\b',prefix))
            if negations:negative=True
            if negative:continue
            verb=action.group()
            if not _DATA.search(text):continue
            if verb=='doc' and not _READ_FILE.search(part):continue
            if verb=='nhap' and not _READ_FILE.search(text):continue
            return 'file.transform'
    # Ranking/breakdown needs sales facts, not a count of catalog SKUs.
    sales=re.search(r'\b(?:doanh thu|doanh so|ban chay|ban nhieu|so luong ban)\b',text)
    product=re.search(r'\b(?:sku|san pham|mat hang|tung mau|tung may|laptop)\b',text)
    rank=re.search(r'\b(?:top\s*\d*|xep hang|cao nhat|nhieu nhat|ban chay|tung mau|tung san pham|tung sku|theo sku)\b',text)
    if sales and product and rank:
        # No override when ranking itself is explicitly negated. Do not turn
        # "không ghi đè" into a negation of a separate sales request.
        rank_prefix=text[max(0,rank.start()-35):rank.start()]
        if not re.search(r'\b(?:khong|dung)\b[^,;.!?]*$',rank_prefix):
            return 'sales.rank'
    return None
