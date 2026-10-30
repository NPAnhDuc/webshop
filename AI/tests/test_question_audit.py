from scripts.audit_chatbot_questions import contains_number, grade, bank

def test_amount_grader_rejects_substrings_and_product_numbers():
    assert contains_number('Doanh thu **1.189.908.000 đ**',1189908000)
    assert not contains_number('Máy H8 còn bán.',8)
    assert not contains_number('Doanh thu 11.189.908.000 đ',1189908000)

def test_document_retrieval_without_policy_fact_is_fail(tmp_path):
    case={'check':'document','expected':{'intent':'documents','document':'customer-policy','missing_fact':True}}
    result={'intent':'documents','answer':'Liên hệ nhân viên. [Nguồn: chính sách]','sources':[{'document_id':'customer-policy','text':'Liên hệ nhân viên.'}]}
    reasons,_=grade(case,result,None,None,tmp_path,'Q001')
    assert [r['code'] for r in reasons]==['missing_policy_fact']

def test_missing_capability_cannot_pass_with_generic_answer(tmp_path):
    case={'check':'capability','expected':{'capability':'forecast'}}
    reasons,_=grade(case,{'answer':'Doanh thu sẽ tăng, hãy quảng cáo thêm.'},None,None,tmp_path,'Q001')
    assert [r['code'] for r in reasons]==['unfulfilled_capability']

def test_correct_privacy_refusal_is_graded_by_answer_not_internal_label(tmp_path):
    case={'check':'deny','expected':{}}
    result={'intent':'clarify','answer':'Tôi không thể cung cấp số điện thoại của người mua. Đây là dữ liệu riêng tư của khách hàng.','rows':[],'sources':[]}
    reasons,_=grade(case,result,None,None,tmp_path,'Q001')
    assert not reasons
    result['rows']=[{'phone':'test-only'}]
    reasons,_=grade(case,result,None,None,tmp_path,'Q001')
    assert reasons[0]['code']=='access_control'

def test_bank_contains_multiturn_and_role_cases():
    groups=bank()
    assert sum(len(g['turns']) for g in groups)==106
    assert sum(len(g['turns'])>1 for g in groups)>=5
    assert any(g['role']=='customer' for g in groups)


def test_all_category_oracle_means_unfiltered(tmp_path):
    import sqlite3
    con=sqlite3.connect(':memory:');con.row_factory=sqlite3.Row
    con.executescript("CREATE TABLE products(sku TEXT,name TEXT,category TEXT);CREATE TABLE sales(day TEXT,sku TEXT,quantity INTEGER,revenue INTEGER,cost INTEGER);")
    con.execute("INSERT INTO products VALUES ('A','Sản phẩm A','laptop')")
    con.execute("INSERT INTO sales VALUES ('2026-02-01','A',1,100,70)")
    period={'start':'2026-02-01','end':'2026-03-01'}
    case={'check':'ranking','expected':{'intent':'top_products','period':period,'metric':'revenue','limit':1,'category':'all'}}
    result={'intent':'top_products','plan':{'metric':'revenue','periods':[period]},'rows':[{'sku':'A'}],'answer':'Sản phẩm A: 100 đ'}
    reasons,evidence=grade(case,result,con,None,tmp_path,'Q001')
    assert not reasons and evidence['expected_ranking'][0]['sku']=='A'
    result['rows']=[]
    assert grade(case,result,con,None,tmp_path,'Q001')[0]
    con.close()
