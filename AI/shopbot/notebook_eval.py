"""Grade notebook-agent answers against values computed independently by SQL."""
import json
import re
import sqlite3
from decimal import Decimal,ROUND_HALF_UP
from pathlib import Path

from .notebook_agent import DATE_TOKENS,DB_PATH,NUMBER_TOKEN,ROOT
from .rag_answer import numbers

BANK_PATH=ROOT/'evaluation/notebook_agent_20261030/bank.json'
MONTH_PATTERNS=(r'(\d{4})-(\d{2})',r'(?<![\d/])(\d{1,2})/(\d{4})',r'tháng\s+(\d{1,2})\s+năm\s+(\d{4})')


def load_bank(split='all',path=BANK_PATH):
    return [item for item in json.loads(Path(path).read_text(encoding='utf-8')) if split=='all' or item['split']==split]


def expected_value(item,db_path=DB_PATH):
    conn=sqlite3.connect(Path(db_path).resolve().as_uri()+'?mode=ro',uri=True)
    try:rows=conn.execute(item['expected_sql']).fetchall()
    finally:conn.close()
    return [row[0] for row in rows] if item['kind']=='months' else rows[0][0]


def mentioned_months(text):
    found=[]
    for pattern in MONTH_PATTERNS:
        for match in re.finditer(pattern,text.lower()):
            first,second=match[1],match[2]
            found.append((match.start(),f'{first}-{second}' if len(first)==4 else f'{second}-{int(first):02d}'))
    return list(dict.fromkeys(month for _,month in sorted(found)))


def stated_numbers(text):
    """(value, negative) for each number, ignoring dates; the sign may be given in words."""
    lowered=DATE_TOKENS.sub(' ',text.lower());found=[]
    for match in NUMBER_TOKEN.finditer(lowered):
        value=next(iter(numbers(match[0])),None)
        if value is None:continue
        before=lowered[max(0,match.start()-24):match.start()]
        found.append((value,before.rstrip().endswith(('-','−')) or bool(re.search(r'giảm|âm|lỗ|thấp hơn|sụt',before))))
    return found


def rounded(value,places):
    return Decimal(repr(float(value))).quantize(Decimal(1).scaleb(-places),rounding=ROUND_HALF_UP)


def same_number(value,expected,places):
    return rounded(abs(value),places)==rounded(abs(expected),places) if places else abs(value)==abs(Decimal(int(expected)))


def grade(item,answer,expected=None):
    """Exact: the same months in the same order, or the same number with the same sign."""
    expected=expected_value(item) if expected is None else expected
    if item['kind']=='months':return mentioned_months(answer)==expected
    places=2 if item['kind']=='pct' else 0
    return any(same_number(value,expected,places) and negative==(expected<0) for value,negative in stated_numbers(answer))


def output_has_expected(item,evidence,expected):
    """Did any cell print the right value, whatever the final sentence said."""
    if item['kind']=='months':return all(month in evidence for month in expected)
    places=2 if item['kind']=='pct' else 0
    return any(same_number(value,expected,places) for value in numbers(evidence))
