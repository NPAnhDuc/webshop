"""Stage user-provided reference material; never execute it or train weights."""
import hashlib
import json
from pathlib import Path
import sys
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from shopbot.chunking import chunk_document
SOURCE=ROOT.parent/'knowledge_base/business_ai_handbook'
OUT=ROOT/'data/knowledge_imports/business_ai_handbook/revision_20261024_r1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

P='01_unit_economics_and_metrics/01_ecommerce_pnl_and_unit_economics.md'
C='01_unit_economics_and_metrics/02_customer_acquisition_retention_metrics.md'
I='02_inventory_and_pricing_economics/01_inventory_control_and_supply_chain.md'
PRICE='02_inventory_and_pricing_economics/02_pricing_strategies_and_elasticity.md'
DE='03_data_engineering_and_sql/01_dimensional_modeling_and_schema_design.md'
SQL='03_data_engineering_and_sql/02_production_retail_sql_queries.md'
RFM='04_data_science_and_algorithms/01_rfm_segmentation_and_customer_lifecycle.md'
BASKET='04_data_science_and_algorithms/02_market_basket_analysis_and_clv.md'
FORECAST='04_data_science_and_algorithms/03_demand_forecasting_and_time_series.md'
AGENT='05_ai_agent_and_system_prompts/02_text_to_sql_and_data_agent_architecture.md'

# Author-reviewed derivatives, deliberately excluding unsupported market rates,
# shop facts, forced action prompts and executable source code.
NOTES=[
 ('metrics', 'Phân biệt chỉ tiêu và định nghĩa kinh doanh',[P,C],'''## Doanh thu, giá vốn và biên lợi nhuận
Doanh thu, tiền đã thu và lợi nhuận là các chỉ tiêu khác nhau. Phải khai báo kỳ, trạng thái đơn, hoàn trả, giảm giá, VAT và cơ sở ghi nhận trước khi tính. Không đổi định nghĩa SQL hiện hành chỉ vì handbook dùng tên gần giống.
Lãi gộp = doanh thu thuần - giá vốn hàng bán theo cùng phạm vi. Lãi gộp không phải lãi ròng; thiếu lãi vay/thuế thì chưa tính được lãi ròng đầy đủ.
CM1/CM2/CM3 là tầng biên đóng góp theo quy ước chi phí của tổ chức, không đồng nhất máy móc CM1 với lãi gộp. Cần từ điển metric nêu chi phí nào được trừ, tránh trừ chiết khấu hai lần.
## AOV và CAC
AOV = doanh thu đủ điều kiện / số đơn đủ điều kiện trong cùng kỳ; mẫu số bằng 0 thì chưa xác định.
Paid CAC = chi phí quảng cáo trả phí / số khách hàng mới được quy thuộc kênh trả phí. Không thay khách mới bằng tổng đơn. Blended CAC dùng phạm vi chi phí marketing tổng hợp và khách mới toàn kênh; cần công bố quy tắc quy thuộc.''',[
 ('Lãi gộp có phải lãi ròng không?','Không. Lãi gộp mới trừ giá vốn khỏi doanh thu thuần; để tính lãi ròng còn cần các chi phí, lãi vay và thuế theo định nghĩa đã thống nhất.'),
 ('AOV cần dữ liệu gì?','Cần doanh thu và số đơn đủ điều kiện trong cùng kỳ, với cùng quy tắc trạng thái/hoàn trả/VAT. AOV là doanh thu chia số đơn; không tính khi mẫu số bằng 0.'),
 ('Paid CAC có chia cho tổng số đơn không?','Không. Mẫu số là khách hàng mới được quy thuộc kênh trả phí, theo quy tắc quy thuộc đã công bố; tổng đơn có thể chứa khách cũ và mua lặp lại.')]),
 ('inventory','Tồn kho và điều kiện áp dụng công thức',[I],'''## Vòng quay và DIO
ITR = giá vốn hàng bán trong kỳ / giá trị tồn kho bình quân. Hai đại lượng phải cùng đơn vị tiền và cơ sở định giá. Có thể ước lượng bình quân bằng đầu/cuối kỳ, nhưng phải nêu rõ cách tính.
DIO = tồn kho bình quân / giá vốn trong kỳ × số ngày trong kỳ. Chỉ dùng 365 khi cơ sở tính là năm 365 ngày; không áp 365 máy móc cho báo cáo tháng/quý. Mẫu số bằng 0 cần báo chưa xác định.
## EOQ và ROP
EOQ = sqrt(2 × D × S / H), với D là nhu cầu/năm, S là chi phí/lần đặt, H là chi phí lưu kho/đơn vị/năm. Công thức cơ bản cần giả định nhu cầu và chi phí phù hợp, chưa xử lý đầy đủ MOQ, ngân sách, biến động giá và rủi ro lỗi thời.
ROP = nhu cầu trung bình/ngày × thời gian giao hàng trung bình/ngày + tồn an toàn. Đây là điểm xem xét bổ sung, không tự suy ra số lượng đặt hoặc tạo PO. Các ngưỡng minh họa trong handbook không phải chính sách đã duyệt của shop.''',[
 ('DIO của một quý có luôn nhân 365 không?','Không. Nếu giá vốn là của quý, dùng số ngày của quý tương ứng. Chỉ dùng 365 với cơ sở năm 365 ngày; phải giữ cùng kỳ và cơ sở định giá.'),
 ('EOQ cần những đầu vào nào?','Nhu cầu năm D, chi phí mỗi lần đặt S và chi phí lưu một đơn vị trong một năm H; EOQ cơ bản bằng căn bậc hai của 2DS/H và cần kiểm tra các giả định áp dụng.'),
 ('Chạm ROP có được tự tạo đơn nhập hàng không?','Không. ROP là mức xem xét bổ sung. Cần kiểm tra tồn khả dụng, hàng đang về, nhu cầu, MOQ và ngân sách; công cụ tạo PO còn phải được triển khai và cấp quyền riêng.')]),
 ('pricing','Giảm giá và hòa vốn sản lượng',[PRICE],'''## Hòa vốn lãi gộp khi giảm giá
Gọi P là giá bán ban đầu, C là giá vốn đơn vị cố định và M=(P-C)/P. Nếu giảm giá theo tỷ lệ x, hệ số sản lượng cần để giữ tổng lãi gộp là M/(M-x); phần tăng tương đối là x/(M-x), chỉ có nghiệm hữu hạn dương khi M>x.
Ví dụ giả định M=15%, x=10%: sản lượng cần gấp 3 lần, tức tăng 200%, để giữ lãi gộp theo các giả định trên. Đây không phải dự báo khách sẽ mua gấp 3, cũng chưa chứng minh lợi nhuận ròng hay dòng tiền.
Khi x=M thì biên đơn vị bằng 0 nên không có sản lượng hữu hạn khôi phục lãi gộp dương ban đầu; khi x>M thì mỗi đơn vị lỗ gộp. Muốn kết luận tác động thật cần phí giao dịch, chi phí biến đổi và bằng chứng về phản ứng nhu cầu.
Hai mốc giá/lượng quan sát không tự chứng minh quan hệ nhân quả giữa giảm giá và lượng bán; có thể đồng thời đổi quảng cáo, mùa vụ hoặc tồn kho.''',[
 ('Biên gộp 15%, giảm giá 10% cần tăng lượng bán bao nhiêu để giữ lãi gộp?','Theo giả định giá vốn đơn vị cố định và chưa xét chi phí khác: hệ số là 0,15/(0,15-0,10)=3, tức tăng 200%. Đây là điều kiện hòa vốn lãi gộp, không phải dự báo sản lượng.'),
 ('Giảm giá bằng đúng biên gộp có thể bán nhiều hơn để giữ lãi không?','Không có sản lượng hữu hạn khôi phục lãi gộp dương ban đầu trong mô hình giá vốn đơn vị cố định, vì biên đơn vị sau giảm giá bằng 0.'),
 ('Thấy giá giảm và lượng bán tăng có kết luận giảm giá gây tăng bán không?','Chưa đủ. Cần kiểm tra mùa vụ, quảng cáo, hàng có sẵn và các thay đổi đồng thời; hai mốc quan sát không tự chứng minh nhân quả.')]),
 ('data_grain','Grain, đối soát và thiết kế dữ liệu',[DE,SQL],'''## Xác định grain
Grain mô tả một dòng đại diện cho gì: đơn hàng, dòng hàng của đơn, hay SKU-ngày. Khóa và phép tổng hợp phải phù hợp grain.
Không cộng tổng tiền đơn sau khi join trực tiếp sang nhiều dòng hàng mà chưa kiểm soát nhân bản. Ví dụ một đơn có hai dòng sẽ lặp tổng đơn hai lần nếu tổng hợp sai.
Số dòng sổ bán/hoàn không phải số đơn; phải đếm khóa đơn đủ điều kiện khi muốn số đơn. Bảng minh họa trong handbook không phải schema đang có của shop.
## Các tầng dữ liệu
Raw giữ dữ liệu nguồn cùng dấu vết phiên bản. Staging kiểm định dạng, đơn vị, ngày, khóa và cách ly dòng lỗi. Curated chỉ công bố sau kiểm tra và đối soát, có lineage/hash và định nghĩa metric.
Không ghép các nguồn hoặc revision khác nhau như cùng tập giao dịch đầy đủ. SQL minh họa có cú pháp phụ thuộc hệ quản trị; không tự chạy trên SQLite hoặc sửa schema production.''',[
 ('Grain là gì và vì sao phải xác định trước khi SUM?','Grain là ý nghĩa của một dòng, chẳng hạn đơn hàng hoặc dòng hàng. Nếu join sang grain chi tiết hơn rồi cộng tổng đơn, số tiền có thể bị nhân bản.'),
 ('Số dòng sổ bán hoàn có bằng số đơn không?','Không. Một đơn có thể có nhiều dòng hàng và hoàn trả. Cần đếm khóa đơn hợp lệ theo định nghĩa số đơn, không thay bằng số dòng sổ.'),
 ('Có thể chạy nguyên SQL trong handbook lên database hiện tại không?','Chưa. Phải kiểm schema, grain, kiểu ngày, quy tắc hoàn trả, dialect và quyền công cụ. SQL minh họa không phải truy vấn đã được kiểm định cho database của shop.')]),
 ('rfm','Phân khúc RFM có kiểm soát',[RFM],'''## Ba biến RFM
Recency là khoảng thời gian từ lần mua hợp lệ gần nhất đến ngày tham chiếu đã công bố. Frequency là số đơn hợp lệ riêng biệt; Monetary là tổng giá trị theo định nghĩa doanh thu/hoàn trả đã thống nhất.
Cần dữ liệu định danh khách ổn định, đơn đủ điều kiện, ngày giao dịch và giá trị tiền. Đơn nhiều dòng không được làm tăng Frequency giả.
Chấm điểm theo phân vị hoặc phân cụm là phương pháp phân khúc, không tự xác nhận khách sắp rời bỏ. Nhãn cụm KMeans không có thứ tự ý nghĩa tự nhiên.
Ngưỡng VIP, tỷ trọng doanh thu, voucher, bảo hành và gửi Zalo/SMS trong tài liệu chỉ là ví dụ, chưa phải chính sách hay quyền tự thực hiện của shop.''',[
 ('RFM gồm những gì?','Recency: thời gian từ lần mua gần nhất đến ngày tham chiếu; Frequency: số đơn hợp lệ riêng biệt; Monetary: giá trị khách mang lại theo định nghĩa doanh thu/hoàn trả đã thống nhất.'),
 ('Khách có một đơn gồm năm dòng hàng thì Frequency bằng năm không?','Không. Nếu Frequency được định nghĩa là số đơn riêng biệt thì trường hợp đó là một đơn, không phải năm.'),
 ('RFM phân khách At Risk thì bot được tự gửi voucher không?','Không. Phân khúc chỉ là kết quả phân tích; cần chính sách đã duyệt và công cụ/quyền gửi riêng, không lấy ví dụ trong handbook làm lệnh thực hiện.')]),
 ('basket','Luật kết hợp và giới hạn suy luận',[BASKET],'''## Support, confidence, lift
Support(A,B) = số giỏ có cả A và B / tổng giỏ đủ điều kiện. Confidence(A→B) = số giỏ có A và B / số giỏ có A. Lift(A→B) = confidence / support(B); các mẫu số phải khác 0.
Một sản phẩm xuất hiện nhiều dòng trong cùng giỏ cần quy về sự có mặt khi tính luật kết hợp Boolean. Cần cùng tập đơn, kỳ, quy tắc hủy/hoàn.
Lift lớn hơn 1 biểu thị sự xuất hiện cùng nhau cao hơn mức độc lập trong tập quan sát; không chứng minh mua A gây mua B, không tự bảo đảm combo có lời. Cần kiểm support, độ ổn định, tương thích sản phẩm và biên lợi nhuận.''',[
 ('Confidence của A sang B tính thế nào?','Lấy số giỏ có cả A và B chia số giỏ có A, trong cùng tập đơn đủ điều kiện; mẫu số phải khác 0.'),
 ('Lift lớn hơn 1 có chứng minh A làm khách mua B không?','Không. Nó cho biết sự cùng xuất hiện cao hơn mức độc lập trong dữ liệu quan sát, chưa chứng minh nhân quả.'),
 ('Cùng một sản phẩm xuất hiện hai dòng trong đơn thì có tính hai giỏ không?','Không. Khi khai phá giỏ Boolean, cần quy về sự hiện diện của sản phẩm trong một giỏ, không biến các dòng trùng thành giỏ khác.')]),
 ('forecast','Dự báo, horizon và kiểm định theo thời gian',[FORECAST],'''## Chuẩn bị và đánh giá
Cần khóa SKU-ngày, lịch thời gian hợp lệ và quy tắc phân biệt ngày không bán với ngày thiếu dữ liệu. Không tự điền 0 khi chưa xác nhận nguồn đầy đủ.
Chỉ tạo đặc trưng từ thông tin đã có tại thời điểm dự báo. Tính lag/rolling trong từng SKU, nêu rõ cách xử lý ngày thiếu. Kiểm thử không trộn nhóm và không dùng số thực tế tương lai.
Phân biệt dự báo một bước có cập nhật số thực tế mỗi ngày với dự báo cố định nhiều ngày từ một mốc. Nếu dự báo cố định 14 ngày, lag từ các ngày tương lai trong 14 ngày đó chưa biết; không được dùng số thực tế validation để giả lập sẵn biết trước.
Backtest theo thời gian và tách giai đoạn tuning khỏi đánh giá cuối. So sánh baseline đơn giản, gồm naive và seasonal naive khi đủ lịch sử cho mùa vụ; mô hình phức tạp chỉ có giá trị khi thắng baseline theo thước đo phù hợp.
## WAPE
WAPE = tổng trị tuyệt đối sai số / tổng trị tuyệt đối actual. Với nhu cầu không âm, mẫu số là tổng actual. Nếu mọi actual bằng 0 thì WAPE chưa xác định; không trả 0% hay infinity như độ chính xác hợp lệ. Các ngưỡng 15%/25% trong handbook chưa phải tiêu chuẩn nghiệm thu shop.''',[
 ('Có thể điền ngày không có dữ liệu bán hàng thành 0 để dự báo luôn không?','Không tự động. Phải xác nhận ngày đó không phát sinh bán hay chỉ thiếu dữ liệu; sau đó mới áp dụng quy tắc điền phù hợp.'),
 ('WAPE có luôn tính được khi actual bằng 0 không?','Một số actual bằng 0 vẫn có thể tính nếu tổng trị tuyệt đối actual dương. Nếu tất cả actual bằng 0 thì mẫu số bằng 0 và WAPE chưa xác định.'),
 ('Vì sao backtest một bước khác dự báo cố định 14 ngày?','Một bước có thể cập nhật số thực tế đã quan sát mỗi ngày. Dự báo cố định 14 ngày từ một mốc không biết actual các ngày tương lai để dùng làm lag; dùng chúng sẽ đánh giá quá lạc quan.')]),
 ('audit_math','Hiệu chỉnh ví dụ toán học trong handbook',[P,C],'''## Ví dụ CM2 giả định, không phải giao dịch của shop
Với doanh thu 5.600.000, giá vốn 4.800.000, đóng gói 20.000 và phí sàn 392.000 đồng: CM1 theo ví dụ = 388.000 đồng.
Nếu chi phí quảng cáo phân bổ là 300.000 thì CM2 = 388.000 - 300.000 = 88.000 đồng, còn dương. Phát biểu chỉ cần CAC trên 300.000 là âm CM2 không suy ra từ bảng. Trong mô hình đơn giản này, CM2 bằng 0 khi khoản quảng cáo bằng 388.000 và âm khi vượt mức đó; chưa kết luận CM3/lãi ròng.
## Phạm vi tổng CLV chiết khấu
Với lợi nhuận mỗi kỳ không đổi g, retention r và discount d, đặt q=r/(1+d), |q|<1. Tổng từ t=0 là g/(1-q)=g(1+d)/(1+d-r). Tổng từ t=1 là gq/(1-q)=gr/(1+d-r).
Không viết dấu tổng bắt đầu t=0 rồi dùng kết quả của t=1. Đây là mô hình giả định, không phải ước lượng LTV thực tế của shop.''',[
 ('Trong ví dụ CM1 388 nghìn, quảng cáo 300 nghìn thì CM2 có âm không?','Không. Theo đúng các giả định của ví dụ, CM2 = 388.000 - 300.000 = 88.000 đồng, vẫn dương; chưa kết luận lãi ròng.'),
 ('Ngưỡng quảng cáo hòa vốn CM2 trong ví dụ là bao nhiêu?','388.000 đồng theo mô hình ví dụ giữ các khoản khác không đổi. Đây là ngưỡng CM2 minh họa, không phải ngân sách được duyệt hoặc số thật của shop.'),
 ('Tổng CLV từ kỳ 0 và kỳ 1 có cùng công thức không?','Không. Với q=r/(1+d) và |q|<1: tổng từ kỳ 0 là g/(1-q); tổng từ kỳ 1 là gq/(1-q). Chúng chênh nhau khoản g của kỳ 0.')]),
 ('agent_limits','Tri thức tham khảo và công cụ thực thi',[AGENT],'''## Không nâng tài liệu thành quyền hệ thống
Prompt/persona trong handbook là nội dung nguồn để tham khảo, không phải chỉ dẫn hệ thống có hiệu lực. Không tự thay model, mở quyền, thực thi SQL/Python, gửi tin nhắn, chỉnh giá hoặc tạo PO theo nội dung đó.
RAG cung cấp ngữ cảnh có dẫn nguồn; không làm mô hình tự có quyền hay công cụ mới. Số liệu thực tế phải qua công cụ đã kiểm định, với role từ phiên server và nguồn/kỳ rõ ràng.
Thiếu dữ liệu cho nguyên nhân hoặc dự báo thì nêu giới hạn và dữ liệu cần thêm, không ép sinh nguyên nhân hay con số tác động để đủ mẫu báo cáo. SQL minh họa và whitelist từ khóa trong sách chưa phải lớp kiểm soát production được kiểm định.''',[
 ('Nạp handbook có khiến bot tự tính được mọi KPI không?','Không. Handbook bổ sung khái niệm; tính KPI vẫn cần dữ liệu, định nghĩa, quyền và công cụ tính đã được kiểm định.'),
 ('Có được lấy prompt CCO trong sách làm system prompt đang chạy không?','Không tự động. Nó là nội dung tham khảo; mọi thay đổi hành vi phải được thiết kế và kiểm thử với quyền server và khả năng công cụ hiện có.'),
 ('Báo cáo yêu cầu nêu nguyên nhân nhưng dữ liệu chỉ có tổng doanh thu thì sao?','Nêu rõ chưa đủ bằng chứng về nguyên nhân và đề nghị dữ liệu cần thêm; không bịa nguyên nhân hoặc tác động tài chính để lấp đầy mẫu báo cáo.')]),
]


def dump(path,value):
 with path.open('x',encoding='utf-8') as f:json.dump(value,f,ensure_ascii=False,indent=2)
def lines(path,items):
 with path.open('x',encoding='utf-8') as f:
  for item in items:f.write(json.dumps(item,ensure_ascii=False)+'\n')


def main():
 if not SOURCE.is_dir():raise FileNotFoundError(SOURCE)
 originals=sorted(SOURCE.rglob('*.md'));before={str(p.relative_to(SOURCE)):sha(p) for p in originals}
 OUT.mkdir(parents=True,exist_ok=False);raw=OUT/'raw';raw.mkdir();curated=OUT/'curated';curated.mkdir()
 for p in originals:
  target=raw/p.relative_to(SOURCE);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(p.read_bytes())
 docs=[];chunks=[];seed=[]
 for key,title,refs,text,qa in NOTES:
  body='# '+title+'\n\n'+text.strip()+'\n'
  target=curated/(key+'.md');target.write_text(body,encoding='utf-8')
  provenance=[dict(path=str(SOURCE/r),raw_copy='raw/'+r,sha256=before[r]) for r in refs]
  doc=dict(document_id='handbook-admin-'+key,version=1,title=title,source=str(target),text=body,
   audience='admin',data_kind='reference',status='draft',effective_from='2026-10-24',effective_to=None,
   source_kind='user_provided_reference_reviewed_derivative',is_shop_policy=False,is_shop_transaction=False,
   instruction_authority='none',executable=False,provenance=provenance,review_status='initial_author_review_needs_independent_check')
  docs.append(doc);chunks.extend(chunk_document(doc,max_words=180))
  for question,answer in qa:
   seed.append(dict(id=f'HB-SFT-{len(seed)+1:03}',group_id=key,audience='admin',status='candidate',eligible_for_training=False,
    training_performed=False,split='unassigned_grouped',document_id=doc['document_id'],source_sha256=sha(target),provenance=provenance,
    messages=[dict(role='system',content='Trả lời từ đoạn tham khảo, không suy số liệu thật của shop hoặc quyền công cụ.'),
     dict(role='user',content='Đoạn tham khảo:\n'+body+'\nCâu hỏi: '+question),
     dict(role='assistant',content=answer+'\n[Nguồn: '+title+'; bản hiệu chỉnh handbook r1]')]))
 lines(OUT/'rag_documents.jsonl',docs);lines(OUT/'rag_chunks.jsonl',chunks);lines(OUT/'sft_seed.jsonl',seed)
 refs=[dict(url='https://pandas.pydata.org/docs/user_guide/groupby.html',use='Group-local transformations; no raw handbook code executed.'),
  dict(url='https://robjhyndman.com/hyndsight/wape.html',use='WAPE denominator and undefined all-zero actuals.'),
  dict(url='https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html',use='Time-ordered evaluation, not random temporal leakage.')]
 dump(OUT/'external_references.json',refs)
 audit=dict(status='reviewed_subset_only',issues=[
  dict(id='HB01',source=P,status='confirmed_arithmetic_error',finding='CM2 at300000 is88000, not negative; break-even CM2 is388000 under the stated example.'),
  dict(id='HB02',source=C,status='confirmed_indexing_error',finding='CLV sum t=0 is not the displayed closed form for t=1; specify origin and assumptions.'),
  dict(id='HB03',source=FORECAST,status='confirmed_edge_case',finding='WAPE is undefined if all actuals are zero; code lacks denominator guard.'),
  dict(id='HB04',source=FORECAST,status='conditional_validation_risk',finding='Using future observed lags in a fixed14-day forecast is leakage; rolling one-step evaluation is a different task.'),
  dict(id='HB05',source=FORECAST,status='not_reproduced_not_a_confirmed_bug',finding='Suspected cross-SKU rolling contamination was not reproduced with shift(1) and default full-window min_periods; do not present it as established.'),
  dict(id='HB06',source=AGENT,status='confirmed_metric_mapping_problem',finding='SUM(unit_selling_price-unit_cost_price) ignores quantity/discounts and is not a generic product gross-profit formula.'),
  dict(id='HB07',source=P,status='held_pending_authoritative_dated_sources',finding='Tax, platform fees and COD market percentages have no verified effective dates/provenance here; excluded from curated notes and SFT.'),
  dict(id='HB08',source='05_ai_agent_and_system_prompts',status='reference_only_never_executed',finding='System/persona instructions and arbitrary SQL/code are not runtime authority or a production-approved agent.'),
  dict(id='HB09',source=I,status='period_definition_required',finding='DIO annual365 factor must not silently be applied to month/quarter COGS; benchmarks are not shop policy.'),
 ],arithmetic_checks=dict(example_cm1=5600000-4800000-20000-392000,example_cm2_at300000=88000,
  example_clv_t0=float(100/(1-Fraction(8,10)/(1+Fraction(1,10)))),example_clv_t1=float(100*Fraction(8,10)/(1+Fraction(1,10)-Fraction(8,10)))))
 dump(OUT/'audit.json',audit)
 assert before=={str(p.relative_to(SOURCE)):sha(p) for p in originals}
 assert all(sha(raw/rel)==h for rel,h in before.items())
 assert len({c['chunk_id'] for c in chunks})==len(chunks)
 assert all(c['audience']=='admin' and c['status']=='draft' and not c['executable'] for c in chunks)
 assert all(not q['eligible_for_training'] for q in seed)
 dump(OUT/'verification.json',dict(original_source_unchanged=True,raw_hash_parity=True,chunk_ids_unique=True,
  admin_only=True,draft_not_active=True,training_started=False,model_calls=0,book_code_executed=False,
  old_bank_gold_touched=False,records_checked=len(seed),chunk_count=len(chunks)))
 manifest=dict(revision='business_ai_handbook_20261024_r1',original_file_count=len(originals),original_bytes=sum(p.stat().st_size for p in originals),
  originals=before,curated_documents=len(docs),chunks=len(chunks),sft_candidates=len(seed),
  audience='admin',activated_in_app=False,weights_trained=False,embedding_started=False,rights='user_provided; authorship/license not independently verified; internal review only',
  files={str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()})
 dump(OUT/'manifest.json',manifest)
 print(json.dumps({k:manifest[k] for k in ('original_file_count','original_bytes','curated_documents','chunks','sft_candidates','activated_in_app','weights_trained')},ensure_ascii=False))


if __name__=='__main__':main()
