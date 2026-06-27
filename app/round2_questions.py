"""Static fill-in-the-blank question pack for tournament round 2."""

import random
import re
from types import SimpleNamespace


ROUND2_READ_SECONDS = 7
ROUND2_ANSWER_SECONDS = 4
ROUND2_QUESTIONS_PER_TEAM = 6

_RAW = """
ĐỘI 1: NHÓM "MA TRẬN HỢP ĐỒNG KỲ NGHỈ" (Luật sư DIMAC & Công ty A&B)
Câu 1: Trong hợp đồng kỳ nghỉ, việc Hùng tự ý tick sẵn ô chấp thuận xử lý dữ liệu của Thanh bị coi là vi phạm nguyên tắc "Sự đồng ý" vì thiếu tính _____. (Gợi ý: Tự nguyện / Chủ động / Minh bạch) Đáp án: Chủ động
Câu 2: Nếu luật sư Hưng cố ý làm lộ lịch trình di chuyển nhạy cảm của khách hàng VIP để Hùng lừa đảo, hành vi này cấu thành tội "Cố ý làm lộ _____" theo Điều 7. (Gợi ý: Bí mật riêng tư / Đời sống riêng tư / Thông tin cá nhân) Đáp án: Đời sống riêng tư
Câu 3: Lê Mạnh Hùng có thể bị phạt tối đa 3 tỷ đồng nếu hành vi lừa đảo dữ liệu không xác định được _____. (Gợi ý: Khoản thu lợi / Khoản thu bất hợp pháp / Lợi nhuận vi phạm) Đáp án: Khoản thu bất hợp pháp
Câu 4: Khi bị lừa ký hợp đồng "vĩnh viễn", Thanh có quyền yêu cầu _____ xử lý dữ liệu của mình bất cứ lúc nào. (Gợi ý: Đình chỉ / Hạn chế / Ngăn chặn) Đáp án: Hạn chế
Câu 5: Nguyễn Thái Sơn đề xuất dùng _____ để kiểm soát việc nhân viên IT gửi các bản dự thảo hợp đồng lừa đảo cho khách hàng qua email. (Gợi ý: Mail Gazer / Mail Defender / Mail Guard) Đáp án: Mail Defender
Câu 6: Vũ Quốc Hưng nhận định: Việc lừa đảo thông qua hợp đồng kỳ nghỉ có sử dụng dữ liệu khách hàng sẽ khiến doanh nghiệp mất khả năng đạt chứng nhận _____. (Gợi ý: ISO 27001 / ISO 27701 / ISO 29100) Đáp án: ISO 27701
ĐỘI 2: NHÓM "BẢN QUYỀN & CHIA SẺ 1/7" (Thời sự Luật mới)
Câu 7: Từ 1/7/2026, hành vi chia sẻ lại (share) bài viết của người khác mà không được phép sẽ bị xử lý về hành vi vi phạm _____ trên không gian mạng. (Gợi ý: Quyền tác giả / Quyền sở hữu / Bản quyền) Đáp án: Bản quyền
Câu 8: Doanh nghiệp cung cấp mạng xã hội phải cung cấp cơ chế để chủ bài viết _____ các vi phạm bản quyền một cách tự động. (Gợi ý: Khiếu nại / Tố cáo / Báo cáo) Đáp án: Báo cáo
Câu 9: Để tránh nhân viên share nhầm tài liệu nội bộ (vi phạm bản quyền công ty), Sơn khuyên dùng tính năng "Tự động chuyển tệp sang _____" của Mail Defender. (Gợi ý: Đường dẫn / URL / Liên kết) Đáp án: URL
Câu 10: Việc sử dụng AI để "xào" lại nội dung của người khác mà không xin phép là hành vi lợi dụng công nghệ mới để _____ dữ liệu cá nhân. (Gợi ý: Khai thác / Xử lý / Phát tán) Đáp án: Xử lý
Câu 11: Một doanh nghiệp quảng cáo bị kiện vì share ảnh khách hàng trái phép từ 10 năm trước. Luật 2025 quy định phải xin phép lại nếu thay đổi _____. (Gợi ý: Phương thức xử lý / Mục đích xử lý / Phạm vi xử lý) Đáp án: Mục đích xử lý
Câu 12: Sơn giới thiệu giải pháp _____ giúp doanh nghiệp tập huấn nhân viên nhận diện đâu là hành vi share bài vi phạm bản quyền mạng. (Gợi ý: CY attack / CYAS / CY Sim) Đáp án: CYAS
ĐỘI 3: NHÓM "RỬA TIỀN 80 TỶ & THUÊ TÀI KHOẢN" (Tội phạm Ngân hàng)
Câu 13: Hành vi cho thuê tài khoản ngân hàng để tội phạm rửa tiền 80 tỷ/ngày có thể bị truy cứu hình sự theo tội "Thu thập, mua bán trái phép thông tin _____" (Điều 291 BLHS). (Gợi ý: Thẻ tín dụng / Tài khoản ngân hàng / Dữ liệu tài chính) Đáp án: Tài khoản ngân hàng
Câu 14: Thông tin về số tài khoản và lịch sử giao dịch được Luật 2025 xếp vào nhóm dữ liệu cá nhân _____. (Gợi ý: Đặc biệt / Nhạy cảm / Quan trọng) Đáp án: Nhạy cảm
Câu 15: Các tổ chức tài chính bị cấm sử dụng dữ liệu thuê tài khoản để tự ý _____ tín dụng của chủ thể khi chưa được đồng ý. (Gợi ý: Đánh giá / Xếp hạng / Phân loại) Đáp án: Xếp hạng
Câu 16: Khi phát hiện đường dây rửa tiền qua hệ thống của mình, Giám đốc Hùng phải thông báo cho A05 trong vòng _____ giờ. (Gợi ý: 24 giờ / 72 giờ / 3 ngày) Đáp án: 72 giờ
Câu 17: Sơn khẳng định giải pháp _____ có thể lưu vết (log) chính xác ai đã truy cập vào danh sách các tài khoản ngân hàng VIP bị rao bán. (Gợi ý: Fast Sanitizer / Smooth File / File Defender) Đáp án: Smooth File
Câu 18: Vũ Quốc Hưng cảnh báo: Nếu công ty Hùng tiếp tục để lộ dữ liệu ngân hàng khách hàng, mức phạt tối đa sẽ là 5% _____. (Gợi ý: Doanh thu / Lợi nhuận / Tổng vốn) Đáp án: Doanh thu
ĐỘI 4: NHÓM "LỪA ĐẢO CỌC TIỀN TRỌ" (Deepfake & Social Media)
Câu 19: Kẻ gian phát sóng bộ nhiễu và dùng trạm thu phát sóng giả để lấy mã OTP chuyển tiền cọc trọ, vi phạm tội "Xâm phạm bí mật _____" (Điều 159 BLHS). (Gợi ý: Thư tín / Điện thoại / Điện tín) Đáp án: Điện thoại
Câu 20: Việc dùng AI giả giọng (voice cloning) chủ nhà trọ để lừa Thanh chuyển tiền là hành vi _____ người khác bị nghiêm cấm tại Điều 7. (Gợi ý: Mạo danh / Giả mạo / Chiếm quyền) Đáp án: Giả mạo
Câu 21: Chủ sàn TMĐT/Mạng xã hội có nghĩa vụ _____ nội dung Deepfake lừa đảo do người dùng đăng tải trên hội nhóm tìm phòng trọ. (Gợi ý: Loại bỏ / Giám sát / Kiểm soát) Đáp án: Kiểm soát
Câu 22: Thanh bị lừa gửi ảnh CCCD cho "chủ trọ giả". Để bảo vệ dữ liệu này, Sơn đề xuất dùng _____, biến CCCD thành dạng không thể xác định lại cá nhân. (Gợi ý: Mã hóa / Khử độc / Khử nhận dạng) Đáp án: Khử nhận dạng
Câu 23: Khi bị lừa mất tiền cọc, Thanh có quyền yêu cầu cơ quan chức năng thực hiện các biện pháp _____ dữ liệu của mình khỏi các trang mạng lừa đảo. (Gợi ý: Xóa bỏ / Bảo vệ / Đình chỉ) Đáp án: Bảo vệ
Câu 24: Một doanh nghiệp mạng xã hội để xảy ra quá nhiều vụ lừa cọc tiền trọ mà không khắc phục sau 03 lần thông báo sẽ buộc phải đặt _____ tại Việt Nam. (Gợi ý: Máy chủ / Chi nhánh / Văn phòng) Đáp án: Chi nhánh
ĐỘI 5: NHÓM "NAM SINH LỚP 10 & HACK NGÂN HÀNG" (Trading Data)
Câu 25: Nam sinh lớp 10 bán hàng ngàn dữ liệu khách hàng lấy 10 triệu đồng. Theo Luật mới, mức phạt tối đa cho hành vi "Mua bán dữ liệu" này là bao nhiêu lần khoản thu? (Gợi ý: 05 lần / 10 lần / 20 lần) Đáp án: 10 lần
Câu 26: Hành vi hack ngân hàng của nam sinh thuộc nhóm hành vi bị nghiêm cấm: "_____ trái pháp luật dữ liệu cá nhân". (Gợi ý: Thu giữ / Chiếm đoạt / Đánh cắp) Đáp án: Chiếm đoạt
Câu 27: Ngân hàng bị hack do nhân viên mở file PDF "thông báo học phí" chứa mã độc _____ ẩn dưới dạng đối tượng nhúng OLE. (Gợi ý: Macro / Virus / Script) Đáp án: Macro
Câu 28: Sơn đề xuất giải pháp _____ để chặn đứng các tệp tin chứa mã độc Macro mà nam sinh sử dụng, kể cả khi virus chưa được nhận diện. (Gợi ý: Fast Filter / Fast Sanitizer / Fast Guard) Đáp án: Fast Sanitizer
Câu 29: Nếu ngân hàng chứng minh đã triển khai đầy đủ các biện pháp _____ theo Điều 19, họ có thể được giảm nhẹ trách nhiệm khi sự cố xảy ra. (Gợi ý: Giám sát / Bảo mật / Phòng vệ) Đáp án: Giám sát
Câu 30: Vũ Quốc Hưng lưu ý: Ngân hàng phải lập hồ sơ _____ trong vòng 60 ngày kể từ khi bắt đầu xử lý dữ liệu của các học sinh như nam sinh này. (Gợi ý: CTIA / DPIA / DPO) Đáp án: DPIA
ĐỘI 6: NHÓM "CHỮ NHẤT, SỐ 1 & CHỨNG MINH VĂN BẢN" (Quảng cáo vi phạm)
Câu 31: Mọi quảng cáo trên mạng sử dụng từ "Duy nhất", "Số 1" mà không có văn bản chứng minh bị coi là đưa thông tin _____ trên mạng máy tính. (Gợi ý: Sai sự thật / Trái phép / Không hợp lệ) Đáp án: Trái phép
Câu 32: Việc tự xưng là đơn vị "Nhất" để thu hút dữ liệu của Thanh rồi làm lộ sẽ cấu thành tội "_____ uy tín của tổ chức" theo Điều 155, 156. (Gợi ý: Xâm phạm / Vu khống / Xúc phạm) Đáp án: Xúc phạm
Câu 33: Để khẳng định vị thế "Số 1" một cách hợp pháp, doanh nghiệp cần rà soát lại _____ để phân loại và bảo vệ dữ liệu khách hàng đúng quy trình. (Gợi ý: Data Flow / Data Mapping / Data Chart) Đáp án: Data Mapping
Câu 34: Doanh nghiệp nhỏ tự xưng "Số 1" nhưng thực tế chỉ được quyền _____ thực hiện nghĩa vụ DPO trong 05 năm (trừ khi xử lý dữ liệu nhạy cảm). (Gợi ý: Miễn / Hoãn / Hủy) Đáp án: Hoãn
Câu 35: Sơn đề xuất gói giải pháp giúp doanh nghiệp bảo vệ vị thế "Số 1" bằng cách xây dựng "_____" cho nhân viên trong vòng 6 tháng. (Gợi ý: System Firewall / Human Firewall / Cyber Firewall) Đáp án: Human Firewall
Câu 36: Khi Thanh yêu cầu bồi thường vì tin vào quảng cáo "Số 1" dỏm, doanh nghiệp phải chịu trách nhiệm _____ theo Bộ luật Dân sự 2015. (Gợi ý: Hình sự / Hành chính / Dân sự) Đáp án: Dân sự
ĐỘI 7: NHÓM "SÓNG GIẢ & TRUY VẾT DỮ LIỆU" (Công nghệ tấn công mới)
Câu 37: Tội phạm can thiệp vào mạng viễn thông bằng sóng giả gây rối loạn thông tin của Thanh bị xử lý theo tội "_____ hoạt động mạng máy tính" (Điều 287 BLHS). (Gợi ý: Phá hoại / Cản trở / Đình chỉ) Đáp án: Cản trở
Câu 38: Sơn cho biết hệ thống _____ giúp doanh nghiệp "lưu vết" chính xác các phiên truy cập lạ từ thiết bị sóng giả vào Cloud công ty. (Gợi ý: Smooth File Sync / Mail Defender / Audit Log) Đáp án: Smooth File Sync
Câu 39: Để phòng chống tấn công sóng giả lấy thông tin qua iPad, Hùng nên dùng tính năng "Đồng bộ iPad" của Smooth File để làm việc từ xa mà không cần _____. (Gợi ý: Proxy / VPN / Gateway) Đáp án: VPN
Câu 40: Vũ Quốc Hưng nhận định: Việc sử dụng sóng giả lấy DLCN là hành vi xử lý dữ liệu _____, bị nghiêm cấm tuyệt đối. (Gợi ý: Sai mục đích / Không cho phép / Trái quy định) Đáp án: Trái quy định
Câu 41: Sau khi bị tấn công sóng giả, doanh nghiệp có thể sử dụng "Option _____" của Smooth File để phục hồi nội dung dữ liệu trong 72 giờ. (Gợi ý: Backup / BCP / Restore) Đáp án: BCP
Câu 42: Việc thống nhất quản lý an ninh mạng và sóng viễn thông sẽ tập trung về đầu mối duy nhất là _____ từ 01/07/2026. (Gợi ý: Cục A05 / Bộ TT&TT / Cục An toàn thông tin) Đáp án: Cục A05
"""


def _parse_pack():
    text = re.sub(r"\s+", " ", _RAW.strip())
    topic_matches = list(re.finditer(r"ĐỘI\s+(\d+):\s+NHÓM\s+\"([^\"]+)\"", text))
    packs = {}
    for index, match in enumerate(topic_matches):
        topic_no = int(match.group(1))
        title = match.group(2)
        start = match.end()
        end = topic_matches[index + 1].start() if index + 1 < len(topic_matches) else len(text)
        section = text[start:end]
        questions = []
        for q_no_raw, body in re.findall(r"Câu\s+(\d+):\s*(.*?)(?=Câu\s+\d+:|$)", section):
            q_no = int(q_no_raw)
            parsed = re.match(r"(.*?)\s+\(Gợi ý:\s*(.*?)\)\s+Đáp án:\s*(.*)", body)
            if not parsed:
                raise ValueError(f"Cannot parse round 2 question {q_no}")
            content, hints_raw, answer = [part.strip() for part in parsed.groups()]
            hints = [hint.strip() for hint in hints_raw.split("/") if hint.strip()]
            correct_index = next((i for i, hint in enumerate(hints) if hint.lower() == answer.lower()), None)
            if correct_index is None:
                raise ValueError(f"Answer for round 2 question {q_no} is not in hints")
            questions.append(SimpleNamespace(
                id=2000 + q_no,
                content=content,
                option_a=hints[0],
                option_b=hints[1],
                option_c=hints[2],
                option_d="",
                correct_answer=["a", "b", "c"][correct_index],
                explanation=f"Đáp án đúng: {answer}",
                article_id=2000 + q_no,
                article_name=f"Vòng 2 - {title}",
                difficulty="medium",
                is_static_round=True,
            ))
        if len(questions) != ROUND2_QUESTIONS_PER_TEAM:
            raise ValueError(f"Round 2 topic {topic_no} must contain 6 questions")
        packs[topic_no] = {"title": title, "questions": questions}
    if len(packs) != 7:
        raise ValueError("Round 2 must contain 7 topic packs")
    return packs


ROUND2_TOPIC_PACKS = _parse_pack()


def allocate_round2_questions(active_teams):
    """Assign the 7 active teams to the 7 themed packs in stable team order."""
    assignments = {}
    for topic_no, team_id in enumerate(sorted(active_teams), 1):
        pack = ROUND2_TOPIC_PACKS[topic_no]
        questions = list(pack["questions"])
        # Keep each team's thematic block intact while varying order between teams.
        random.shuffle(questions)
        assignments[team_id] = {
            "title": pack["title"],
            "questions": questions,
        }
    return assignments
