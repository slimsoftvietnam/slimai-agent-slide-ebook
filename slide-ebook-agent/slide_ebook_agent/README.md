# Agent tạo Slide và Ebook

Chuyển tài liệu thô (PDF, DOCX, PPTX, Markdown, TXT, trang web) thành **bộ slide** (`.pptx` sửa được và `.pdf`) và **ebook** A4 (`.pdf`) dùng chung nội dung, thuật ngữ, hình ảnh và nhận diện SlimAI. Thiết kế theo khung PEAS tại [PEAS.md](PEAS.md).

## Chuẩn thương hiệu

- [brand_voice.md](brand_voice.md): giọng văn, xưng hô, tiêu đề, chữ trên nút, quy tắc sự thật. Tác tử biên tập tự đọc file này.
- [design_system.md](design_system.md): màu, chữ, hình khối, thành phần, chuyển động, biểu đồ — dùng chung cho ebook, slide và landing.

## Cài đặt

Từ thư mục gốc dự án:

```sh
python3 -m venv slide_ebook_agent/.venv
slide_ebook_agent/.venv/bin/pip install -r slide_ebook_agent/requirements.txt
```

- **Không bắt buộc API key.** Dùng trong Claude Code / Codex: lệnh `doc` đọc nguồn, AI tự soạn `ban-thao.json` theo [BAN_THAO.md](BAN_THAO.md), lệnh `kiem` kiểm tra. Có `OPENAI_API_KEY` trong `.env` thì lệnh `dan-y`/`chay` soạn tự động (tuỳ chọn `OPENAI_MODEL`, mặc định `gpt-4.1-mini`).
- Cần skill **tai-lieu-slimai** tại `~/.claude/skills/tai-lieu-slimai`. Skill này chứa logo, link, slogan, khoá học (`assets/brand.json`) và mẫu ebook. Nếu đặt ở chỗ khác, khai báo bằng `SLIMAI_SKILL_DIR`.
- Agent dùng Chromium của Playwright. Nếu chưa có, agent tự dùng Google Chrome cài sẵn trên máy. Muốn cài Chromium riêng: `slide_ebook_agent/.venv/bin/python -m playwright install chromium`.

## Chạy

**Bước 1: đọc nguồn và biên tập bản thảo.** Agent dừng ở đây để bạn duyệt:

```sh
slide_ebook_agent/.venv/bin/python slide_ebook_agent/agent.py dan-y ~/Downloads/tai-lieu.pdf --ten cam-nang-ai --so-slide 24
```

Agent tạo `output/slide-ebook/cam-nang-ai/` gồm:

- `ban-thao.md`: bản đọc nhanh để duyệt (10 phương án tên, cảnh báo bản quyền, lời mở đầu, các chương, danh sách slide).
- `ban-thao.json`: bản thảo chung cho cả ebook lẫn slide. Muốn sửa câu chữ, đổi tên hay bỏ slide thì sửa trực tiếp file này.
- `nguon.md`, `anh/`: nội dung và ảnh đã trích từ nguồn.

Agent **tự chọn một bảng màu** hợp chủ đề và đối tượng (nền khối dùng 3–7 sắc độ). Ảnh xem trước nằm trong `bang-mau.png`, mã màu ghi trong `ban-thao.md`. Muốn màu cụ thể thì nói luôn từ đầu: `--mau "xanh navy và vàng"`. Agent chỉ hỏi lại khi thật sự cần, ví dụ tài liệu làm cho một thương hiệu khác mà nguồn không ghi màu nhận diện.

**Bước 2: dựng và kiểm định.**

```sh
slide_ebook_agent/.venv/bin/python slide_ebook_agent/agent.py dung output/slide-ebook/cam-nang-ai --xuat ~/Downloads
```

Đổi màu trước khi dựng: `--mau "tông xanh lá tươi"` (mô tả bằng lời) hoặc `--bang-mau "#0f7c86,#ef7d32,#0b2e36,#eef8f8,#11191b"` (5 mã màu chính xác theo thứ tự `chính,phụ,đậm,nền,chữ`). Slide, nền khối và ebook đều đổi theo.

Kết quả:

- `SlimAI - <Tên> (Slide).pptx`: slide 16:9, mọi chữ, hình khối và ảnh đều là đối tượng gốc, sửa được trong PowerPoint, Keynote hoặc Google Slides. Có sẵn ghi chú thuyết trình.
- `SlimAI - <Tên> (Slide).pdf`: cùng toạ độ và cỡ chữ với bản PPTX.
- `SlimAI - <Tên> (Trinh chieu).html`: bản trình chiếu một tệp, mở bằng Chrome, Edge hoặc Safari 18 trở lên. Chuyển trang kiểu morph, nội dung hiện lần lượt. Phím: ← → để chuyển, F để toàn màn hình.
- `SlimAI - <Tên> (Ebook).pdf`: ebook A4 theo chuẩn tai-lieu-slimai.
- `bao-cao-qa.md` và `qa/*.jpg`: báo cáo kiểm định và ảnh từng trang, từng slide.

**Bước 3 (tuỳ chọn): landing page có form đăng ký.**

```sh
slide_ebook_agent/.venv/bin/python slide_ebook_agent/agent.py landing output/slide-ebook/cam-nang-ai --xuat ~/Downloads --form-action https://…
```

- `SlimAI - <Tên> (Landing).html`: một tệp, font nhúng sẵn, chạy tốt trên điện thoại. Các khối: hero có thẻ số liệu lơ lửng, dải công cụ, vấn đề + so sánh, quy trình các bước, lộ trình cấp độ, các chương, biểu đồ trước/sau (nếu bản thảo có bảng dạng `A → B`), khối điểm chính nền navy, việc cần làm, **form đăng ký**, khoá học AI Agent, hệ sinh thái SlimAI.
- Phong cách mặc định `saas-soft` (nền sáng xanh nhạt, thẻ kính mờ, khối navy có quầng sáng). Muốn phong cách khác thì đưa ảnh mẫu/mô tả để chỉnh `landing_page.py`.
- `--form-action`: URL nhận dữ liệu form (POST FormData: ho_ten, so_dien_thoai, email, cong_ty, vai_tro, nhu_cau, dong_y, nguon, tai_lieu, trang, thoi_gian). Bỏ trống thì form chỉ kiểm tra dữ liệu và báo "bản xem trước", không gửi đi đâu. `--cta` đổi chữ nút kêu gọi.
- Chỉ dùng nội dung trong bản thảo: không bịa khách hàng, logo đối tác, lời chứng thực hay số liệu.

Muốn chạy liền không dừng duyệt: dùng `chay` thay cho `dan-y` (nhận cùng tham số với `dan-y`, cộng thêm `--loai` và `--xuat`).

| Tham số | Ý nghĩa |
|---|---|
| `--so-slide 24` | Số slide mong muốn. Agent tự cộng bìa, mục lục, mở chương, tóm tắt, khoá học và hệ sinh thái. |
| `--doi-tuong "…"` | Đối tượng đọc. Mặc định: chủ doanh nghiệp SME, quản lý, dân văn phòng. |
| `--ghi-cong author/compile/translate` | Biên soạn / Sưu tầm và biên soạn lại / Biên dịch bởi SlimAI. |
| `--loai ca-hai/ebook/slide` | Chỉ dựng một trong hai sản phẩm. |
| `--phong-cach saas/retron/visual/co-dien` | `saas` (mặc định): hệ thiết kế SaaS xanh dương dùng chung cho slide, ebook và landing (thẻ kính, khối navy có quầng sáng, Be Vietnam Pro, Morph) — xem [design_system.md](design_system.md). `retron`: phong cách Retron tím — panel gradient tím→lilac, khối lập phương 3D bóng, tiêu đề Space Grotesk hai màu, thẻ trắng đổ bóng, slide mở chương tím phủ kín, nút tím; có Morph. `visual`: dàn trang Visual-First theo bảng màu tài liệu. `co-dien`: kiểu ebook SlimAI, không chuyển động. |
| `--mau "…"` | Yêu cầu màu bằng lời. Bỏ trống thì agent tự chọn theo chủ đề. |
| `--bang-mau "5 mã màu"` | Ghi đè bảng màu bằng mã chính xác. |
| `--khong-khoa-hoc` | Bỏ box CTA và trang khoá học AI Agent. |

## Bộ slide gồm gì

- **Slide tự động:** bìa, nội dung chính, mở đầu từng chương, điểm chính cần nhớ, khoá học AI Agent (nút bấm và QR), hệ sinh thái SlimAI (logo và 5 kênh mạng xã hội, đều có link).
- **Slide nội dung:** mô hình chọn 1 trong 9 khung `bullets`, `cards`, `steps`, `stats`, `compare`, `quote`, `prompt`, `image`, `table`. Mô hình chỉ điền chữ vào khung, không tự vẽ toạ độ.
- **Chữ:** agent đo từng ô chữ trong Chromium và co lại tới khi vừa. Chữ cùng cấp trên một slide dùng cùng một cỡ. Nếu vẫn tràn ở cỡ tối thiểu, agent nhờ mô hình rút gọn slide đó (tối đa 2 vòng).
- **Chuyển động:** các phần tử tên `!!…` (nền, tiêu đề, thẻ, logo) có mặt ở 2 slide liên tiếp sẽ trượt và đổi kích thước sang vị trí mới. PPTX dùng **Morph**, chạy trên PowerPoint 2019, 2021 và Microsoft 365; Keynote và Google Slides chỉ hiện hiệu ứng mờ dần. Bản HTML dùng View Transitions.
- **Màu:** phong cách `saas` (mặc định) dùng bảng màu xanh dương của design system cho cả slide, ebook và landing; `retron` dùng tím. Cả hai giữ màu riêng, trừ khi bạn yêu cầu màu (`--mau` hoặc `--bang-mau`); khi đó khối 3D, đốm màu và nền được xoay sắc độ sang màu chính. Bảng màu agent tự chọn vẫn lưu trong `ban-thao.json` để dùng khi chạy `--phong-cach visual`.
- **Font:** phong cách `retron` dùng **Space Grotesk** (tiêu đề) và **Be Vietnam Pro** (nội dung); phong cách `visual` dùng **Be Vietnam Pro** và **Playfair Display** (miễn phí, Google Fonts, đủ dấu tiếng Việt). Bản PDF và HTML luôn đúng font. Muốn sửa PPTX đúng font thì cài hai font này trên máy; nếu không, PowerPoint tự thay font khác. Phong cách `co-dien` dùng Arial nên hiển thị đúng trên mọi máy.

## Giới hạn

- Không đọc PDF scan (không OCR). Hãy gửi bản có chữ hoặc transcript.
- Agent không gửi hay chia sẻ file. Nó chỉ ghi vào thư mục đầu ra.
- Nội dung nguồn được coi là dữ liệu. Câu chỉ dẫn nằm trong tài liệu sẽ không được làm theo.
- Ảnh lấy từ nguồn thuộc về tác giả gốc. Kiểm tra quyền sử dụng trước khi phát hành.
