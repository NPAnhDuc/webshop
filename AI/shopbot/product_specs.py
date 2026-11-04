"""Catalog fields of named products, read from their own records.

"X với Y: CPU khác gì nhau?" asks for one labelled line per product. A 4B selector
kept only one side, or a neighbouring field, and changed its pick between runs. The
lines are already labelled, so the server can pick them. Anything it is unsure of
(a field it cannot name, a yes/no check, an opinion) returns None for the selector.
"""
import re
from .retrieval import normalize

# Labels the catalog keeps in English, longest wording first so "loại RAM" is not read as "RAM".
ALIASES = [
    (r'card (?:do hoa )?roi hay tich hop', 'graphics memory accessibility'),
    (r'bo nho do hoa', 'graphics memory'),
    (r'card do hoa|chip do hoa|\bgpu\b', 'graphics chipset'),
    (r'kich thuoc man hinh', 'display size (inch)'),
    (r'do phan giai', 'display resolution'),
    (r'loai man hinh', 'display type'),
    (r'man hinh cam ung', 'touch screen'),
    (r'(?:so )?cong hdmi', 'hdmi port'),
    (r'cong (?:mang )?lan', 'lan'),
    (r'he dieu hanh', 'operating system'),
    (r'loai ssd|chuan ssd', 'installed ssd type'),
    (r'cong suat sac|bo sac', 'power adapter'),
    (r'loai ram', 'ram type'),
    (r'so nhan', 'processor core'),
    (r'\bcpu\b|vi xu ly', 'processor model'),
    (r'\bram\b', 'ram'),
]
# Vague labels would match ordinary words in a question.
TOO_VAGUE = {'loai', 'ten', 'hang', 'dung', 'nguon'}
NOT_A_LOOKUP = re.compile(r'\b(?:khong|giai thich|nghia la|vi sao|tai sao|y nghia|co nen|tot|manh|nen|hon|phu hop|'
                          r'du dung|dung duoc|tuong thich|gia|ton kho|con hang|dac biet)\b')
# "RAM hàn hay khe rời" asks how the memory is fitted; the size line does not answer that.
FITTING = re.compile(r'\b(?:han|khe|nang cap|gan them)\b')
LABELLED = re.compile(r'([^:]{2,50}):\s*\S')


def _label(fragment):
    title = fragment['source'].get('title', '')
    if not fragment['text'].startswith(title + ': '):
        return None
    found = LABELLED.match(fragment['text'][len(title) + 2:])
    return normalize(found[1]) if found else None


def _asked(q, labels):
    asked = []
    for alias, label in ALIASES:
        if label in labels and re.search(alias, q):
            asked.append(label)
            q = re.sub(alias, ' ', q)
    for label in sorted(labels - TOO_VAGUE, key=len, reverse=True):
        pattern = r'(?<!\w)' + re.escape(label) + r'(?!\w)'
        if re.search(pattern, q):
            asked.append(label)
            q = re.sub(pattern, ' ', q)
    return asked


def pick_fields(question, fragments, products):
    """One fragment per asked field per product, in product order, or None."""
    q = re.sub(r'^\s*(?:shop|ban|ad|admin|anh|chi|em) oi\b[\s,]*', '', normalize(question))
    for title in sorted(products, key=len, reverse=True):
        q = q.replace(normalize(re.sub(r'\s*\([^)]*\)', '', title)).strip(), ' ')
    if not 1 <= len(products) <= 3 or NOT_A_LOOKUP.search(q):
        return None
    table = {title: {} for title in products}
    for fragment in fragments:
        label = _label(fragment)
        title = fragment['source'].get('title')
        if label and title in table:
            table[title].setdefault(label, fragment)
    asked = _asked(q, set().union(*table.values()))
    # "CPU và pin" with only CPU recognised must not lose the second request.
    requests = [piece for piece in re.split(r'\bva\b|,|;', q) if re.search(r'\w{2}', piece)]
    if not asked or len(requests) > len(asked):
        return None
    if FITTING.search(q) and not any('khe' in label for label in asked):
        return None
    if any(label not in table[title] for title in products for label in asked):
        return None
    return [table[title][label] for title in products for label in asked]
