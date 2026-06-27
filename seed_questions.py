#!/usr/bin/env python3
import sqlite3
import os
import json
from datetime import datetime

def seed():
    db_path = os.environ.get('DB_NAME', 'data.db')
    print(f"Seeding database: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Questions data
    questions_data = [
        # Điều 2
        {
            "content": "Dữ liệu cá nhân theo Nghị định 13/2023/NĐ-CP được định nghĩa là gì?",
            "option_a": "Là bất kỳ thông tin nào liên quan đến một con người cụ thể hoặc giúp xác định một con người cụ thể.",
            "option_b": "Chỉ gồm họ tên và số căn cước công dân.",
            "option_c": "Là thông tin bí mật do Nhà nước quản lý.",
            "option_d": "Chỉ gồm thông tin tài khoản ngân hàng.",
            "correct_answer": "a",
            "explanation": "Theo Điều 2 khoản 1 Nghị định 13/2023/NĐ-CP, dữ liệu cá nhân là thông tin dưới dạng ký hiệu, chữ viết, chữ số, hình ảnh, âm thanh hoặc dạng tương tự trên môi trường điện tử gắn liền với một con người cụ thể hoặc giúp xác định một con người cụ thể.",
            "article_id": 2,
            "article_name": "Điều 2 - Giải thích từ ngữ",
            "difficulty": "easy",
            "category": "definitions"
        },
        {
            "content": "Theo Điều 2 Nghị định 13/2023/NĐ-CP, 'Chủ thể dữ liệu' được định nghĩa là ai?",
            "option_a": "Cá nhân được dữ liệu cá nhân phản ánh.",
            "option_b": "Cơ quan, tổ chức xử lý dữ liệu cá nhân.",
            "option_c": "Cảnh sát phòng chống tội phạm công nghệ cao.",
            "option_d": "Doanh nghiệp cung cấp dịch vụ mạng xã hội.",
            "correct_answer": "a",
            "explanation": "Theo Điều 2 khoản 3 Nghị định 13/2023/NĐ-CP, chủ thể dữ liệu là cá nhân được dữ liệu cá nhân phản ánh.",
            "article_id": 2,
            "article_name": "Điều 2 - Giải thích từ ngữ",
            "difficulty": "medium",
            "category": "definitions"
        },
        {
            "content": "'Xử lý dữ liệu cá nhân' theo Điều 2 Nghị định 13/2023/NĐ-CP bao gồm những hành động nào sau đây?",
            "option_a": "Chỉ thu thập và lưu trữ dữ liệu cá nhân.",
            "option_b": "Chỉ chuyển giao và xóa dữ liệu cá nhân.",
            "option_c": "Một hoặc nhiều hoạt động tác động tới dữ liệu cá nhân (thu thập, ghi, phân tích, lưu trữ, chỉnh sửa, tiết lộ, chia sẻ, truy xuất, xóa hoặc tiêu hủy...).",
            "option_d": "Phân tích hành vi mua sắm của khách hàng trên mạng xã hội.",
            "correct_answer": "c",
            "explanation": "Theo Điều 2 khoản 7 Nghị định 13/2023/NĐ-CP, xử lý dữ liệu cá nhân là một hoặc nhiều hoạt động tác động tới dữ liệu cá nhân, như: thu thập, ghi, phân tích, lưu trữ, chỉnh sửa, tiết lộ, kết hợp, truy cập, truy xuất, thu hồi, mã hóa, giải mã, sao chép, chuyển giao, xóa, hủy dữ liệu cá nhân hoặc các hành động khác có liên quan.",
            "article_id": 2,
            "article_name": "Điều 2 - Giải thích từ ngữ",
            "difficulty": "hard",
            "category": "definitions"
        },
        # Điều 8
        {
            "content": "Nguyên tắc nào yêu cầu dữ liệu cá nhân chỉ được thu thập cho mục đích rõ ràng, hợp pháp và được chủ thể dữ liệu đồng ý?",
            "option_a": "Nguyên tắc hợp pháp.",
            "option_b": "Nguyên tắc giới hạn mục đích.",
            "option_c": "Nguyên tắc bảo mật.",
            "option_d": "Nguyên tắc tối thiểu hóa.",
            "correct_answer": "b",
            "explanation": "Theo Điều 8 khoản 2 Nghị định 13/2023/NĐ-CP, nguyên tắc giới hạn mục đích quy định dữ liệu cá nhân chỉ được xử lý đúng với mục đích đã được Bên Kiểm soát dữ liệu cá nhân đăng ký, tuyên bố về xử lý dữ liệu cá nhân.",
            "article_id": 8,
            "article_name": "Điều 8 - Nguyên tắc xử lý dữ liệu",
            "difficulty": "easy",
            "category": "principles"
        },
        {
            "content": "Theo Điều 8, nguyên tắc 'chính xác' (accuracy) trong xử lý dữ liệu cá nhân yêu cầu điều gì?",
            "option_a": "Dữ liệu cá nhân phải được cập nhật, bảo đảm chính xác và đầy đủ theo mục đích xử lý.",
            "option_b": "Dữ liệu cá nhân phải luôn được lưu giữ mãi mãi để tránh sai sót.",
            "option_c": "Dữ liệu cá nhân phải được mã hóa 100% bằng thuật toán AES.",
            "option_d": "Chỉ xử lý dữ liệu của người có CCCD còn hạn sử dụng.",
            "correct_answer": "a",
            "explanation": "Theo Điều 8 khoản 5 Nghị định 13/2023/NĐ-CP, dữ liệu cá nhân phải được cập nhật, bổ sung phù hợp với mục đích xử lý.",
            "article_id": 8,
            "article_name": "Điều 8 - Nguyên tắc xử lý dữ liệu",
            "difficulty": "medium",
            "category": "principles"
        },
        {
            "content": "Theo nguyên tắc 'tối thiểu hóa dữ liệu' tại Điều 8 Nghị định 13/2023/NĐ-CP, việc xử lý dữ liệu cá nhân phải như thế nào?",
            "option_a": "Chỉ xử lý dữ liệu cá nhân cơ bản, không xử lý dữ liệu nhạy cảm.",
            "option_b": "Phải giới hạn trong phạm vi và mục đích cần thiết để đạt được mục đích đã đề ra, không thu thập dư thừa.",
            "option_c": "Phải xóa dữ liệu ngay lập tức sau 24 giờ kể từ khi thu thập.",
            "option_d": "Phải lưu giữ ở dạng mã hóa một chiều.",
            "correct_answer": "b",
            "explanation": "Theo Điều 8 khoản 4 Nghị định 13/2023/NĐ-CP, dữ liệu cá nhân chỉ được xử lý trong phạm vi cần thiết để đạt được mục đích xử lý dữ liệu cá nhân đã được đồng ý.",
            "article_id": 8,
            "article_name": "Điều 8 - Nguyên tắc xử lý dữ liệu",
            "difficulty": "hard",
            "category": "principles"
        },
        # Điều 9
        {
            "content": "Theo Điều 9 Nghị định 13/2023/NĐ-CP, loại dữ liệu nào sau đây được xếp vào Dữ liệu cá nhân CƠ BẢN?",
            "option_a": "Quan điểm chính trị, tôn giáo.",
            "option_b": "Họ và tên khai sinh, ngày tháng năm sinh, số điện thoại.",
            "option_c": "Tình trạng sức khỏe ghi trong hồ sơ bệnh án.",
            "option_d": "Thông tin về tài khoản ngân hàng.",
            "correct_answer": "b",
            "explanation": "Theo Điều 9 khoản 2 Nghị định 13/2023/NĐ-CP, họ tên, ngày sinh, số điện thoại, email, quốc tịch... thuộc nhóm dữ liệu cá nhân cơ bản.",
            "article_id": 9,
            "article_name": "Điều 9 - Phân loại dữ liệu cá nhân",
            "difficulty": "easy",
            "category": "classification"
        },
        {
            "content": "Theo Điều 9 Nghị định 13/2023/NĐ-CP, loại dữ liệu nào sau đây được coi là dữ liệu cá nhân NHẠY CẢM?",
            "option_a": "Họ và tên đầy đủ",
            "option_b": "Số điện thoại di động",
            "option_c": "Thông tin về sức khỏe và tình trạng bệnh tật",
            "option_d": "Địa chỉ email công việc",
            "correct_answer": "c",
            "explanation": "Theo Điều 9 khoản 3 Nghị định 13/2023/NĐ-CP, thông tin về đời tư, quan điểm chính trị, tôn giáo, dữ liệu sinh trắc học, tình trạng y tế/sức khỏe và dữ liệu tài chính là dữ liệu cá nhân nhạy cảm.",
            "article_id": 9,
            "article_name": "Điều 9 - Phân loại dữ liệu cá nhân",
            "difficulty": "easy",
            "category": "classification"
        },
        {
            "content": "Loại dữ liệu cá nhân nào dưới đây được phân loại là dữ liệu cá nhân NHẠY CẢM?",
            "option_a": "Dữ liệu về vị trí thực tế của cá nhân được xác định qua dịch vụ định vị.",
            "option_b": "Ảnh chân dung công khai của người dùng trên trang tin điện tử.",
            "option_c": "Số định danh cá nhân (CCCD) và nơi thường trú.",
            "option_d": "Địa chỉ IP và lịch sử duyệt web công cộng.",
            "correct_answer": "a",
            "explanation": "Theo Điều 9 khoản 3 điểm h, dữ liệu về vị trí thực tế của cá nhân được xác định qua dịch vụ định vị là dữ liệu cá nhân nhạy cảm.",
            "article_id": 9,
            "article_name": "Điều 9 - Phân loại dữ liệu cá nhân",
            "difficulty": "medium",
            "category": "classification"
        },
        {
            "content": "Theo Nghị định 13/2023/NĐ-CP, dữ liệu về 'đời tư cá nhân, xu hướng tình dục' và 'dữ liệu về tội phạm, hành vi phạm tội' thuộc nhóm dữ liệu nào?",
            "option_a": "Dữ liệu cá nhân cơ bản.",
            "option_b": "Dữ liệu cá nhân đặc biệt bí mật.",
            "option_c": "Dữ liệu cá nhân nhạy cảm.",
            "option_d": "Dữ liệu cá nhân mật quốc gia.",
            "correct_answer": "c",
            "explanation": "Theo Điều 9 khoản 3 Nghị định 13/2023/NĐ-CP, xu hướng tình dục, dữ liệu về tội phạm, hành vi phạm tội thu thập bởi cơ quan thực thi pháp luật được phân loại thuộc dữ liệu cá nhân nhạy cảm.",
            "article_id": 9,
            "article_name": "Điều 9 - Phân loại dữ liệu cá nhân",
            "difficulty": "hard",
            "category": "classification"
        },
        # Điều 11
        {
            "content": "Khi xử lý dữ liệu cá nhân nhạy cảm, chủ thể dữ liệu có bắt buộc phải được thông báo không?",
            "option_a": "Không cần thông báo nếu bên xử lý dữ liệu là doanh nghiệp lớn.",
            "option_b": "Phải thông báo cho chủ thể dữ liệu biết về việc xử lý dữ liệu cá nhân nhạy cảm của họ, trừ một số trường hợp luật định.",
            "option_c": "Chỉ cần thông báo sau khi đã hoàn thành việc xử lý dữ liệu.",
            "option_d": "Chỉ thông báo khi chủ thể dữ liệu có đơn yêu cầu bằng văn bản.",
            "correct_answer": "b",
            "explanation": "Theo quy định chung và Điều 11, việc xử lý dữ liệu cá nhân nhạy cảm đòi hỏi sự minh bạch tối đa và thông báo rõ ràng cho chủ thể dữ liệu.",
            "article_id": 11,
            "article_name": "Điều 11 - Xử lý dữ liệu cá nhân nhạy cảm",
            "difficulty": "easy",
            "category": "sensitive"
        },
        {
            "content": "Theo Điều 11, bên kiểm soát dữ liệu cá nhân nhạy cảm phải áp dụng các biện pháp bảo vệ nào?",
            "option_a": "Chỉ cần lưu trữ ngoại tuyến.",
            "option_b": "Chỉ cần tuyển dụng nhân sự chuyên trách bảo mật.",
            "option_c": "Các biện pháp quản lý, kỹ thuật cụ thể và chỉ định bộ phận bảo vệ dữ liệu cá nhân, nhân sự bảo vệ dữ liệu cá nhân.",
            "option_d": "Chỉ cần đăng ký thông báo với Bộ Công an.",
            "correct_answer": "c",
            "explanation": "Theo Điều 28 và Điều 11, bên kiểm soát dữ liệu phải chỉ định bộ phận bảo vệ dữ liệu cá nhân, chỉ định nhân sự phụ trách bảo vệ và trao đổi thông tin với Cơ quan chuyên trách bảo vệ dữ liệu cá nhân.",
            "article_id": 11,
            "article_name": "Điều 11 - Xử lý dữ liệu cá nhân nhạy cảm",
            "difficulty": "medium",
            "category": "sensitive"
        },
        {
            "content": "Trường hợp nào xử lý dữ liệu cá nhân nhạy cảm KHÔNG cần sự đồng ý của chủ thể dữ liệu (theo Điều 11 và các quy định khẩn cấp)?",
            "option_a": "Để phục vụ mục đích quảng cáo sản phẩm của doanh nghiệp.",
            "option_b": "Trong tình trạng khẩn cấp, đe dọa đến tính mạng, sức khỏe của chủ thể dữ liệu hoặc người khác.",
            "option_c": "Khi bên xử lý dữ liệu muốn nâng cao chất lượng dịch vụ khách hàng.",
            "option_d": "Để thực hiện nghiên cứu thị trường cho bên thứ ba.",
            "correct_answer": "b",
            "explanation": "Theo quy định tại các trường hợp đặc biệt không cần sự đồng ý (như tình trạng khẩn cấp bảo vệ tính mạng sức khỏe, quốc phòng an ninh quốc gia, xử lý theo luật chuyên ngành hành chính/hình sự).",
            "article_id": 11,
            "article_name": "Điều 11 - Xử lý dữ liệu cá nhân nhạy cảm",
            "difficulty": "hard",
            "category": "sensitive"
        },
        # Điều 13
        {
            "content": "Theo Điều 13 Nghị định 13/2023/NĐ-CP, sự đồng ý của chủ thể dữ liệu đối với việc xử lý dữ liệu cá nhân phải có tính chất gì?",
            "option_a": "Tự nguyện và rõ ràng dưới dạng có thể in, sao chép được bằng văn bản, hành động hoặc hình thức tương đương.",
            "option_b": "Im lặng hoặc không phản đối được coi là đồng ý.",
            "option_c": "Được mặc định chấp thuận khi truy cập trang web.",
            "option_d": "Chỉ cần đồng ý bằng lời nói không cần lưu trữ lại.",
            "correct_answer": "a",
            "explanation": "Theo Điều 13 khoản 1, sự đồng ý của chủ thể dữ liệu phải được thể hiện rõ ràng, tự nguyện, cho phép Bên Kiểm soát và Bên Xử lý dữ liệu thực hiện các hoạt động xử lý.",
            "article_id": 13,
            "article_name": "Điều 13 - Sự đồng ý của chủ thể dữ liệu",
            "difficulty": "easy",
            "category": "consent"
        },
        {
            "content": "Chủ thể dữ liệu có quyền rút lại sự đồng ý của mình đối với việc xử lý dữ liệu cá nhân hay không?",
            "option_a": "Không được rút lại sau khi đã ký hợp đồng.",
            "option_b": "Có, và việc rút lại sự đồng ý không ảnh hưởng đến tính hợp pháp của việc xử lý dữ liệu trước đó.",
            "option_c": "Có, nhưng phải nộp một khoản phí bồi thường cho bên kiểm soát dữ liệu.",
            "option_d": "Chỉ được rút lại sau khi có sự đồng ý của Bộ Công an.",
            "correct_answer": "b",
            "explanation": "Theo Điều 13 khoản 5 và Điều 16 khoản 4, chủ thể dữ liệu có quyền rút lại sự đồng ý, việc này không làm ảnh hưởng đến tính hợp pháp của việc xử lý dữ liệu trước đó.",
            "article_id": 13,
            "article_name": "Điều 13 - Sự đồng ý của chủ thể dữ liệu",
            "difficulty": "medium",
            "category": "consent"
        },
        {
            "content": "Theo Điều 13, sự đồng ý của chủ thể dữ liệu cho một mục đích xử lý này có được áp dụng tự động cho các mục đích xử lý khác hay không?",
            "option_a": "Có, vì dữ liệu đã được thu thập hợp pháp.",
            "option_b": "Không, sự đồng ý phải được thể hiện một cách rõ ràng cho từng mục đích cụ thể.",
            "option_c": "Chỉ được áp dụng tự động nếu đó là các mục đích thương mại liên quan.",
            "option_d": "Có, nếu bên xử lý dữ liệu thông báo qua email sau 30 ngày.",
            "correct_answer": "b",
            "explanation": "Theo Điều 13 khoản 3, sự đồng ý của chủ thể dữ liệu phải được thể hiện một cách rõ ràng, cụ thể cho từng mục đích xử lý dữ liệu cá nhân.",
            "article_id": 13,
            "article_name": "Điều 13 - Sự đồng ý của chủ thể dữ liệu",
            "difficulty": "hard",
            "category": "consent"
        },
        # Điều 16
        {
            "content": "Quyền nào sau đây KHÔNG phải là quyền của chủ thể dữ liệu theo Điều 16 Nghị định 13/2023/NĐ-CP?",
            "option_a": "Quyền được biết, quyền đồng ý, quyền truy cập.",
            "option_b": "Quyền rút lại sự đồng ý, quyền yêu cầu xóa dữ liệu.",
            "option_c": "Quyền đơn phương yêu cầu bắt giam người xử lý dữ liệu trái phép.",
            "option_d": "Quyền phản đối xử lý dữ liệu, quyền tự bảo vệ.",
            "correct_answer": "c",
            "explanation": "Điều 16 quy định 11 quyền của chủ thể dữ liệu bao gồm: Quyền được biết, Quyền đồng ý, Quyền truy cập, Quyền rút lại sự đồng ý, Quyền xóa dữ liệu, Quyền hạn chế xử lý dữ liệu, Quyền cung cấp dữ liệu, Quyền phản đối xử lý dữ liệu, Quyền khiếu nại tố cáo, Quyền yêu cầu bồi thường thiệt hại, Quyền tự bảo vệ.",
            "article_id": 16,
            "article_name": "Điều 16 - Quyền của chủ thể dữ liệu",
            "difficulty": "easy",
            "category": "rights"
        },
        {
            "content": "Theo Điều 16, khi chủ thể dữ liệu yêu cầu xóa dữ liệu cá nhân của mình, bên kiểm soát dữ liệu phải thực hiện trong thời gian bao lâu?",
            "option_a": "Ngay lập tức trong vòng 24 giờ.",
            "option_b": "Trong vòng 72 giờ kể từ khi nhận được yêu cầu hợp lệ, trừ trường hợp luật định khác.",
            "option_c": "Trong vòng 30 ngày làm việc.",
            "option_d": "Chỉ xóa khi hợp đồng giữa hai bên kết thúc.",
            "correct_answer": "b",
            "explanation": "Theo Điều 16 khoản 5, việc xóa dữ liệu cá nhân phải được thực hiện trong vòng 72 giờ sau khi nhận được yêu cầu hợp lệ từ phía chủ thể dữ liệu.",
            "article_id": 16,
            "article_name": "Điều 16 - Quyền của chủ thể dữ liệu",
            "difficulty": "medium",
            "category": "rights"
        },
        {
            "content": "Theo Điều 16, chủ thể dữ liệu có quyền yêu cầu hạn chế xử lý dữ liệu cá nhân của mình. Yêu cầu này phải được bên kiểm soát dữ liệu thực hiện trong thời hạn bao lâu?",
            "option_a": "Trong vòng 72 giờ kể từ khi nhận được yêu cầu hợp lệ.",
            "option_b": "Trong vòng 24 giờ kể từ khi nhận được yêu cầu.",
            "option_c": "Trong vòng 5 ngày làm việc.",
            "option_d": "Không giới hạn thời gian thực hiện.",
            "correct_answer": "a",
            "explanation": "Theo Điều 16 khoản 6, việc hạn chế xử lý dữ liệu cá nhân phải được thực hiện trong vòng 72 giờ sau khi nhận được yêu cầu hợp lệ từ phía chủ thể dữ liệu.",
            "article_id": 16,
            "article_name": "Điều 16 - Quyền của chủ thể dữ liệu",
            "difficulty": "hard",
            "category": "rights"
        },
        # Điều 17
        {
            "content": "Nghĩa vụ quan trọng nhất của Bên kiểm soát dữ liệu cá nhân theo Điều 17 là gì?",
            "option_a": "Phải đăng quảng cáo trên truyền hình về chính sách bảo mật.",
            "option_b": "Áp dụng các biện pháp tổ chức và kỹ thuật phù hợp để bảo vệ dữ liệu cá nhân, chống xử lý trái phép hoặc mất mát.",
            "option_c": "Lưu trữ dữ liệu cá nhân mãi mãi không bao giờ xóa.",
            "option_d": "Chia sẻ dữ liệu cá nhân cho các đối tác kinh doanh để tăng lợi nhuận.",
            "correct_answer": "b",
            "explanation": "Theo Điều 17 và các điều khoản liên quan, bên kiểm soát dữ liệu có nghĩa vụ thực hiện các biện pháp quản lý và kỹ thuật phù hợp để đảm bảo an toàn thông tin.",
            "article_id": 17,
            "article_name": "Điều 17 - Nghĩa vụ của bên kiểm soát dữ liệu",
            "difficulty": "easy",
            "category": "obligations"
        },
        {
            "content": "Theo Điều 17, Bên kiểm soát dữ liệu có nghĩa vụ gì khi xảy ra sự cố vi phạm quy định bảo vệ dữ liệu cá nhân?",
            "option_a": "Tự âm thầm khắc phục và không thông báo cho ai để bảo vệ uy tín.",
            "option_b": "Thông báo cho Bộ Công an (Cục An ninh mạng và phòng, chống tội phạm sử dụng công nghệ cao) chậm nhất 72 giờ sau khi phát hiện vi phạm.",
            "option_c": "Đăng thông báo xin lỗi công khai trên mạng xã hội Facebook.",
            "option_d": "Chỉ cần thông báo cho khách hàng của mình.",
            "correct_answer": "b",
            "explanation": "Theo các quy định tại Nghị định 13/2023/NĐ-CP, trường hợp phát hiện xảy ra vi phạm quy định bảo vệ dữ liệu cá nhân, Bên Kiểm soát phải lập hồ sơ thông báo gửi Bộ Công an chậm nhất 72 giờ.",
            "article_id": 17,
            "article_name": "Điều 17 - Nghĩa vụ của bên kiểm soát dữ liệu",
            "difficulty": "medium",
            "category": "obligations"
        },
        {
            "content": "Khi Bên kiểm soát dữ liệu cá nhân thuê Bên xử lý dữ liệu cá nhân, trách nhiệm pháp lý cao nhất đối với các thiệt hại gây ra cho chủ thể dữ liệu thuộc về ai?",
            "option_a": "Bên xử lý dữ liệu chịu trách nhiệm hoàn toàn.",
            "option_b": "Bên kiểm soát dữ liệu cá nhân chịu trách nhiệm chính, trừ khi có thỏa thuận khác và luật định khác.",
            "option_c": "Chủ thể dữ liệu tự gánh chịu rủi ro.",
            "option_d": "Đơn vị cung cấp dịch vụ Internet (ISP).",
            "correct_answer": "b",
            "explanation": "Mối quan hệ giữa bên kiểm soát và bên xử lý: Bên kiểm soát dữ liệu cá nhân chịu trách nhiệm cuối cùng trước pháp luật và chủ thể dữ liệu về mọi thiệt hại xảy ra.",
            "article_id": 17,
            "article_name": "Điều 17 - Nghĩa vụ của bên kiểm soát dữ liệu",
            "difficulty": "hard",
            "category": "obligations"
        },
        # Điều 23
        {
            "content": "Theo Điều 23 Nghị định 13/2023/NĐ-CP, trẻ em từ bao nhiêu tuổi trở lên thì việc xử lý dữ liệu cá nhân của trẻ em cần phải có sự đồng ý của cả trẻ em đó?",
            "option_a": "Từ đủ 6 tuổi trở lên.",
            "option_b": "Từ đủ 7 tuổi trở lên.",
            "option_c": "Từ đủ 14 tuổi trở lên.",
            "option_d": "Chỉ cần cha mẹ đồng ý, không cần sự đồng ý của trẻ em ở bất kỳ độ tuổi nào.",
            "correct_answer": "b",
            "explanation": "Theo Điều 23 khoản 1, trường hợp xử lý dữ liệu cá nhân của trẻ em từ đủ 7 tuổi trở lên, phải có sự đồng ý của trẻ em và sự đồng ý của cha, mẹ hoặc người giám hộ.",
            "article_id": 23,
            "article_name": "Điều 23 - Bảo vệ dữ liệu cá nhân của trẻ em",
            "difficulty": "easy",
            "category": "children"
        },
        {
            "content": "Theo Điều 23, việc xử lý dữ liệu cá nhân của trẻ em dưới 7 tuổi bắt buộc phải có sự đồng ý của ai?",
            "option_a": "Của chính trẻ em đó.",
            "option_b": "Của cha, mẹ hoặc người giám hộ theo quy định của pháp luật.",
            "option_c": "Của cơ sở giáo dục nơi trẻ em đang học tập.",
            "option_d": "Của Ủy ban nhân dân xã, phường nơi trẻ em cư trú.",
            "correct_answer": "b",
            "explanation": "Theo Điều 23 khoản 1, đối với trẻ em dưới 7 tuổi, việc xử lý dữ liệu cá nhân chỉ cần có sự đồng ý của cha, mẹ hoặc người giám hộ hợp pháp.",
            "article_id": 23,
            "article_name": "Điều 23 - Bảo vệ dữ liệu cá nhân của trẻ em",
            "difficulty": "medium",
            "category": "children"
        },
        {
            "content": "Khi thu thập dữ liệu cá nhân của trẻ em, Bên kiểm soát dữ liệu cá nhân có trách nhiệm gì đặc biệt theo Điều 23?",
            "option_a": "Phải xác minh tuổi của trẻ em và yêu cầu sự đồng ý của cha, mẹ hoặc người giám hộ theo quy định.",
            "option_b": "Chỉ cần cam kết không bán dữ liệu cho bên thứ ba.",
            "option_c": "Phải tặng quà miễn phí cho trẻ em khi thu thập dữ liệu.",
            "option_d": "Không cần xác minh tuổi mà chỉ dựa vào lời khai của người dùng.",
            "correct_answer": "a",
            "explanation": "Theo Điều 23 khoản 2, Bên Kiểm soát dữ liệu cá nhân phải thực hiện việc xác minh tuổi của trẻ em trước khi tiến hành xử lý dữ liệu cá nhân.",
            "article_id": 23,
            "article_name": "Điều 23 - Bảo vệ dữ liệu cá nhân của trẻ em",
            "difficulty": "hard",
            "category": "children"
        },
        # Điều 26
        {
            "content": "Hành vi nào sau đây bị nghiêm cấm theo quy định tại Điều 26 và Nghị định 13/2023/NĐ-CP?",
            "option_a": "Xóa dữ liệu cá nhân khi chủ thể dữ liệu yêu cầu.",
            "option_b": "Mua bán, chuyển giao trái phép dữ liệu cá nhân.",
            "option_c": "Sử dụng dữ liệu cá nhân để thực hiện hợp đồng đã ký kết.",
            "option_d": "Mã hóa dữ liệu để bảo mật thông tin.",
            "correct_answer": "b",
            "explanation": "Nghị định nghiêm cấm việc mua, bán, tiết lộ, chuyển giao dữ liệu cá nhân trái phép hoặc sử dụng dữ liệu cá nhân sai mục đích ban đầu.",
            "article_id": 26,
            "article_name": "Điều 26 - Vi phạm và mức phạt",
            "difficulty": "easy",
            "category": "violations"
        },
        {
            "content": "Tổ chức, cá nhân vi phạm quy định bảo vệ dữ liệu cá nhân tùy theo tính chất, mức độ vi phạm có thể bị xử lý như thế nào?",
            "option_a": "Chỉ bị nhắc nhở rút kinh nghiệm.",
            "option_b": "Bị xử lý kỷ luật, xử phạt vi phạm hành chính hoặc bị truy cứu trách nhiệm hình sự theo quy định của pháp luật.",
            "option_c": "Bị đình chỉ hoạt động vĩnh viễn không cần xem xét mức độ.",
            "option_d": "Chỉ bị phạt tiền không quá 10 triệu đồng.",
            "correct_answer": "b",
            "explanation": "Quy định chung tại Nghị định 13/2023/NĐ-CP nêu rõ các hình thức kỷ luật, hành chính hoặc hình sự áp dụng đối với chủ thể vi phạm.",
            "article_id": 26,
            "article_name": "Điều 26 - Vi phạm và mức phạt",
            "difficulty": "medium",
            "category": "violations"
        },
        {
            "content": "Theo quy định pháp luật hiện hành và Nghị định 13/2023/NĐ-CP, việc thiết lập các hệ thống thu thập thông tin cá nhân của người dân khi chưa được đồng ý bị coi là hành vi gì?",
            "option_a": "Hành vi hợp pháp phục vụ cộng đồng.",
            "option_b": "Hành vi vi phạm quy định về bảo vệ dữ liệu cá nhân và có thể bị phạt hành chính hoặc xử lý hình sự.",
            "option_c": "Hành vi được khuyến khích trong chuyển đổi số.",
            "option_d": "Hành vi bình thường không vi phạm pháp luật.",
            "correct_answer": "b",
            "explanation": "Mọi hành vi thu thập thông tin cá nhân quy mô lớn khi chưa được chủ thể đồng ý và không thuộc trường hợp miễn trừ đều vi phạm nghiêm trọng và sẽ bị xử phạt nghiêm khắc.",
            "article_id": 26,
            "article_name": "Điều 26 - Vi phạm và mức phạt",
            "difficulty": "hard",
            "category": "violations"
        },
        # Điều 30
        {
            "content": "Cơ quan chuyên trách bảo vệ dữ liệu cá nhân tại Việt Nam theo Điều 30 Nghị định 13/2023/NĐ-CP là cơ quan nào?",
            "option_a": "Cục An toàn thông tin (Bộ Thông tin và Truyền thông).",
            "option_b": "Cục An ninh mạng và phòng, chống tội phạm sử dụng công nghệ cao (A05) thuộc Bộ Công an.",
            "option_c": "Tòa án nhân dân tối cao.",
            "option_d": "Viện kiểm sát nhân dân tối cao.",
            "option_a": "Cục An toàn thông tin (Bộ Thông tin và Truyền thông).",
            "option_b": "Cục An ninh mạng và phòng, chống tội phạm sử dụng công nghệ cao thuộc Bộ Công an.",
            "option_c": "Tòa án nhân dân tối cao.",
            "option_d": "Viện kiểm sát nhân dân tối cao.",
            "correct_answer": "b",
            "explanation": "Theo Điều 30 khoản 2, Cục An ninh mạng và phòng, chống tội phạm sử dụng công nghệ cao thuộc Bộ Công an là Cơ quan chuyên trách bảo vệ dữ liệu cá nhân.",
            "article_id": 30,
            "article_name": "Điều 30 - Cơ quan bảo vệ dữ liệu cá nhân",
            "difficulty": "easy",
            "category": "government"
        },
        {
            "content": "Cổng thông tin quốc gia về bảo vệ dữ liệu cá nhân được vận hành bởi cơ quan nào?",
            "option_a": "Bộ Tư pháp.",
            "option_b": "Bộ Công an.",
            "option_c": "Bộ Thông tin và Truyền thông.",
            "option_d": "Bộ Khoa học và Công nghệ.",
            "correct_answer": "b",
            "explanation": "Cổng thông tin quốc gia về bảo vệ dữ liệu cá nhân do Cơ quan chuyên trách bảo vệ dữ liệu cá nhân (thuộc Bộ Công an) xây dựng và quản lý.",
            "article_id": 30,
            "article_name": "Điều 30 - Cơ quan bảo vệ dữ liệu cá nhân",
            "difficulty": "medium",
            "category": "government"
        },
        {
            "content": "Trách nhiệm xây dựng và hướng dẫn thực hiện các biện pháp kỹ thuật bảo vệ dữ liệu cá nhân tại Cổng thông tin quốc gia thuộc về cơ quan nào theo Điều 30?",
            "option_a": "Bộ Công an phối hợp với các Bộ, ngành liên quan.",
            "option_b": "Hiệp hội An toàn thông tin Việt Nam (VNISA).",
            "option_c": "Các doanh nghiệp viễn thông lớn tự chịu trách nhiệm.",
            "option_d": "Phòng Thương mại và Công nghiệp Việt Nam (VCCI).",
            "correct_answer": "a",
            "explanation": "Theo Điều 30, Bộ Công an có trách nhiệm chủ trì xây dựng, vận hành và phối hợp hướng dẫn các biện pháp kỹ thuật bảo vệ dữ liệu cá nhân.",
            "article_id": 30,
            "article_name": "Điều 30 - Cơ quan bảo vệ dữ liệu cá nhân",
            "difficulty": "hard",
            "category": "government"
        }
    ]

    # 2. Badges data
    badges_data = [
        {
            "badge_key": "thanh_than",
            "name": "Thần Thánh Bảo Mật",
            "description": "Trả lời đúng 10 câu liên tiếp",
            "icon": "🥇",
            "condition": json.dumps({"type": "streak", "value": 10})
        },
        {
            "badge_key": "biet_luat",
            "name": "Thông Thạo Pháp Lý",
            "description": "Trả lời đúng câu hỏi về tất cả 10 điều khoản",
            "icon": "📚",
            "condition": json.dumps({"type": "all_articles", "value": 10})
        },
        {
            "badge_key": "chien_binh",
            "name": "Chiến Binh Dữ Liệu",
            "description": "Đứng đầu leaderboard trong 1 ván game",
            "icon": "🏆",
            "condition": json.dumps({"type": "leaderboard_top1", "value": 1})
        },
        {
            "badge_key": "nhanh_tay",
            "name": "Tốc Độ Ánh Sáng",
            "description": "Hoàn thành game trong dưới 3 phút",
            "icon": "⚡",
            "condition": json.dumps({"type": "time", "value": 180})
        },
        {
            "badge_key": "kien_nhan",
            "name": "Kiên Nhẫn Sắt Đá",
            "description": "Chơi đủ 5 ván game",
            "icon": "💪",
            "condition": json.dumps({"type": "total_games", "value": 5})
        },
        {
            "badge_key": "toan_ven",
            "name": "Toàn Vẹn Hoàn Hảo",
            "description": "Đúng 100% một ván game (không sai câu nào)",
            "icon": "✨",
            "condition": json.dumps({"type": "perfect_game", "value": 1})
        }
    ]

    # Use SQLAlchemy to seed database
    from models.engine.sql import session
    from models.category import Category
    from models.question import Question
    from models.badge_definition import BadgeDefinition

    # Clear existing questions and badges to ensure fresh seed
    session.query(Question).delete()
    session.query(BadgeDefinition).delete()
    session.commit()

    # Seed Categories and Questions
    categories_inserted = {}
    for q in questions_data:
        cat_name = q["category"]
        if cat_name not in categories_inserted:
            # Check if category exists
            cat = session.query(Category).filter_by(name=cat_name).first()
            if not cat:
                cat = Category(name=cat_name)
                session.add(cat)
                session.commit()
                print(f"Inserted Category: {cat_name} with id {cat.id}")
            categories_inserted[cat_name] = cat.id

        # Insert Question
        db_q = Question(
            content=q["content"],
            option_a=q["option_a"],
            option_b=q["option_b"],
            option_c=q["option_c"],
            option_d=q["option_d"],
            correct_answer=q["correct_answer"],
            explanation=q["explanation"],
            article_id=q["article_id"],
            article_name=q["article_name"],
            difficulty=q["difficulty"],
            category=q["category"],
            category_id=categories_inserted[cat_name]
        )
        session.add(db_q)
    session.commit()
    print(f"Seeded {len(questions_data)} questions.")

    # Seed Badges
    for b in badges_data:
        # Check if badge exists
        badge = session.query(BadgeDefinition).filter_by(badge_key=b["badge_key"]).first()
        if badge:
            badge.name = b["name"]
            badge.description = b["description"]
            badge.icon = b["icon"]
            badge.condition = b["condition"]
        else:
            badge = BadgeDefinition(
                badge_key=b["badge_key"],
                name=b["name"],
                description=b["description"],
                icon=b["icon"],
                condition=b["condition"]
            )
            session.add(badge)
    session.commit()
    print(f"Seeded {len(badges_data)} badges.")

    session.close()
    print("Database seeding completed successfully!")

if __name__ == '__main__':
    seed()
