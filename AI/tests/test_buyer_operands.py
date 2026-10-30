import pytest
from shopbot.catalog_planner import StagedCatalogPlanner,search_literals,comparison_refs,grounded_category,restates_operands


@pytest.mark.parametrize('question,budget,inclusive,count',[
    ('Trong danh mục hiện có, lấy 3 mainboard giá dưới 2640000 đồng giúp mình.',2_640_000,False,3),
    ('lấy 1 case máy tính giá tối đa 1990000 đồng',1_990_000,True,1),
    ('lấy 3 bộ nguồn giá dưới 1950000 đồng',1_950_000,False,3),
    ('lấy 3 card đồ họa giá dưới 7810000 đồng',7_810_000,False,3),
    ('lấy 5 phụ kiện giá dưới 1020000 đồng',1_020_000,False,5),
    ('Vẫn loại vừa rồi, hạ trần xuống 18000000 đồng và lấy 2 món nhé.',18_000_000,False,2),
    ('Bỏ lựa chọn cũ, chuyển sang thanh RAM, lấy 3 món dưới 24000000 đồng.',24_000_000,False,3),
])
def test_buyer_bank_operands_are_parsed_literally(question,budget,inclusive,count):
    assert search_literals(question)[:3]==(budget,inclusive,count)


def test_accessories_is_a_grounded_category():
    assert grounded_category('lấy 3 phụ kiện giá dưới 510000 đồng',{})=='accessories'


@pytest.mark.parametrize('extra,expected',[
    ('lấy 2',True),('số lượng 2',True),('2',True),('2 món',True),('thanh RAM',True),('ổ SSD',True),
    ('hạ trần xuống 18000000 đồng',True),('giá dưới 18000000 đồng',True),
    ('lấy 4',False),('số lượng 5',False),('giá dưới 2000000 đồng',False),('tối đa 18000000 đồng',False),
    ('màn hình cảm ứng',False),('RAM 16GB',False),('DDR5',False),
])
def test_only_exact_restatements_are_dropped(extra,expected):
    # Parsed request: strict ceiling 18.000.000 VND, count 2.
    assert restates_operands(extra,18_000_000,False,2)==expected


def test_restated_count_and_category_do_not_block_search():
    def caller(system,data,schema,**kwargs):
        if 'action' in schema['properties']:return dict(action='search')
        return dict(category='',brand='',continuation=False,clear_brand=False,extra_requirements=['giá dưới 1950001 đồng','số lượng 2'])
    p=dict(question='Trong danh mục hiện có, lấy 2 bộ nguồn giá dưới 1950001 đồng giúp mình.',role='customer',today='2026-10-23',
           previous_filters={},last_selection=[],history=[],catalog=[])
    plan=StagedCatalogPlanner(caller)(p)
    assert (plan['category'],plan['limit'],plan['budget_max_vnd'],plan['unsupported_filters'])==('psu',2,1_950_001,False)


def test_real_technical_extra_still_defers():
    def caller(system,data,schema,**kwargs):
        if 'action' in schema['properties']:return dict(action='search')
        return dict(category='ram',brand='',continuation=False,clear_brand=False,extra_requirements=['DDR5','lấy 2'])
    p=dict(question='lấy 2 thanh RAM DDR5 dưới 3 triệu',role='customer',today='2026-10-23',
           previous_filters={},last_selection=[],history=[],catalog=[])
    assert StagedCatalogPlanner(caller)(p)['unsupported_filters']


SELECTION=[dict(position=i,ref=f'P{i}') for i in (1,2,3)]


@pytest.mark.parametrize('question,expected',[
    ('So sánh món đầu và món thứ hai trong danh sách mới.',['P1','P2']),
    ('Hai sản phẩm đầu của lượt vừa rồi khác nhau ở đâu?',['P1','P2']),
    ('Đặt sản phẩm số một cạnh số hai giúp mình.',['P1','P2']),
    ('Cho mình bảng đối chiếu hai món đứng đầu danh sách đó.',['P1','P2']),
    ('So cấu hình món thứ hai với món đầu tiên nhé.',['P2','P1']),
    ('Lấy hai lựa chọn đầu vừa tìm để so, thiếu thông số thì ghi thiếu.',['P1','P2']),
    ('Mình muốn đối chiếu số một và số hai của kết quả gần nhất.',['P1','P2']),
    ('So sánh lựa chọn thứ nhất với lựa chọn thứ hai vừa hiển thị.',['P1','P2']),
    ('Món đầu so với món kế tiếp có chênh lệch gì?',['P1','P2']),
    ('So hai món đầu tiên, đừng dùng danh sách ở lượt trước nữa.',['P1','P2']),
    ('So máy thứ ba với máy đầu tiên',['P3','P1']),
])
def test_ordinal_phrasings_bind_to_last_selection(question,expected):
    assert comparison_refs(question,SELECTION,[])==expected


def test_ordinals_without_selection_and_named_pairs():
    catalog=[dict(ref='P1',name='Acer A315'),dict(ref='P2',name='Lenovo 15ITL6')]
    assert comparison_refs('Hai món đầu khác gì?',[],catalog)==[]
    assert comparison_refs('So hai máy Acer A315 và Lenovo 15ITL6',[],catalog)==['P1','P2']
