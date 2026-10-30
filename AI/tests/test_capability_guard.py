import copy
from datetime import date
import pytest
from shopbot.capability_guard import unsupported_capability
from shopbot.admin_conversation import AdminConversation


@pytest.mark.parametrize('question,expected',[
 ('Xóa các dòng lỗi trong dữ liệu.','file.transform'),
 ('Làm sạch bản sao Excel, không ghi đè file gốc.','file.transform'),
 ('Không sửa file gốc, nhưng chuẩn hóa bản sao Excel.','file.transform'),
 ('Kiểm tra nguồn rồi xóa dòng lỗi.','file.transform'),
 ('Đọc file Excel mới.','file.transform'),
 ('Nhập Excel bán hàng.','file.transform'),
 ('Top5 SKU bán chạy tháng9/2026?','sales.rank'),
 ('SKU nào doanh thu cao nhất?','sales.rank'),
 ('Chuyển sang laptop: doanh thu từng mẫu?','sales.rank'),
 ('Doanh thu từng SKU?','sales.rank'),
 ('Không xóa hay sửa gì, chỉ kiểm tra nguồn dữ liệu.',None),
 ('Nguồn đã đối soát chưa? Đừng clean hay thay đổi dữ liệu.',None),
 ('Chỉ đọc báo cáo nguồn có sẵn, không nhập file mới.',None),
 ('Không clean gì cả, chỉ kiểm tra nguồn có sẵn.',None),
 ('Có bao nhiêu mã SKU trong dữ liệu?',None),
 ('Đọc báo cáo dữ liệu có sẵn.',None),
 ('Không xếp hạng SKU, chỉ kiểm tra nguồn dữ liệu.',None),
 ('Giải thích chuẩn hóa dữ liệu là gì?',None),
 ('Giá vốn tháng9/2026?',None),
 ('Vẽ biểu đồ doanh thu tháng9/2026?',None),
 ('Laptop nào có xung nhịp cao nhất?',None),
])
def test_explicit_actions_and_negative_controls(question,expected):
    assert unsupported_capability(question)==expected


@pytest.mark.parametrize('question,expected',[
 ('Chuẩn hóa dữ liệu là gì?',None),
 ('Xóa dữ liệu có nghĩa là gì?',None),
 ('Làm sạch Excel nghĩa là gì?',None),
 ('Vì sao phải chuẩn hóa dữ liệu?',None),
 ('Hướng dẫn cách làm sạch file Excel.',None),
 ('Giải thích cách clean và chuẩn hóa dữ liệu.',None),
 ('Dữ liệu đã làm sạch chưa?',None),
 ('File Excel đã được chuẩn hóa chưa?',None),
 ('Các dòng lỗi đã xóa chưa?',None),
 ('Giải thích Excel là gì rồi xóa dữ liệu lỗi.','file.transform'),
 ('Chuẩn hóa dữ liệu là gì? Sau đó làm sạch Excel giúp tôi.','file.transform'),
 ('Không xóa hay sửa dữ liệu, chỉ kiểm tra nguồn.',None),
 ('Đừng clean hoặc chuẩn hóa file, chỉ kiểm tra dữ liệu.',None),
 ('Không clean file gốc nhưng làm sạch bản sao Excel.','file.transform'),
 ('Làm sạch file Excel được không?','file.transform'),
 ('Có thể chuẩn hóa file này giúp tôi không?','file.transform'),
 ('Xóa các dòng chưa chuẩn hóa.','file.transform'),
 ('Dữ liệu chưa làm sạch, hãy chuẩn hóa file Excel.','file.transform'),
 ('Giải thích doanh thu là gì rồi tìm top5 SKU bán chạy.','sales.rank'),
 ('Chỉ giải thích khái niệm xếp hạng doanh thu theo SKU là gì.',None),
])
def test_mentions_status_and_separate_real_commands_have_distinct_scope(question,expected):
    assert unsupported_capability(question)==expected


class NoTools:
    def execute(self,*args):raise AssertionError('No substitute tool may execute')


def test_guard_precedes_bad_planner_and_preserves_confirmed_finance_context():
    def planner(_):raise AssertionError('Explicit unsupported request must not need model')
    memory=dict(owner_role='admin',admin_context=dict(metric='revenue',operation='finance',pending=False))
    original=copy.deepcopy(memory)
    result=AdminConversation(NoTools(),planner).run('Làm sạch bản sao Excel, không ghi đè.', 'admin',memory,date(2026,10,24))
    assert result['basic_action']=='deferred' and result['rows']==[] and result['sources']==[]
    assert result['capability_status']==dict(name='file.transform',status='unsupported',executed=False)
    assert 'tool_evidence' not in result and result['admin_plan']['operation']=='unsupported'
    assert result['profile']==original and memory==original


@pytest.mark.parametrize('role',['customer','owner',None])
def test_principal_is_denied_before_guard_and_planner(role):
    def planner(_):raise AssertionError('No planner for untrusted principal')
    result=AdminConversation(NoTools(),planner).run('Xóa dữ liệu Excel.',role,{},date(2026,10,24))
    assert result['basic_action']=='denied' and 'capability_status' not in result
