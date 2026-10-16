# Cài đặt Agent tạo Slide, Ebook và Landing page

## 1. Đặt skill

Chép thư mục `slide-ebook-agent` (giữ nguyên cấu trúc) vào:

| Công cụ | Theo dự án | Dùng chung mọi dự án |
|---|---|---|
| Claude Code | `<dự-án>/.claude/skills/slide-ebook-agent` | `~/.claude/skills/slide-ebook-agent` |
| Codex | `<dự-án>/.agents/skills/slide-ebook-agent` | `~/.codex/skills/slide-ebook-agent` |

## 2. Tạo môi trường chạy (Python 3.9 trở lên)

Trong thư mục `slide-ebook-agent`:

```sh
python3 -m venv slide_ebook_agent/.venv
slide_ebook_agent/.venv/bin/python -m pip install -r slide_ebook_agent/requirements.txt
slide_ebook_agent/.venv/bin/python -m playwright install chromium
```

Windows PowerShell:

```powershell
py -m venv slide_ebook_agent\.venv
slide_ebook_agent\.venv\Scripts\python.exe -m pip install -r slide_ebook_agent\requirements.txt
slide_ebook_agent\.venv\Scripts\python.exe -m playwright install chromium
```

Máy đã có Google Chrome thì có thể bỏ lệnh `playwright install chromium`: agent tự dùng Chrome khi không thấy Chromium của Playwright.

## 3. Kiểm tra nhanh

```sh
slide_ebook_agent/.venv/bin/python slide_ebook_agent/agent.py --help
```

Mở lại Claude Code hoặc Codex để skill được nhận, rồi gõ `/slide-ebook-agent` (Codex: `$slide-ebook-agent`).

## 4. Font (tuỳ chọn, để sửa PPTX đúng font)

Bản PDF, bản trình chiếu HTML và landing luôn hiển thị đúng font. Muốn mở PPTX trong PowerPoint/Keynote đúng font thì cài **Be Vietnam Pro** (miễn phí, Google Fonts). Phong cách `retron` dùng thêm **Space Grotesk**.

## 5. API key (không bắt buộc)

- Không có key: AI trong Claude Code / Codex tự soạn bản thảo (lệnh `doc` → viết `ban-thao.json` → `kiem`). Đây là cách mặc định.
- Có key OpenAI: tạo `.env` ở thư mục làm việc với `OPENAI_API_KEY=...` (tuỳ chọn `OPENAI_MODEL`) để dùng lệnh `dan-y`/`chay` soạn tự động và lệnh rút gọn slide tràn chữ.

## Bộ nhận diện

Agent đọc logo, link, slogan, khoá học từ `~/.claude/skills/tai-lieu-slimai` nếu máy có; nếu không, dùng bản đóng kèm `slide-ebook-agent/tai-lieu-slimai`. Đặt biến `SLIMAI_SKILL_DIR` để chỉ sang bộ nhận diện khác.
