import pytest
from shopbot.catalog_planner import StagedCatalogPlanner,search_literals,comparison_refs,grounded_category,UnsupportedCategory,SearchClarification


def payload():
    return dict(question='Cho 5 laptop dưới 20 triệu', role='customer', today='2026-10-23',
                previous_filters={}, last_selection=[], history=[dict(question='Xin chào', answer='untrusted old answer')],
                catalog=[dict(ref='P1', name='Laptop A')])


def test_search_stage_is_small_and_does_not_inherit_old_answer_prose():
    calls=[]
    def caller(system, data, schema, **kwargs):
        calls.append(data)
        if len(calls)==1:return dict(action='search')
        return dict(category='laptop', brand='', continuation=False, clear_brand=False, extra_requirements=[])
    result=StagedCatalogPlanner(caller)(payload())
    assert result['budget_max_vnd']==20_000_000 and not result['unsupported_filters']
    assert len(calls)==2 and all('catalog' not in c and 'history' not in c for c in calls)
    assert calls[0]['recent_questions']==['Xin chào']


def test_unsupported_condition_remains_guarded_and_must_be_in_user_question():
    def caller(system, data, schema, **kwargs):
        if 'action' in schema['properties']:return dict(action='search')
        return dict(category='laptop', brand='', continuation=False, clear_brand=False, extra_requirements=['OLED'])
    p=payload()
    with pytest.raises(ValueError, match='Ungrounded'):StagedCatalogPlanner(caller)(p)
    p['question']+=' OLED'
    assert StagedCatalogPlanner(caller)(p)['unsupported_filters']


def test_compare_uses_server_selection_positions_without_model_guessing_ids():
    calls=[]
    def caller(system, data, schema, **kwargs):
        calls.append(data)
        return dict(action='compare')
    p=payload();p['question']='So máy thứ hai với máy đầu tiên'
    p['last_selection']=[dict(position=1,ref='P3'),dict(position=2,ref='P8')]
    result=StagedCatalogPlanner(caller)(p)
    assert result['product_refs']==['P8','P3'] and result['continuation']
    assert len(calls)==1 and 'catalog' not in calls[0]


def test_admin_route_does_not_expose_catalog_or_invoke_filter_planner():
    calls=[]
    def caller(system, data, schema, **kwargs):
        calls.append(data);return dict(action='admin')
    assert StagedCatalogPlanner(caller)(payload())['action']=='admin'
    assert len(calls)==1


@pytest.mark.parametrize('question,budget,inclusive,count',[
    ('Cho 5 laptop giá dưới 20 triệu',20_000_000,False,5),
    ('3 laptop tối đa 20tr',20_000_000,True,3),
    ('Còn dưới15triệu thì sao?',15_000_000,False,0),
    ('2 máy không quá 19,5 triệu',19_500_000,True,2),
    ('laptop < 20.000.000 đồng',20_000_000,False,0),
    ('Tìm laptop giúp tôi',0,False,0),
])
def test_literal_operands_do_not_depend_on_model_numbers(question,budget,inclusive,count):
    assert search_literals(question)[:3]==(budget,inclusive,count)


def test_literal_parsing_preserves_unimplemented_conditions():
    assert 'oled ram16gb' in search_literals('5 laptop OLED RAM16GB dưới20triệu')[3]
    with pytest.raises(ValueError):search_literals('dưới 20tr hoặc dưới15triệu')


def test_comparison_without_names_or_prior_selection_cannot_choose_catalog_rows():
    catalog=[dict(ref='P1',name='Acer A315'),dict(ref='P2',name='Lenovo 15ITL6')]
    assert comparison_refs('So sánh hai máy đó',[],catalog)==[]
    assert comparison_refs('So máy thứ ba với máy đầu tiên',[],catalog)==[]
    assert comparison_refs('So Lenovo 15ITL6 và Acer A315',[],catalog)==['P2','P1']
    selection=[dict(position=1,ref='P1'),dict(position=2,ref='P2')]
    assert comparison_refs('So máy thứ nhất và thứ hai',selection,catalog)==['P1','P2']


@pytest.mark.parametrize('extra,unsupported',[
    ('dưới 20 triệu',False),('giá dưới 20 triệu',False),
    ('OLED dưới 20 triệu',True),('RAM16GB',True),
])
def test_redundant_price_span_is_not_confused_with_a_technical_constraint(extra,unsupported):
    def caller(system,data,schema,**kwargs):
        if 'action' in schema['properties']:return dict(action='search')
        return dict(category='laptop',brand='',continuation=False,clear_brand=False,extra_requirements=[extra])
    p=payload();p['question']='Cho 5 laptop '+extra+' dưới 20 triệu' if '20' not in extra else 'Cho 5 laptop '+extra
    assert StagedCatalogPlanner(caller)(p)['unsupported_filters']==unsupported


def test_category_is_grounded_in_named_entity_not_a_model_default():
    assert grounded_category('Cho 3 RAM dưới3triệu',{})=='ram'
    assert grounded_category('Laptop có RAM16 và màn hình OLED',{})=='laptop'
    with pytest.raises(UnsupportedCategory):grounded_category('Đổi sang điện thoại',{'category':'laptop'})
    with pytest.raises(SearchClarification):grounded_category('Cho vài sản phẩm',{})
    assert grounded_category('Còn dưới15triệu',{'category':'ram'})=='ram'


def test_whitespace_only_quote_variation_does_not_drop_oled_requirement():
    def caller(system,data,schema,**kwargs):
        if 'action' in schema['properties']:return dict(action='search')
        return dict(category='laptop',brand='',continuation=False,clear_brand=False,extra_requirements=['OLED','dưới 25 triệu'])
    p=payload();p['question']='Cho 2 laptop OLED dưới25triệu'
    assert StagedCatalogPlanner(caller)(p)['unsupported_filters']
