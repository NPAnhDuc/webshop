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
_EXPLAIN=re.compile(r'^\s*(?:giai thich|dinh nghia|thuat ngu|the nao la|vi sao|huong dan)\b')
_DEFINITION=re.compile(r'\b(?:la gi|nghia la gi)\s*$')
_COMPLETED_STATUS=re.compile(r'\bda\b.+\b(?:chua|khong)\s*$')
_SALES=re.compile(r'\b(?:doanh thu|doanh so|ban chay|ban nhieu|so luong ban)\b')
_PRODUCT=re.compile(r'\b(?:sku|san pham|mat hang|tung mau|tung may|laptop)\b')
_RANK=re.compile(r'\b(?:top\s*\d*|xep hang|cao nhat|nhieu nhat|ban chay|tung mau|tung san pham|tung sku|theo sku)\b')
_WRITE=re.compile(r'\b(?:update\s+(?:(?:gia|san pham)\b|[a-z_][\w.]*\s+set\b)|delete\s+from\b|insert\s+into\b|drop\s+(?:table|database|schema)\b|truncate\s+(?:table\s+)?[a-z_][\w.]*|alter\s+table\b)')


def unsupported_write(question):
    """Explicit SQL execution intent only; not a SQL parser or a write tool."""
    negative=False;descriptive=False
    parts=re.split(r'([,;.!?]|\b(?:nhung|chi|roi|va|hay|hoac)\b)',plain(question))
    for part in parts:
        if part in ('nhung','chi','roi','.', ';','!','?'):
            negative=False;descriptive=False;continue
        if part==',':descriptive=False;continue
        if part in ('va','hay','hoac'):continue
        descriptive=descriptive or bool(_EXPLAIN.search(part) or _DEFINITION.search(part) or _COMPLETED_STATUS.search(part))
        if descriptive:continue
        for action in _WRITE.finditer(part):
            prefix=part[:action.start()]
            if re.search(r'\b(?:khong|dung|chua can)\b',prefix):negative=True
            if negative:continue
            if not prefix.strip() or re.search(r'\b(?:chay|thuc thi|thuc hien|toi muon|giup toi)\b',prefix):
                return 'data.mutate'
    return None


def unsupported_capability(question):
    """Return an explicit unsupported capability, or None (no override).

    Negation carries across coordinated verbs ("không xóa hay sửa") until a
    contrast/restriction marker or sentence boundary. A negated write clause
    never cancels an earlier affirmative clean-copy request.
    """
    write=unsupported_write(question)
    if write:return write
    text=plain(question)
    # Keep separators so negation scope cannot leak across "nhưng/chỉ".
    parts=re.split(r'([,;.!?]|\b(?:nhung|chi|roi|va|hay|hoac)\b)',text)
    negative=False;descriptive=False
    for part in parts:
        if part in ('nhung','chi','roi','.', ';','!','?'):
            negative=False;descriptive=False
            continue
        if part==',':
            descriptive=False
            continue
        if part in ('va','hay','hoac'):continue
        # Mentioning a transformation as a definition, tutorial or completed
        # status is not requesting its execution. Scope ends before a separate
        # affirmative action; "explain ... then delete" must still be blocked.
        descriptive=descriptive or bool(_EXPLAIN.search(part) or _DEFINITION.search(part) or _COMPLETED_STATUS.search(part))
        if descriptive:continue
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
        # Evaluate the ranking verb in its own clause; a negated earlier
        # ranking or an explanation must not swallow a later real request.
        if _SALES.search(text) and _PRODUCT.search(text):
            for rank in _RANK.finditer(part):
                if re.search(r'\b(?:khong|dung)\b',part[:rank.start()]):negative=True
                if not negative:return 'sales.rank'
    return None
