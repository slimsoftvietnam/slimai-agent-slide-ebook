# SlimAI — Design system cho tài liệu (ebook · slide · landing page)

> **Trạng thái: CHÍNH THỨC (duyệt 16/10/2026).** Hướng **SaaS xanh dương** là mặc định cho cả ba dạng: slide (`--phong-cach saas`), ebook (bảng màu `SAAS` + `ebook_css`) và landing (`saas-soft`). Demo đã duyệt: `~/Downloads/Demo SaaS xanh/`.
> Phong cách khác vẫn dùng được: `retron` (tím gradient + khối 3D), `visual` (Visual-First theo bảng màu tài liệu), `co-dien`.
> Đây là **nguồn sự thật về thiết kế**. Đổi token ở đây thì phải đổi cùng lúc trong: `phong_cach_saas.py` (slide), `SAAS["ebook_css"]` (ebook), `landing_page.py` → `CSS` (landing).
> Logo, link, slogan, khoá học: chỉ từ `tai-lieu-slimai/assets/brand.json`. Giọng văn: `brand_voice.md`.

## 1. Nguyên tắc

1. **Một hệ, ba dạng.** Cùng màu, cùng font, cùng chất liệu (nền sáng có quầng xanh, thẻ kính trắng, khối navy có quầng sáng) — chỉ đổi bố cục theo dạng.
2. **Sáng là chính, navy để nhấn.** Mở chương, số liệu lớn, trích dẫn, tổng kết dùng nền navy; còn lại nền sáng.
3. **Dữ liệu là hình.** Có số thì vẽ (cột, thẻ số liệu, bậc thang) — kèm nhãn "ví dụ giả định" nếu là minh hoạ.
4. **Không ảnh stock, không logo đối tác.** Minh hoạ tự vẽ theo bảng màu (sơ đồ, thẻ giao diện nhỏ, biểu tượng nét).
5. **Đọc được trước, đẹp sau.** Chữ nội dung slide ≥ 14pt; landing không cuộn ngang ở 390px; tương phản chữ ≥ 4.5:1.

## 2. Màu

| Token | Mã | Dùng cho |
|---|---|---|
| `blue` | `#2F6BFF` | màu chính: nút, chữ nhấn, viên số, link |
| `blue-2` | `#5B8CFF` | điểm giữa gradient, hover |
| `cyan` | `#38C6F4` | điểm cuối gradient, đường nối, điểm sáng |
| `blue-deep` | `#1D47C8` | đầu gradient panel, bóng màu |
| `ink` | `#0D1838` | chữ chính, tiêu đề |
| `ink-2` | `#2B3656` | chữ phụ đậm |
| `muted` | `#5F6C8C` | mô tả, chú thích |
| `line` | `#E4E9F5` | viền, đường kẻ |
| `bg` | `#F6F8FE` / `soft` `#EEF4FF` | nền trang / nền khối mềm |
| `navy` | `#08112F` (→ `#12235E` ở đỉnh) | khối tối, slide mở chương |
| `warn` | chữ `#8A5600` trên `#FFF6E3`, viền `#FFE3AD` | nhãn "ví dụ giả định" |
| `ok` / `err` | `#16A34A` / `#D93B3B` | form thành công / lỗi |

- **Gradient chữ & nút:** `linear-gradient(100deg, #2F6BFF, #5B8CFF 45%, #38C6F4)`.
- **Gradient panel (slide, khối khoá học):** 40°: `#1D47C8 → #2F6BFF → #38B8FF`.
- **Quầng sáng:** xanh `#7AA5FF` (góc trái dưới), cyan `#8FDCFF` (góc phải dưới), mờ 70–160px.
- **Biểu đồ 2 nhóm (đã kiểm mù màu):** "trước/làm tay" `#7FA6FF`, "sau/có agent" `#1F5BFF`; luôn có số trên cột + chú giải + bảng (tương phản `#7FA6FF` < 3:1 nên bắt buộc có số).

## 3. Chữ

- **Font duy nhất: Be Vietnam Pro** (400 · 500 · 600 · 700) — đủ dấu tiếng Việt, nhúng sẵn trong `assets/fonts/` cho landing; slide/ebook tải Google Fonts (PPTX cần cài font trên máy).
- Tiêu đề: 600–700, `letter-spacing -0.025em` (hero -0.035em), `text-wrap: balance`.

| Vai trò | Landing | Slide (khung 720×405pt) | Ebook A4 |
|---|---|---|---|
| H1 / bìa | 38–68px, 600 | 37pt, 700 | 32pt |
| H2 / tiêu đề slide | 30–46px | 28.5pt (co tối thiểu 16.5pt) | 17pt, 700 |
| Nội dung | 16–17.5px | ≥ 14pt (thẻ 11pt) | 10.4pt |
| Nhãn (kicker/pill) | 12.5px, 600 | 9.75pt CAPS, giãn 1.5pt | 7.6pt CAPS |

## 4. Hình khối & chất liệu

- **Bo góc:** thẻ 20px (landing) · 0.22in ≈ 12pt (slide) · 12pt (ebook); nút 13px; pill 99px; panel 0.35in.
- **Thẻ kính:** `rgba(255,255,255,.88)` + `backdrop-filter: blur(14px)` + viền trắng 1px + bóng `0 24px 60px -28px rgba(31,73,170,.35)`.
- **Bóng màu:** panel `#1D47C8` α .30; thẻ `#1F49AA` α .16 (slide: `shadow="#rrggbb/alpha"`).
- **Nút chính:** gradient dọc `#4A83FF → #2A62F5`, chữ trắng 600, bóng xanh, hover nhấc 2px + vệt sáng lướt; nút phụ trắng viền `line`.
- **Đường trang trí:** nét 1px `rgba(47,107,255,.16)`, vòng cung đồng tâm ở đáy hero, đường nối bước lượn sóng nét đứt cyan.
- **Thẻ giao diện nhỏ** (thay khối 3D ở phong cách saas): biểu đồ cột, ô gradient có dấu ✓, thẻ số liệu, danh sách tick, ô mờ, chấm sáng — `assets/saas/w_*.png`.

## 5. Thành phần theo dạng

| Thành phần | Landing (`landing_page.py`) | Slide (`phong_cach_saas.py`) | Ebook (mẫu tai-lieu-slimai + `ebook_css`) |
|---|---|---|---|
| Mở đầu | Hero: badge, H1 nửa sau gradient, 2 nút, thẻ kính số liệu quanh khung biểu đồ | Bìa: tiêu đề 2 dòng (dòng 2 xanh), panel gradient số chương, nút "Bắt đầu" | Bìa tối + lưới ảnh mở chương |
| Mục lục | Thanh menu dính + thanh tiến độ | Panel gradient liệt kê chương | Mục lục có số trang |
| Mở chương | — (khối section có pill) | Nền navy + quầng/vệt sáng, số chương 130pt | Ảnh mở chương navy + thẻ kính biểu tượng |
| Quy trình | Bước + minh hoạ giao diện + nối lượn sóng | Bậc thang cột / dải thẻ có viên số | Hình quy trình vẽ sẵn |
| So sánh | Thẻ trắng ✕ ↔ thẻ gradient ✓ | Thẻ trắng ↔ panel | Bảng 2 cột |
| Số liệu | Biểu đồ + thẻ nổi bật + bảng | Slide navy, thẻ số trắng | Bảng + biểu đồ vẽ sẵn + hộp cảnh báo |
| Tổng kết | Khối navy: thẻ kính + trích dẫn | Panel liệt kê ý chính | Hộp "Tóm tắt chương" |
| CTA | Form trong viền gradient + khối khoá học có QR | Slide khoá học: nút + QR | Box CTA cuối chương + trang khoá học |
| Thương hiệu | Footer: hệ sinh thái + mạng xã hội | Logo trái trên, footer slogan · ai.slim.vn · số trang | Header/footer mọi trang |

## 6. Chuyển động

- **Slide:** Morph (PPTX) / View Transitions (HTML) — phần tử tên `!!…` ghép cặp giữa 2 slide (panel, thẻ, tiêu đề, thẻ giao diện, quầng sáng); 1.1s `cubic-bezier(.45,0,.2,1)`.
- **Landing:** hiện dần khi cuộn (0.8s, trễ so le 70–90ms), thẻ hero lơ lửng 8s, dải công cụ chạy 40s, cột biểu đồ mọc 1s, vệt sáng khối navy 9s.
- Luôn tôn trọng `prefers-reduced-motion` (tắt hết chuyển động).

## 7. Biểu đồ (theo skill dataviz)

- Chọn dạng theo việc của dữ liệu; cặp màu ở mục 2 đã chạy `validate_palette.js`.
- Một trục; cột bo đầu 4–7px, khoảng hở giữa cột; số trực tiếp trên cột; chú giải luôn có khi ≥ 2 nhóm; tooltip khi rê/Tab; bảng dữ liệu kèm theo (`details`).
- Chữ trong biểu đồ dùng màu chữ (`ink`/`muted`), không dùng màu của cột.

## 8. Kiểm tra trước khi giao

- Slide: `bao-cao-qa.md` không lỗi chặn; xem từng ảnh trong `qa/`.
- Ebook: mục lục 1 trang, không trang trống thừa, hình đọc được khi in (sơ đồ dùng `wide`).
- Landing: desktop 1440 + mobile 390 không cuộn ngang, form báo lỗi đúng, không lỗi console.
