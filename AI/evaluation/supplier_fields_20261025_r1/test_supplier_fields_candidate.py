from datetime import date
import pytest
from shopbot.supplier_fields import requested_field,bind_supplier_evidence
from shopbot.grounded_rag import answer
from test_grounded_rag import source


@pytest.mark.parametrize('part,field',[
 ('MOQ nhà cung cấp bao nhiêu?','supplier_moq'),
 ('Số lượng đặt hàng tối thiểu là bao nhiêu?','supplier_moq'),
 ('Lead time nhà cung cấp bao lâu?','supplier_lead_time'),
 ('Thời gian giao hàng của nhà cung cấp là bao lâu?','supplier_lead_time'),
 ('MOQ là gì?',None),('Giải thích cách tính lead time',None),
 ('Lợi nhuận là bao nhiêu?',None),('Đơn hàng tối thiểu để miễn phí vận chuyển?',None),
])
def test_field_is_an_operand_not_a_guessed_answer(part,field):
 assert requested_field(part,part)==field


def fragment(text,kind='procedure',authority='shop_policy',title='Quy trình'):
 return dict(text=text,source=dict(doc_type=kind,authority=authority,title=title))


@pytest.mark.parametrize('text,kind,authority',[
 ('Nhà cung cấp lead time 4 ngày.','procedure','shop_policy'),
 ('MOQ ví dụ là 10 sản phẩm.','procedure','internal_methodology'),
 ('Bảo hành là 12 tháng.','policy','shop_policy'),
 ('MOQ lý thuyết là 10 sản phẩm.','glossary','reference'),
])
def test_related_field_or_methodology_does_not_supply_actual_supplier_moq(text,kind,authority):
 result,trace=bind_supplier_evidence('MOQ nhà cung cấp là bao nhiêu?',{'P1':'MOQ nhà cung cấp là bao nhiêu?'},
  {'P1':['x']},{'x':fragment(text,kind,authority)})
 assert result=={'P1':[]} and trace[0]['rejected_ids']==['x']


def test_customer_shipping_time_is_not_supplier_lead_time():
 result,_=bind_supplier_evidence('Lead time nhà cung cấp bao lâu?',{'P1':'Lead time nhà cung cấp bao lâu?'},
  {'P1':['x']},{'x':fragment('Thời gian giao hàng là 2 ngày.','policy',title='Giao hàng cho người mua')})
 assert result=={'P1':[]}


def test_single_attribute_comparison_can_inherit_field_but_mixed_cannot():
 assert requested_field('NCC A','NCC A và NCC B có cùng lead time không?')=='supplier_lead_time'
 assert requested_field('NCC A','NCC A có MOQ bao nhiêu và lead time bao lâu?') is None


def test_wrong_advisory_moq_evidence_becomes_missing_while_lead_time_is_preserved(monkeypatch):
 d=source('Nhà cung cấp có lead time 4 ngày.');d.update(doc_type='procedure',audience='admin',authority='shop_policy',title='Quy trình nhập hàng')
 monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:[d])
 def bad(system,payload,schema):
  return dict(action='answer',answers={k:[payload['fragments'][0]['id']] for k in payload['parts']},missing=[],negative=[])
 result=answer('Tài liệu có ghi MOQ không, hay chỉ có lead time?','admin',{},'unused',date(2026,10,24),model=bad)
 assert result['rag']['answerability']=='partial'
 assert any('MOQ' in part for part in result['rag']['unanswered'])
 assert 'lead time 4 ngày' in result['answer']
 assert result['rag']['part_evidence']['P1']==[] and result['rag']['part_evidence']['P2']
 assert result['rag']['field_bindings'][0]['rejected_ids']
