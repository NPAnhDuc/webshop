"""Stage reviewed technology notes and richer existing catalog facts; no publication.

Raw webpages are deliberately excluded from import-ready documents: they contain
navigation, prices, advertising and foreign warranty terms. Family-level references
never update an exact SKU automatically. No LLM generated specifications are used.
"""
import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PACK=ROOT/'data/unstructured/technology_20261020'
DB=ROOT/'data/business_sql/scenario_v1/shop.sqlite'

# Short paraphrases reviewed against the named primary sources. An anchor is an
# evidence locator, not a claim that string matching verifies every paraphrase.
# web_reviewed = read through web connector; full raw download was unavailable.
NOTES=[
 ('ram-capacity','intel-ram','RAM 8 GB, 16 GB hay 32 GB: chọn theo tác vụ',
  'RAM là bộ nhớ tạm khi chương trình chạy, khác dung lượng SSD lưu tệp. Nhiều ứng dụng cùng lúc cần thêm RAM. Intel khuyến nghị 16 GB cho game mới và cân nhắc 32 GB nếu vừa chơi vừa stream, trò chuyện hoặc mở nhiều ứng dụng. Đây là hướng dẫn theo tác vụ, không bảo đảm mọi game chạy được. Với học tập cần hỏi phần mềm, số ứng dụng chạy đồng thời và khả năng nâng cấp của đúng máy.',
  'RAM is volatile memory that stores data temporarily for rapid access.','web_reviewed'),
 ('ram-upgrade','intel-ram','Nâng cấp RAM laptop: SO-DIMM và RAM hàn',
  'DIMM thường dùng ở máy bàn; SO-DIMM nhỏ hơn, thường dùng ở laptop. Có laptop hàn RAM lên bo mạch nên không thay được như thanh RAM rời. Trước khi mua RAM, kiểm tra đúng mã máy, loại bộ nhớ, số khe và giới hạn được hãng hỗ trợ. Không suy ra khả năng nâng cấp chỉ từ RAM hiện tại là 8 GB hay 16 GB.',
  '', 'web_reviewed'),
 ('cpu-cores-clock','intel-cpu','Nhân CPU, luồng và xung GHz dùng để làm gì?',
  'CPU nhiều nhân có thể xử lý nhiều công việc đồng thời; dựng video hoặc vừa chơi vừa stream có thể hưởng lợi. Xung GHz mô tả số chu kỳ mỗi giây. Khi chọn CPU phải xét cả tác vụ, số nhân/luồng và tính năng, không chỉ nhìn một thông số GHz. Với một mã CPU cụ thể, cần đọc bảng thông số của chính mã đó trước khi kết luận có đồ họa tích hợp.',
  'Modern gaming CPUs have multiple cores.','web_reviewed'),
 ('cpu-gpu','intel-cpu-gpu','CPU khác GPU như thế nào? GPU có thay CPU được không?',
  'CPU phù hợp xử lý nhiều loại công việc và tác vụ cần hiệu năng từng nhân hoặc độ trễ thấp. GPU có nhiều lõi chuyên biệt cùng xử lý song song, hữu ích cho đồ họa, video và một số tác vụ AI. Hai loại bổ sung cho nhau. Có GPU mạnh không có nghĩa máy sẽ nhanh ở mọi phần mềm; phần mềm phải sử dụng được khả năng tăng tốc tương ứng.',
  'The GPU excels at highly parallel tasks','web_reviewed'),
 ('laptop-choice','intel-gaming-laptop','Chọn laptop chơi game: cần hỏi gì trước?',
  'Cần biết game, độ phân giải và yêu cầu sử dụng trước khi chọn CPU/GPU. RAM, SSD, màn hình và cổng kết nối cũng ảnh hưởng trải nghiệm. Máy nhẹ thuận tiện mang đi; máy gaming dày, nặng có thể dành thêm chỗ cho tản nhiệt và cổng. Pin phụ thuộc tải; chơi game tiêu hao nhanh hơn sử dụng thông thường. Đây là tiêu chí tham khảo của hãng, chưa phải bài hướng dẫn do shop phê duyệt và không phải cam kết FPS.',
  'A thinner and lighter design means more portability.','web_reviewed'),
 ('thunderbolt-usbc','intel-thunderbolt','Cổng USB-C có chắc sạc và xuất màn hình được không?',
  'USB-C mô tả kiểu đầu nối. Thunderbolt 4 dùng đầu USB-C nhưng có yêu cầu chứng nhận về dữ liệu, hình ảnh và cấp điện. Không phải mọi cổng USB-C đều có cùng các chức năng đó. Khi mua hub, dây hoặc màn hình, phải đối chiếu tính năng của cổng máy, phụ kiện và dây; tốc độ thực tế bị giới hạn bởi khả năng chung của các thiết bị kết nối.',
  'Thunderbolt™ 4 is not the same as USB-C','web_reviewed'),
 ('wifi-bands','intel-wifi-bands','Wi-Fi 6, 6E và 7: vì sao chưa chắc dùng được 6 GHz?',
  'Theo hướng dẫn Intel, sản phẩm Wi-Fi 6 của hãng hoạt động ở 2,4 và 5 GHz; 6E/7 có thể hỗ trợ 6 GHz. Để dùng 6 GHz cần cả card mạng, router tương thích và môi trường phần mềm hỗ trợ. Chỉ nâng router không đủ nếu máy không hỗ trợ. Không biến thông lượng lý thuyết của chuẩn Wi-Fi thành tốc độ Internet được bảo đảm.',
  'Intel Wi-Fi 6 products conform to the Wi-Fi Alliance','web_reviewed'),
 ('ssd-m2-nvme','kingston-m2','SSD SATA, NVMe và M.2 khác nhau thế nào?',
  'M.2 là dạng thiết kế ổ cắm/ổ lưu trữ, không đồng nghĩa với NVMe. Ổ M.2 có thể dùng SATA hoặc NVMe qua PCIe. NVMe và SATA khác giao tiếp và đặc tính hiệu năng. Trước khi nâng cấp phải kiểm tra giao tiếp mà khe của máy hỗ trợ; thấy cùng hình dáng M.2 chưa đủ kết luận lắp được. Không dùng tốc độ quảng cáo tối đa làm cam kết tốc độ cho mọi tác vụ.',
  'The main difference between a SATA and NVMe M.2 SSD is the interface technology','web_reviewed'),
 ('photoshop-requirements','adobe-photoshop','Máy học Photoshop cần bao nhiêu RAM?',
  'Bảng yêu cầu Adobe Photoshop 27.x trở lên, cập nhật ngày 09/09/2026, ghi RAM tối thiểu 8 GB và khuyến nghị 16 GB trở lên cho Windows Intel/AMD. Đây chỉ là một phần yêu cầu: cần đối chiếu cả CPU, hệ điều hành và GPU với phiên bản đang dùng. Đạt RAM tối thiểu không bảo đảm làm tệp lớn mượt. Chưa có căn cứ để khẳng định một laptop cụ thể phù hợp nếu thiếu các thông số còn lại.',
  '16 GB or more','web_reviewed'),
 ('panels-ips-oled','benq-panels','IPS, TN, VA và OLED: phân biệt tấm nền',
  'IPS, TN và VA là các kiểu tấm nền LCD; OLED dùng cơ chế khác. Khi so sánh cần xem cả góc nhìn, màu, tương phản và chuyển động của đúng màn hình. Không suy ra chất lượng màu chỉ từ tên IPS. Từ FHD chỉ biết độ phân giải; mô tả LED chung chung chưa xác nhận máy là IPS hay OLED. Chỉ gán tấm nền cho sản phẩm khi có nguồn xác nhận đúng phiên bản.',
  'OLED is another option','web_reviewed'),
 ('ddr5-basics','kingston-ddr5-pdf','DDR5 khác DDR4 ở đâu, có cắm chung được không?',
  'DDR5 là thế hệ RAM mới hơn DDR4, có thay đổi về tổ chức truy cập và cấp điện. Rãnh khóa được thiết kế để ngăn lắp nhầm các thế hệ không tương thích. Phải chọn CPU, bo mạch và loại RAM phù hợp; không coi DDR5 là thanh thay thế trực tiếp cho khe DDR4.',
  'MODULE KEY','local'),
 ('ddr5-ecc','kingston-ddr5-pdf','DDR5 có on-die ECC nghĩa là RAM ECC máy chủ không?',
  'On-die ECC của DDR5 sửa lỗi trong chip DRAM. Nó không sửa được lỗi xảy ra ngoài chip hoặc trên đường truyền tới bộ điều khiển CPU. Vì vậy on-die ECC không tự biến RAM DDR5 phổ thông thành bộ nhớ ECC cấp hệ thống của máy chủ; cần kiểm tra hỗ trợ của cả nền tảng.',
  'ON-DIE ECC','local'),
 ('refresh-study','samsung-refresh','Học tập, văn phòng có bắt buộc màn hình 144 Hz không?',
  'Hz là số lần màn hình làm mới mỗi giây. Samsung xem 60 Hz đáp ứng nhiều tác vụ thường ngày như đọc tài liệu, email và duyệt web. Tần số cao có thể làm chuyển động mượt hơn nhưng không phải yêu cầu bắt buộc cho mọi nhu cầu học tập. Chọn theo công việc và khả năng tạo khung hình của máy, không chỉ chọn con số Hz cao nhất.',
  '60Hz','local'),
 ('refresh-fps','samsung-refresh','Màn hình nhiều Hz có tự làm game tăng FPS không?',
  'Tần số quét là khả năng làm mới hình ảnh của màn hình. Để tận dụng tần số cao, hệ thống CPU/GPU còn phải tạo đủ khung hình cho nội dung. Một màn hình 144 Hz không tự bảo đảm máy chơi mọi game ở 144 FPS. Đánh giá cần dựa vào game, thiết lập và cấu hình thực tế.',
  'CPU','local'),
 ('oled-basics','samsung-oled','OLED là gì và vì sao hiển thị màu đen sâu?',
  'OLED dùng điểm ảnh tự phát sáng thay cho đèn nền truyền thống. Khả năng điều khiển điểm ảnh giúp tạo tương phản và vùng đen sâu. Bài nguồn nói về TV Samsung: chỉ dùng để giải thích nguyên lý, không gán các tính năng riêng của TV sang laptop OLED bất kỳ.',
  'self-illuminating pixels','local'),
 ('oled-static','samsung-oled','Màn hình OLED và nội dung tĩnh: cần lưu ý gì?',
  'Nguồn Samsung nêu hình ảnh hoặc logo tĩnh có thể gây lưu ảnh vĩnh viễn theo thời gian. Điều kiện sử dụng và thiết kế từng model khác nhau. Cần xem hướng dẫn của chính màn hình; không khẳng định mọi OLED đều bị hoặc không thể bị burn-in, và không suy ra điều kiện bảo hành của shop từ bài viết này.',
  'Static images or logos','local'),
 ('monitor-response','benq-input-response','Response time khác input lag như thế nào?',
  'Response time nói về phản hồi của điểm ảnh trên màn hình. Input lag liên quan độ trễ từ thao tác đầu vào đến khi hành động tương ứng xuất hiện. Hai chỉ số khác nhau; số 1 ms được quảng cáo cho response time không đồng nghĩa cả hệ thống có input lag 1 ms. Cần xem phương pháp đo và thiết bị được đo.',
  'Response time is entirely native to the monitor proper','local'),
 ('monitor-photo','benq-photo','Chọn màn hình làm ảnh: ngoài IPS còn xem gì?',
  'Cần xem độ phân giải theo kích thước màn hình, góc nhìn, độ chính xác màu, không gian màu và hiệu chuẩn. sRGB, Adobe RGB là các không gian màu; con số phủ màu không thay thế việc kiểm tra độ chính xác màu. IPS có thể hữu ích cho góc nhìn nhưng không đủ để khẳng định màn hình nào cũng phù hợp in ấn hoặc chỉnh ảnh chuyên nghiệp.',
  'What is Color Gamut?','local'),
 ('usb-pd','usb-power-delivery','USB Power Delivery 240 W có nghĩa máy nào cũng sạc được 240 W?',
  'USB PD Revision 3.1 mở rộng khả năng cấp điện tới 240 W cùng yêu cầu cáp phù hợp. Đây là mức hỗ trợ của đặc tả, không phải công suất mọi máy hoặc mọi dây USB-C nhận được. Muốn xác nhận sạc qua USB-C phải kiểm tra khả năng của laptop, bộ sạc và cáp cho đúng trường hợp.',
  '240W','local'),
 ('flash-speed','kingston-flash-vn','Vì sao USB hoặc ổ lưu trữ không đạt tốc độ quảng cáo?',
  'Hướng dẫn Kingston nêu thiết bị tốc độ cao nối vào máy chỉ hỗ trợ tốc độ thấp hơn sẽ không tự đạt tốc độ cao của thiết bị. Tốc độ còn phụ thuộc cấu hình hệ thống. Khi tư vấn phải phân biệt khả năng giao tiếp với kết quả truyền tệp thực tế, và kiểm tra cả cổng, thiết bị và môi trường sử dụng.',
  '20 Gbps','local'),
 ('flash-capacity','kingston-flash-vn','Dung lượng công bố và dung lượng dùng được có giống nhau không?',
  'Một phần dung lượng bộ nhớ Flash được dùng cho định dạng và chức năng khác nên không phải toàn bộ dung lượng công bố đều dành cho dữ liệu người dùng. Không kết luận ổ bị lỗi chỉ từ việc dung lượng sử dụng hiển thị nhỏ hơn nhãn sản phẩm; cần kiểm tra cách tính đơn vị và phần dung lượng dành riêng.',
  'định dạng','local'),
 ('loq-family','lenovo-loq15irh8','Lenovo LOQ 15IRH8: tài liệu nền tảng của dòng máy',
  'PSREF LOQ 15IRH8 mô tả hai khe SO-DIMM DDR5 và pin 60 Wh, đồng thời liệt kê nhiều lựa chọn CPU, GPU và màn hình. Đây là tài liệu dòng máy, chưa xác nhận đầy đủ mã 82XV00SGLK của danh mục. Không chọn tùy ý một cấu hình cao nhất trong bảng rồi gán cho sản phẩm shop. Dung lượng Wh không phải cam kết số giờ pin cho mọi tác vụ.',
  'Two DDR5 SO-DIMM slots','local'),
 ('legion-family','lenovo-legion-slim5','Legion Slim 5 16IRH8: khả năng RAM theo dòng máy',
  'PSREF của Legion Slim 5 16IRH8 ghi hai khe SO-DIMM DDR5 và nhiều cấu hình trong dòng. Mã 82YA00F0LK của danh mục cần đối chiếu riêng trước khi gán tần số RAM, màn hình hay GPU. Tùy chọn tối đa trong tài liệu nền tảng không đồng nghĩa tất cả máy bán ra đều trang bị mức đó.',
  'Two DDR5 SO-DIMM slots','local'),
 ('thinkbook-family','lenovo-thinkbook15','ThinkBook 15 G2 ITL: RAM hàn và khe SO-DIMM',
  'Tài liệu nền tảng ThinkBook 15 G2 ITL mô tả một phần RAM hàn trên bo mạch và một khe DDR4 SO-DIMM. Cần tra mã 20VE015VIN để xác nhận lượng RAM hàn, thanh đang lắp và cấu hình chính xác. Không lấy giới hạn cấu hình khác trong dòng làm cam kết nâng cấp cho máy cụ thể.',
  'One memory soldered to systemboard','local'),
 ('ideapad-family','lenovo-ideapad3','IdeaPad 3 15ITL6: thông số theo dòng không phải theo SKU',
  'PSREF IdeaPad 3 15ITL6 mô tả RAM hàn cùng một khe DDR4 SO-DIMM. Danh mục shop đang gọi sản phẩm là IdeaPad Slim 3i 15ITL6; cần đối chiếu tên thương mại và mã 82H803UCIN trước khi nhập thêm thông số. Chưa tự xác nhận hai tên sản phẩm chỉ dựa vào phần 15ITL6.',
  'One memory soldered to systemboard','local'),
 ('msi-variant','msi-modern15-408au','MSI Modern 15 B12M: phải phân biệt mã vùng',
  'Bản thông số MSI Modern 15 B12M-408AU ghi RAM 16 GB DDR4-3200 onboard. Mã trong danh mục là B12M-041BD-BB71255U16GXXDX11EMH, khác mã 408AU. Tài liệu này chỉ xác nhận bản 408AU; chưa đủ để kết luận bản 041BD nâng cấp được hay không. Cũng không được nhầm Modern 15 với Modern 15 H.',
  '16GB DDR4-3200 onboard','local'),
 ('msi-081sg','msi-modern15-081sg','Modern 15 B12M-081SG: thông số chỉ cho bản SG',
  'Bản thông số hãng cho B12M-081SG nêu màn hình 15,6 inch FHD IPS-Level và pin 39,3 Wh. Đây là bản vùng SG, khác mã 041BD trong danh mục. Giữ làm tài liệu đối chiếu; không tự điền tấm nền, pin hoặc điều kiện bảo hành của bản SG vào máy của shop.',
  '39.3','local'),
 ('macbook-air-m1','apple-air-m1','MacBook Air M1 2020: màn hình và cổng của dòng máy',
  'Apple mô tả MacBook Air M1 2020 có màn hình 13,3 inch IPS 2560×1600, pin tích hợp 49,9 Wh và hai cổng Thunderbolt/USB 4 hỗ trợ sạc cùng DisplayPort. RAM và SSD có lựa chọn theo cấu hình đặt hàng. Cần xác nhận mã máy thực tế trước khi gán lựa chọn cấu hình; số giờ pin hãng thử nghiệm không phải cam kết sử dụng thực tế của shop.',
  '49.9','local'),
 ('g305-source-conflict','logitech-g305','Logitech G305: phát hiện xung đột dữ liệu kết nối',
  'Trang hãng gọi G305 là LIGHTSPEED Wireless Gaming Mouse. Dữ liệu PCPartPicker đã nhập lại ghi Wired, Wireless. Trường kết nối này được đánh dấu cần đối chiếu và không đưa vào bản thông số sẵn sàng nhập. Không kết luận G305 có chế độ truyền dữ liệu qua dây chỉ từ dữ liệu tổng hợp.',
  'LIGHTSPEED Wireless Gaming Mouse','local'),
 ('ryzen9800x3d','amd-ryzen9000','Ryzen 7 9800X3D: thông số và giới hạn diễn giải',
  'Bảng AMD ghi Ryzen 7 9800X3D có 8 nhân, 16 luồng, boost tối đa 5,2 GHz và TDP mặc định 120 W. Boost tối đa không phải xung được duy trì trong mọi tác vụ; TDP trong bảng không phải phép đo điện năng của cả dàn máy. Không suy ra mức FPS của một PC chỉ từ các thông số này.',
  '9800X3D','local'),
 ('nv2-capacity','kingston-nv2','Kingston NV2: thông số tốc độ thay đổi theo dung lượng',
  'Datasheet NV2 ghi dạng M.2 2280, giao tiếp PCIe 4.0 x4 NVMe. Tốc độ đọc/ghi tuần tự được liệt kê theo dung lượng: bản 1 TB tới 3.500/2.100 MB/s, khác bản 2 TB tới 3.500/2.800 MB/s. Đây là mức tối đa theo điều kiện thử của hãng. Phải xác nhận dung lượng và mã ổ trước khi trích tốc độ; không áp một con số chung cho mọi NV2.',
  'PCIe 4.0 x4 NVMe','local'),
 ('kc3000-capacity','kingston-kc3000','Kingston KC3000: giao tiếp, DRAM và phiên bản dung lượng',
  'Datasheet KC3000 ghi M.2 2280, PCIe 4.0 x4 NVMe, NAND 3D TLC và có DRAM cache. Bảng tốc độ phân biệt theo dung lượng; ví dụ 1.024 GB tới 7.000/6.000 MB/s. Mức tối đa này không phải cam kết cho mọi máy và mọi tệp. Xác nhận mã dung lượng và khe máy hỗ trợ trước khi khuyến nghị nâng cấp.',
  'DRAM Cache Yes','local'),
 ('thunderbolt5','intel-thunderbolt5-pdf','Thunderbolt 5: không nhầm thông lượng chuẩn với mọi cổng USB-C',
  'Tài liệu kỹ thuật Intel mô tả Thunderbolt 5 trên nền đầu nối USB-C và các yêu cầu hỗ trợ đi kèm. Khi tư vấn cần xác nhận cả cổng máy, cáp và dock đạt chuẩn phù hợp. Không dùng tên hoặc tốc độ của Thunderbolt 5 để mô tả một máy chỉ được ghi USB-C hoặc Thunderbolt thế hệ khác.',
  'Thunderbolt','local'),
 ('wifi7-theory','intel-wifi7-pdf','Wi-Fi 7: thông lượng lý thuyết có phải tốc độ tải Internet không?',
  'Infographic Intel nêu kênh 320 MHz và 4K QAM là các tính năng Wi-Fi 7. Đây là khả năng kỹ thuật theo điều kiện được ghi trong tài liệu; kết quả thực tế còn phụ thuộc cấu hình và môi trường. Không lấy thông lượng đỉnh để hứa tốc độ Internet hay tự gán Wi-Fi 7 cho máy chưa có thông số card mạng.',
  '320 MHz','local'),
]

LAPTOP_KEYS=['Processor Brand','Processor Model','Processor Core','RAM','RAM Type','Installed SSD Type',
             'Graphics Chipset','Graphics Memory Accessibility','Graphics Memory','Display Size (Inch)',
             'Display Type','Display Resolution','Touch Screen','Optical Drive','HDMI Port','LAN',
             'Finger Print Sensor','Operating System','Power Adapter','Weight (Kg)']
PART_KEYS={
 'cpu':['core_count','core_clock','boost_clock','microarchitecture','tdp','graphics'],
 'motherboard':['socket','form_factor','max_memory','memory_slots'],
 'memory':['speed','modules','first_word_latency','cas_latency'],
 'internal-hard-drive':['capacity','type','cache','form_factor','interface'],
 'video-card':['chipset','memory','core_clock','boost_clock','length'],
 'case':['type','side_panel','external_volume','internal_35_bays'],
 'power-supply':['type','efficiency','wattage','modular'],
 'monitor':['screen_size','resolution','refresh_rate','response_time','panel_type','aspect_ratio'],
 'mouse':['tracking_method','connection_type','max_dpi','hand_orientation'],
}
LABELS={
 'core_count':('số nhân',''),'core_clock':('xung cơ bản','GHz'),'boost_clock':('xung boost','GHz'),
 'microarchitecture':('vi kiến trúc',''),'tdp':('TDP','W'),'graphics':('đồ họa tích hợp theo dữ liệu nguồn',''),
 'socket':('socket',''),'form_factor':('kích thước/chuẩn thiết kế',''),'max_memory':('RAM tối đa theo danh mục','GB'),
 'memory_slots':('số khe RAM',''),'capacity':('dung lượng','GB'),'cache':('cache','MB'),
 'interface':('giao tiếp',''),'chipset':('GPU',''),'memory':('VRAM','GB'),'length':('chiều dài','mm'),
 'screen_size':('đường chéo','inch'),'refresh_rate':('tần số quét','Hz'),'response_time':('thời gian phản hồi','ms'),
 'panel_type':('tấm nền',''),'resolution':('độ phân giải','pixel'),'aspect_ratio':('tỉ lệ',''),
 'wattage':('công suất định mức theo danh mục','W'),'efficiency':('mức hiệu suất theo danh mục',''),
 'modular':('cáp modular',''),'first_word_latency':('độ trễ từ đầu tiên','ns'),'cas_latency':('CAS latency',''),
 'type':('loại',''),'side_panel':('vật liệu hông',''),'external_volume':('thể tích ngoài','L'),
 'internal_35_bays':('số khay 3,5 inch',''),'tracking_method':('cảm biến',''),
 'connection_type':('kết nối',''),'max_dpi':('DPI tối đa','dpi'),'hand_orientation':('kiểu tay','')}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def write(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
def norm(text):return re.sub(r'\s+',' ',text).casefold().strip()


def main():
    before=sha(DB)
    code={str(p.relative_to(ROOT)):sha(p) for p in [ROOT/'app.py',*sorted((ROOT/'shopbot').glob('*.py'))]}
    sources=json.loads((PACK/'manifest.json').read_text(encoding='utf8'))
    by_id={s['id']:s for s in sources};notes=[];questions=[];word_counts=Counter();errors=[]
    for identifier,source_id,title,body,anchor,method in NOTES:
        source=by_id[source_id]
        if method=='local':
            assert source['status']=='downloaded',source_id
            text=(PACK/source['extracted']).read_text(encoding='utf8')
            if norm(anchor) not in norm(text):errors.append(f'evidence anchor missing: {identifier}: {anchor}')
        metadata=dict(document_id='tech-'+identifier,title=title,doc_type='buying_guide' if identifier in ['laptop-choice','monitor-photo','ram-capacity','photoshop-requirements'] else 'glossary',
                      audience='customer',category='all',authority='external_technical_reference',
                      status='staged_reviewed_summary',indexed=False,source_id=source_id,
                      source_url=source['url'],source_capture=method,reviewed_on='2026-10-20',
                      scope=source['scope'],evidence_anchor=anchor,body=body,
                      rights='short paraphrase; source rights retained; raw source redistribution not cleared')
        note='# '+title+'\n\n'+body+'\n\nNguồn: '+source['url']+'\n\nĐối chiếu: 20/10/2026. Tài liệu tham khảo bên ngoài; không phải chính sách hoặc cam kết của shop.\n'
        path=PACK/'curated'/f'{identifier}.md';path.write_text(note,encoding='utf8')
        metadata.update(file=str(path.relative_to(PACK)),sha256=sha(path))
        notes.append(metadata);word_counts[source_id]+=len(body.split())
        questions.append(dict(id=identifier,question=title,expected_document_id=metadata['document_id'],
                              expected_behavior='answer_with_source_and_scope_limit',split='development_not_heldout'))
    assert not errors,'\n'.join(errors)
    assert max(word_counts.values())<=200,word_counts
    # Project existing catalog fields only; never copy money, inventory, foreign
    # warranty, URLs with marketing claims, or row numbers as product specifications.
    facts=[];quarantine=[];missing=[];units_schema=ROOT/'references/pc-part-dataset/API.md'
    with sqlite3.connect(DB.as_uri()+'?mode=ro',uri=True) as con:
        rows=con.execute('SELECT p.sku,p.name,p.category,f.record_json FROM products p JOIN product_facts f USING(sku) ORDER BY p.sku').fetchall()
        for sku,name,category,record_json in rows:
            record=json.loads(record_json);attrs=record.get('attributes') or {}
            keys=LAPTOP_KEYS if category=='laptop' else PART_KEYS[category]
            selected={k:attrs[k] for k in keys if attrs.get(k) is not None and attrs[k]!=''}
            if 'G305' in name and selected.get('connection_type'):
                quarantine.append(dict(sku=sku,name=name,field='connection_type',old_value=selected.pop('connection_type'),
                                       reason='external dataset conflicts with official Wireless product description',official_source='logitech-g305'))
            unknown=[k for k in keys if k not in selected]
            for k in unknown:missing.append(dict(sku=sku,name=name,field=k,reason='absent_or_quarantined; do not infer'))
            fact=dict(sku=sku,name=name,category=category,part_number=record.get('part_number'),
                      source_dataset=record.get('source_dataset'),source_file=record.get('source_file'),
                      source_row=record.get('source_row'),source_sha256=record.get('source_sha256'),
                      provenance='existing_external_catalog_not_manufacturer_verification',
                      verified_current_vietnam_sku=False,approved_for_shop_sales=False,indexed=False,
                      attributes=selected,missing_fields=unknown)
            if category=='laptop':
                fact['critical_claims_not_verified_for_exact_sku']=[
                    'RAM slot count and upgrade limit','USB-C charging/video capabilities',
                    'battery Wh and task-specific runtime','exact display panel variant',
                    'current Vietnam configuration and shop warranty']
            if category=='memory' and 'speed' in selected:
                fact['schema_note']='speed=[DDR generation, source speed rating]; upstream API labels rating MHz. Preserve raw; do not confuse with physical clock.'
            paragraphs=['# '+name,
                        'Thông số mở rộng từ danh mục tham khảo hiện có, chưa xác minh đúng SKU Việt Nam. Không phải cam kết hàng đang bán.',
                        f'Mã danh mục: {sku}. Mã linh kiện: '+str(fact['part_number'] or 'chưa có')+'.',
                        'Nguồn bộ dữ liệu: '+str(fact['source_dataset'])+'.']
            for key,value in selected.items():
                label,unit=LABELS.get(key,(key,''))
                if category=='video-card' and key in ['core_clock','boost_clock']:unit='MHz'
                if key=='resolution' and isinstance(value,list):value=' × '.join(map(str,value))
                if key=='speed' and isinstance(value,list) and len(value)==2:
                    label='thế hệ và tốc độ RAM';value=f'DDR{value[0]}, mức {value[1]} theo danh mục (nhãn đơn vị nguồn: MHz; không coi là xung vật lý)'
                if key=='modules' and isinstance(value,list) and len(value)==2:
                    label='bộ RAM';value=f'{value[0]} thanh × {value[1]} GB mỗi thanh'
                if value is False:value='không (theo trường dữ liệu nguồn)'
                paragraphs.append(f'{name}: {label}: {value} {unit}.'.replace(' .','.'))
            paragraphs.append('Trường không có trong nguồn chưa được xác nhận. Không suy từ tên hoặc ảnh. Nguồn tổng hợp có thể có sai sót; xem conflicts.json trước khi nhập.')
            path=PACK/'device_facts'/f'{sku}.md';path.write_text('\n\n'.join(paragraphs)+'\n',encoding='utf8')
            fact.update(file=str(path.relative_to(PACK)),sha256=sha(path));facts.append(fact)
    assert len(facts)==67 and len({f['sku'] for f in facts})==67
    forbidden={'price','stock','cost_price','supplier','Warranty','price_per_gb'}
    assert all(not forbidden.intersection(f['attributes']) for f in facts)
    assert sha(DB)==before
    assert all(sha(ROOT/p)==v for p,v in code.items())
    write(PACK/'knowledge_notes.json',notes)
    write(PACK/'catalog_facts.json',facts)
    write(PACK/'conflicts.json',quarantine)
    write(PACK/'missing_fields.json',missing)
    write(PACK/'development_questions.json',questions)
    write(PACK/'web_review_evidence.json',[
        dict(source_id=n['source_id'],source_url=n['source_url'],document_id=n['document_id'],
             evidence_anchor=n['evidence_anchor'],reviewed_on=n['reviewed_on'],
             method='Primary-source page read via web connector; short paraphrase only. Full local download unavailable.')
        for n in notes if n['source_capture']=='web_reviewed'])
    raw_hashes=[s['sha256'] for s in sources if s['status']=='downloaded']
    assert len(raw_hashes)==len(set(raw_hashes)),'Duplicate raw source files must be reviewed before counting'
    for source in sources:
        if source['status']=='downloaded':
            assert sha(PACK/source['raw'])==source['sha256']
            assert sha(PACK/source['extracted'])==source['text_sha256']
    managed=ROOT/'data/unstructured/managed/e397df083984c120/manifest.json'
    counts=dict(downloaded_sources=sum(s['status']=='downloaded' for s in sources),attempted_sources=len(sources),
                raw_bytes=sum(s.get('bytes',0) for s in sources),pdf_pages=sum(s.get('pages',0) for s in sources),
                curated_notes=len(notes),web_reviewed_notes=sum(n['source_capture']=='web_reviewed' for n in notes),
                catalog_products=len(facts),catalog_attributes=sum(len(f['attributes']) for f in facts),
                categories=dict(Counter(f['category'] for f in facts)),quarantined_fields=len(quarantine),
                missing_fields=len(missing),indexed_new_documents=0,source_word_counts=dict(word_counts),
                financial_db_sha256=before,code_sha256=code,unchanged_financial_db=True,unchanged_chatbot_code=True,
                units_schema_sha256=sha(units_schema),development_questions=len(questions),
                quality_note='Evidence anchors and manual review do not measure chatbot answer accuracy. Existing 50-question heldout baseline untouched.')
    counts['active_managed_manifest_sha256']=sha(managed)
    counts['unique_raw_sources']=len(set(raw_hashes))
    counts['catalog_missing_fields_scope']='Only whitelisted raw attributes. Critical laptop claims listed separately; this is not a total completeness score.'
    write(PACK/'validation.json',counts)
    print(json.dumps({k:v for k,v in counts.items() if k not in ['code_sha256','source_word_counts']},ensure_ascii=False))


if __name__=='__main__':main()
