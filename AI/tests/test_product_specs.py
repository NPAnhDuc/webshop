import pytest
from shopbot.product_specs import pick_fields


def fragments(title,**fields):
    source=dict(title=title,chunk_id=title)
    return [dict(text=f'{title}: {label}: {value}.',quotes=[f'{title}: {label}: {value}.'],source=source) for label,value in fields.items()]


A=fragments('Acer Swift',**{'Processor Model':'Ryzen 5','RAM':'8GB','RAM Type':'DDR4','Display Size (Inch)':'14','HDMI Port':'1'})
B=fragments('Dell Inspiron',**{'Processor Model':'Core i3','RAM':'16GB','Display Size (Inch)':'15.6'})
BOARD=fragments('Asus Prime',**{'socket':'AM5','số khe RAM':'4','RAM tối đa theo danh mục':'192 GB'})


def texts(lines):
    return [line['text'] for line in lines]


def test_compare_gives_the_field_of_both_products():
    assert texts(pick_fields('Acer Swift với Dell Inspiron: CPU khác gì nhau?',A+B,['Acer Swift','Dell Inspiron']))==[
        'Acer Swift: Processor Model: Ryzen 5.','Dell Inspiron: Processor Model: Core i3.']


def test_longer_wording_wins_over_the_short_one():
    assert texts(pick_fields('Acer Swift loại RAM gì?',A,['Acer Swift']))==['Acer Swift: RAM Type: DDR4.']


def test_vietnamese_labels_match_without_an_alias():
    assert texts(pick_fields('asus prime co ram toi da theo danh muc la gi vay',BOARD,['Asus Prime']))==['Asus Prime: RAM tối đa theo danh mục: 192 GB.']


def test_two_fields_are_both_returned():
    assert len(pick_fields('CPU và RAM của Acer Swift thế nào?',A,['Acer Swift']))==2


def test_greeting_is_not_a_request():
    assert texts(pick_fields('Shop ơi, số cổng HDMI của Acer Swift thế nào?',A,['Acer Swift']))==['Acer Swift: HDMI Port: 1.']


@pytest.mark.parametrize('question',[
    'Acer Swift có RAM 8GB không?',
    'Acer Swift và Dell Inspiron máy nào mạnh hơn?',
    'CPU của Acer Swift có nên mua không?',
    'CPU và pin của Acer Swift thế nào?',
    'Acer Swift giá bao nhiêu?',
])
def test_uncertain_questions_go_to_the_selector(question):
    assert pick_fields(question,A+B,['Acer Swift','Dell Inspiron'] if 'Dell' in question else ['Acer Swift']) is None


def test_a_field_missing_on_one_side_goes_to_the_selector():
    assert pick_fields('HDMI port của Acer Swift và Dell Inspiron thế nào?',A+B,['Acer Swift','Dell Inspiron']) is None


def test_a_line_of_another_product_is_never_used():
    assert pick_fields('CPU của Dell Inspiron thế nào?',A,['Dell Inspiron']) is None


def test_compare_answer_needs_no_selector_and_cites_both_products(monkeypatch):
    from datetime import date
    from test_grounded_rag import source
    docs=[]
    for title,value in (('Laptop A1','Core i5'),('Laptop B2','Ryzen 7')):
        doc=source(f'{title}: Processor Model: {value}.')
        doc.update(doc_type='product',title=title,document_id=title,chunk_id=title,retrieval='explicit named product')
        docs.append(doc)
    monkeypatch.setattr('shopbot.grounded_rag.search',lambda *a,**k:docs)
    calls=[]
    def model(system,payload,schema,**kwargs):
        calls.append(payload)
        return dict(action='answer',query='q',doc_types=['product'],task='comparison',private_request=False)
    monkeypatch.setattr('shopbot.grounded_rag.chat',model)
    from shopbot.grounded_rag import answer
    result=answer('Laptop A1 với Laptop B2: CPU khác gì nhau?','customer',{},'unused',date(2026,10,24))
    assert len(calls)==1 and 'Core i5' in result['answer'] and 'Ryzen 7' in result['answer']
    assert result['rag']['answerability']=='full' and len(result['rag']['claims'])==2


@pytest.mark.parametrize('question',[
    'Acer Swift có RAM hàn hay khe SO-DIMM vậy?',
    'Acer Swift có mấy khe RAM?',
    'Acer Swift nâng cấp RAM được không?',
    'Acer Swift có gì đặc biệt cho game?',
])
def test_a_question_about_how_a_part_is_fitted_is_not_a_lookup(question):
    assert pick_fields(question,A,['Acer Swift']) is None


def test_a_slot_count_with_its_own_label_is_still_read():
    assert texts(pick_fields('Asus Prime có số khe RAM là bao nhiêu?',BOARD,['Asus Prime']))==['Asus Prime: số khe RAM: 4.']
