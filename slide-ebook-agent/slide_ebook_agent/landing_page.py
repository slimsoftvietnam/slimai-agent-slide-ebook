"""Tác tử làm landing page: bản thảo chung (ban-thao.json) -> MỘT tệp HTML landing page có form đăng ký, nhận diện SlimAI.

Phong cách mặc định 'saas-soft' (dùng khi người dùng không đưa phong cách riêng): nền sáng xanh nhạt, tiêu đề lớn căn giữa
có cụm nhấn gradient, thẻ số liệu kính mờ lơ lửng quanh khung biểu đồ, đường nét trang trí mảnh, dải công cụ chạy ngang,
quy trình theo bước có minh hoạ giao diện nhỏ, khối navy đậm có vệt sáng, form đăng ký trong thẻ viền gradient.

Mọi chữ và số lấy từ bản thảo; không bịa số liệu, khách hàng, logo đối tác hay lời chứng thực.
Form gửi tới URL cấu hình (--form-action). Chưa cấu hình thì form chỉ kiểm tra dữ liệu và báo rõ là bản xem trước.
"""
from __future__ import annotations

import base64
import html
import json
import re
from pathlib import Path

from thuong_hieu import ASSETS as BRAND_ASSETS, brand, logo, qr_png

HERE = Path(__file__).resolve().parent
FONTS = HERE / "assets" / "fonts"
TOOLS = ["ChatGPT", "Claude", "Gemini", "Gmail", "Google Drive", "Google Sheets", "Excel", "Word", "Zalo", "Facebook",
         "Notion", "Telegram", "Canva", "Slack", "Zoom", "Google Meet", "Outlook", "CapCut", "Midjourney", "SlimCRM"]

# icon nét mảnh (kiểu Lucide, ISC) — vẽ inline, đổi màu bằng currentColor
ICONS = {
    "book": '<path d="M2 4h6a4 4 0 0 1 4 4v13a3 3 0 0 0-3-3H2z"/><path d="M22 4h-6a4 4 0 0 0-4 4v13a3 3 0 0 1 3-3h7z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "trend": '<path d="M22 7 13.5 15.5l-5-5L2 17"/><path d="M16 7h6v6"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "arrow": '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
    "spark": '<path d="M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9z"/><path d="M19 17v4M17 19h4"/>',
    "layers": '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/>',
    "shield": '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/>',
    "zap": '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>',
    "list": '<path d="M9 6h11M9 12h11M9 18h11"/><path d="m3 6 1 1 2-2M3 12l1 1 2-2M3 18l1 1 2-2"/>',
    "send": '<path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>',
}


def ic(name: str, cls: str = "ic") -> str:
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


# ---------------------------------------------------------------- tiện ích
def esc(s) -> str:
    return html.escape(str(s or ""))


def rich(s: str) -> str:
    """**đậm** -> <b>, *nhấn* -> <em> (màu xanh), giữ an toàn HTML."""
    t = esc(s)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"\*([^*\s][^*]*?)\*", r'<em>\1</em>', t)


def plain(s: str) -> str:
    return re.sub(r"\*+", "", s or "")


def data_uri(path: Path) -> str:
    ext = path.suffix.lower().lstrip(".")
    mime = {"svg": "image/svg+xml", "jpg": "image/jpeg", "jpeg": "image/jpeg"}.get(ext, f"image/{ext}")
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def font_css() -> str:
    out = []
    for w, f in ((400, "Regular"), (500, "Medium"), (600, "SemiBold"), (700, "Bold")):
        p = FONTS / f"BeVietnamPro-{f}.ttf"
        if p.exists():
            out.append(f"@font-face{{font-family:'Be Vietnam Pro';font-weight:{w};font-display:swap;"
                       f"src:url({data_uri(p)}) format('truetype')}}")
    return "\n".join(out)


def all_slides(doc):
    for ch in doc["chapters"]:
        for s in ch["slides"]:
            yield ch, s


def pick(doc, layout, prefer=None, last=False):
    found = [s for _, s in all_slides(doc) if s["layout"] == layout]
    if prefer:
        pref = [s for s in found if re.search(prefer, plain(s["title"]), re.I)]
        found = pref + [s for s in found if s not in pref]
    if not found:
        return None
    return found[-1] if last else found[0]


def num(v: float) -> str:
    return f"{v:g}".replace(".", ",")


def arrow_table(doc):
    """Bảng có cột dạng 'A → B' (trước/sau) -> dữ liệu cho biểu đồ cột ghép."""
    for _, s in all_slides(doc):
        if s["layout"] != "table" or not s.get("rows"):
            continue
        for j in range(1, len(s["header"])):
            vals = [re.search(r"(\d+(?:[.,]\d+)?)\s*→\s*(\d+(?:[.,]\d+)?)", r[j] if j < len(r) else "") for r in s["rows"]]
            if vals and all(vals):
                unit = re.sub(r"[\d.,→\s]+", " ", s["rows"][0][j]).strip()
                parts = [h.strip() for h in re.split(r"→", s["header"][j])]
                a = parts[0] if len(parts) > 1 else "Trước"
                b = parts[1] if len(parts) > 1 else "Sau"
                ex = 2 if len(s["header"]) > 2 and j != 2 else None
                return {"slide": s, "unit": unit, "a": a[:1].upper() + a[1:], "b": b[:1].upper() + b[1:],
                        "rows": [(r[0], float(v.group(1).replace(",", ".")), float(v.group(2).replace(",", "."))) for r, v in zip(s["rows"], vals)],
                        "extra": [r[ex] if ex and len(r) > ex else "" for r in s["rows"]], "extra_head": s["header"][ex] if ex else ""}
    return None


def tools_in(work: Path, doc) -> list[str]:
    src = (work / "nguon.md").read_text() if (work / "nguon.md").exists() else ""
    blob = src + json.dumps(doc, ensure_ascii=False)
    found = []
    for t in TOOLS:
        key = "Drive" if t == "Google Drive" else t
        if re.search(rf"\b{re.escape(key)}\b", blob) and t not in found:
            found.append(t)
    return found


def split_title(t: str) -> tuple[str, str]:
    """Tách tiêu đề: phần cuối (~40% chữ) được nhấn gradient."""
    w = t.split()
    if len(w) < 3:
        return t, ""
    k = max(1, round(len(w) * 0.6))
    return " ".join(w[:k]), " ".join(w[k:])


def caveat(label: str) -> tuple[str, str]:
    """Tách '(ví dụ giả định)' khỏi nhãn số liệu để hiện thành chip riêng."""
    m = re.search(r"\(([^)]*giả định[^)]*)\)", label or "", re.I)
    if not m:
        return label, ""
    return (label[:m.start()] + label[m.end():]).strip(), m.group(1)


# ---------------------------------------------------------------- các khối giao diện
def mini_ui(k: int) -> str:
    """Minh hoạ giao diện nhỏ cho từng bước (thay ảnh 3D của mẫu)."""
    v = k % 3
    if v == 0:
        body = ('<div class="ui-card"><span class="ui-av"></span><i style="width:62%"></i><i style="width:44%"></i>'
                '<i style="width:74%"></i></div><span class="ui-chip" style="top:4px;right:22px;width:60px"></span>'
                '<span class="ui-btn" style="right:2px;bottom:18px">' + ic("arrow") + '</span>')
    elif v == 1:
        body = ('<div class="ui-card"><b class="ui-num"></b><i style="width:80%"></i><i style="width:55%"></i>'
                '<span class="ui-bar"></span></div><span class="ui-sq" style="top:2px;left:30px"></span>'
                '<span class="ui-sq b" style="top:8px;left:60px"></span><span class="ui-sq c" style="top:30px;right:2px"></span>')
    else:
        body = ('<div class="ui-card cols">' + "".join(f'<span style="height:{h}%"></span>' for h in (45, 70, 52, 88, 64)) +
                '</div><span class="ui-tag" style="top:2px;right:12px">' + ic("trend") + '</span><span class="ui-spark"></span>')
    return f'<div class="ui"><span class="ui-glow"></span>{body}</div>'


def hero_widgets(doc, stats, steps, chart) -> str:
    w = []
    n_app = len(doc.get("appendix") or [])
    w.append(f'<div class="wg w-tl"><span class="wg-ic">{ic("book")}</span><div><small>Nội dung</small>'
             f'<b>{len(doc["chapters"])} chương</b>{f"<em>+ {n_app} phụ lục</em>" if n_app else ""}</div></div>')
    for k, pos in ((0, "w-tr"), (1, "w-br")):
        if stats and len(stats.get("stats") or []) > k:
            st = stats["stats"][k]
            lab, cav = caveat(plain(st["label"]))
            chip = f'<span class="chip">{esc(cav)}</span>' if cav else ""
            icon = ic("clock") if k == 0 else ic("zap")
            w.append(f'<div class="wg {pos}"><div class="wg-top"><span class="wg-ic sm">{icon}</span>{chip}</div>'
                     f'<b class="big">{esc(st["value"])}</b><small>{esc(lab)}</small></div>')
    if steps and steps.get("steps"):
        items = "".join(f'<li><span>{ic("check")}</span>{esc(plain(x["title"]))}</li>' for x in steps["steps"][:4])
        w.append(f'<div class="wg w-ml"><small class="cap">{esc(plain(steps["title"]))}</small><ul>{items}</ul></div>')
    if chart:
        mx = max(max(a, b) for _, a, b in chart["rows"]) or 1
        best = max(chart["rows"], key=lambda r: r[1] - r[2])
        bars = ""
        for name, a, b in chart["rows"]:
            hot = " hot" if (name, a, b) == best else ""
            tag = (f'<span class="flag" style="--top:{max(a, b) / mx * 100:.0f}%">−{num(best[1] - best[2])} {esc(chart["unit"])}<i>tiết kiệm nhiều nhất</i></span>' if hot else "")
            bars += (f'<div class="g{hot}">{tag}<span class="a" style="--h:{a / mx * 100:.0f}%"></span>'
                     f'<span class="b" style="--h:{b / mx * 100:.0f}%"></span><p>{esc(name)}</p></div>')
        center = (f'<div class="dash"><div class="dash-h"><b>{esc(plain(chart["slide"]["title"]))}</b>'
                  f'<span class="lg"><i class="a"></i>{esc(chart["a"])}<i class="b"></i>{esc(chart["b"])}</span></div>'
                  f'<div class="dash-plot">{bars}</div></div>')
    else:
        rows = "".join(f'<li><span>{i + 1:02d}</span>{esc(c["title"])}</li>' for i, c in enumerate(doc["chapters"][:5]))
        center = f'<div class="dash"><div class="dash-h"><b>Lộ trình nội dung</b></div><ol class="dash-list">{rows}</ol></div>'
    return f'<div class="stage-wg" aria-hidden="true">{center}{"".join(w)}</div>'


def chart_section(chart, stats) -> str:
    if not chart:
        return ""
    s = chart["slide"]
    mx = max(max(a, b) for _, a, b in chart["rows"]) or 1
    groups = []
    for i, (name, a, b) in enumerate(chart["rows"]):
        groups.append(
            f'<div class="cg" style="--d:{i * 90}ms"><div class="cb">'
            f'<span class="bar a" style="--h:{a / mx * 100:.1f}%" tabindex="0" data-tip="{esc(name)} · {esc(chart["a"])}: {num(a)} {esc(chart["unit"])}">'
            f'<em>{num(a)}</em></span>'
            f'<span class="bar b" style="--h:{b / mx * 100:.1f}%" tabindex="0" data-tip="{esc(name)} · {esc(chart["b"])}: {num(b)} {esc(chart["unit"])}">'
            f'<em>{num(b)}</em></span></div><p>{esc(name)}</p></div>')
    xh = f"<th>{esc(chart['extra_head'])}</th>" if chart["extra_head"] else ""
    rows = "".join(f"<tr><td>{esc(n)}</td><td>{num(a)}</td><td>{num(b)}</td>" + (f"<td>{esc(x)}</td>" if xh else "") + "</tr>"
                   for (n, a, b), x in zip(chart["rows"], chart["extra"]))
    head = f"<tr><th>{esc(s['header'][0])}</th><th>{esc(chart['a'])}</th><th>{esc(chart['b'])}</th>{xh}</tr>"
    note = f'<p class="note">{ic("spark")}<span>{rich(s["subtitle"])}</span></p>' if s.get("subtitle") else ""
    best = max(chart["rows"], key=lambda r: r[1] - r[2])
    side = [f'<div class="hl"><small>Tiết kiệm nhiều nhất</small><b>−{num(best[1] - best[2])} <span>{esc(chart["unit"])}</span></b>'
            f'<p>{esc(best[0])}: {num(best[1])} → {num(best[2])} {esc(chart["unit"])} mỗi lần</p></div>']
    if stats and stats.get("stats"):
        st = stats["stats"][0]
        lab, cav = caveat(plain(st["label"]))
        side.append(f'<div class="hl hl-dk"><small>{esc(lab)}</small><b>{esc(st["value"])}</b>'
                    f'{f"<p>{esc(cav[:1].upper() + cav[1:])}</p>" if cav else ""}</div>')
    return f'''<section class="sec" id="so-lieu"><div class="wrap">
<div class="head rv"><span class="pill">{ic("trend")}Số liệu</span><h2>{rich(s["title"])}</h2>{note}</div>
<div class="chart-wrap"><div class="chart rv"><div class="chart-top"><span class="unit">{esc(chart["unit"])} / lần</span>
<span class="lg"><i class="a"></i>{esc(chart["a"])}<i class="b"></i>{esc(chart["b"])}</span></div>
<div class="plot">{"".join(groups)}</div><div class="tip" role="status"></div>
<details><summary>Xem dạng bảng</summary><table>{head}{rows}</table></details></div>
<div class="side rv">{"".join(side)}</div></div></div></section>'''


# ---------------------------------------------------------------- trang
def build(doc: dict, work: Path, out: Path, form_action: str = "", cta_text: str = "") -> Path:
    b = brand()
    course = b["course"]
    stats = pick(doc, "stats")
    process = pick(doc, "steps", prefer=r"bước|quy trình")
    levels = next((s for _, s in all_slides(doc) if s["layout"] == "steps" and s is not process), None)
    cmp = pick(doc, "compare")
    quote = pick(doc, "quote", last=True)
    chart = arrow_table(doc)
    todo = next((s for s in reversed([s for _, s in all_slides(doc)]) if s["layout"] == "bullets"), None)
    tools = tools_in(work, doc)
    intro = doc["intro"]
    cta = cta_text or "Nhận tài liệu miễn phí"
    logo_uri = data_uri(logo("slimai"))
    qr = data_uri(qr_png(course["url"], work / "qr-khoa-hoc.png"))

    nav = [("van-de", "Vấn đề"), ("quy-trinh", "Quy trình") if process else None, ("noi-dung", "Nội dung"),
           ("so-lieu", "Số liệu") if chart else None, ("dang-ky", "Đăng ký")]
    nav_html = "".join(f'<a href="#{i}">{t}</a>' for i, t in filter(None, nav))

    # --- hero
    t1, t2 = split_title(doc["title"])
    h1 = esc(t1) + (f' <span class="grad">{esc(t2)}</span>' if t2 else "")
    deco = ('<svg class="deco" viewBox="0 0 1200 700" preserveAspectRatio="none" aria-hidden="true">'
            '<path d="M0 120 L250 120 Q300 120 300 170 L300 700"/><path d="M1200 120 L950 120 Q900 120 900 170 L900 700"/>'
            '<path d="M80 0 L80 60 Q80 90 110 90 L240 90"/><path d="M1120 0 L1120 60 Q1120 90 1090 90 L960 90"/>'
            '<circle cx="300" cy="170" r="3"/><circle cx="900" cy="170" r="3"/></svg>')
    hero = f'''<header class="hero"><div class="orb o1"></div><div class="orb o2"></div><div class="rings" aria-hidden="true"></div>{deco}
<div class="wrap"><span class="badge rv"><i></i>{esc(doc["kicker"])}</span><h1 class="rv">{h1}</h1>
<p class="sub rv">{rich(doc["subtitle"])}</p>
<div class="cta rv"><a class="btn" href="#dang-ky">{esc(cta)}{ic("arrow")}</a><a class="btn ghost" href="#noi-dung">Xem nội dung</a></div>
{hero_widgets(doc, stats, process or levels, chart)}</div></header>'''

    tools_html = ""
    if tools:
        row = "".join(f"<span>{esc(t)}</span>" for t in tools)
        tools_html = (f'<section class="tools"><p>Áp dụng ngay với công cụ bạn đang dùng</p>'
                      f'<div class="marquee"><div class="track">{row}{row}{row}{row}</div></div></section>')

    # --- vấn đề + so sánh
    chips = "".join(f"<li>{ic('check')}<span>{rich(x)}</span></li>" for x in intro["for_whom"])
    cmp_html = ""
    if cmp:
        li = lambda items, icon: "".join(f"<li>{ic(icon)}<span>{rich(x)}</span></li>" for x in items)
        cmp_html = (f'<div class="cmp rv"><div class="cmp-c"><span class="tag">Trước</span><h4>{esc(cmp["left"]["title"])}</h4>'
                    f'<ul>{li(cmp["left"]["items"], "x")}</ul></div><span class="cmp-arrow">{ic("arrow")}</span>'
                    f'<div class="cmp-c on"><span class="tag">Sau</span><h4>{esc(cmp["right"]["title"])}</h4>'
                    f'<ul>{li(cmp["right"]["items"], "check")}</ul></div></div>')
    problem = f'''<section class="sec" id="van-de"><div class="wrap two">
<div class="rv"><span class="pill">{ic("zap")}Vấn đề</span><h2>{rich(doc["chapters"][0]["title"])}</h2>
<p class="lead">{rich(intro["paragraphs"][0])}</p>
<h3>Tài liệu dành cho</h3><ul class="for">{chips}</ul></div>{cmp_html}</div></section>'''

    # --- quy trình
    proc_html = ""
    if process:
        st = process["steps"]
        cells = []
        for k, x in enumerate(st):
            cells.append(f'<div class="step rv" style="--d:{k * 80}ms">{mini_ui(k)}<span class="num">Bước {k + 1:02d}</span>'
                         f'<h4>{esc(x["title"])}</h4><p>{rich(x["text"])}</p></div>')
            if k < len(st) - 1:
                cells.append('<svg class="wave" viewBox="0 0 80 20" aria-hidden="true"><path d="M2 10 C 15 0, 25 20, 40 10 S 65 0, 78 10"/></svg>')
        sub = f'<p class="lead">{rich(process["subtitle"])}</p>' if process.get("subtitle") else ""
        proc_html = f'''<section class="sec soft" id="quy-trinh"><div class="wrap">
<div class="head rv"><span class="pill">{ic("layers")}Quy trình</span><h2>{rich(process["title"])}</h2>{sub}</div>
<div class="steps n{len(st)}">{"".join(cells)}</div></div></section>'''

    # --- lộ trình cấp độ (slide steps thứ hai)
    lv_html = ""
    if levels:
        n = len(levels["steps"])
        cols = "".join(f'<div class="lv rv" style="--h:{56 + k * 120 / max(1, n - 1):.0f};--t:{k / max(1, n - 1):.2f};--d:{k * 80}ms">'
                       f'<div class="lv-bar"><b>{k + 1:02d}</b></div><h4>{esc(x["title"])}</h4><p>{rich(x["text"])}</p></div>'
                       for k, x in enumerate(levels["steps"]))
        sub = f'<p class="lead">{rich(levels["subtitle"])}</p>' if levels.get("subtitle") else ""
        lv_html = f'''<section class="sec"><div class="wrap"><div class="head rv"><span class="pill">{ic("trend")}Lộ trình</span>
<h2>{rich(levels["title"])}</h2>{sub}</div><div class="ladder n{n}">{cols}</div></div></section>'''

    # --- nội dung (chương)
    cards = "".join(f'''<article class="ch rv" style="--d:{(i % 3) * 80}ms"><span class="num">{i + 1:02d}</span><h3>{esc(c["title"])}</h3>
<p>{rich(c["lead"])}</p><ul>{"".join(f"<li>{rich(x)}</li>" for x in c["summary"][:3])}</ul></article>''' for i, c in enumerate(doc["chapters"]))
    content = f'''<section class="sec soft" id="noi-dung"><div class="wrap"><div class="head rv"><span class="pill">{ic("book")}Nội dung</span>
<h2>{len(doc["chapters"])} chương, từ vấn đề đến <em>hành động</em></h2><p class="lead">{rich(doc["subtitle"])}</p></div>
<div class="grid">{cards}</div></div></section>'''

    # --- khối navy: điểm chính
    keys = "".join(f'<div class="kc rv" style="--d:{(i % 3) * 80}ms"><span>{i + 1:02d}</span><p>{rich(c["summary"][0] if c["summary"] else c["lead"])}</p></div>'
                   for i, c in enumerate(doc["chapters"]))
    cite = f"<cite>{esc(quote['by'])}</cite>" if quote and quote.get("by") else ""
    q = f'<blockquote class="rv"><span class="qm">“</span>{rich(quote["quote"])}{cite}</blockquote>' if quote else ""
    dark = f'''<section class="dark" id="diem-chinh"><div class="beam"></div><div class="glow"></div><div class="stars"></div><div class="wrap">
<div class="head rv"><span class="pill on-dark">{ic("spark")}Tổng kết</span><h2>Điểm chính <span class="grad light">cần nhớ</span></h2>
<p class="lead">Mỗi chương một ý quan trọng nhất.</p></div><div class="keys">{keys}</div>{q}</div></section>'''

    # --- việc cần làm
    todo_html = ""
    if todo:
        items = "".join(f'<li class="rv" style="--d:{i * 70}ms"><span>{i + 1}</span><p>{rich(x)}</p></li>' for i, x in enumerate(todo["bullets"]))
        sub = f'<p class="lead">{rich(todo["subtitle"])}</p>' if todo.get("subtitle") else ""
        todo_html = f'''<section class="sec"><div class="wrap two top">
<div class="rv sticky"><span class="pill">{ic("list")}Bắt đầu</span><h2>{rich(todo["title"])}</h2>{sub}
<a class="btn" href="#dang-ky">{esc(cta)}{ic("arrow")}</a></div><ol class="todo">{items}</ol></div></section>'''

    # --- form đăng ký
    gets = [(ic("book"), f"Ebook {len(doc['chapters'])} chương", plain(doc["title"])),
            (ic("layers"), "Bộ slide trình bày", "PPTX + PDF, dùng ngay cho buổi họp nội bộ")]
    for a in doc.get("appendix", []):
        name = plain(a["title"]).split("·", 1)[-1].strip()
        gets.append((ic("list"), name, "Phụ lục kèm theo ebook"))
    gets_html = "".join(f'<li><span class="gi">{i}</span><div><b>{esc(t)}</b><small>{esc(d)}</small></div></li>' for i, t, d in gets)
    needs = ["Nhận tài liệu", "Tư vấn đưa AI Agent vào doanh nghiệp", f"Tìm hiểu {course['name']}"]
    form = f'''<section class="sec soft" id="dang-ky"><div class="wrap two top form-wrap">
<div class="rv"><span class="pill">{ic("send")}Đăng ký</span><h2>Nhận <span class="grad">trọn bộ tài liệu</span></h2>
<p class="lead">Để lại thông tin, SlimAI gửi tài liệu và liên hệ khi bạn cần hỗ trợ triển khai.</p>
<ul class="gets">{gets_html}</ul></div>
<div class="form-shell rv"><form class="form" id="lead" novalidate data-action="{esc(form_action)}">
<div class="form-h"><b>Đăng ký nhận tài liệu</b><small>Các ô có dấu * là bắt buộc</small></div>
<input type="hidden" name="nguon" value="{esc(work.name)}"><input type="hidden" name="tai_lieu" value="{esc(plain(doc['title']))}">
<label>Họ và tên *<input name="ho_ten" autocomplete="name" required placeholder="Nguyễn Văn A"></label>
<div class="row"><label>Số điện thoại *<input name="so_dien_thoai" type="tel" autocomplete="tel" required inputmode="tel" pattern="[+]?[0-9 .]{{9,15}}" placeholder="09xx xxx xxx"></label>
<label>Email *<input name="email" type="email" autocomplete="email" required placeholder="ban@congty.vn"></label></div>
<div class="row"><label>Công ty<input name="cong_ty" autocomplete="organization" placeholder="Tên công ty"></label>
<label>Vai trò<select name="vai_tro"><option value="">Chọn vai trò</option><option>Chủ doanh nghiệp</option><option>Trưởng phòng / quản lý</option><option>Nhân viên văn phòng</option><option>Khác</option></select></label></div>
<label>Bạn cần gì?<select name="nhu_cau">{"".join(f"<option>{esc(x)}</option>" for x in needs)}</select></label>
<label class="chk"><input type="checkbox" name="dong_y" required><span>Tôi đồng ý để SlimAI liên hệ qua điện thoại/email về tài liệu và dịch vụ liên quan.</span></label>
<button class="btn" type="submit">{esc(cta)}{ic("arrow")}</button><p class="msg" role="status" aria-live="polite"></p>
<div class="done" hidden>{ic("check", "ic big")}<b>Đã nhận đăng ký!</b><p>SlimAI sẽ gửi tài liệu và liên hệ trong thời gian sớm nhất.</p></div>
</form></div></div></section>'''

    # --- khoá học + chân trang
    course_html = f'''<section class="sec"><div class="wrap"><div class="course rv"><div class="c-orb"></div><div class="c-txt">
<span class="pill on-dark">{ic("spark")}Bước tiếp theo</span><h2>Để AI làm việc thay bạn</h2><p>{esc(course["audience"])}</p>
<a class="btn light" href="{esc(course["url"])}" target="_blank" rel="noopener">Xem {esc(course["name"])}{ic("arrow")}</a></div>
<a class="qr" href="{esc(course["url"])}" target="_blank" rel="noopener"><img src="{qr}" alt="Mã QR khoá học AI Agent"><span>Quét mã để xem lộ trình</span></a></div></div></section>'''
    socials = "".join(
        f'<a href="{esc(s["link"])}" target="_blank" rel="noopener" aria-label="{esc(s["name"])}" style="--c:{s["color"]}">'
        f'{(BRAND_ASSETS / "logos" / (s["key"] + ".svg")).read_text().replace("<svg ", "<svg fill=currentColor ", 1)}</a>' for s in b["social"])
    eco = "".join(f'<a href="{esc(e["link"])}" target="_blank" rel="noopener"><img src="{data_uri(logo(e["key"]))}" alt="{esc(e["name"])}">'
                  f'<span>{esc(e["desc"])}</span><i>{esc(e["label"])} {ic("arrow")}</i></a>' for e in b["ecosystem"])
    footer = f'''<footer><div class="wrap"><div class="eco">{eco}</div><div class="foot">
<img src="{logo_uri}" alt="SlimAI" class="flogo"><span class="slogan">{esc(b["slogan"])}</span><div class="soc">{socials}</div>
<span class="copy">© SlimAI · <a href="{esc(b["site"])}">{esc(b["site_label"])}</a></span></div></div></footer>'''

    page = f'''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(doc["title"])} · SlimAI</title><meta name="description" content="{esc(plain(doc["subtitle"]))}">
<meta property="og:title" content="{esc(doc["title"])}"><meta property="og:description" content="{esc(plain(doc["subtitle"]))}">
<meta name="theme-color" content="#2f6bff"><link rel="icon" href="{data_uri(logo("slimai_icon"))}">
<style>{font_css()}
{CSS}</style></head><body>
<nav class="nav"><div class="prog"></div><div class="wrap"><a href="{esc(b["site"])}" class="logo"><img src="{logo_uri}" alt="SlimAI"></a>
<div class="links">{nav_html}</div><a class="btn sm" href="#dang-ky">{esc(cta)}</a></div></nav>
<main>{hero}{tools_html}{problem}{proc_html}{lv_html}{content}{chart_section(chart, stats)}{dark}{todo_html}{form}{course_html}</main>{footer}
<script>{JS}</script></body></html>'''
    out.write_text(page)
    return out


CSS = r"""
:root{--bg:#f6f8fe;--ink:#0d1838;--ink2:#2b3656;--mut:#5f6c8c;--line:#e4e9f5;--blue:#2f6bff;--blue2:#5b8cff;--cyan:#38c6f4;--navy:#08112f;
--a:#7FA6FF;--b:#1F5BFF;--r:20px;--sh:0 24px 60px -28px rgba(31,73,170,.35),0 2px 6px -2px rgba(31,73,170,.08);
--grad:linear-gradient(100deg,#2f6bff 0%,#5b8cff 45%,#38c6f4 100%);--ease:cubic-bezier(.2,.7,.2,1)}
*{box-sizing:border-box;margin:0;padding:0}html{scroll-behavior:smooth;scroll-padding-top:80px}
html,body{overflow-x:clip}
body{font-family:'Be Vietnam Pro',system-ui,sans-serif;color:var(--ink);background:var(--bg);line-height:1.65;-webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility}
img{max-width:100%;display:block}a{color:inherit}::selection{background:#cfe0ff}
.ic{width:18px;height:18px;flex:none}.ic.big{width:44px;height:44px}
.wrap{max-width:1180px;margin:0 auto;padding:0 24px;position:relative}
h1,h2,h3,h4{line-height:1.18;letter-spacing:-.025em;font-weight:600;text-wrap:balance}
h2{font-size:clamp(30px,3.8vw,46px)}h2 em,p em,.lead em{font-style:normal;color:var(--blue)}
.grad{background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.grad.light{background:linear-gradient(100deg,#9cc4ff,#6fe0ff);-webkit-background-clip:text;background-clip:text}
.pill{display:inline-flex;align-items:center;gap:7px;font-size:12.5px;font-weight:600;color:var(--blue);background:#fff;border:1px solid #d9e4ff;
padding:6px 13px 6px 10px;border-radius:99px;margin-bottom:18px;box-shadow:0 6px 16px -10px rgba(47,107,255,.6)}.pill .ic{width:14px;height:14px}
.pill.on-dark{background:rgba(255,255,255,.08);border-color:rgba(255,255,255,.18);color:#cfe0ff;box-shadow:none}
.lead{color:var(--mut);font-size:17.5px;max-width:640px;text-wrap:pretty}
.btn{position:relative;overflow:hidden;display:inline-flex;align-items:center;gap:10px;background:linear-gradient(180deg,#4a83ff,#2a62f5);color:#fff;
text-decoration:none;font:inherit;font-weight:600;font-size:15.5px;padding:14px 22px;border-radius:13px;border:0;cursor:pointer;
box-shadow:0 12px 26px -12px rgba(47,107,255,.9),inset 0 1px 0 rgba(255,255,255,.28);transition:transform .25s var(--ease),box-shadow .25s}
.btn:after{content:"";position:absolute;inset:0;background:linear-gradient(110deg,transparent 30%,rgba(255,255,255,.35) 50%,transparent 70%);transform:translateX(-120%);transition:transform .7s}
.btn:hover{transform:translateY(-2px);box-shadow:0 18px 32px -14px rgba(47,107,255,.95)}.btn:hover:after{transform:translateX(120%)}
.btn .ic{transition:transform .25s}.btn:hover .ic{transform:translateX(3px)}
.btn.ghost{background:#fff;color:var(--ink);box-shadow:0 0 0 1px var(--line),0 8px 20px -14px rgba(13,24,56,.4)}
.btn.sm{padding:10px 16px;font-size:14px;border-radius:11px}.btn.light{background:#fff;color:var(--navy);box-shadow:0 12px 26px -14px rgba(0,0,0,.5)}
a:focus-visible,button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible,.bar:focus-visible{outline:3px solid rgba(47,107,255,.45);outline-offset:3px}
/* nav */
.nav{position:sticky;top:0;z-index:30;background:rgba(255,255,255,.72);backdrop-filter:saturate(1.6) blur(16px);-webkit-backdrop-filter:saturate(1.6) blur(16px);border-bottom:1px solid transparent;transition:box-shadow .3s,border-color .3s}
.nav.scrolled{border-color:var(--line);box-shadow:0 10px 30px -22px rgba(13,24,56,.5)}
.prog{position:absolute;left:0;top:0;height:2px;width:0;background:var(--grad)}
.nav .wrap{display:flex;align-items:center;gap:24px;height:68px}.logo img{height:30px;width:auto}
.links{display:flex;gap:4px;margin:0 auto;font-size:14.5px}.links a{text-decoration:none;color:var(--mut);padding:7px 13px;border-radius:9px;transition:background .2s,color .2s}
.links a:hover,.links a.on{color:var(--ink);background:#eef3ff}
/* hero */
.hero{position:relative;overflow:hidden;padding:84px 0 0;text-align:center;background:linear-gradient(180deg,#ffffff 0%,#f6f9ff 55%,#e8f0ff 100%)}
.orb{position:absolute;border-radius:50%;filter:blur(70px);opacity:.75;pointer-events:none}
.o1{width:520px;height:520px;left:-140px;bottom:-200px;background:radial-gradient(circle,#7aa5ff,transparent 65%)}
.o2{width:560px;height:560px;right:-160px;bottom:-160px;background:radial-gradient(circle,#8fdcff,transparent 65%)}
.rings{position:absolute;left:50%;bottom:-760px;width:1500px;height:1500px;transform:translateX(-50%);border-radius:50%;
box-shadow:0 0 0 1px rgba(47,107,255,.10),0 0 0 120px rgba(255,255,255,0),0 0 0 121px rgba(47,107,255,.07),0 0 0 260px rgba(255,255,255,0),0 0 0 261px rgba(47,107,255,.05);pointer-events:none}
.deco{position:absolute;inset:0;width:100%;height:100%;fill:none;stroke:rgba(47,107,255,.16);stroke-width:1;pointer-events:none}.deco circle{fill:#9ab9ff;stroke:none}
.badge{display:inline-flex;align-items:center;gap:8px;font-size:12.5px;font-weight:500;color:var(--blue);background:#fff;border:1px solid #d9e4ff;border-radius:99px;
padding:6px 15px;box-shadow:0 8px 20px -12px rgba(47,107,255,.7)}.badge i{width:7px;height:7px;border-radius:50%;background:var(--blue);box-shadow:0 0 0 4px #e3ecff}
.hero h1{font-size:clamp(38px,5.6vw,68px);font-weight:600;letter-spacing:-.035em;max-width:920px;margin:22px auto 18px;line-height:1.08}
.hero .sub{color:var(--mut);font-size:clamp(16px,1.6vw,19px);max-width:640px;margin:0 auto;text-wrap:balance}
.cta{display:flex;gap:12px;justify-content:center;margin:32px 0 54px;flex-wrap:wrap}
.stage-wg{position:relative;height:430px;max-width:1100px;margin:0 auto}
.dash{position:absolute;left:50%;bottom:0;transform:translateX(-50%);width:min(560px,94%);height:356px;background:rgba(255,255,255,.9);
-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,.9);border-bottom:0;border-radius:24px 24px 0 0;
box-shadow:var(--sh),0 0 0 8px rgba(255,255,255,.35);padding:22px 24px 0;text-align:left}
.dash-h{display:flex;justify-content:space-between;align-items:center;gap:10px;font-size:15px}.dash-h b{font-weight:600}
.lg{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:var(--mut);white-space:nowrap}.lg i{width:10px;height:10px;border-radius:3px;display:inline-block;margin-left:10px}
.lg i.a{background:var(--a)}.lg i.b{background:var(--b)}
.dash-plot{position:relative;display:flex;align-items:flex-end;justify-content:space-around;height:270px;margin-top:10px;padding:56px 0 34px;
background:repeating-linear-gradient(180deg,transparent 0 56px,#eef2fa 56px 57px)}
.dash-plot .g{position:relative;display:flex;gap:5px;align-items:flex-end;height:100%}
.dash-plot .g span{width:24px;height:var(--h);border-radius:7px 7px 2px 2px;transform-origin:bottom;animation:grow 1.1s var(--ease) both}
.dash-plot .g .b{animation-delay:.15s}.dash-plot .a{background:linear-gradient(180deg,#a9c3ff,#7FA6FF)}.dash-plot .b{background:linear-gradient(180deg,#4b7dff,#1F5BFF)}
.dash-plot p{position:absolute;bottom:-30px;left:50%;transform:translateX(-50%);font-size:11px;color:var(--mut);white-space:nowrap}
.flag{position:absolute;z-index:2;bottom:calc(var(--top,100%) + 10px);left:50%;transform:translateX(-50%);background:var(--ink);color:#fff;font-size:12.5px;font-weight:600;
padding:6px 10px;border-radius:9px;white-space:nowrap;box-shadow:0 10px 20px -10px rgba(13,24,56,.7);animation:pop .6s .9s var(--ease) both}
.flag i{display:block;font-style:normal;font-weight:400;font-size:10.5px;color:#b9c6ea}
.flag:after{content:"";position:absolute;left:50%;top:100%;transform:translateX(-50%);border:6px solid transparent;border-top-color:var(--ink)}
.dash-list{list-style:none;margin-top:16px}.dash-list li{display:flex;gap:12px;padding:10px 0;border-bottom:1px solid var(--line);font-size:14px}.dash-list span{color:var(--blue);font-weight:600}
.wg{position:absolute;background:rgba(255,255,255,.88);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);border:1px solid rgba(255,255,255,.95);
border-radius:18px;box-shadow:var(--sh);padding:14px 16px;text-align:left;font-size:13px;animation:float 8s ease-in-out infinite}
.wg small{display:block;color:var(--mut);font-size:12px;line-height:1.4}.wg b{display:block;font-weight:600;font-size:17px;line-height:1.2}
.wg b.big{font-size:30px;letter-spacing:-.03em;margin:6px 0 2px}.wg em{font-style:normal;font-size:11.5px;color:var(--blue)}
.wg-ic{width:40px;height:40px;border-radius:12px;display:grid;place-items:center;color:#fff;background:var(--grad);box-shadow:0 8px 18px -8px rgba(47,107,255,.9);flex:none}
.wg-ic.sm{width:30px;height:30px;border-radius:9px}.wg-ic.sm .ic{width:16px;height:16px}
.wg-top{display:flex;justify-content:space-between;align-items:center;gap:10px}
.chip{font-size:10.5px;font-weight:600;color:#9a5b00;background:#fff4dd;border:1px solid #ffe2a8;padding:2px 8px;border-radius:99px;white-space:nowrap}
.w-tl{left:4%;top:34px;display:flex;gap:12px;align-items:center}
.w-tr{right:4%;top:16px;width:236px;animation-delay:-2s}.w-br{right:11%;top:196px;width:220px;animation-delay:-5s}
.w-ml{left:8%;top:150px;width:250px;animation-delay:-3.5s}.w-ml .cap{font-weight:600;color:var(--ink2);margin-bottom:6px}
.w-ml ul{list-style:none}.w-ml li{display:flex;gap:9px;align-items:center;padding:4px 0;font-size:13px}
.w-ml li span{color:#fff;background:var(--blue);width:18px;height:18px;border-radius:50%;display:grid;place-items:center;flex:none}.w-ml li .ic{width:11px;height:11px;stroke-width:3}
@keyframes float{50%{transform:translateY(-10px)}}@keyframes grow{from{transform:scaleY(0)}}@keyframes pop{from{opacity:0;transform:translate(-50%,8px) scale(.9)}}
/* tools */
.tools{background:#fff;border-block:1px solid var(--line);padding:26px 0 24px;overflow:hidden}
.tools p{text-align:center;color:var(--mut);font-size:13px;margin-bottom:14px}
.marquee{-webkit-mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent);mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent)}
.track{display:flex;gap:56px;width:max-content;animation:slide 40s linear infinite}.marquee:hover .track{animation-play-state:paused}
.track span{font-weight:700;font-size:21px;color:#2c3757;opacity:.55;letter-spacing:-.02em;white-space:nowrap;transition:opacity .2s}.track span:hover{opacity:1}
@keyframes slide{to{transform:translateX(-50%)}}
/* sections */
.sec{padding:112px 0;position:relative}.sec.soft{background:linear-gradient(180deg,#eef4ff 0%,#f7f9ff 100%)}
.head{text-align:center;max-width:780px;margin:0 auto 60px}.head .lead{margin:14px auto 0}
.note{display:inline-flex;gap:8px;align-items:center;margin-top:16px;color:#8a5600;background:#fff6e3;border:1px solid #ffe3ad;font-size:14px;padding:7px 14px;border-radius:99px}
.note .ic{width:15px;height:15px}.note em{color:inherit;font-weight:600}
.two{display:grid;grid-template-columns:1.02fr 1fr;gap:64px;align-items:center}.two.top{align-items:start}
.two h3{margin:28px 0 12px;font-size:15px;text-transform:uppercase;letter-spacing:.08em;color:var(--mut)}
.for{list-style:none;display:grid;gap:10px}.for li{display:flex;gap:12px;align-items:flex-start;background:#fff;border:1px solid var(--line);border-radius:14px;padding:12px 16px;font-size:15px}
.for .ic{color:#fff;background:var(--blue);border-radius:50%;padding:3px;width:20px;height:20px;stroke-width:3;margin-top:2px}
.cmp{display:grid;grid-template-columns:1fr auto 1fr;gap:14px;align-items:center}
.cmp-c{position:relative;background:#fff;border-radius:var(--r);padding:26px 22px 22px;box-shadow:var(--sh);border:1px solid var(--line)}
.cmp-c h4{font-size:20px;margin-bottom:12px}.cmp-c ul{list-style:none}.cmp-c li{display:flex;gap:10px;padding:9px 0;font-size:14.5px;border-top:1px dashed var(--line);color:var(--ink2)}
.cmp-c li .ic{width:16px;height:16px;margin-top:3px;color:#c0c8da}.tag{position:absolute;top:-11px;left:20px;font-size:11px;font-weight:600;background:#eef2fa;color:var(--mut);padding:3px 10px;border-radius:99px}
.cmp-c.on{background:linear-gradient(155deg,#3f7bff 0%,#2457e6 60%,#1d47c8 100%);color:#fff;border:0;transform:scale(1.04);
box-shadow:0 30px 60px -24px rgba(36,87,230,.8),0 0 0 6px rgba(47,107,255,.12)}
.cmp-c.on li{border-color:rgba(255,255,255,.22);color:#fff}.cmp-c.on li .ic{color:#9fe6ff}.cmp-c.on .tag{background:#fff;color:var(--blue)}
.cmp-arrow{width:42px;height:42px;border-radius:50%;background:#fff;box-shadow:var(--sh);display:grid;place-items:center;color:var(--blue);z-index:1}
/* steps */
.steps{display:flex;align-items:flex-start;justify-content:center;gap:6px}
.step{flex:1;max-width:240px;text-align:center}.step h4{font-size:17.5px;margin:6px 0 8px}.step p{color:var(--mut);font-size:14.5px;line-height:1.55}
.step .num{display:inline-block;font-size:11.5px;font-weight:700;color:var(--blue);letter-spacing:.12em;text-transform:uppercase}
.wave{width:64px;flex:none;margin-top:76px;fill:none;stroke:#38b6c8;stroke-width:2;stroke-dasharray:4 6;animation:dash 2.5s linear infinite}
@keyframes dash{to{stroke-dashoffset:-20}}
.ui{position:relative;width:180px;height:150px;margin:0 auto 22px;transition:transform .5s var(--ease)}.step:hover .ui{transform:translateY(-6px) rotate(-1.5deg)}
.ui-glow{position:absolute;left:10%;right:10%;bottom:0;height:60%;border-radius:50%;background:radial-gradient(closest-side,rgba(91,140,255,.45),transparent);filter:blur(12px)}
.ui-card{position:absolute;inset:26px 14px 18px;background:#fff;border-radius:16px;box-shadow:0 18px 34px -18px rgba(31,73,170,.55),0 0 0 1px #edf1fa;padding:16px 14px;display:flex;flex-direction:column;gap:8px;align-items:flex-start}
.ui-card i{height:7px;border-radius:4px;background:#e2e8f5;display:block}.ui-av{width:28px;height:28px;border-radius:9px;background:linear-gradient(135deg,#dbe6ff,#c2d5ff)}
.ui-chip{position:absolute;height:16px;border-radius:6px;background:var(--grad)}
.ui-btn{position:absolute;width:34px;height:34px;border-radius:10px;background:var(--grad);color:#fff;display:grid;place-items:center;box-shadow:0 10px 18px -8px rgba(47,107,255,.9)}
.ui-num{width:46px;height:12px;border-radius:4px;background:var(--ink);display:block}.ui-bar{margin-top:auto;width:100%;height:16px;border-radius:6px;background:var(--grad)}
.ui-sq{position:absolute;width:26px;height:26px;border-radius:8px;background:#fff;box-shadow:0 8px 16px -8px rgba(13,24,56,.45);border:6px solid #8bc34a}
.ui-sq.b{border-color:#ff6b6b}.ui-sq.c{border-color:#2f6bff}
.ui-card.cols{flex-direction:row;align-items:flex-end;justify-content:space-around}.ui-card.cols span{width:14px;background:linear-gradient(180deg,#7aa5ff,#2f6bff);border-radius:4px 4px 1px 1px}
.ui-tag{position:absolute;background:var(--ink);color:#fff;border-radius:8px;padding:5px;display:grid;place-items:center}.ui-tag .ic{width:14px;height:14px}
.ui-spark{position:absolute;left:4px;top:8px;width:58px;height:32px;border-radius:9px;background:#fff;box-shadow:0 8px 16px -8px rgba(13,24,56,.45)}
/* ladder */
.ladder{display:grid;gap:18px;align-items:end;grid-template-columns:repeat(var(--n,5),1fr)}.ladder.n3{--n:3}.ladder.n4{--n:4}.ladder.n5{--n:5}
.lv h4{font-size:16.5px;margin:14px 0 4px}.lv p{font-size:14px;color:var(--mut)}
.lv-bar{height:calc(var(--h) * 1px);border-radius:16px 16px 6px 6px;position:relative;box-shadow:var(--sh);transform-origin:bottom;
background:linear-gradient(180deg,color-mix(in oklab,#2f6bff calc(var(--t) * 100%),#cfe0ff),color-mix(in oklab,#1d47c8 calc(var(--t) * 100%),#a9c3ff))}
.lv.rv .lv-bar{transform:scaleY(.2);transition:transform .9s var(--ease) var(--d,0ms)}.lv.rv.in .lv-bar{transform:none}
.lv-bar b{position:absolute;left:16px;top:12px;color:#fff;font-size:21px;text-shadow:0 1px 6px rgba(13,24,56,.18)}
/* chapters */
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
.ch{position:relative;background:#fff;border:1px solid var(--line);border-radius:var(--r);padding:28px;box-shadow:0 14px 34px -26px rgba(31,73,170,.45);
transition:transform .35s var(--ease),box-shadow .35s,border-color .35s}
.ch:before{content:"";position:absolute;inset:-1px;border-radius:inherit;padding:1px;background:var(--grad);opacity:0;transition:opacity .35s;
-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude}
.ch:hover{transform:translateY(-6px);box-shadow:var(--sh)}.ch:hover:before{opacity:1}
.ch .num{display:inline-grid;place-items:center;width:40px;height:40px;border-radius:12px;background:var(--grad);color:#fff;font-weight:700;font-size:14px;box-shadow:0 10px 18px -10px rgba(47,107,255,.9)}
.ch h3{font-size:19.5px;margin:16px 0 8px}.ch p{color:var(--mut);font-size:14.5px}
.ch ul{list-style:none;margin-top:16px;border-top:1px solid var(--line);padding-top:12px}
.ch li{font-size:14px;padding:5px 0 5px 20px;position:relative;color:var(--ink2)}.ch li:before{content:"";position:absolute;left:3px;top:13px;width:7px;height:7px;border-radius:50%;background:var(--grad)}
/* chart */
.chart-wrap{display:grid;grid-template-columns:1fr 300px;gap:22px;align-items:stretch;max-width:1060px;margin:0 auto}
.chart{background:#fff;border:1px solid var(--line);border-radius:24px;padding:28px 28px 22px;box-shadow:var(--sh);position:relative}
.chart-top{display:flex;justify-content:space-between;color:var(--mut);font-size:13px}
.plot{display:flex;justify-content:space-around;align-items:flex-end;gap:12px;height:300px;margin-top:26px;border-bottom:1px solid var(--line);
background:repeating-linear-gradient(0deg,transparent 0 74px,#eef2f9 74px 75px)}
.cg{flex:1;display:flex;flex-direction:column;align-items:center;height:100%}.cb{flex:1;display:flex;gap:3px;align-items:flex-end;width:100%;justify-content:center}
.cg p{font-size:13px;margin-top:10px;text-align:center;min-height:40px;color:var(--ink2)}
.bar{width:min(44px,32%);height:var(--h);border-radius:6px 6px 2px 2px;position:relative;cursor:pointer;transform-origin:bottom;transform:scaleY(0);transition:transform 1s var(--ease) var(--d,0ms),filter .2s}
.chart.in .bar{transform:none}.bar.a{background:linear-gradient(180deg,#a9c3ff,#7FA6FF)}.bar.b{background:linear-gradient(180deg,#4b7dff,#1F5BFF)}
.bar:hover,.bar:focus{filter:brightness(1.08)}
.bar em{position:absolute;bottom:100%;left:50%;transform:translateX(-50%);font-style:normal;font-weight:600;font-size:13px;color:var(--ink);padding-bottom:5px}
.tip{position:absolute;pointer-events:none;background:var(--ink);color:#fff;font-size:12.5px;padding:8px 11px;border-radius:9px;opacity:0;transition:opacity .15s;white-space:nowrap;z-index:3;box-shadow:0 10px 20px -10px rgba(13,24,56,.7)}
details{margin-top:18px;font-size:14px}summary{cursor:pointer;color:var(--blue);font-weight:600}
table{width:100%;border-collapse:collapse;margin-top:12px}th,td{text-align:left;padding:10px;border-bottom:1px solid var(--line)}th{color:var(--mut);font-weight:600;font-size:13px}
.side{display:grid;gap:16px;align-content:start}.hl{background:#fff;border:1px solid var(--line);border-radius:22px;padding:24px;box-shadow:var(--sh)}
.hl small{color:var(--mut);font-size:13px}.hl b{display:block;font-size:44px;letter-spacing:-.04em;line-height:1.1;margin:8px 0 6px;background:var(--grad);-webkit-background-clip:text;background-clip:text;color:transparent}
.hl b span{font-size:18px;letter-spacing:0}.hl p{font-size:14px;color:var(--ink2)}
.hl.hl-dk{background:linear-gradient(160deg,#0f1d4d,#08112f);border:0;color:#fff}.hl.hl-dk small{color:#9fb0dd}.hl.hl-dk p{color:#ffd58a;font-size:13px}
.hl.hl-dk b{background:linear-gradient(100deg,#9cc4ff,#6fe0ff);-webkit-background-clip:text;background-clip:text}
/* dark */
.dark{position:relative;overflow:hidden;background:radial-gradient(120% 80% at 50% 0%,#12235e 0%,var(--navy) 60%);color:#fff;padding:120px 0;margin:0 16px;border-radius:32px;isolation:isolate}
.glow{position:absolute;inset:-20% -10% auto 35%;height:110%;background:radial-gradient(40% 40% at 60% 40%,rgba(56,140,255,.55),transparent 70%),
radial-gradient(28% 32% at 85% 20%,rgba(64,220,255,.45),transparent 70%);filter:blur(40px);z-index:-1}
.beam{position:absolute;top:-40%;left:55%;width:340px;height:180%;background:linear-gradient(90deg,transparent,rgba(120,190,255,.28),transparent);
transform:rotate(28deg);filter:blur(18px);z-index:-1;animation:beam 9s ease-in-out infinite alternate}
@keyframes beam{to{transform:translateX(-220px) rotate(28deg)}}
.stars{position:absolute;inset:0;z-index:-1;opacity:.5;background-image:radial-gradient(1px 1px at 20% 30%,#fff,transparent),radial-gradient(1px 1px at 70% 60%,#fff,transparent),
radial-gradient(1px 1px at 40% 80%,#fff,transparent),radial-gradient(1px 1px at 85% 25%,#fff,transparent),radial-gradient(1px 1px at 10% 70%,#fff,transparent)}
.dark .head h2{color:#fff}.dark .lead{color:#b9c6ea}
.keys{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.kc{position:relative;background:linear-gradient(180deg,rgba(255,255,255,.08),rgba(255,255,255,.03));border:1px solid rgba(255,255,255,.12);
-webkit-backdrop-filter:blur(10px);backdrop-filter:blur(10px);border-radius:18px;padding:24px;transition:border-color .3s,transform .3s var(--ease)}
.kc:hover{border-color:rgba(140,195,255,.5);transform:translateY(-4px)}
.kc span{font-size:13px;font-weight:700;color:#8fc2ff;letter-spacing:.06em}.kc p{margin-top:10px;color:#e6ecff;font-size:15.5px}.kc p b{color:#fff}
blockquote{position:relative;margin:64px auto 0;max-width:820px;text-align:center;font-size:clamp(22px,2.6vw,32px);font-weight:500;line-height:1.38;letter-spacing:-.02em;text-wrap:balance}
.qm{display:block;font-size:72px;line-height:.6;color:#6fb6ff;height:34px}
cite{display:block;margin-top:16px;font-size:14px;color:#9fb0dd;font-style:normal;letter-spacing:0}
/* todo */
.sticky{position:sticky;top:110px}.sticky .btn{margin-top:26px}
.todo{list-style:none;display:grid;gap:12px;counter-reset:t;position:relative}
.todo:before{content:"";position:absolute;left:33px;top:28px;bottom:28px;width:2px;background:linear-gradient(180deg,#bcd2ff,#e4ecff)}
.todo li{position:relative;display:flex;gap:16px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:16px;padding:16px 20px;
box-shadow:0 12px 26px -22px rgba(31,73,170,.5);transition:transform .3s var(--ease)}.todo li:hover{transform:translateX(6px)}
.todo span{width:30px;height:30px;border-radius:10px;background:var(--grad);color:#fff;display:grid;place-items:center;font-weight:700;flex:none;font-size:14px}
.todo p{margin:0;color:var(--ink)}
/* form */
.gets{list-style:none;display:grid;gap:12px;margin-top:28px}.gets li{display:flex;gap:14px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:16px;padding:14px 16px}
.gi{width:40px;height:40px;border-radius:12px;background:#eaf1ff;color:var(--blue);display:grid;place-items:center;flex:none}
.gets b{display:block;font-weight:600;font-size:15px}.gets small{color:var(--mut);font-size:13px}
.form-shell{position:relative;border-radius:26px;padding:1.5px;background:linear-gradient(140deg,#7aa5ff,#e4ecff 40%,#e4ecff 60%,#6fe0ff);box-shadow:0 40px 80px -40px rgba(31,73,170,.6)}
.form-shell:before{content:"";position:absolute;inset:-30px;z-index:-1;background:radial-gradient(50% 50% at 50% 50%,rgba(91,140,255,.35),transparent 70%);filter:blur(20px)}
.form{background:#fff;border-radius:25px;padding:32px;display:grid;gap:15px;position:relative}
.form-h b{display:block;font-size:20px;letter-spacing:-.02em}.form-h small{color:var(--mut);font-size:13px}
.form .row{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.form label{display:grid;gap:7px;font-size:13.5px;font-weight:600;color:var(--ink2)}
.form input,.form select{font:inherit;font-weight:400;font-size:15px;padding:13px 14px;border:1px solid #d9e0ee;border-radius:12px;background:#f9fbff;color:var(--ink);width:100%;transition:border-color .2s,box-shadow .2s,background .2s;appearance:none;-webkit-appearance:none}
.form select{background-image:linear-gradient(45deg,transparent 50%,#7a86a6 50%),linear-gradient(135deg,#7a86a6 50%,transparent 50%);background-position:calc(100% - 20px) 55%,calc(100% - 15px) 55%;background-size:5px 5px;background-repeat:no-repeat;padding-right:36px}
.form input:hover,.form select:hover{border-color:#c4d0ea}
.form input:focus,.form select:focus{outline:none;background:#fff;border-color:var(--blue);box-shadow:0 0 0 4px rgba(47,107,255,.14)}
.form input[aria-invalid=true]{border-color:#d93b3b;box-shadow:0 0 0 4px rgba(217,59,59,.1)}
.form .chk{display:flex;gap:10px;align-items:flex-start;font-weight:400;color:var(--mut);font-size:13px;line-height:1.5;cursor:pointer}
.form .chk input{appearance:auto;-webkit-appearance:checkbox;width:18px;height:18px;margin-top:1px;flex:none;accent-color:var(--blue);padding:0}
.form button{margin-top:4px;justify-content:center;width:100%;font-size:16px;padding:16px}.form button[disabled]{opacity:.7;cursor:wait}
.msg{font-size:14px;min-height:1.2em}.msg.err{color:#d93b3b}.msg.warn{color:#8a5600;background:#fff6e3;border:1px solid #ffe3ad;border-radius:10px;padding:10px 12px}
.done{position:absolute;inset:0;background:#fff;border-radius:25px;display:grid;place-content:center;justify-items:center;text-align:center;gap:8px;padding:30px;animation:pop2 .5s var(--ease)}
.done .ic{color:#fff;background:linear-gradient(135deg,#22c55e,#16a34a);border-radius:50%;padding:10px;stroke-width:3}.done b{font-size:22px}.done p{color:var(--mut);max-width:300px}
@keyframes pop2{from{opacity:0;transform:scale(.96)}}
.done[hidden],[hidden]{display:none!important}
/* course + footer */
.course{position:relative;overflow:hidden;display:flex;justify-content:space-between;gap:36px;align-items:center;background:linear-gradient(120deg,#1d47c8 0%,#2f6bff 50%,#38b8ff 100%);
color:#fff;border-radius:30px;padding:52px 56px;box-shadow:0 40px 80px -40px rgba(36,87,230,.9);isolation:isolate}
.c-orb{position:absolute;right:-120px;top:-160px;width:420px;height:420px;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.35),transparent 65%);z-index:-1}
.course:after{content:"";position:absolute;inset:0;z-index:-1;background-image:linear-gradient(rgba(255,255,255,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.07) 1px,transparent 1px);background-size:36px 36px;-webkit-mask-image:linear-gradient(90deg,transparent,#000);mask-image:linear-gradient(90deg,transparent,#000)}
.course h2{color:#fff}.course p{color:#e3ecff;margin:12px 0 26px;max-width:560px}
.qr{display:grid;gap:10px;justify-items:center;text-decoration:none;color:#fff;font-size:13px;flex:none}
.qr img{width:164px;background:#fff;border-radius:20px;padding:12px;box-shadow:0 20px 40px -20px rgba(0,0,0,.5);transition:transform .3s var(--ease)}.qr:hover img{transform:rotate(-2deg) scale(1.03)}
footer{background:#fff;border-top:1px solid var(--line);margin-top:40px;padding:52px 0 30px}
.eco{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}
.eco a{display:grid;gap:10px;text-decoration:none;border:1px solid var(--line);border-radius:18px;padding:20px;transition:border-color .25s,box-shadow .25s,transform .25s var(--ease)}
.eco a:hover{border-color:#cfdcff;box-shadow:var(--sh);transform:translateY(-3px)}
.eco img{height:30px;width:auto}.eco span{font-size:13.5px;color:var(--mut)}.eco i{display:flex;align-items:center;gap:6px;font-style:normal;font-size:13px;font-weight:600;color:var(--blue)}.eco i .ic{width:14px;height:14px}
.foot{display:flex;flex-wrap:wrap;gap:18px;align-items:center;justify-content:space-between;margin-top:32px;padding-top:24px;border-top:1px solid var(--line);font-size:13px;color:var(--mut)}
.flogo{height:26px;width:auto}.slogan{font-weight:600}
.soc{display:flex;gap:10px}.soc a{width:36px;height:36px;border-radius:11px;display:grid;place-items:center;color:var(--c);background:#f2f5fb;transition:transform .2s,background .2s}
.soc a:hover{transform:translateY(-2px);background:#e8eefb}.soc svg{width:18px;height:18px}
/* reveal */
.rv{opacity:0;transform:translateY(22px);transition:opacity .8s var(--ease) var(--d,0ms),transform .8s var(--ease) var(--d,0ms)}.rv.in{opacity:1;transform:none}
.hero .rv{transition-duration:1s}.hero h1.rv{--d:80ms}.hero .sub.rv{--d:160ms}.hero .cta.rv{--d:240ms}
@media (prefers-reduced-motion:reduce){*{animation:none!important}.rv,.bar,.lv-bar{opacity:1!important;transform:none!important;transition:none!important}html{scroll-behavior:auto}}
@media (max-width:1080px){.w-br{right:3%;top:250px}.w-ml{left:2%}.w-tl{left:1%}.w-tr{right:1%}}
@media (max-width:980px){.links{display:none}.nav .btn.sm{margin-left:auto}.wg{display:none}.stage-wg{height:330px}.dash{height:300px}.dash-plot{height:210px}
.two,.cmp,.chart-wrap{grid-template-columns:1fr}.cmp-c.on{transform:none}.cmp-arrow{justify-self:center;transform:rotate(90deg)}
.grid,.keys,.eco{grid-template-columns:1fr 1fr}.sticky{position:static}
.steps{flex-direction:column;align-items:center}.wave{transform:rotate(90deg);margin:-6px 0}.ladder{grid-template-columns:1fr 1fr}.lv-bar{height:72px}
.side{grid-template-columns:1fr 1fr}.course{flex-direction:column;text-align:center;padding:44px 28px}.course p{margin-inline:auto}.deco{display:none}}
@media (max-width:620px){.wrap{padding:0 16px}.sec{padding:72px 0}.grid,.keys,.eco,.form .row,.ladder,.side{grid-template-columns:1fr}
.head{margin-bottom:40px}.dark{margin:0;border-radius:0;padding:80px 0}.hero{padding-top:56px}.cta{margin:26px 0 40px}.cta .btn{width:100%;justify-content:center}
.stage-wg{height:290px}.dash{height:270px;padding:18px 16px 0}.dash-h{flex-direction:column;align-items:flex-start}.dash-plot{height:180px}.dash-plot .g span{width:16px}.dash-plot p{display:none}
.flag{font-size:11px}.form{padding:24px 20px}.plot{height:240px}.cg p{font-size:11.5px}.bar em{font-size:11.5px}.chart{padding:22px 16px}
.todo:before{left:29px}.track span{font-size:18px}.course{border-radius:24px}.hl b{font-size:38px}}
"""

JS = r"""
const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target)}}),{threshold:.14,rootMargin:'0px 0px -40px 0px'});
document.querySelectorAll('.rv').forEach(el=>io.observe(el));
// thanh menu: bóng khi cuộn, thanh tiến độ đọc, mục đang xem
const nav=document.querySelector('.nav'),prog=document.querySelector('.prog'),links=[...document.querySelectorAll('.links a')];
const secs=links.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
const onScroll=()=>{const y=scrollY,h=document.documentElement.scrollHeight-innerHeight;nav.classList.toggle('scrolled',y>8);prog.style.width=(h>0?y/h*100:0)+'%';
  let cur=null;secs.forEach(s=>{if(s.getBoundingClientRect().top<innerHeight*.35)cur=s.id});links.forEach(a=>a.classList.toggle('on',a.getAttribute('href')==='#'+cur))};
addEventListener('scroll',onScroll,{passive:true});onScroll();
// tooltip cho cột biểu đồ (rê chuột hoặc Tab)
document.querySelectorAll('.chart').forEach(c=>{const tip=c.querySelector('.tip');
  const show=b=>{tip.textContent=b.dataset.tip;tip.style.opacity=1;const r=b.getBoundingClientRect(),cr=c.getBoundingClientRect();
    tip.style.left=Math.min(cr.width-tip.offsetWidth-8,Math.max(8,r.left-cr.left+r.width/2-tip.offsetWidth/2))+'px';
    tip.style.top=(r.top-cr.top-tip.offsetHeight-12)+'px'};
  c.querySelectorAll('.bar').forEach(b=>{b.addEventListener('mouseenter',()=>show(b));b.addEventListener('focus',()=>show(b));
    b.addEventListener('mouseleave',()=>tip.style.opacity=0);b.addEventListener('blur',()=>tip.style.opacity=0)})});
// form đăng ký
const f=document.getElementById('lead');
if(f){const msg=f.querySelector('.msg'),btn=f.querySelector('button'),label=btn.innerHTML,done=f.querySelector('.done');
 const say=(t,c)=>{msg.textContent=t;msg.className='msg '+c};
 f.querySelectorAll('input,select').forEach(i=>i.addEventListener('input',()=>{if(i.getAttribute('aria-invalid')==='true'&&i.checkValidity())i.setAttribute('aria-invalid','false')}));
 f.addEventListener('submit',async ev=>{ev.preventDefault();let bad=null;
  f.querySelectorAll('input,select').forEach(i=>{const ok=i.checkValidity();i.setAttribute('aria-invalid',!ok);if(!ok&&!bad)bad=i});
  if(bad){const name=bad.closest('label')?.firstChild?.textContent?.replace('*','').trim()||'thông tin';
    say(bad.name==='dong_y'?'Vui lòng đồng ý để SlimAI liên hệ.':'Vui lòng kiểm tra lại ô "'+name+'".','err');bad.focus();return}
  const url=f.dataset.action;
  if(!url){say('Bản xem trước: form chưa nối nơi nhận dữ liệu, thông tin chưa được gửi đi.','warn');return}
  btn.disabled=true;btn.textContent='Đang gửi…';say('','');
  const data=new FormData(f);data.append('trang',location.href);data.append('thoi_gian',new Date().toISOString());
  try{try{const r=await fetch(url,{method:'POST',body:data});if(!r.ok)throw new Error('HTTP '+r.status)}
      catch(e){if(String(e.message).startsWith('HTTP'))throw e;await fetch(url,{method:'POST',body:data,mode:'no-cors'})}
      done.hidden=false;f.reset()}
  catch(e){say('Chưa gửi được ('+e.message+'). Vui lòng thử lại hoặc liên hệ SlimAI qua Zalo.','err')}
  finally{btn.disabled=false;btn.innerHTML=label}})}
"""
