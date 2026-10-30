import re
import unicodedata

import pytest

from shopbot import notebook_eval as evaluation
from shopbot.notebook_agent import ROOT


def test_every_bank_question_has_a_computable_expected_value():
    bank=evaluation.load_bank()
    assert len(bank)>=20 and len({item['id'] for item in bank})==len(bank)
    for item in bank:assert evaluation.expected_value(item) not in (None,[])


def normalized(text):
    return re.sub(r'\W+',' ',unicodedata.normalize('NFC',text).casefold()).strip()


@pytest.mark.parametrize('path',['evaluation/heldout_20261028/bank.json','evaluation/expansion_20261029/bank.json'])
def test_bank_shares_no_question_with_locked_banks(path):
    text=normalized((ROOT/path).read_text(encoding='utf-8'))
    assert not [item['id'] for item in evaluation.load_bank() if normalized(item['question']) in text]


INT=dict(kind='int');PCT=dict(kind='pct');MONTHS=dict(kind='months')


@pytest.mark.parametrize('item,answer,expected,correct',[
    (INT,'Tổng là 1.234.567 đồng.',1234567,True),
    (INT,'Tổng là 1,234,567 VND',1234567,True),
    (INT,'Tổng là 1234567.0',1234567,True),
    (INT,'Tổng là 1.234.568 đồng.',1234567,False),
    (INT,'Khoảng 1,2 triệu đồng.',1234567,False),
    (INT,'Thấp hơn 500.000 đồng.',-500000,True),
    (INT,'Chênh lệch -500.000 đồng.',-500000,True),
    (INT,'Chênh lệch 500.000 đồng.',-500000,False),
    (PCT,'Tăng 12,34%.',12.3412,True),
    (PCT,'Tăng 12.34%.',12.3412,True),
    (PCT,'Tăng 12.3412%.',12.3412,True),
    (PCT,'Giảm 12,34%.',-12.3412,True),
    (PCT,'Tăng 12,34%.',-12.3412,False),
    (PCT,'Giảm 12,34%.',12.3412,False),
    (PCT,'Tăng 12,3%.',12.3412,False),
    (MONTHS,'Tháng cao nhất là 2026-03.',['2026-03'],True),
    (MONTHS,'Cao nhất là tháng 03/2026.',['2026-03'],True),
    (MONTHS,'Cao nhất là tháng 3 năm 2026.',['2026-03'],True),
    (MONTHS,'Lần lượt 2026-03, 2025-12 và 2026-06.',['2026-03','2025-12','2026-06'],True),
    (MONTHS,'Lần lượt 2025-12, 2026-03 và 2026-06.',['2026-03','2025-12','2026-06'],False),
    (MONTHS,'Tháng 2026-03 và 2026-04.',['2026-03'],False),
])
def test_grade_is_exact(item,answer,expected,correct):
    assert evaluation.grade(item,answer,expected) is correct
