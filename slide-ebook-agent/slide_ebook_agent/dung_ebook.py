"""Tác tử dựng ebook: bản thảo -> dự án ebook của skill tai-lieu-slimai (ebook.json + content/*.html + img/) -> build.py -> PDF A4."""
from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

from PIL import Image, ImageDraw

from thuong_hieu import EBOOK_TEMPLATE, brand

BOX_TITLE = {"ai": "◉ Áp dụng cho AI", "tip": "💡 Mẹo", "warn": "⚠ Lưu ý", "sum": "✦ Tóm tắt"}


def rich(t: str | None) -> str:
    t = html.escape(t or "")
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"\*([^*\s][^*]*?)\*", r"<i>\1</i>", t)


def block_html(b: dict) -> str:
    t = b["type"]
    if t == "p":
        return f"<p>{rich(b['text'])}</p>"
    if t == "bullets":
        return "<ul>" + "".join(f"<li>{rich(x)}</li>" for x in b["items"] or []) + "</ul>"
    if t == "box":
        tone = b["tone"] or "tip"
        title = b["title"] or BOX_TITLE[tone]
        if not re.match(r"^[^\w\s]", title):
            title = BOX_TITLE[tone].split(" ")[0] + " " + title
        body = f"<p>{rich(b['text'])}</p>" if b["text"] else ""
        if b["items"]:
            body += "<ul>" + "".join(f"<li>{rich(x)}</li>" for x in b["items"]) + "</ul>"
        return f'<div class="box {tone}"><div class="bt">{html.escape(title)}</div>{body}</div>'
    if t == "prompt":
        txt = html.escape(b["text"] or "")
        txt = re.sub(r"\[([^\]]+)\]", r"<em>[\1]</em>", txt)
        return f'<div class="prompt"><span class="lb">{html.escape(b["title"] or "Prompt mẫu")}</span>{txt}</div>'
    if t == "table" and b["header"]:
        head = "".join(f"<th>{rich(h)}</th>" for h in b["header"])
        rows = "".join("<tr>" + "".join(f"<td>{rich(c)}</td>" for c in r) + "</tr>" for r in b["rows"] or [])
        return f"<table><tr>{head}</tr>{rows}</table>"
    if t == "image" and b["image_id"]:
        cls = "" if b.get("wide") else ' class="narrow"'   # wide: sơ đồ/biểu đồ nhiều chữ, giãn hết bề ngang trang
        return f'<figure{cls}><img src="img/{b["image_id"]}.jpg"><figcaption>{rich(b["text"])}</figcaption></figure>'
    return ""


def cta_macro(c: dict) -> str:
    clean = lambda s: (s or "").replace("|", "/").replace("-->", "→")
    return f"<!--CTA {clean(c['kicker'])} | {clean(rich(c['title']))} | {clean(rich(c['text']))} | {clean(c['button'])} -->"


def placeholder(path: Path) -> None:
    w, h = 1200, 700
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    cols = [(11, 26, 58), (59, 31, 99), (18, 120, 170)]
    for x in range(w):
        t = x / (w - 1) * 2
        i = min(int(t), 1)
        f = t - i
        d.line([(x, 0), (x, h)], fill=tuple(int(cols[i][k] * (1 - f) + cols[i + 1][k] * f) for k in range(3)))
    im.save(path, quality=85)


def build(doc: dict, work: Path, catalog: list[dict], out_pdf: Path) -> dict:
    proj = work / "ebook"
    if proj.exists():
        shutil.rmtree(proj)
    (proj / "content").mkdir(parents=True)
    (proj / "img").mkdir()
    for c in catalog:
        shutil.copy(work / "anh" / c["file"], proj / "img" / f"{c['id']}.jpg")
    saas_bg = Path(__file__).resolve().parent / "assets" / "saas" / "dark.png"
    if (doc.get("palette") or {}).get("ebook_css") and saas_bg.exists():   # SaaS: nền navy có quầng sáng (design_system.md)
        Image.open(saas_bg).convert("RGB").crop((160, 160, 1920, 960)).resize((1600, 730)).save(proj / "img" / "_nen.jpg", quality=88)
    else:
        placeholder(proj / "img" / "_nen.jpg")

    intro = doc["intro"]
    src_note = html.escape(doc.get("source_credit") or "")
    nc = " Bản biên soạn này chỉ dùng cho mục đích <b>học tập, phi thương mại</b>." if doc["noncommercial"] else ""
    parts = ['<section class="intro">', "<h2>Lời mở đầu</h2>", *[f"<p>{rich(p)}</p>" for p in intro["paragraphs"]],
             "<h3>Tài liệu dành cho ai?</h3>", "<ul>", *[f"<li>{rich(x)}</li>" for x in intro["for_whom"]], "</ul>",
             "<h3>Cách đọc hiệu quả</h3>", f"<p>{rich(intro['how_to_read'])}</p>"]
    if src_note or nc:
        parts.append(f'<div class="box sum"><div class="bt">✦ Ghi nhận nguồn</div><p>{src_note}.{nc}</p></div>')
    parts += ["</section>", '<section class="toc pb" id="toc"><h2>Mục lục</h2><!--TOC--></section>']
    (proj / "content" / "00-mo-dau.html").write_text("\n".join(parts))

    for i, ch in enumerate(doc["chapters"], 1):
        img = f"img/{ch['image_id']}.jpg" if ch.get("image_id") else "img/_nen.jpg"
        h = [f'<section class="chapter">',
             f'<div class="opener"><img src="{img}"><div class="ot"><div class="num">Chương {i:02d}</div>'
             f'<h1>{html.escape(ch["title"])}</h1><p class="lead">{rich(ch["lead"])}</p></div><div class="bar"></div></div>']
        for j, s in enumerate(ch["sections"], 1):
            h.append(f"<h2>{i}.{j} {html.escape(s['heading'])}</h2>")
            h += [block_html(b) for b in s["blocks"]]
        if ch["summary"]:
            h.append('<div class="box sum"><div class="bt">✦ Tóm tắt chương</div><ul>'
                     + "".join(f"<li>{rich(x)}</li>" for x in ch["summary"]) + "</ul></div>")
        if doc.get("course_enabled", True):
            h.append(cta_macro(ch["cta"]))
        h.append("</section>")
        (proj / "content" / f"{i:02d}-chuong.html").write_text("\n".join(h))

    for k, a in enumerate(doc.get("appendix", []), 1):
        h = ['<section class="chapter">', f"<h2>{html.escape(a['title'])}</h2>", *[block_html(b) for b in a["blocks"]], "</section>"]
        (proj / "content" / f"9{k}-phu-luc.html").write_text("\n".join(h))

    cover_ids = doc.get("cover_image_ids") or [c["image_id"] for c in doc["chapters"] if c.get("image_id")]
    imgs = [f"img/{i}.jpg" for i in cover_ids] or ["img/_nen.jpg"]
    cfg = {
        "title": doc["title"], "series": doc["series"], "year": date.today().year,
        "cover": {"kicker": html.escape(doc["kicker"]), "title_html": html.escape(doc["title"]),
                  "subtitle_html": html.escape(doc["subtitle"]), "credit": doc["credit"],
                  "source": html.escape(doc.get("source_credit") or ""), "images": (imgs * 12)[:12]},
        "course": {"enabled": doc.get("course_enabled", True), "kicker": "Bước tiếp theo sau tài liệu này",
                   "intro": "Bạn vừa nắm phần kiến thức nền. Bước tiếp theo là để AI <b style=\"color:#ffd166\">làm việc thay bạn</b>: "
                            "tự nghiên cứu, soạn nội dung, xử lý dữ liệu và chạy các quy trình lặp lại mỗi ngày."},
        "eco_follow": f"Theo dõi SlimAI để nhận thêm tài liệu <b>{html.escape(doc['series'])}</b>",
        "footer_note": "Tài liệu học tập, phi thương mại." if doc["noncommercial"] else "",
    }
    pal = doc.get("palette")
    if pal:   # ebook dùng cùng bảng màu với bộ slide
        cfg["extra_css"] = (f":root{{--navy:{pal['deep']};--pink:{pal['secondary']};--cyan:{pal['primary']};--soft:{pal['soft']};"
                            f"--grad:linear-gradient(90deg,{pal['secondary']},{pal['primary']} 55%,{pal['deep']})}}"
                            f".prompt{{border-left-color:{pal['primary']}}}.toc .pg,b,strong{{color:{pal['deep']}}}"
                            + pal.get("ebook_css", ""))
    (proj / "ebook.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=1))
    builder = EBOOK_TEMPLATE / "build.py"
    if not builder.exists():
        raise RuntimeError(f"Không thấy {builder}. Cài skill tai-lieu-slimai.")
    r = subprocess.run([sys.executable, str(builder), str(proj), str(out_pdf)], capture_output=True, text=True, timeout=900)
    if r.returncode:
        raise RuntimeError("Dựng ebook thất bại:\n" + (r.stderr or r.stdout)[-1500:])
    missing = [l for l in r.stdout.splitlines() if "KHÔNG TÌM THẤY" in l]
    return {"stdout": r.stdout.strip(), "toc_missing": missing}
