"""Load TechStore policy v1 (documnets/team/chinh-sach-techstore.md) into the document store.

Sentences stand alone: the selector cites one to three lines, so each line names its own
subject. Dated 2026-10-30 on purpose: every frozen bank runs on an earlier `today`, so
those banks keep answering from the same documents; evaluation/policy_20261031 tests these.
Safe to run again: a document with unchanged text is skipped.
"""
import hashlib
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot.knowledge import KnowledgeStore

DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'
EFFECTIVE='2026-10-30'
POLICIES={
 'policy-warranty':('Chính sách bảo hành TechStore','''# Chính sách bảo hành TechStore

Laptop được bảo hành 24 tháng tại TechStore.

CPU, mainboard, RAM, ổ cứng, card đồ hoạ, nguồn và màn hình được bảo hành 24 tháng tại TechStore.

Vỏ case và chuột được bảo hành 12 tháng tại TechStore.

Thời hạn bảo hành tính từ ngày mua, tra theo số đơn hàng hoặc số điện thoại đặt hàng.

Bảo hành áp dụng cho lỗi phần cứng do nhà sản xuất.

Bảo hành không áp dụng khi máy bị rơi vỡ, vào nước, cháy nổ do nguồn điện ngoài, hoặc đã bị sửa chữa ngoài TechStore.

Vệ sinh máy và tra keo tản nhiệt được miễn phí trong thời hạn bảo hành.'''),
 'policy-returns':('Chính sách đổi trả TechStore','''# Chính sách đổi trả TechStore

TechStore đổi 1 đổi 1 trong 30 ngày cho sản phẩm lỗi phần cứng do nhà sản xuất, được kỹ thuật xác nhận, đủ hộp và phụ kiện.

Sản phẩm đổi 1 đổi 1 là sản phẩm cùng mẫu; hết hàng cùng mẫu thì đổi mẫu tương đương hoặc hoàn tiền.

TechStore nhận trả hàng hoàn tiền trong 7 ngày với sản phẩm chưa kích hoạt, còn nguyên tem và đủ hộp, phụ kiện.

Trả hàng trong 7 ngày được hoàn 100% giá đã trả.

Tiền hoàn về đúng phương thức đã thanh toán.

Đổi trả không áp dụng cho sản phẩm hư hỏng do người dùng.

TechStore đền 200% giá trị sản phẩm nếu phát hiện hàng giả.'''),
 'policy-installment':('Chính sách trả góp TechStore','''# Chính sách trả góp TechStore

TechStore có trả góp 0% lãi suất qua thẻ tín dụng, kỳ hạn 3, 6, 9 hoặc 12 tháng.

Trả góp 0% chỉ áp dụng cho sản phẩm có nhãn "Trả góp 0%" trên web.

Trả góp bằng CCCD đi qua công ty tài chính, duyệt online khoảng 15 phút.

Lãi suất trả góp bằng CCCD do công ty tài chính quyết định, không phải 0%.

Số tiền trả hằng tháng và danh sách ngân hàng xem ở bước thanh toán hoặc hỏi nhân viên.'''),
 'policy-shipping':('Chính sách giao hàng TechStore','''# Chính sách giao hàng TechStore

TechStore miễn phí giao hàng cho đơn từ 500.000đ.

Đơn dưới 500.000đ tính phí giao hàng khi thanh toán.

TechStore giao nhanh 2 giờ ở nội thành Hà Nội và TP.HCM.

Các tỉnh thành khác nhận hàng trong 2–4 ngày làm việc.

Khách được kiểm tra hàng trước khi nhận.

Lắp đặt PC build được miễn phí khi giao ở nội thành Hà Nội và TP.HCM.'''),
 'policy-promotion':('Chính sách khuyến mãi TechStore','''# Chính sách khuyến mãi TechStore

Tính đến 30/10/2026, TechStore không có chương trình khuyến mãi nào đang chạy.

Chương trình gần nhất là C-BTS, kết thúc ngày 31/08/2026.

Giá trên web là giá bán hiện tại của TechStore.

TechStore không giảm thêm khi không có chương trình khuyến mãi.'''),
}


def load(db=DB,root=None):
    store=KnowledgeStore(db,root);current={d['document_id']:d for d in store.records()}
    saved=[]
    for identifier,(title,text) in POLICIES.items():
        if current.get(identifier,{}).get('sha256')==hashlib.sha256(text.strip().encode('utf8')).hexdigest():continue
        saved.append(store.save(identifier,text,role='admin',title=title,doc_type='policy',audience='customer',
                                approved=True,effective_from=EFFECTIVE))
    return saved


if __name__=='__main__':
    print([(d['document_id'],d['version']) for d in load()])
