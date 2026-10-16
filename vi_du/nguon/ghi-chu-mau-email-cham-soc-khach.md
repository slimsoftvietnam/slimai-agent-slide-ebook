# ghi chú buổi chia sẻ - dùng AI viết email chăm sóc khách cho shop online (bản nháp)

Ghi chép nhanh, chưa biên tập. Tình huống và số liệu trong ghi chú là VÍ DỤ GIẢ ĐỊNH để minh hoạ, không phải số liệu khảo sát.
Đối tượng: chủ shop online nhỏ, nhân viên chăm sóc khách hàng.

## 1. vấn đề
- shop có nhiều khách mua 1 lần rồi thôi. email chăm sóc sau mua gần như không ai làm vì "không có thời gian".
- khi có làm thì viết tay từng email, mỗi email một kiểu, hay quên gửi.
- dùng ChatGPT/Claude viết thì ra email chung chung, đọc là biết máy viết, khách không mở.
- nguyên nhân: chỉ gõ "viết email chăm sóc khách" — không nói khách là ai, đã mua gì, mình muốn khách làm gì sau khi đọc.

## 2. ba loại email nên có
- email cảm ơn sau mua (gửi trong 24h): cảm ơn, hướng dẫn dùng sản phẩm, số điện thoại hỗ trợ.
- email hỏi thăm sau 7 ngày: hỏi trải nghiệm, xin đánh giá.
- email mời quay lại sau 30 ngày: gợi ý sản phẩm liên quan đến món đã mua, có hạn dùng ưu đãi nếu shop đang có.

## 3. quy trình 4 bước
Bước 1 - xuất danh sách đơn hàng tuần trước ra Excel (tên, email, sản phẩm, ngày mua).
Bước 2 - viết 1 email mẫu thật tốt cho từng loại, có chỗ trống [tên khách], [sản phẩm].
Bước 3 - giao cho agent: đọc danh sách, chọn loại email theo số ngày từ lúc mua, điền thông tin, soạn nháp.
Bước 4 - người phụ trách đọc lướt nháp và bấm gửi. agent KHÔNG tự gửi.

## 4. công thức yêu cầu
- khách là ai (mua gì, khi nào)
- mục đích của email (cảm ơn / xin đánh giá / mời quay lại)
- giọng văn của shop (thân thiện, xưng "shop" - gọi "bạn")
- độ dài (dưới 120 chữ), 1 lời kêu gọi duy nhất
ví dụ thiếu: "viết email chăm sóc khách" -> chung chung.
ví dụ đủ: "viết email hỏi thăm chị Lan mua nồi chiên 7 ngày trước, xin chị đánh giá 1 câu, giọng thân thiện, dưới 120 chữ" -> email cụ thể, có lời kêu gọi.

## 5. thời gian trước / sau (ví dụ giả định)
| Việc | Viết tay (phút) | Có agent (phút) |
|---|---|---|
| 20 email cảm ơn | 60 | 10 (duyệt nháp) |
| 20 email hỏi thăm | 50 | 8 (duyệt nháp) |
| 20 email mời quay lại | 80 | 12 (duyệt nháp) |
nhóm tự tính: nếu đúng như ví dụ, mỗi tuần tiết kiệm khoảng 2,5 giờ cho 60 email. cần đo thật ở từng shop.

## 6. lưu ý
- không gửi email khi khách chưa đồng ý nhận thư.
- không để agent tự gửi; người phụ trách luôn duyệt.
- không đưa thông tin thanh toán, địa chỉ chi tiết của khách vào prompt nếu không cần.
câu chốt: email chăm sóc không cần dài, chỉ cần đúng người, đúng lúc, đúng một lời mời.
