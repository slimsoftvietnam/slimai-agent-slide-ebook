# SlimAI — Giọng thương hiệu cho tài liệu (ebook · slide · landing page)

> Nguồn: bản nháp `../brand_voice.md` (tổng hợp từ bài mẫu mạng xã hội) + các chuẩn người dùng đã chốt khi làm ebook, slide và landing (10/2026).
> Tác tử biên tập (`bien_tap.py`) tự đọc file này mỗi lần soạn bản thảo. Sửa giọng văn ở ĐÂY, không sửa rải rác trong code.
> Mục đánh dấu `[CẦN XÁC NHẬN]` là điều chủ thương hiệu chưa chốt.

## 1. Thương hiệu và người đọc

- **Thương hiệu:** SlimAI (ai.slim.vn) — AI Agent Agency: tư vấn, đào tạo, triển khai AI cho doanh nghiệp. Tên, link, logo, slogan, khoá học chỉ lấy từ `tai-lieu-slimai/assets/brand.json`.
- **Người đọc mặc định:** chủ doanh nghiệp nhỏ (SME), trưởng phòng, nhân viên văn phòng — muốn dùng AI vào việc thật, không nhất thiết biết kỹ thuật.
- **Xưng hô:** gọi người đọc là **"bạn"**; thương hiệu tự xưng **"SlimAI"** (không "chúng tôi/em/mình"). `[CẦN XÁC NHẬN]` nếu muốn xưng "chúng tôi" trong báo giá/đề xuất.

## 2. Tính cách

| Là | Không là |
|---|---|
| Thực tế, làm được ngay | Lý thuyết suông, khẩu hiệu chung chung |
| Gần gũi, rõ ràng như đồng nghiệp giỏi giải thích | Học thuật, văn dịch máy, sính tiếng Anh |
| Tự tin, khuyến khích hành động | Cường điệu, hứa chắc kết quả |
| Trung thực về giới hạn và rủi ro | Giấu điều kiện, phóng đại số liệu |

## 3. Quy tắc viết (mọi dạng tài liệu)

- **Biên soạn lại, không dịch từng trang.** Gom ý, bỏ trùng; giữ nguyên số liệu, kết luận, ví dụ, thuật ngữ quan trọng.
- Câu ngắn, mỗi đoạn một ý; động từ cụ thể ("phân loại email", "gửi tóm tắt lúc 8h") thay cho danh từ trừu tượng ("tối ưu hoá quy trình").
- Mở bằng **tình huống quen thuộc / điểm nghẽn**, rồi mới đến giải pháp; luôn nói rõ **con người vẫn duyệt bước quan trọng**.
- Thuật ngữ tiếng Anh giữ nguyên khi phổ biến (AI Agent, prompt, skill, workflow) và giải nghĩa ở lần đầu cho người mới.
- **In đậm** ý chính (tối đa 1–2 cụm mỗi đoạn). Cụm *nhấn* (`*…*`) chỉ dùng trong tiêu đề slide/landing — 1–3 từ đắt nhất.
- Không lạm dụng: dấu chấm than, VIẾT HOA cả câu, emoji, hashtag, "cách mạng hoá", "thay đổi cuộc chơi", "bí mật", "siêu".
- Prompt mẫu, lệnh, code giữ nguyên ngôn ngữ gốc; chỗ cần điền để trong `[ngoặc vuông]`.

## 4. Sự thật và tuyên bố (bắt buộc)

- **Không bịa:** số liệu, giá, lịch khai giảng, ưu đãi, kết quả học viên, khách hàng, logo đối tác, lời chứng thực, trích dẫn.
- Số liệu minh hoạ phải đi kèm nhãn **"ví dụ giả định"** ở MỌI chỗ xuất hiện (bảng, slide số liệu, thẻ trên landing, biểu đồ).
- Phép tính suy ra từ số trong nguồn (vd 60 → 5 = tiết kiệm 55 phút) được phép, nhưng vẫn mang nhãn của số gốc.
- Thiếu bằng chứng → ghi `[CẦN XÁC NHẬN]` trong bản nháp, báo trong `warnings`, không trình bày như sự thật.
- Ghi công tác giả/nguồn gốc; nguồn cấm thương mại → ghi "Tài liệu học tập, phi thương mại".

## 5. Giọng theo từng dạng

| Dạng | Giọng | Độ dài | Ghi chú |
|---|---|---|---|
| **Ebook** | Hướng dẫn, giải thích đủ ý | Đoạn 2–4 câu | Mỗi chương: dẫn nhập 1 câu → mục → hộp mẹo/lưu ý → tóm tắt 3–5 ý → box CTA khoá học (góc thuyết phục riêng mỗi chương) |
| **Slide** | Khẳng định, ít chữ | Tiêu đề ≤ 70 ký tự, ý ≤ 95 ký tự | Tiêu đề là **một câu khẳng định**, không dấu chấm cuối; mỗi slide **một thông điệp**; ghi chú thuyết trình 2–4 câu nói tự nhiên |
| **Landing page** | Thuyết phục nhẹ, lợi ích trước | Đoạn ≤ 3 dòng trên điện thoại | Hero = tên tài liệu + lợi ích; mỗi khối một lời hứa đã có trong nguồn; form ngắn, nói rõ dữ liệu dùng để làm gì |

## 6. Tiêu đề và chữ trên nút (microcopy)

- Tên tài liệu: gọi thẳng đối tượng hoặc lợi ích ("Đưa AI Agent vào doanh nghiệp nhỏ", "Mua AI rồi, sao năng suất chưa tăng?"). Đưa 10 phương án để duyệt.
- Tiêu đề slide/landing: câu khẳng định + cụm nhấn: "Chatbot trả lời, *agent làm việc*".
- Nhãn nhỏ (kicker/pill): danh từ 1–3 chữ: "Vấn đề", "Quy trình", "Số liệu", "Bước tiếp theo".
- **CTA chuẩn:**
  - Nút chính landing: **"Nhận tài liệu miễn phí"** (đổi bằng `--cta`), nút phụ: "Xem nội dung".
  - Khoá học: **"Xem khoá học →"** / "Xem Khoá học AI Agent cho người đi làm →"; câu dẫn: "Để AI làm việc thay bạn".
  - Form gửi xong: "Cảm ơn bạn! SlimAI sẽ liên hệ trong thời gian sớm nhất." · Lỗi: nói ô nào sai, cách sửa.
  - Bản xem trước chưa nối form: "Bản xem trước: form chưa nối nơi nhận dữ liệu, thông tin chưa được gửi đi."
- Ô đồng ý: "Tôi đồng ý để SlimAI liên hệ qua điện thoại/email về tài liệu và dịch vụ liên quan."
- Chân trang: slogan **"Tối ưu · Tự động · Tăng trưởng"** (từ brand.json), ai.slim.vn, số trang.

## 7. Từ nên dùng / tránh

| Dùng | Tránh |
|---|---|
| giao việc cho AI, agent làm, bạn duyệt | AI thay thế con người, sa thải |
| tiết kiệm thời gian (kèm "ví dụ giả định" nếu là minh hoạ) | tiết kiệm 90%, x10 năng suất (không nguồn) |
| bước duyệt của con người, người chịu trách nhiệm | tự động 100%, không cần kiểm tra |
| khoá học, tài liệu, cẩm nang | bí kíp, tuyệt chiêu, độc quyền |

## 8. Cần chủ thương hiệu xác nhận

- `[CẦN XÁC NHẬN]` Mức trang trọng cho tài liệu B2B (báo giá, đề xuất).
- `[CẦN XÁC NHẬN]` Kênh TikTok/Zalo chính thức (brand.json đang dùng `@slimai.x.think`, `slim.vn/link/zalo`).
- `[CẦN XÁC NHẬN]` Nơi nhận dữ liệu form landing (SlimCRM / Google Sheet / webhook) và chính sách dữ liệu cá nhân hiển thị kèm form.
