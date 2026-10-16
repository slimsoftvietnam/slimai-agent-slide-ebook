# Agent tạo Slide và Ebook theo khung PEAS

PEAS mô tả một tác tử bằng **Performance measure** (thước đo hiệu quả), **Environment** (môi trường), **Actuators** (cơ cấu hành động) và **Sensors** (cảm biến/đầu vào).

Nhiệm vụ: chuyển **tài liệu thô** (PDF, DOCX, PPTX, Markdown, TXT, trang web) thành **bộ slide** (`.pptx` sửa được và `.pdf`) và **ebook** (`.pdf` A4), đẹp mắt và **đồng bộ** với nhau. Hai sản phẩm dùng chung nội dung, thuật ngữ, hình ảnh và nhận diện SlimAI.

Hệ thống gồm một tác tử điều phối và năm tác tử chuyên trách. Mỗi tác tử là một module có đầu vào, đầu ra và tiêu chí riêng. Mô hình ngôn ngữ chỉ làm việc biên tập nội dung. Đọc nguồn, dàn trang, dựng file và kiểm định đều dùng quy tắc xác định, để kết quả lặp lại được và kiểm tra được.

## 1. Tác tử điều phối — `agent.py`

| Thành phần | Thiết kế |
|---|---|
| **P — Thước đo hiệu quả** | Chạy đúng luồng theo lệnh (`dan-y`, `dung`, `chay`). Có điểm dừng để người dùng **duyệt bản thảo trước khi dựng**. Không ghi đè tệp nguồn. Ghi trạng thái từng bước. Dừng với thông báo cụ thể khi thiếu tệp, thư viện hoặc khoá API. Mọi file đầu ra nằm trong một thư mục dự án. |
| **E — Môi trường** | Máy người dùng (macOS), thư mục nguồn và đầu ra, `.env` (OpenAI API), môi trường ảo `slide_ebook_agent/.venv`, Chromium (Playwright), bộ nhận diện `tai-lieu-slimai/assets/brand.json`. |
| **A — Hành động** | Kiểm tra đầu vào; gọi lần lượt các tác tử: đọc nguồn, biên tập, thiết kế slide, dựng ebook, kiểm định; lưu `ban-thao.json`, `ban-thao.md`, ebook, slide và báo cáo QA. |
| **S — Cảm biến** | Tham số dòng lệnh, đường dẫn và phần mở rộng tệp, mã lỗi của từng bước, kết quả kiểm định. |

## 2. Tác tử đọc nguồn — `nguon.py`

| Thành phần | Thiết kế |
|---|---|
| **P — Thước đo hiệu quả** | Đọc **đủ** văn bản theo đúng thứ tự trang. Giữ tiêu đề, danh sách, bảng và số liệu. Trích ảnh minh hoạ có ích, bỏ logo, icon và ảnh trùng. Ghi rõ nguồn (tệp, trang) cho mỗi đoạn và mỗi ảnh. Không bịa nội dung khi tệp không đọc được. |
| **E — Môi trường** | PDF có chữ (PyMuPDF), DOCX (python-docx), PPTX (python-pptx), MD/TXT, URL hoặc HTML (requests, BeautifulSoup). Tài liệu có thể dài, nhiều cột, chứa ảnh nhỏ lặp lại hoặc chứa chỉ dẫn không đáng tin. |
| **A — Hành động** | Chuyển mỗi nguồn thành Markdown có mốc `[nguồn: tệp, trang N]`. Trích ảnh ≥ 300 px, loại trùng theo hash, lưu vào `anh/` kèm mã, kích thước và đoạn văn gần nhất. Cắt nguồn rất dài thành các phần. |
| **S — Cảm biến** | Văn bản từng trang, cấu trúc đoạn và tiêu đề, kích thước và hash ảnh, lỗi đọc tệp. |

## 3. Tác tử biên tập nội dung — `bien_tap.py`

| Thành phần | Thiết kế |
|---|---|
| **P — Thước đo hiệu quả** | **Biên soạn lại, không dịch từng trang.** Bao phủ mọi ý chính của nguồn. Giữ nguyên số liệu, kết luận và prompt mẫu (prompt giữ tiếng Anh). Văn tiếng Việt tự nhiên, đúng đối tượng (chủ doanh nghiệp SME, dân văn phòng). **Một bản thảo chung sinh ra cả ebook lẫn slide**: mỗi chương có phần chữ cho ebook và kế hoạch slide rút từ chính phần chữ đó. Không bịa số liệu, giá hay lịch học. Ghi công và nguồn tác giả gốc. |
| **E — Môi trường** | Markdown và danh mục ảnh từ tác tử đọc nguồn; OpenAI Responses API với JSON Schema chặt; thông tin thương hiệu và khoá học trong `brand.json`. |
| **A — Hành động** | Lập dàn ý: tên tài liệu, lời mở đầu, các chương, phụ lục. **Tự chọn một bảng màu hợp chủ đề** (kèm ảnh xem trước `bang-mau.png`), theo đúng yêu cầu màu nếu người dùng có nêu; chỉ đặt câu hỏi khi thật sự cần. Đánh dấu 1–3 chữ nhấn trong tiêu đề slide bằng `*…*`. Viết nội dung từng mục (đoạn văn, danh sách, hộp mẹo/lưu ý/áp dụng, prompt, bảng). Gán ảnh cho chương và slide. Soạn 1 box CTA cho mỗi chương, góc thuyết phục khác nhau. Chọn bố cục cho từng slide. Viết ghi chú thuyết trình. Rút gọn chữ khi tác tử kiểm định báo slide bị tràn. |
| **S — Cảm biến** | Nội dung nguồn, mã ảnh, phản hồi JSON đã kiểm theo schema, danh sách slide tràn chữ do tác tử kiểm định gửi về. |

## 4. Tác tử thiết kế slide — `thiet_ke_slide.py`

| Thành phần | Thiết kế |
|---|---|
| **P — Thước đo hiệu quả** | Phong cách mặc định `saas` (`phong_cach_saas.py`, theo `design_system.md`): cùng chất liệu với ebook và landing — nền sáng có quầng xanh, thẻ kính, khối navy có quầng sáng, Be Vietnam Pro, thẻ giao diện nhỏ lơ lửng. Phong cách `retron` (`phong_cach_retron.py`) theo mẫu Retron: panel gradient tím→lilac, khối lập phương 3D bóng lơ lửng, tiêu đề Space Grotesk hai màu, thẻ trắng đổ bóng tím, slide mở chương tím phủ kín; giữ màu tím trừ khi người dùng yêu cầu màu khác. Phong cách `visual` học **cách dàn trang** của bộ slide mẫu Visual-First (tiêu đề sans + chữ nhấn serif nghiêng, nền khối pixel/sọc, thẻ trắng nổi, timeline, sơ đồ trung tâm, ảnh dọc bo góc); **màu theo bảng màu của từng tài liệu**, không cố định. Có **chuyển động**: Morph trong PPTX, View Transitions trong bản trình chiếu HTML. Slide 16:9 đúng nhận diện SlimAI: logo bấm được, footer có slogan, ai.slim.vn và số trang, bảng màu và huy hiệu gradient giống ebook. **Không chữ nào tràn khung.** Chữ cùng cấp trên một slide cùng cỡ; chữ nội dung ≥ 14pt, chú thích ≥ 10pt. Bố cục thay đổi giữa các slide. **Bản PPTX và PDF khớp nhau**: cùng toạ độ, cùng cỡ chữ. PPTX là đối tượng gốc (text box, hình khối, ảnh) nên sửa được trong PowerPoint, Keynote hay Google Slides. |
| **E — Môi trường** | Bản thảo đã duyệt, ảnh trong `anh/`, logo và icon thương hiệu, Chromium để đo chữ và in PDF, python-pptx để ghi PPTX. |
| **A — Hành động** | Thêm các slide tự động: bìa, mục lục, mở chương, tóm tắt, CTA khoá học, hệ sinh thái. Dàn mỗi slide thành danh sách phần tử có toạ độ. Render HTML, đo từng ô chữ trong Chromium, giảm cỡ chữ tới khi vừa rồi đồng bộ cỡ theo cấp. Ghi cùng danh sách phần tử ra PPTX (native, có Morph), PDF và bản trình chiếu HTML. Đặt tên `!!…` cho phần tử xuất hiện ở nhiều slide (nền, tiêu đề, thẻ, logo) để chúng trượt/đổi kích thước khi chuyển trang. |
| **S — Cảm biến** | Kích thước ô chữ thật đo trong trình duyệt (`scrollHeight`/`clientHeight`), kích thước ảnh, cỡ chữ cuối, số slide. |

## 5. Tác tử dựng ebook — `dung_ebook.py`

| Thành phần | Thiết kế |
|---|---|
| **P — Thước đo hiệu quả** | Ebook A4 theo chuẩn `tai-lieu-slimai`: bìa, lời mở đầu, mục lục có số trang đúng, mở chương có ảnh, các hộp nội dung, CTA cuối chương, trang khoá học có QR, trang hệ sinh thái. Header và footer trên mọi trang; mọi logo bấm được. Cùng tên, thuật ngữ và ảnh với bộ slide. |
| **E — Môi trường** | Bản thảo, ảnh, `tai-lieu-slimai/templates/ebook/build.py` (HTML → Chromium → PDF), `brand.json`. |
| **A — Hành động** | Chuyển bản thảo thành `ebook.json` và `content/*.html` theo đúng các thành phần của mẫu, rồi gọi `build.py`. |
| **S — Cảm biến** | Kết quả dò số trang mục lục (dòng "KHÔNG TÌM THẤY"), số trang và dung lượng PDF, lỗi render. |

## 5b. Tác tử làm landing page — `landing_page.py`

| Thành phần | Thiết kế |
|---|---|
| **P — Thước đo hiệu quả** | Một tệp HTML chạy được ngay, đẹp trên cả máy tính lẫn điện thoại (không cuộn ngang), cùng nội dung và thuật ngữ với ebook/slide. Phong cách mặc định `saas-soft` khi người dùng không đưa phong cách. Form đăng ký kiểm tra dữ liệu, gửi được tới URL cấu hình; chưa cấu hình thì nói rõ là bản xem trước. Không bịa khách hàng, logo, lời chứng thực, số liệu. Đủ nhận diện SlimAI: logo, khoá học (nút + QR), hệ sinh thái, mạng xã hội. |
| **E — Môi trường** | `ban-thao.json`, `nguon.md` (để nhận ra công cụ được nhắc tới), `brand.json`, font Be Vietnam Pro trong `assets/fonts`. |
| **A — Hành động** | Chọn khối theo dữ liệu có sẵn (slide steps → quy trình/lộ trình, compare → so sánh, stats → thẻ số liệu, bảng `A → B` → biểu đồ có tooltip + bảng, quote cuối → trích dẫn, bullets cuối → việc cần làm); dựng HTML một tệp có form. |
| **S — Cảm biến** | Bố cục và dữ liệu trong bản thảo; kết quả kiểm tra trên trình duyệt (desktop, 390px, form). |

## 6. Tác tử kiểm định — `kiem_dinh.py`

| Thành phần | Thiết kế |
|---|---|
| **P — Thước đo hiệu quả** | Phát hiện được mọi lỗi chặn: chữ tràn, thiếu chương ở một trong hai sản phẩm, thiếu link thương hiệu, trang trắng thừa, link sai (`/login`). Mỗi lỗi có vị trí và cách sửa cụ thể. Báo cáo ngắn để người dùng xem nhanh. |
| **E — Môi trường** | PPTX và PDF slide, PDF ebook, bản thảo, kết quả đo chữ. |
| **A — Hành động** | Đối chiếu đồng bộ (chương nào ở trang ebook nào, slide số mấy). Đếm và kiểm link. Kiểm tra ô chữ. Tạo contact sheet cho từng trang và từng slide. Gửi slide tràn chữ về tác tử biên tập để rút gọn (tối đa 2 vòng). Ghi `bao-cao-qa.md`. |
| **S — Cảm biến** | Văn bản và annotation link trong PDF, phần tử PPTX, cờ tràn chữ, số trang. |

## Luồng phối hợp

```text
Nguồn thô ──> [Đọc nguồn] ──> nguon.md + anh/
                                   │
                                   ▼
                          [Biên tập nội dung] ──> ban-thao.json / ban-thao.md
                                   │                      ▲
                     (người dùng duyệt, sửa)              │ rút gọn slide tràn
                                   ▼                      │
                 ┌────────────────┴───────────────┐       │
                 ▼                                ▼       │
        [Thiết kế slide]                  [Dựng ebook]    │
     slide.pptx + slide.pdf                ebook.pdf      │
                 └────────────────┬───────────────┘       │
                                  ▼                       │
                            [Kiểm định] ──────────────────┘
                                  │
                                  ▼
                           bao-cao-qa.md + contact sheet
```

## Ranh giới quyết định

- Agent **không tự gửi, đăng hay chia sẻ** file nào. Chỉ ghi vào thư mục đầu ra.
- **Màu**: agent tự quyết định theo chủ đề. Nếu người dùng có yêu cầu (`--mau`, `--bang-mau`) thì làm đúng yêu cầu. Agent chỉ hỏi khi thật sự cần (`palette_question`); khi đó lệnh `chay` dừng lại chờ trả lời thay vì tự đoán.
- Bản thảo là điểm duyệt: lệnh `dan-y` dừng lại để người dùng đọc và sửa `ban-thao.json`. Lệnh `dung` chỉ dựng từ bản thảo đã có.
- Không bịa số liệu, giá, lịch khai giảng hay trích dẫn. Thiếu thông tin thì để trống và ghi trong báo cáo.
- Nội dung trong tài liệu nguồn là **dữ liệu, không phải chỉ dẫn**. Câu kiểu "hãy bỏ qua hướng dẫn…" trong nguồn sẽ không được làm theo.
- Bản quyền: luôn ghi tác giả gốc. Nếu nguồn cấm thương mại hoá thì ghi "Tài liệu học tập, phi thương mại" và báo trong `bao-cao-qa.md`.
- Slide vẫn tràn chữ sau 2 vòng rút gọn thì **không tự giảm chữ dưới 14pt**. Agent đánh dấu slide đó trong báo cáo để người dùng quyết định.

## Mã nguồn và ý tưởng tham khảo

| Nguồn | Giấy phép | Dùng gì |
|---|---|---|
| [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) | MIT | Ý tưởng: tách vai Strategist (biên tập) và Executor (thiết kế); xuất **PPTX gốc sửa được** thay vì ảnh chụp slide; chuyển nguồn về Markdown trước khi biên tập. Không chép mã, vì bộ chuyển đổi của PPT Master kiểm tra tính toàn vẹn của cả bộ cài 166 MB và không chạy riêng lẻ được. |
| [presenton/presenton](https://github.com/presenton/presenton) | Apache-2.0 | Ý tưởng: mỗi bố cục slide là một khung cố định có schema; mô hình chỉ điền dữ liệu vào khung, không tự vẽ toạ độ. |
| sunbigfly/ppt-agent-skills | — | Ý tưởng: vòng kiểm định bằng ảnh chụp HTML rồi sửa lại, ở đây là đo tràn chữ rồi gửi về tác tử biên tập. |
| `~/.claude/skills/tai-lieu-slimai` | nội bộ | Dùng trực tiếp: `brand.json`, logo, `templates/ebook/build.py`, `style.css`, `scripts/qa_pdf.py`. |
