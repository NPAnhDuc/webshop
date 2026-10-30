"""Report manual review against the frozen baseline; never auto-score answers."""
import importlib.util,json,re,statistics,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'evaluation/adversarial_100_20261020'
OUT=Path(sys.argv[1]).resolve()
def read(p):return json.loads(p.read_text(encoding='utf8'))
spec=importlib.util.spec_from_file_location('manual_report',ROOT/'scripts/summarize_adversarial_100_20261020.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
module.OUT=OUT;module.main()
before=read(BASE/'summary.json');after=read(OUT/'summary.json')
old=read(BASE/'review.json');new=read(OUT/'review.json')
improved=[k for k in old if old[k]['status']=='FAIL' and new[k]['status']=='PASS']
regressed=[k for k in old if old[k]['status']=='PASS' and new[k]['status']=='FAIL']
oldrows=read(BASE/'results.json');rows=read(OUT/'results.json')
assert [x['id'] for x in oldrows]==[x['id'] for x in rows]
def med(items):return round(statistics.median(items),2)
latency={}
for role in ['customer','admin']:
 latency[role]={label:med(x['seconds'] for x in data if x['role']==role) for label,data in [('before',oldrows),('after',rows)]}
comparison=dict(before=before,after=after,improved=improved,regressed=regressed,role_median_seconds=latency,
 disclaimer='Same development stress set used during debugging; not held-out or real-traffic accuracy. Different run dates/cache warmth/resource pressure; timings are observations, not a controlled speedup or SLA.')
(OUT.parent/'comparison.json').write_text(json.dumps(comparison,ensure_ascii=False,indent=2),encoding='utf8')
lines=['# Cải thiện RAG cơ bản — 21/10/2026',
 f"Đã chạy lại đủ100 câu với cùng câu hỏi, tiêu chí, vai trò, lịch sử theo nhóm và mốc20/10/2026. Tổng **{before['overall']['passed']}/100 → {after['overall']['passed']}/100**.",
 '| Chỉ tiêu | Trước | Sau |','|---|---:|---:|',
 f"| Người mua | {before['roles']['customer']['passed']}/50 | {after['roles']['customer']['passed']}/50 |",
 f"| Admin | {before['roles']['admin']['passed']}/50 | {after['roles']['admin']['passed']}/50 |",
 f"| Trả nội dung/phần đã biết | {before['content']['passed']}/67 | {after['content']['passed']}/67 |",
 f"| Hỏi lại/thiếu/giới hạn/quyền | {before['boundaries']['passed']}/33 | {after['boundaries']['passed']}/33 |",
 f"| Trung vị thời gian | {before['seconds_median']}s | {after['seconds_median']}s |",
 f"| Tổng thời gian100 câu | {before['seconds_total']}s | {after['seconds_total']}s |",
 f"| Chậm nhất | {before['seconds_max']}s | {after['seconds_max']}s |",
 '## Những gì đã thay đổi',
 '- Giữ phạm vi thời gian có cấu trúc qua các lượt; xác định tháng/quý tương đối bằng lịch. Lọc đúng kỳ trước khi đưa nguồn vào model; kỳ không có thì không lấy năm khác thay.',
 '- Giữ chủ đề hội thoại và tách câu nhiều ý để yêu cầu model chọn bằng chứng cho từng phần. Đưa thuộc tính nguồn vào ID để giảm nhầm RAM/CPU, mục tiêu/thực hiện; đây là hỗ trợ model, không phải bộ chứng minh đã trả đủ.',
 '- Ưu tiên SKU được gọi tên, chia ngân sách ngữ cảnh giữa nhiều sản phẩm. Loại tài liệu do model đoán được mở rộng trong miền tương thích; thiếu chính sách shop không lấy bài kỹ thuật để lấp.',
 '- Đã mở đọc archive khi admin yêu cầu rõ, chỉ với mã tài liệu đã duyệt còn tồn tại; không phục hồi tài liệu đã gỡ hoặc mở nguồn nội bộ cho người mua. Tuy nhiên hai câu đối chiếu lịch sử vẫn FAIL, nên chưa nghiệm thu chức năng này.',
 '- Cache vector theo hash nội dung và model/revision, dùng lại giữa các tập nguồn và sau khởi động lại. Thay tài liệu/model tạo khóa mới; quyền đọc, phiên bản và ngày hiệu lực vẫn được lọc ở mỗi câu hỏi. Cache không lưu câu trả lời hoặc quyền truy cập.',
 '- Giữ hai bước model local: hiểu yêu cầu rồi chọn nguồn. Phương án gộp một lần gọi bị loại vì làm sai các câu thuật ngữ vốn đúng. Không fine-tune, không train Colab, không thêm dữ liệu thật/giả để làm đẹp điểm; SQL và manifest tri thức giữ nguyên hash.',
 '## Lỗi được sửa và lỗi còn lại',
 f"Chuyển FAIL→PASS: {', '.join(improved) or 'không có'}. Chuyển PASS→FAIL: {', '.join(regressed) or 'không có'}.",
 f"Còn {after['overall']['failed']} câu FAIL: {', '.join(after['failed_ids'])}. Có {len(after['fail_but_self_full'])} câu FAIL nhưng bot tự gắn full; nhãn đó chưa đủ đáng tin để nghiệm thu tự động.",
 'Các lỗi và câu trả lời nguyên văn được giữ trong báo cáo từng câu bên dưới. Những câu thiếu ý, sai kỳ hoặc sai trọng tâm vẫn bị đánh FAIL dù trích đúng văn bản.',
 '## Kiểm chứng và giới hạn',
 f"Đã kiểm tra {after['exact_quotes_checked']} trích đoạn: {len(after['quote_errors'])} lỗi đoạn không có trong nguồn; {len(after['customer_private_source_leaks'])} ca nguồn admin lọt sang người mua; {len(after['exceptions'])} kết quả rỗng do ngoại lệ. Hash dữ liệu và mã trong lượt chạy không đổi. Chỉ kiểm tra đúng nguyên văn không chứng minh đã chọn đúng ý.",
 '159 kiểm tra tự động đã qua (155 lõi và4 Streamlit;39 kiểm tra tập trung nằm trong155). [Lệnh chạy và phạm vi kiểm tra](VALIDATION.md). React/Express chưa được kết nối trong thay đổi này; Streamlit dùng pipeline mới theo mặc định, RAG_PIPELINE=legacy cho đối chiếu.',
 'Bộ100 này được dùng để tìm và sửa lỗi, nên là bộ hồi quy phát triển, chưa phải bộ nghiệm thu mù. Codex soạn và chấm thủ công theo tiêu chí/nguồn, không phải đánh giá độc lập của người thật hoặc tỷ lệ đúng ngoài thực tế.',
 'Hai lượt chạy khác ngày, trạng thái cache và áp lực RAM khác nhau. Mốc thời gian nghiệp vụ vẫn cố định để so đáp án. Các số thời gian là quan sát cả lượt chạy, không phải chứng minh tăng tốc trong môi trường kiểm soát hay SLA nhiều người dùng.',
 'Dữ liệu kinh doanh vẫn là mô phỏng67 SKU và12 tháng. Các chính sách thật còn thiếu phải được shop xác nhận. RAG này đọc báo cáo có sẵn; chưa tính KPI từ giao dịch, dự báo hay thực hiện hành động.',
 'Cần ưu tiên sửa bốn câu thoái luiC03,C06,C44,A39 và kiểm tra trên bộ câu hỏi mới độc lập; không coi85/100 là đã hoàn thiện RAG.',
 '## Tệp đối chiếu',
 f'- [Chấm đủ100 câu]({OUT.name}/REPORT.md) và [đáp án nguyên văn]({OUT.name}/ANSWERS.md).',
 f'- [Kết quả thô và thời gian]({OUT.name}/results.json), [chấm thủ công]({OUT.name}/review.json), [hash/kiểm tra]({OUT.name}/integrity.json).',
 '- [Baseline67/100](../adversarial_100_20261020/REPORT.md). Các thư mục pilot/full_v1…full_v6 là bản thử bị bỏ hoặc dừng, không cộng thành điểm lượt cuối.'
]
(OUT.parent/'REPORT.md').write_text('\n\n'.join(lines)+'\n',encoding='utf8')
print('comparison',json.dumps({'before':before['overall'],'after':after['overall'],'improved':improved,'regressed':regressed},ensure_ascii=False))

# Tables need contiguous rows in CommonMark; paragraphs stay separated.
for file in [OUT/'REPORT.md',OUT.parent/'REPORT.md']:
 text=file.read_text(encoding='utf8')
 text=re.sub(r'(?m)^(\|.*\|)\n\n(?=\|)',r'\1\n',text)
 for before,after in {'đủ100':'đủ 100','mốc20':'mốc 20','gian100':'gian 100','và4':'và 4',';39':'; 39','trong155':'trong 155','Bộ100':'Bộ 100','phỏng67':'phỏng 67','và12':'và 12','luiC03,C06,C44,A39':'lui C03, C06, C44, A39','coi85':'coi 85','Baseline67':'Baseline 67'}.items():text=text.replace(before,after)
 file.write_text(text,encoding='utf8')
