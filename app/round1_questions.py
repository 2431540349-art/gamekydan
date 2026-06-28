"""Static question pack and allocator for tournament round 1."""

import random
import re
from types import SimpleNamespace


ROUND1_READ_SECONDS = 8
ROUND1_ANSWER_SECONDS = 5
ROUND1_QUESTIONS_PER_PLAYER = 8

_ANSWERS = {
    1: "b", 2: "b", 3: "c", 4: "b", 5: "a", 6: "b", 7: "b", 8: "b",
    9: "b", 10: "b", 11: "c", 12: "b", 13: "b", 14: "b", 15: "c", 16: "b",
    17: "b", 18: "a", 19: "b", 20: "b", 21: "a", 22: "b", 23: "c", 24: "c",
    25: "b", 26: "a", 27: "b", 28: "b", 29: "b", 30: "a", 31: "b", 32: "c",
    33: "c", 34: "a", 35: "b", 36: "b", 37: "a", 38: "b", 39: "b", 40: "c",
    41: "b", 42: "b", 43: "b", 44: "b", 45: "b", 46: "b", 47: "b", 48: "b",
}

_RAW = """
Câu 1: Nguyễn Thái Sơn phát hiện dữ liệu của Hồ Ngọc Thanh bị rò rỉ khi nhân viên công ty sử dụng AI để phân tích. Theo Luật 2025, hành vi này vi phạm quy định nào? A. Lưu trữ dữ liệu cốt lõi sai vị trí. B. Chuyển dữ liệu cá nhân xuyên biên giới không kiểm soát. C. Vi phạm quyền được biết của chủ thể dữ liệu. D. Sử dụng mật mã dân sự không có giấy phép.
Câu 2: Vũ Quốc Hưng (DIMAC) nhận định thông tin lịch trình và số thẻ VIP của Hồ Ngọc Thanh thuộc loại dữ liệu nào theo Nghị định 356/2025/NĐ-CP? A. Dữ liệu cá nhân cơ bản. B. Dữ liệu cá nhân nhạy cảm. C. Dữ liệu hành vi thông thường. D. Dữ liệu định danh tài sản công.
Câu 3: Lê Mạnh Hùng lo lắng về mức phạt. Nếu không xác định được khoản thu bất hợp pháp từ việc rò rỉ dữ liệu của 50.000 khách hàng như Thanh, mức phạt tối đa theo Luật BVDLCN 2025 là bao nhiêu? A. 1 tỷ đồng. B. 2 tỷ đồng. C. 3 tỷ đồng. D. 5% tổng doanh thu năm trước liền kề.
Câu 4: Hồ Ngọc Thanh yêu cầu công ty cho biết mục đích và cách thức xử lý dữ liệu của mình. Đây là quyền gì của chủ thể dữ liệu? A. Quyền yêu cầu bảo vệ. B. Quyền được biết. C. Quyền đồng ý. D. Quyền khiếu nại và bồi thường.
Câu 5: Nguyễn Thái Sơn thừa nhận công ty đang lưu trữ dữ liệu của người dùng Việt Nam trên Cloud đặt hoàn toàn tại nước ngoài. Vũ Quốc Hưng cảnh báo hành vi này vi phạm: A. Khoản 3 Điều 25 Luật 116/2025/QH15 về nghĩa vụ lưu trữ dữ liệu tại Việt Nam. B. Quy định về mã hóa dân sự AES-256. C. Luật Viễn thông 2023. D. Nghĩa vụ bổ nhiệm DPO nội bộ.
Câu 6: Khi Hồ Ngọc Thanh yêu cầu xóa dữ liệu, Lê Mạnh Hùng có tối đa bao nhiêu ngày để thực hiện nếu có bên thứ ba cùng xử lý? A. 15 ngày. B. 20 ngày. C. 30 ngày. D. 72 giờ.
Câu 7: Vũ Quốc Hưng soi lỗi: Công ty A & B đã tick sẵn ô "Đồng ý" xử lý dữ liệu trong hợp đồng VIP của Thanh. Theo Luật mới, sự đồng ý này: A. Vẫn có hiệu lực nếu khách hàng không phản đối. B. Không có giá trị vì phải là sự tự nguyện, rõ ràng. C. Hợp lệ nếu dữ liệu đã được khử nhận dạng. D. Được chấp nhận đối với khách hàng VIP.
Câu 8: Nguyễn Thái Sơn đề xuất dùng Smooth File để thay thế cách gửi file qua email truyền thống. Tính năng nào của Smooth File giúp "lưu vết" khi ai đó tải dữ liệu của Thanh? A. Khử độc file tự động. B. Logging chi tiết: Ai, Gì, Khi nào. C. Chống gửi nhầm email (DLP). D. Phân quyền tải theo địa lý.
Câu 9: Lê Mạnh Hùng hỏi về nguy cơ bị phạt 5% doanh thu. Vũ Quốc Hưng khẳng định mức phạt này áp dụng cho vi phạm nào? A. Không nộp báo cáo tình hình xử lý dữ liệu định kỳ. B. Vi phạm quy định về chuyển dữ liệu cá nhân xuyên biên giới (CTIA) dẫn đến lộ mất dữ liệu. C. Không bổ nhiệm nhân sự DPO đủ 2 năm kinh nghiệm. D. Không thực hiện đào tạo nhận thức 6 tháng/lần.
Câu 10: Hồ Ngọc Thanh phát hiện kẻ xấu dùng AI giả mạo giọng nói của nhân viên công ty A & B để lừa cô chuyển tiền. Luật An ninh mạng 2025 nghiêm cấm hành vi này tại: A. Điều 10 về quản lý rủi ro. B. Điều 7 về các hành vi bị nghiêm cấm (Deepfake). C. Điều 20 về lưu vết dữ liệu. D. Điều 42 về sản phẩm an ninh mạng.
Câu 11: Nguyễn Thái Sơn cho biết dữ liệu của Thanh bị mất do nhân viên mở file đính kèm chứa mã độc Macro. Giải pháp nào của CYLLENGE giúp ngăn chặn loại virus này? A. CYAS. B. Mail Defender. C. Fast Sanitizer. D. Smooth File Sync.
Câu 12: Vũ Quốc Hưng yêu cầu Hùng kiểm tra xem công ty đã lập hồ sơ DPIA chưa. DPIA là gì? A. Đánh giá tác động chuyển dữ liệu xuyên biên giới. B. Đánh giá tác động xử lý dữ liệu cá nhân. C. Chứng nhận mật mã dân sự. D. Báo cáo định kỳ 6 tháng cho A05.
Câu 13: Vũ Quốc Hưng phát hiện công ty A & B là doanh nghiệp nhỏ. Hùng hỏi có được hoãn thực hiện một số nghĩa vụ không? Hưng trả lời: A. Được miễn hoàn toàn vì doanh thu dưới 50 tỷ. B. Được quyền hoãn 05 năm trừ khi xử lý dữ liệu nhạy cảm hoặc quy mô lớn. C. Phải thực hiện ngay lập tức vì đã xảy ra sự cố rò rỉ. D. Chỉ cần nộp hồ sơ DPIA là đủ.
Câu 14: Khi kiểm tra nhân sự IT của Sơn, Hưng phát hiện Sơn chưa có chứng chỉ bồi dưỡng về bảo vệ dữ liệu cá nhân. Điều này vi phạm yêu cầu đối với: A. Người quản trị hệ thống Cloud. B. Nhân sự bảo vệ dữ liệu cá nhân (DPO). C. Giám đốc điều hành doanh nghiệp. D. Chuyên gia đánh giá rủi ro mạng.
Câu 15: Hưng hỏi Hùng: "Ông đã thông báo cho Cục A05 trong vòng bao lâu sau khi phát hiện dữ liệu của bà Thanh bị lộ?". Thời hạn đúng theo Nghị định 13 là: A. 24 giờ. B. 48 giờ. C. 72 giờ. D. Ngay lập tức không trì hoãn.
Câu 16: Nguyễn Thái Sơn lập luận rằng dữ liệu đã được mã hóa bằng chuẩn AES nên không cần lập hồ sơ CTIA. Hưng phản bác dựa trên lý do nào? A. AES thuộc mật mã dân sự, không được tính là bảo mật. B. Mã hóa chỉ là một biện pháp bảo vệ, không miễn trừ nghĩa vụ lập hồ sơ đánh giá tác động. C. Chỉ có mật mã cơ yếu mới được miễn trừ. D. AES không ngăn được hacker nằm vùng.
Câu 17: Hồ Ngọc Thanh yêu cầu bồi thường thiệt hại về tinh thần. Vũ Quốc Hưng tư vấn cho Hùng rằng Thanh có quyền này dựa trên: A. Bộ luật Hình sự 2015. B. Quyền khiếu nại & bồi thường của chủ thể dữ liệu theo Luật BVDLCN 2025. C. Luật An toàn thông tin mạng 2015. D. Chính sách bồi thường nội bộ của Công ty.
Câu 18: Hưng soi lỗi: Công ty A & B không có hợp đồng bằng văn bản phân định trách nhiệm với bên đối tác xử lý Cloud. Theo Luật 2025, điều này dẫn đến: A. Mức phạt từ 30 - 50 triệu đồng. B. Tước giấy phép kinh doanh vĩnh viễn. C. Sơn phải chịu trách nhiệm hình sự thay Hùng. D. Thanh có quyền rút lại sự đồng ý ngay lập tức.
Câu 19: Để chứng minh việc tuân thủ, Hưng yêu cầu Hùng phải xuất được "bằng chứng tổ chức có kiểm tra, đánh giá rủi ro định kỳ". Giải pháp nào giúp tự động hóa việc này? A. Fast Sanitizer. B. CYAS với hệ thống tập huấn và xuất báo cáo lịch sử tuân thủ. C. Smooth File Sync. D. M-Defender bản Appliance.
Câu 20: Hùng hỏi: "Tại sao tôi phải đặt chi nhánh ở Việt Nam?". Hưng dẫn giải Luật An ninh mạng 2025 áp dụng nghĩa vụ này khi: A. Doanh nghiệp có doanh thu trên 100 tỷ đồng. B. A05 đã thông báo bằng văn bản 03 lần mà doanh nghiệp không khắc phục vi phạm. C. Khách hàng VIP yêu cầu. D. Doanh nghiệp sử dụng công nghệ AI.
Câu 21: Nguyễn Thái Sơn cho rằng chỉ cần xóa tên Hồ Ngọc Thanh trong danh sách là dữ liệu trở thành "ẩn danh". Hưng cảnh báo "khử nhận dạng" (De-identification) yêu cầu: A. Dữ liệu phải thực sự không thể xác định lại cá nhân cụ thể. B. Chỉ cần thay tên bằng mã số là đủ. C. Phải được Bộ Công an cấp phép ẩn danh. D. Dữ liệu phải được lưu trữ tại máy chủ Việt Nam.
Câu 22: Hưng phát hiện công ty A & B chuyển dữ liệu cho công ty mẹ tại Pháp để quản lý nhân sự. Theo Nghị định 356/2025, trường hợp này: A. Được miễn lập hồ sơ CTIA hoàn toàn. B. Được miễn CTIA nếu đã quy định trong Nội quy lao động/Thỏa ước LĐTT phù hợp pháp luật. C. Bắt buộc phải có sự đồng ý của từng nhân viên bằng văn bản công chứng. D. Chỉ cần báo cáo A05 qua email.
Câu 23: Nếu Lê Mạnh Hùng tiếp tục chuyển dữ liệu ra nước ngoài sau khi có quyết định yêu cầu ngừng từ cơ quan chức năng, mức phạt là bao nhiêu? A. 1% doanh thu. B. 3% doanh thu. C. 1% – 5% doanh thu. D. Phạt tiền từ 100 - 200 triệu đồng.
Câu 24: Vũ Quốc Hưng nhấn mạnh mốc thời gian quan trọng: Luật An ninh mạng 2025 sẽ có hiệu lực từ ngày nào để thay thế các luật cũ? A. 01/01/2026. B. 01/07/2025. C. 01/07/2026. D. 01/01/2025.
Câu 25: Sơn đề xuất cài đặt Mail Defender. Tính năng nào giúp Hùng phê duyệt các nội dung quan trọng trước khi nhân viên gửi cho khách hàng như Thanh? A. Thu hồi email sau khi gửi. B. Phê duyệt email theo mô hình Horenso. C. Vô hiệu hóa liên kết URL. D. Gửi email kép (đã khử độc).
Câu 26: Để tránh việc nhân viên gửi nhầm tài liệu nội bộ ra ngoài như trường hợp của Thanh, Mail Defender sử dụng cơ chế nào? A. Tự động chuyển tệp sang URL để kiểm soát. B. Xóa file đính kèm ngay lập tức. C. Chặn tất cả email gửi ra nước ngoài. D. Yêu cầu nhập mã OTP mỗi lần gửi mail.
Câu 27: Sơn giới thiệu Smooth File có khả năng "Lọc thông tin cá nhân". Điều này đáp ứng nghĩa vụ pháp lý nào? A. Nghĩa vụ lưu trữ dữ liệu tại Việt Nam. B. Trách nhiệm ngăn chặn rò rỉ dữ liệu trái phép và kiểm duyệt nội dung (DLP). C. Quyền được xóa dữ liệu của khách hàng. D. Quy định về sử dụng AI trong doanh nghiệp.
Câu 28: Hùng thắc mắc: "Tại sao dùng Anti-virus xịn vẫn bị dính mã độc?". Sơn giải thích Fast Sanitizer khác biệt ở chỗ: A. Nó xóa file nhanh hơn Anti-virus. B. Nó khử độc file (Sanitization) thay vì chỉ quét dựa trên nhận diện mẫu virus đã biết. C. Nó được miễn phí cho doanh nghiệp nhỏ. D. Nó chỉ hoạt động trên hệ điều hành Windows.
Câu 29: Theo Sơn, để xây dựng "Human Firewall" (tường lửa con người) trong 6 tháng, công ty A & B cần triển khai: A. Smooth File Sync. B. CYAS với các bài huấn luyện Phishing giả lập. C. Mail Gazer Cloud. D. File Defender trên thiết bị đầu cuối.
Câu 30: Vũ Quốc Hưng hỏi về việc lưu trữ dữ liệu cốt lõi. Sơn trả lời Smooth File đáp ứng được vì: A. Có bản On-Premise cài đặt trên máy chủ tại Việt Nam. B. Smooth File đã được cấp bằng sáng chế quốc tế. C. Hệ thống có khả năng tự động ẩn danh dữ liệu. D. Smooth File không sử dụng giao thức truyền tin qua mạng.
Câu 31: Tính năng "Đồng bộ iPad" của Smooth File giúp ích gì cho Hùng khi làm việc từ xa? A. Tự động phê duyệt các yêu cầu của Thanh. B. Truy cập dữ liệu công ty an toàn mà không cần VPN. C. Thay thế hoàn toàn hồ sơ DPIA. D. Theo dõi vị trí địa lý của nhân viên IT.
Câu 32: Vũ Quốc Hưng kiểm tra tính pháp lý của CYLLENGE. Công ty này có hơn bao nhiêu năm kinh nghiệm trong lĩnh vực Cloud & Cybersecurity? A. 10 năm. B. 15 năm. C. 26 năm. D. 50 năm.
Câu 33: Sơn cho biết Smooth File hỗ trợ kiểm soát nội dung nhạy cảm tự động cho bao nhiêu ngôn ngữ? A. 2 (Anh, Việt). B. 3 (Anh, Việt, Nhật). C. 5 (Anh, Việt, Nhật, Trung, Hàn). D. Duy nhất tiếng Việt.
Câu 34: Khi Hồ Ngọc Thanh yêu cầu cung cấp bằng chứng về việc ai đã truy cập dữ liệu của mình, Sơn có thể xuất báo cáo từ đâu? A. Audit Log của Smooth File. B. Danh sách đen của Mail Defender. C. Kết quả tập huấn của CYAS. D. Nhật ký hệ thống Windows.
Câu 35: Để chứng minh dữ liệu được bảo vệ bằng "mật mã dân sự" theo Điều 26 Luật ANM, Sơn khẳng định Smooth File sử dụng chuẩn: A. RSA-1024. B. AES-256. C. MD5. D. TLS 1.0.
Câu 36: Hùng hỏi về chi phí. Sơn tư vấn giải pháp nào có gói "Quản lý không giới hạn user" để tiết kiệm ngân sách? A. Fast Sanitizer API. B. Smooth File với gói từ 500GB trở lên. C. CYAS bản trả phí theo năm. D. Mail Defender bản Appliance.
Câu 37: Hồ Ngọc Thanh đe dọa tố cáo công ty lên Cục A05. Vũ Quốc Hưng cảnh báo Hùng rằng nếu A05 thanh tra, công ty có thể bị: A. Phạt tiền gấp 10 lần khoản thu bất hợp pháp. B. Buộc đóng cửa công ty vĩnh viễn. C. Sơn bị tước bằng kỹ sư IT. D. Thanh được quyền sở hữu 5% cổ phần công ty.
Câu 38: Để giảm nhẹ trách nhiệm, Hùng muốn bồi thường tiền cho hacker để lấy lại dữ liệu của Thanh. Hưng ngăn cản vì: A. Chi phí quá cao. B. Việc trả tiền chuộc là bất hợp pháp và tiếp tay cho kẻ xấu. C. Hacker sẽ không bao giờ trả lại dữ liệu. D. Sơn có thể tự khôi phục bằng Smooth File.
Câu 39: Vũ Quốc Hưng tư vấn Hùng thực hiện "Data Mapping". Bước này có tác dụng gì? A. Xác định vị trí địa lý của khách hàng Thanh. B. Rà soát và lập bản đồ toàn bộ hoạt động xử lý dữ liệu để tuân thủ. C. Tăng tốc độ truy cập internet của công ty. D. Tìm ra danh tính thực sự của hacker.
Câu 40: Hồ Ngọc Thanh yêu cầu được biết tên nhân viên đã làm lộ dữ liệu. Theo Luật 2025, công ty A & B: A. Bắt buộc phải cung cấp vì đó là quyền của Thanh. B. Có thể từ chối nếu việc cung cấp gây phương hại đến an ninh quốc gia. C. Chỉ cung cấp khi có yêu cầu từ cơ quan chức năng hoặc theo quy định bảo vệ DLCN. D. Phải đuổi việc nhân viên đó ngay lập tức.
Câu 41: Nếu công ty A & B chứng minh được đã triển khai đầy đủ bộ giải pháp CYLLENGE và có hồ sơ DPIA đầy đủ, mức phạt sẽ: A. Được miễn hoàn toàn. B. Có thể được xem xét giảm nhẹ do đã nỗ lực tuân thủ và phòng ngừa rủi ro. C. Vẫn giữ nguyên vì hậu quả đã xảy ra. D. Được chuyển sang cho bên cung cấp phần mềm CYLLENGE.
Câu 42: Sơn cho biết hệ thống Smooth File có "Option BCP". Tính năng này giúp gì cho công ty sau sự cố? A. Chặn đứng các cuộc tấn công tương tự. B. Phục hồi nội dung dữ liệu trong vòng 72 giờ. C. Tự động gửi email xin lỗi khách hàng. D. Báo cáo trực tiếp cho luật sư Hưng.
Câu 43: Vũ Quốc Hưng nhận định: "Tuân thủ dữ liệu không chỉ là bảo mật, mà còn là...". Điền vào chỗ trống theo tài liệu CYLLENGE: A. Chiến lược marketing. B. Quản trị vận hành. C. Tiết kiệm chi phí IT. D. Nghĩa vụ đối với khách hàng VIP.
Câu 44: Hồ Ngọc Thanh đồng ý không khởi kiện nếu công ty đảm bảo dữ liệu tương lai của cô được bảo vệ. Hùng cam kết bổ nhiệm DPO. Yêu cầu kinh nghiệm của nhân sự này là: A. Ít nhất 1 năm. B. Ít nhất 2 năm trong các lĩnh vực như Pháp chế, IT, An ninh mạng. C. Ít nhất 5 năm làm tại DIMAC. D. Không cần kinh nghiệm nếu có bằng Cao đẳng.
Câu 45: Nguyễn Thái Sơn cảnh báo: "80% kẻ tấn công đều nằm vùng rất lâu". Điều này cho thấy công ty cần tập trung vào: A. Phá tường lửa của đối thủ. B. Kiểm soát và lưu vết truy cập bên trong (Internal Monitoring). C. Mua thêm nhiều ổ cứng dự phòng. D. Thay đổi toàn bộ mật khẩu mỗi tuần.
Câu 46: Vũ Quốc Hưng chốt lại "Liên minh" cần thiết để làm đúng theo quy định pháp luật là: A. Giám đốc + Khách hàng. B. Công nghệ + Pháp chế. C. IT + Marketing. D. Công an + Doanh nghiệp.
Câu 47: Hùng hỏi về việc lưu trữ email để làm bằng chứng pháp lý sau này. Sơn đề xuất tính năng nào của Mail Defender? A. Khử độc email. B. Lưu trữ email gửi và nhận, tìm kiếm nhanh (Evidence Preservation). C. Chuyển nội dung sang dạng text. D. Tự động phân loại địa chỉ người nhận.
Câu 48: Câu hỏi cuối cùng từ Hồ Ngọc Thanh: "Làm sao tôi biết công ty các ông thực sự quan tâm đến an toàn thông tin?". Hùng trả lời bằng cách đưa ra: A. Doanh thu năm vừa qua của công ty. B. Các chứng nhận ISO 27001 và ISO 9001 mà công ty đang nỗ lực đạt được theo hướng dẫn của CYLLENGE. C. Danh sách các luật sư của DIMAC. D. Thẻ VIP mới cho Thanh.
"""


def _parse_question_pack():
    text = re.sub(r"\s+", " ", _RAW.strip())
    blocks = re.findall(r"Câu\s+(\d+):\s*(.*?)(?=Câu\s+\d+:|$)", text)
    questions = []
    for number_raw, body in blocks:
        number = int(number_raw)
        match = re.match(r"(.*?)\s+A\.\s+(.*?)\s+B\.\s+(.*?)\s+C\.\s+(.*?)\s+D\.\s+(.*)", body)
        if not match:
            raise ValueError(f"Cannot parse round 1 question {number}")
        content, option_a, option_b, option_c, option_d = [part.strip() for part in match.groups()]
        questions.append({
            "id": number,
            "content": content,
            "option_a": option_a,
            "option_b": option_b,
            "option_c": option_c,
            "option_d": option_d,
            "correct_answer": _ANSWERS[number],
            "explanation": f"Đáp án đúng: {_ANSWERS[number].upper()}",
            "article_id": 1000 + number,
            "article_name": f"Vòng 1 - Câu {number}",
            "difficulty": "medium",
            "is_round1_static": True,
        })
    if len(questions) != 48:
        raise ValueError(f"Round 1 question pack must contain 48 questions, got {len(questions)}")
    return questions


ROUND1_QUESTIONS = _parse_question_pack()


def make_question(payload):
    return SimpleNamespace(**payload)


def allocate_round1_questions(players):
    """Return sid -> 8 unique questions; no duplicate question inside a team."""
    assignments = {}
    teams = {}
    for sid, player in players.items():
        team_id = player.get("team")
        if team_id:
            teams.setdefault(team_id, []).append(sid)

    for team_id, sids in teams.items():
        sids = sorted(sids)
        deck = list(ROUND1_QUESTIONS)
        random.shuffle(deck)
        required = len(sids) * ROUND1_QUESTIONS_PER_PLAYER
        if required > len(deck):
            raise ValueError(f"Đội {team_id} có quá nhiều người cho bộ 48 câu vòng 1")
        for index, sid in enumerate(sids):
            start = index * ROUND1_QUESTIONS_PER_PLAYER
            chunk = deck[start:start + ROUND1_QUESTIONS_PER_PLAYER]
            assignments[sid] = [make_question(item) for item in chunk]
    return assignments
