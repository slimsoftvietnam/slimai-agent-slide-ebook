"""Dựng ebook SlimAI từ thư mục dự án -> PDF A4.

Cách dùng:  python3 build.py <thư-mục-dự-án> [đường-dẫn-pdf-đầu-ra]

Thư mục dự án gồm:
  ebook.json        thông số (xem ebook.example.json)
  content/*.html    nội dung, ghép theo thứ tự tên file (00-mo-dau.html, 01-chuong-1.html, ...)
  img/              ảnh minh hoạ (src="img/..." trong content)

build.py tự thêm: bìa, mục lục có số trang (2 lượt render), header/footer mọi trang,
macro CTA, trang khoá học (tuỳ chọn), trang hệ sinh thái SlimAI, link cho mọi logo.
Logo, link mạng xã hội, slogan, khoá học: đọc từ assets/brand.json (nguồn duy nhất).
Cần: playwright (chromium), pypdfium2, pypdf.
"""
import base64, html, json, pathlib, re, sys
from playwright.sync_api import sync_playwright
import pypdfium2 as pdfium
from pypdf import PdfReader, PdfWriter
from pypdf.annotations import Link
from pypdf.generic import ArrayObject, NameObject, NumberObject

TPL = pathlib.Path(__file__).resolve().parent
SKILL = TPL.parent.parent
ASSETS = SKILL / "assets"
BRAND = json.loads((ASSETS / "brand.json").read_text())

P = pathlib.Path(sys.argv[1]).expanduser().resolve()
CFG = json.loads((P / "ebook.json").read_text())
OUT = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else CFG.get("output", P / "ebook.pdf")).expanduser()

TITLE = CFG["title"]
SLOGAN = BRAND["slogan"]
SITE, SITE_LABEL = BRAND["site"], BRAND["site_label"]
COURSE = BRAND["course"]
uri = lambda p: pathlib.Path(p).resolve().as_uri()
logo = lambda k: uri(ASSETS / BRAND["logos"][k]["file"])
icon_b64 = base64.b64encode((ASSETS / BRAND["logos"]["slimai_icon"]["file"]).read_bytes()).decode()

# ---------- nội dung ----------
body = "".join(f.read_text() for f in sorted((P / "content").glob("*.html")))

def cta(m):
    """<!--CTA kicker | tiêu đề | đoạn văn | nút (tuỳ chọn) -->"""
    parts = [x.strip() for x in m.group(1).split("|")]
    k, h, p = parts[:3]
    btn = parts[3] if len(parts) > 3 and parts[3] else "Xem khoá học →"
    return (f'<div class="cta"><div class="in"><div class="tx"><div class="k">{k}</div><h4>{h}</h4><p>{p}</p></div>'
            f'<div><a class="btn" href="{COURSE["url"]}">{btn}</a><span class="url">{COURSE["url_label"]}</span></div></div></div>')
body = re.sub(r"<!--CTA\s+(.*?)-->", cta, body, flags=re.S)

def course_html():
    c = CFG.get("course", {})
    intro = c.get("intro", "Bước tiếp theo là để AI <b style=\"color:#ffd166\">làm việc thay bạn</b>: tự nghiên cứu, soạn nội dung, xử lý dữ liệu và chạy các quy trình lặp lại mỗi ngày.")
    mods = ""
    for i, m in enumerate(COURSE["modules"], 1):
        lis = "".join(f"<li>{x}</li>" for x in m["items"])
        mods += f'<div class="mod"><div class="mh"><span class="mn">{i:02d}</span><div><b>{m["title"]}</b><small>{m["sub"]}</small></div></div><ul>{lis}</ul></div>\n'
    n = len(COURSE["modules"]) + 1
    ucs = "".join(f'<div class="uc"><span class="ic">{a}</span><div><b>{t}</b><p>{d}</p></div></div>' for a, t, d in COURSE["usecases"])
    mods += (f'<div class="mod m3"><div class="mh"><span class="mn">{n:02d}</span><div><b>{COURSE["usecases_title"]}</b>'
             f'<small>{COURSE["usecases_sub"]}</small></div></div><div class="ucs">{ucs}</div></div>\n')
    return f'''<section class="course" id="khoa-hoc">
<div class="hero"><div class="k">{c.get("kicker", "Bước tiếp theo sau cuốn cẩm nang này")}</div>
<h1>{COURSE["name"].replace(" cho ", "<br>cho ", 1)}</h1>
<p class="lead-course">{intro}</p>
<p class="aud">{COURSE["audience"]}</p></div>
<h3>Chương trình học</h3>
{mods}
<div class="final"><div style="flex:1"><h3>{c.get("final_title", "Đăng ký tìm hiểu khoá học")}</h3>
<p>{c.get("final_text", "Quét mã QR hoặc bấm vào nút bên dưới để xem lộ trình và đăng ký.")}</p>
<a class="btn" href="{COURSE["url"]}">Xem khoá học AI Agent →</a><div class="u">{COURSE["url_label"]}</div></div>
<div class="qr"><div id="qr"></div><span>QUÉT ĐỂ XEM KHOÁ HỌC</span></div></div>
</section>
'''

def eco_html():
    cards = "".join(
        f'<div class="card"><div class="lg"><a href="{e["link"]}"><img src="{logo(e["key"])}"></a></div>'
        f'<a class="u" href="{e["link"]}">{e["label"]}</a><p>{e["desc"]}</p></div>' for e in BRAND["ecosystem"])
    social = ""
    for s in BRAND["social"]:
        svg = (ASSETS / "logos" / f'{s["key"]}.svg').read_text()
        if s.get("boxed"):
            white = svg.replace("<svg ", '<svg fill="#fff" ', 1)
            svg = f'<span class="zalo">{white}</span>'
        else:
            svg = svg.replace("<svg ", f'<svg fill="{s["color"]}" ', 1)
        social += f'<a href="{s["link"]}"><div>{svg}<span>{s["name"]}</span></div></a>'
    c1, c2, c3 = BRAND["slogan_colors"]
    w = SLOGAN.split(" · ")
    follow = CFG.get("eco_follow", "Theo dõi SlimAI để nhận thêm tài liệu về AI")
    note = CFG.get("footer_note", "")
    return f'''<section class="eco">
<a href="{SITE}"><img class="brand" src="{logo("slimai")}"></a>
<div class="slogan2"><span style="color:{c1}">{w[0]}</span> · <span style="color:{c2}">{w[1]}</span> · <span style="color:{c3}">{w[2]}</span></div>
<h2>Hệ sinh thái SlimAI</h2>
<div class="cards">{cards}</div>
<p style="text-align:center;margin-bottom:4pt">{follow}</p>
<div class="social">{social}</div>
<p style="text-align:center" class="small">© {CFG.get("year", 2026)} SlimAI · {SITE_LABEL}{" · " + note if note else ""}</p>
</section>'''

if CFG.get("course", {}).get("enabled", True):
    body += course_html()
body += eco_html()

# ---------- mục lục ----------
entries = []  # (level, nhãn, chuỗi để dò trang)
for sec in re.findall(r'<section class="chapter[^"]*">(.*?)</section>', body, re.S):
    h1 = re.search(r"<h1>(.*?)</h1>", sec)
    num = re.search(r'<div class="num">(.*?)</div>', sec)
    if h1:
        entries.append(("ch", f"{num.group(1)} · {h1.group(1)}" if num else h1.group(1), h1.group(1)))
        entries += [("sec", h2, h2) for h2 in re.findall(r"<h2>(.*?)</h2>", sec)]
    else:
        entries += [("ch", h2, h2) for h2 in re.findall(r"<h2>(.*?)</h2>", sec)]
if CFG.get("course", {}).get("enabled", True):
    intro_key = re.sub(r"<[^>]+>", "", CFG.get("course", {}).get("intro", "Bước tiếp theo là để AI"))[:30]
    entries.append(("ch", COURSE["name"], intro_key))

def toc_html(pages):
    return "\n".join(f'<div class="row {l}"><span>{lab}</span><span class="dots"></span><span class="pg">{pg}</span></div>'
                     for (l, lab, _), pg in zip(entries, pages))

def norm(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", s))).strip()

QRJS = f"""<script src="https://cdn.jsdelivr.net/npm/qrcode-generator@1.4.4/qrcode.js"></script>
<script>window.addEventListener('DOMContentLoaded',()=>{{const el=document.getElementById('qr');if(!el)return;const q=qrcode(0,'M');q.addData('{COURSE["url"]}');q.make();el.innerHTML=q.createSvgTag({{cellSize:4,margin:0,scalable:true}});}});</script>"""

def page_html(inner, css_files=("style.css",), extra_css=""):
    links = "".join(f'<link rel="stylesheet" href="{uri(TPL / c)}">' for c in css_files)
    return f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>{TITLE}</title>
{links}<style>{extra_css}{CFG.get("extra_css", "")}</style>{QRJS}</head><body>{inner}</body></html>"""

HEADER = f"""<div style="width:100%;padding:0 18mm;font-family:Helvetica,Arial,sans-serif;-webkit-print-color-adjust:exact">
<div style="display:flex;align-items:center;justify-content:space-between;padding-bottom:5px;border-bottom:1px solid #e3e7ef">
<div style="display:flex;align-items:center;gap:6px"><img src="data:image/png;base64,{icon_b64}" style="height:16px">
<span style="font-size:11px;font-weight:800;color:#0b2a5b">SlimAI</span></div>
<span style="font-size:8.5px;color:#5b6475;letter-spacing:.3px;white-space:nowrap">{TITLE}</span></div>
<div style="height:2px;width:60px;background:linear-gradient(90deg,#e8318a,#12b5e5,#f6c21c)"></div></div>"""
FOOTER = f"""<div style="width:100%;padding:0 18mm;font-family:Helvetica,Arial,sans-serif;-webkit-print-color-adjust:exact">
<div style="display:flex;align-items:center;justify-content:space-between;border-top:1px solid #e3e7ef;padding-top:5px;font-size:8.5px;color:#5b6475">
<span style="font-weight:700;color:#0b2a5b">{SLOGAN}</span>
<span>{SITE_LABEL}</span>
<span style="font-weight:700;color:#0b2a5b"><span class="pageNumber"></span></span></div></div>"""

# ---------- bìa ----------
cv = CFG.get("cover", {})
credit = BRAND["credit"].get(cv.get("credit", "author"), BRAND["credit"]["author"])
credit = credit.replace("SlimAI", "<b>SlimAI</b>")
if cv.get("image"):
    bg = f'<img class="poster" src="{cv["image"]}">'
else:
    imgs = "".join('<img src="%s">' % i for i in cv.get("images", []))
    bg = f'<div class="mosaic">{imgs}</div>'
COVER = f"""<div class="cover">{bg}<div class="shade"></div>
 <a class="top" href="{SITE}"><img src="{logo("slimai_icon")}"><span>SlimAI</span>{f'<em>{CFG["series"]}</em>' if CFG.get("series") else ""}</a>
 <div class="main">
  <div class="kicker">{cv.get("kicker", "")}</div>
  <h1>{cv.get("title_html", TITLE)}</h1>
  <p>{cv.get("subtitle_html", "")}</p>
  <div class="bar"></div>
  <div class="by">{credit} · {SITE_LABEL}{f'<br><span>{cv["source"]}</span>' if cv.get("source") else ""}</div>
 </div>
 <div class="foot">{SLOGAN}</div>
</div>"""

def render(pg, htmlstr, path, hf=True):
    f = P / "_tmp.html"
    f.write_text(htmlstr)
    pg.goto(f.as_uri(), wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    opts = dict(path=str(path), prefer_css_page_size=True, print_background=True)
    if hf:
        opts.update(display_header_footer=True, header_template=HEADER, footer_template=FOOTER)
    pg.pdf(**opts)

with sync_playwright() as p:
    b = None
    for kw in ({}, {"channel": "chromium"}, {"channel": "chrome"}):  # Chromium của Playwright, rồi Google Chrome có sẵn
        try:
            b = p.chromium.launch(**kw)
            break
        except Exception:
            continue
    if b is None:
        sys.exit("Không mở được Chromium/Chrome. Cài: python3 -m playwright install chromium")
    pg = b.new_page()
    # Lượt 1: render với số trang giả để tìm vị trí thật của từng mục
    render(pg, page_html(body.replace("<!--TOC-->", toc_html(["00"] * len(entries)))), P / "_pass1.pdf")
    doc = pdfium.PdfDocument(str(P / "_pass1.pdf"))
    texts = [re.sub(r"\s+", " ", doc[i].get_textpage().get_text_range()) for i in range(len(doc))]
    toc_end = next((i for i, t in enumerate(texts) if "Mục lục" in t), 0)
    start = toc_end + 1
    if entries:
        k1 = norm(entries[0][2])
        while start < len(texts) and k1 not in texts[start]:
            start += 1
    pages, cur = [], start
    for _, _, key in entries:
        k = norm(key)
        found = next((i for i in range(cur, len(texts)) if k in texts[i]), None)
        if found is None:
            print("KHÔNG TÌM THẤY TRONG PDF:", k); pages.append("–"); continue
        pages.append(str(found + 1)); cur = found  # khớp số ở footer (bìa không đánh số)
    doc.close()
    # Lượt 2: render thật
    render(pg, page_html(body.replace("<!--TOC-->", toc_html(pages))), P / "_body.pdf")
    render(pg, page_html(COVER, ("style.css", "cover.css")), P / "_cover.pdf", hf=False)
    b.close()

w = PdfWriter()
for part in ["_cover.pdf", "_body.pdf"]:
    for page in PdfReader(str(P / part)).pages:
        w.add_page(page)
# Header/footer của Chrome không giữ link -> gắn link thủ công: logo header + chữ ai.slim.vn ở footer
MM = 72 / 25.4
for i in range(1, len(w.pages)):
    H = float(w.pages[i].mediabox.height)
    for rect in [(18 * MM, H - 17 * MM, 45 * MM, H - 10 * MM), (90 * MM, 5 * MM, 120 * MM, 13 * MM)]:
        a = Link(rect=rect, url=SITE)
        a[NameObject("/Border")] = ArrayObject([NumberObject(0)] * 3)
        w.add_annotation(page_number=i, annotation=a)
w.add_metadata({"/Title": TITLE, "/Author": f"SlimAI ({SITE_LABEL})", "/Subject": f"{CFG.get('series', 'SlimAI')} – {SLOGAN}"})
OUT.parent.mkdir(parents=True, exist_ok=True)
with open(OUT, "wb") as fh:
    w.write(fh)
for f in ["_tmp.html", "_pass1.pdf", "_body.pdf", "_cover.pdf"]:
    (P / f).unlink(missing_ok=True)
print("OK:", OUT, "| số trang:", len(PdfReader(str(OUT)).pages), "| MB:", round(OUT.stat().st_size / 1e6, 1))
