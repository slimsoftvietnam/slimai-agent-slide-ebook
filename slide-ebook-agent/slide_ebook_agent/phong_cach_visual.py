"""Phong cách 'visual': học CÁCH DÀN TRANG của bộ slide mẫu (Visual-First), MÀU lấy theo bảng màu riêng của từng tài liệu.

Đặc trưng: tiêu đề sans nét thường + vài chữ nhấn serif nghiêng màu chủ đạo; nền "pixel mosaic"/sọc dọc sinh từ bảng màu;
thẻ trắng bo góc có bóng nhẹ; timeline với viên số; hình cầu nét mảnh; sơ đồ trung tâm; ảnh dọc bo góc.
Phần tử tên '!!…' được ghép cặp giữa các slide để tạo chuyển động Morph (PPTX) / View Transitions (HTML).
"""
from __future__ import annotations

import hashlib
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

from thiet_ke_slide import H, W, Deck, image, line, oval, qr_png, rect, text
from thuong_hieu import brand, hex_rgb, logo

SANS, SERIF, MONO = "Be Vietnam Pro", "Playfair Display", "Courier New"
M = 44

DEFAULT_PALETTE = {
    "name": "SlimAI", "reason": "Màu thương hiệu SlimAI",
    "primary": "#8a4dea", "secondary": "#e8318a", "deep": "#2a1660", "soft": "#f4effd", "ink": "#16121f",
    "mosaic": ["#efe6ff", "#b48cff", "#8a4dea", "#e8318a", "#3b1f8f"],
}


def mix(a: str, b: str, t: float) -> str:
    ra, rb = hex_rgb(a), hex_rgb(b)
    return "#%02x%02x%02x" % tuple(int(ra[i] * (1 - t) + rb[i] * t) for i in range(3))


def _ramp(colors: list[str], v: float) -> tuple:
    v = min(max(v, 0), 0.9999) * (len(colors) - 1)
    i = int(v)
    return hex_rgb(mix(colors[i], colors[i + 1], v - i))


def make_mosaic(path: Path, colors: list[str], seed: int, cols: int = 48, rows: int = 27) -> Path:
    """Nền khối pixel chuyển màu mượt (như dải màu trên slide mẫu)."""
    if path.exists():
        return path
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, 6.28) for _ in range(4)]
    small = Image.new("RGB", (cols, rows))
    px = small.load()
    for y in range(rows):
        for x in range(cols):
            v = 0.5 + 0.28 * math.sin(x * 0.16 + ph[0]) * math.cos(y * 0.23 + ph[1]) \
                + 0.22 * math.sin((x + y) * 0.09 + ph[2]) + rnd.uniform(-0.07, 0.07)
            r, g, b = _ramp(colors, v)
            k = rnd.uniform(0.94, 1.06)
            px[x, y] = tuple(min(255, int(c * k)) for c in (r, g, b))
    big = small.resize((2160, 1215), Image.NEAREST)
    soft = big.filter(ImageFilter.GaussianBlur(28))
    Image.blend(big, soft, 0.35).save(path, quality=90)
    return path


def make_stripes(path: Path, colors: list[str], seed: int) -> Path:
    """Nền sọc dọc chuyển màu (như slide kết 'Let's Build…')."""
    if path.exists():
        return path
    rnd = random.Random(seed)
    w, h = 2160, 1215
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    x = 0
    while x < w:
        cw = rnd.randint(40, 110)
        a, b = rnd.uniform(0, 1), rnd.uniform(0, 1)
        for y in range(0, h, 3):
            t = y / h
            d.rectangle([x, y, x + cw, y + 3], fill=_ramp(colors, a * (1 - t) + b * t))
        x += cw
    im.filter(ImageFilter.GaussianBlur(3)).save(path, quality=90)
    return path


def make_orb(path: Path, color: str) -> Path:
    """Quầng sáng tròn mờ (PNG trong suốt) trôi giữa các slide nội dung."""
    if path.exists():
        return path
    s = 600
    r, g, b = hex_rgb(color)
    im = Image.new("RGBA", (s, s), (r, g, b, 0))
    px = im.load()
    for y in range(s):
        for x in range(s):
            d = math.hypot(x - s / 2, y - s / 2) / (s / 2)
            px[x, y] = (r, g, b, int(max(0.0, 1 - d) ** 2.2 * 120))
    im.save(path)
    return path


class DeckVisual(Deck):
    sans = SANS
    font_links = ["https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@300;400;500;600;700"
                  "&family=Playfair+Display:ital,wght@0,400;0,500;1,400;1,500&display=swap"]
    transition = "morph"

    def __init__(self, doc, work, images, social):
        super().__init__(doc, work, images, social)
        p = {**DEFAULT_PALETTE, **(doc.get("palette") or {})}
        self.p = p
        self.ink, self.pri, self.sec, self.deep, self.soft = p["ink"], p["primary"], p["secondary"], p["deep"], p["soft"]
        self.mut = mix(self.ink, "#ffffff", 0.45)
        self.line_c = mix(self.soft, self.ink, 0.12)
        seed = int(hashlib.md5((doc["title"] + p["primary"]).encode()).hexdigest()[:8], 16)
        art = work / "visual"
        art.mkdir(exist_ok=True)
        tag = p["primary"].lstrip("#")
        self.images["_mosaic"] = make_mosaic(art / f"mosaic-{tag}.jpg", p["mosaic"], seed)
        self.images["_stripes"] = make_stripes(art / f"stripes-{tag}.jpg", p["mosaic"], seed + 1)
        self.orb = make_orb(art / f"orb-{tag}.png", self.pri)
        self.n_content = 0

    # ---------------------------------------------------------- chi tiết dùng chung
    def T(self, x, y, w, h, paras, size, role, **kw):
        kw.setdefault("color", self.ink)
        kw.setdefault("accent", self.pri)
        kw.setdefault("accent_font", SERIF)
        return text(x, y, w, h, paras, size, role, **kw)

    def caps(self, x, y, w, label, color=None):
        return text(x, y, w, 14, label, 8, "kicker", color=color or self.pri, bold=True, caps=True, spacing_chars=1.2)

    def pill(self, x, y, label, name=""):
        return [rect(x, y, 30, 16, fill=self.ink, radius=8, name=name),
                text(x, y, 30, 16, label, 8, "pill", color="#ffffff", bold=True, align="center", valign="middle")]

    def orb_el(self):
        spots = [(470, -120), (520, 170), (-140, 200), (380, -150), (560, 40)]
        x, y = spots[self.n_content % len(spots)]
        self.n_content += 1
        return image(x, y, 300, 300, self.orb, fit="cover", name="!!orb")

    def art(self, key, x, y, w, h):
        return self.img(key, x, y, w, h, name="!!art")

    def title_block(self, title, subtitle=None, width=None):
        tw = width or (400 if subtitle else W - 2 * M - 40)
        els = [self.T(M, 30, tw, 74, title, 27, "title", min_size=19, valign="bottom", name="!!title")]
        if subtitle:
            els.append(self.T(480, 34, W - M - 480 - 26, 70, subtitle, 11, "subtitle", color=self.mut, min_size=9,
                              valign="bottom"))
        return els, 124

    def chrome(self, idx, s):
        if not s["footer"]:
            return []
        on_art = s["kind"] in ("course",)
        fc = "#ffffff" if on_art else self.mut
        has_photo = any(e.get("name") == "!!photo" for e in s["elements"])
        x0 = 340 if s["kind"] == "section" else M
        els = []
        if not on_art and s["kind"] != "eco" and not has_photo:
            els.append(image(W - M - 18, 26, 18, 18, logo("slimai_icon"), self.b["site"], fit="contain", name="!!logo"))
        lx = W - M - 180 if s["kind"] == "section" else W / 2 - 60
        els += [text(x0, H - 24, 150, 12, self.b["slogan"], 7.5, "footer", color=fc, bold=True),
                text(lx, H - 24, 120, 12, self.b["site_label"], 7.5, "footer", color=fc, align="center", link=self.b["site"]),
                text(W - M - 60, H - 24, 60, 12, f"{idx + 1:02d}", 7.5, "footer", color=fc, align="right", bold=True)]
        return els

    def add(self, kind, elements, **kw):
        super().add(kind, elements, **kw)

    # ---------------------------------------------------------- slide tự động
    def cover(self):
        d = self.doc
        els = self.art("_mosaic", 0, 0, W, H)
        els += [rect(M, 50, 410, 305, fill="#ffffff", radius=14, shadow=True, name="!!card1"),
                image(M + 26, 72, 110, 30, logo("slimai"), self.b["site"], fit="contain-left", name="!!logo"),
                self.caps(M + 26, 120, 360, d["kicker"]),
                self.T(M + 26, 138, 360, 110, d["title"], 30, "cover-title", min_size=20, valign="middle"),
                self.T(M + 26, 252, 360, 40, d["subtitle"], 11, "cover-sub", color=self.mut, min_size=9),
                text(M + 26, 296, 360, 26, [f"{self.b['credit'][d['credit']]} · {self.b['site_label']}", d.get("source_credit") or ""],
                     8.5, "cover-credit", color=self.mut, min_size=7),
                text(M + 26, 328, 360, 14, self.slogan(), 9, "slogan", color=self.mut, bold=True)]
        self.add("cover", els, footer=False, title=d["title"], notes=d["subtitle"])

    def _timeline(self, items, top, name_prefix):
        """items: [(tiêu đề, mô tả)] — đường ngang + viên số 01…; tối đa 5 cột."""
        n = len(items)
        cw = (W - 2 * M - 16 * (n - 1)) / n
        y0 = top + max(20, (H - 50 - top - 150) / 2)
        els = [rect(M, y0 + 7.5, W - 2 * M, 1, fill=mix(self.pri, self.soft, 0.55))]
        for i, (t, dsc) in enumerate(items):
            x = M + i * (cw + 16)
            els += self.pill(x, y0, f"{i + 1:02d}", name=f"!!{name_prefix}{i + 1}")
            els += [self.T(x, y0 + 32, cw, 40, f"**{t}**", 14, "tl-title", min_size=10),
                    self.T(x, y0 + 76, cw, min(90, H - 50 - (y0 + 76)), dsc, 11.5, "tl-text", color=self.mut, min_size=8.5)]
        return els

    def agenda(self):
        chs = self.doc["chapters"]
        els, top = self.title_block("Nội dung *chính*", "Lộ trình của tài liệu, từ nền tảng đến ứng dụng.")
        els.insert(0, self.orb_el())
        if len(chs) <= 5:
            els += self._timeline([(c["title"], c["lead"]) for c in chs], top, "dot")
        else:
            rh = (H - 50 - top) / len(chs)
            for i, c in enumerate(chs):
                y = top + i * rh
                els += self.pill(M, y + 2, f"{i + 1:02d}", name=f"!!dot{i + 1}")
                els.append(self.T(M + 44, y, W - 2 * M - 44, rh - 4, f"**{c['title']}** · {c['lead']}", 12, "agenda", min_size=9))
        self.add("agenda", els, bg=self.soft, title="Nội dung chính", notes="Lộ trình của bài trình bày.")

    def section(self, i, ch):
        key = ch.get("image_id") if ch.get("image_id") in self.images else "_mosaic"
        els = self.art(key, 0, 0, 300, H)
        els += [text(28, 230, 250, 140, f"{i + 1:02d}", 110, "section-num", color="#ffffff", font=SERIF, italic=True),
                self.caps(340, 118, 300, f"Chương {i + 1:02d}"),
                self.T(340, 136, W - M - 340, 118, ch["title"], 30, "section-title", min_size=20, valign="middle", name="!!title"),
                self.T(340, 262, W - M - 340, 70, ch["lead"], 12.5, "section-lead", color=self.mut, min_size=10)]
        self.add("section", els, chapter=ch["id"], title=ch["title"], notes=ch["lead"])

    def summary(self):
        chs = self.doc["chapters"]
        els, top = self.title_block("Điểm chính *cần nhớ*")
        els.insert(0, self.orb_el())
        els += self._rows([c["summary"][0] if c["summary"] else c["lead"] for c in chs], M, top, W - 2 * M, H - 48)
        self.add("summary", els, title="Điểm chính cần nhớ", notes="Nhắc lại thông điệp chính của từng chương.")

    def course(self):
        c = self.b["course"]
        url = c["url"]
        qr = qr_png(url, self.work / "qr-khoa-hoc.png")
        items = [x.split(":")[0] for x in (__import__("re").sub(r"<[^>]+>", "", i) for i in c["modules"][0]["items"])][:4]
        els = self.art("_stripes", 0, 0, W, H)
        els += [text(M, 56, 320, 150, ["Để AI", "*làm việc*", "thay bạn"], 36, "course-big", color="#ffffff",
                     accent="#ffffff", accent_font=SERIF, min_size=24),
                rect(M, 236, 104, 104, fill="#ffffff", radius=10),
                image(M + 8, 244, 88, 88, qr, url, fit="contain"),
                text(M + 116, 300, 180, 30, "Quét mã để xem lộ trình khoá học", 9, "qr", color="#ffffff", min_size=7),
                rect(404, 36, W - M - 404, 323, fill="#ffffff", radius=14, shadow=True, name="!!card1"),
                self.caps(426, 58, 230, "Bước tiếp theo"),
                self.T(426, 76, 230, 62, c["name"].replace("AI Agent", "*AI Agent*"), 21, "course-title", min_size=15),
                self.T(426, 142, 230, 40, c["audience"], 9, "course-aud", color=self.mut, min_size=7.5),
                self.T(426, 188, 230, 108, items, 10.5, "course-item", bullet=self.pri, space=4, min_size=8.5),
                rect(426, 306, 150, 26, fill=self.ink, radius=13),
                text(426, 306, 150, 26, "Xem khoá học →", 10, "button", color="#ffffff", bold=True, align="center",
                     valign="middle", link=url),
                text(426, 336, 230, 12, c["url_label"], 8, "url", color=self.mut, link=url)]
        self.add("course", els, title=c["name"], notes="Giới thiệu khoá học AI Agent cho người đi làm.")

    # ---------------------------------------------------------- slide nội dung
    def content(self, s, chapter_id):
        from thiet_ke_slide import fn_ok

        lay = s["layout"] if fn_ok(s) and hasattr(self, f"l_{s['layout']}") else "bullets"
        if lay == "stats":
            els = self.l_stats_full(s)
        elif lay == "image" or (lay == "bullets" and s.get("image_id") in self.images):
            els, top = self.title_block(s["title"], None, width=350)
            els += getattr(self, f"l_{lay}")(s, top)
        else:
            els, top = self.title_block(s["title"], s.get("subtitle"))
            if lay in ("bullets", "quote", "table", "prompt", "compare"):
                els.insert(0, self.orb_el())
            els += getattr(self, f"l_{lay}")(s, top)
        bg = self.soft if lay in ("steps", "quote", "hub") else "#ffffff"
        self.add(lay, els, chapter=chapter_id, title=s["title"], notes=s.get("notes") or "", bg=bg)

    def _rows(self, items, x, top, w, bottom):
        n = max(1, len(items))
        rh = (bottom - top) / n
        els = []
        for i, it in enumerate(items):
            y = top + i * rh
            els += [text(x, y + 4, 40, rh - 10, f"{i + 1:02d}", 20, "row-num", color=self.pri, font=SERIF, italic=True, valign="middle"),
                    self.T(x + 48, y + 4, w - 48, rh - 10, it, 15, "body", min_size=10.5, valign="middle")]
            if i < n - 1:
                els.append(rect(x, y + rh - 1, w, 0.75, fill=self.line_c))
        return els

    def l_bullets(self, s, top):
        items = s.get("bullets") or [s.get("caption") or ""]
        if s.get("image_id") and s["image_id"] in self.images:
            els = self._rows(items, M, top, 340, H - 48)
            els += self.img(s["image_id"], 412, 36, W - M - 412, 322, name="!!photo")
            els[-1]["radius"] = 12
            return els
        return self._rows(items, M, top, W - 2 * M, H - 48)

    def _motif(self, k, cx, cy, r):
        c = self.pri
        k %= 4
        if k == 0:   # hình cầu kinh tuyến
            return [oval(cx - r, cy - r, 2 * r, 2 * r, line=c, line_w=0.6)] + \
                   [oval(cx - r * f, cy - r, 2 * r * f, 2 * r, line=c, line_w=0.6) for f in (0.72, 0.42, 0.14)]
        if k == 1:   # vòng xoắn chồng
            return [oval(cx - r, cy - r + j * r * 0.22, 2 * r, r * 0.7, line=c, line_w=0.6) for j in range(7)]
        if k == 2:   # vòng đồng tâm lệch
            return [oval(cx - r * f, cy + r - 2 * r * f, 2 * r * f, 2 * r * f, line=c, line_w=0.6) for f in (1, 0.78, 0.56, 0.34)]
        return [oval(cx - r, cy - r, 2 * r, 2 * r, line=c, line_w=0.6)] + \
               [oval(cx - r, cy - r * f, 2 * r, 2 * r * f, line=c, line_w=0.6) for f in (0.66, 0.33)]

    def l_cards(self, s, top):
        cards = (s.get("cards") or [])[:4]
        n = len(cards)
        cw = (W - 2 * M - 22 * (n - 1)) / n
        els = []
        for i, c in enumerate(cards):
            x = M + i * (cw + 22)
            els += self._motif(i, x + 46, top + 54, 44)
            els += [self.T(x, top + 118, cw, 36, f"**{c['title']}**", 15, "card-title", min_size=10.5),
                    self.T(x, top + 156, cw, H - 50 - (top + 156), c["text"], 12, "card-text", color=self.mut, min_size=8.5)]
        return els

    def l_steps(self, s, top):
        return self._timeline([(st["title"], st["text"]) for st in (s.get("steps") or [])[:5]], top, "dot")

    def l_stats_full(self, s):
        stats = (s.get("stats") or [])[:3]
        n = len(stats)
        els = self.art("_mosaic", 0, 0, W, 196)
        els.append(self.T(M, 30, 470, 96, s["title"], 28, "title", color="#ffffff", accent="#ffffff", min_size=19,
                          valign="bottom", name="!!title"))
        if s.get("subtitle"):
            els.append(text(530, 60, W - M - 530, 60, s["subtitle"], 10, "subtitle", color="#ffffff", min_size=8, valign="bottom"))
        cw = (W - 2 * M - 14 * (n - 1)) / n
        for i, st in enumerate(stats):
            x = M + i * (cw + 14)
            els += [rect(x, 150, cw, 196, fill="#ffffff", radius=6, shadow=True, name=f"!!card{i + 1}"),
                    self.caps(x + 16, 166, cw - 32, f"{i + 1:02d}", color=self.ink),
                    text(x + 16, 214, cw - 32, 62, st["value"], 44, "stat-value", color=self.ink, font=SERIF, min_size=26),
                    self.T(x + 16, 280, cw - 32, 56, st["label"], 10.5, "stat-label", color=self.mut, min_size=8.5)]
        return els

    def l_compare(self, s, top):
        cw = (W - 2 * M - 40) / 2
        ch = H - 52 - top
        els = []
        for i, (side, fill, tc) in enumerate([(s["left"], "#ffffff", self.ink), (s["right"], mix(self.soft, self.pri, 0.06), self.pri)]):
            x = M + i * (cw + 40)
            els += [rect(x, top, cw, ch, fill=fill, radius=12, line=self.line_c, shadow=(i == 1), name=f"!!card{i + 1}"),
                    text(x + 18, top + 16, cw - 36, 26, side["title"], 16, "compare-title", color=tc, font=SERIF, italic=True, min_size=12),
                    self.T(x + 18, top + 50, cw - 36, ch - 62, side["items"], 14, "compare-item", bullet=tc, space=7, min_size=9.5)]
        els += [oval(W / 2 - 14, top + ch / 2 - 14, 28, 28, fill=self.ink),
                text(W / 2 - 14, top + ch / 2 - 14, 28, 28, "→", 13, "arrow", color="#ffffff", align="center", valign="middle", bold=True)]
        return els

    def l_quote(self, s, top):
        return [text(M, top - 22, 80, 124, "“", 90, "quote-mark", color=self.pri, font=SERIF, italic=True),
                text(M + 64, top + 6, W - 2 * M - 120, 170, s["quote"], 24, "quote", color=self.ink, font=SERIF, italic=True,
                     min_size=15, valign="middle"),
                self.T(M + 64, top + 190, W - 2 * M - 120, 20, f"— {s['by']}" if s.get("by") else "", 11, "quote-by", color=self.mut)]

    def l_prompt(self, s, top):
        ch = 170 if s.get("caption") else 214
        els = [rect(M, top, W - 2 * M, ch, fill=self.ink, radius=12, name="!!card1"),
               text(M + 20, top + 16, 300, 14, "PROMPT MẪU", 8, "prompt-label", color=mix(self.pri, "#ffffff", 0.45), bold=True, spacing_chars=1.2),
               text(M + 20, top + 38, W - 2 * M - 40, ch - 50, s["prompt"], 14, "prompt", color="#f2eefb", font=MONO, min_size=10)]
        if s.get("caption"):
            els.append(self.T(M, top + ch + 14, W - 2 * M, 40, s["caption"], 12, "caption", color=self.mut, min_size=9.5))
        return els

    def l_image(self, s, top):
        els = []
        if s.get("caption"):
            els.append(self.T(M, top, 350, 54, f"*{s['caption'].strip('*')}*", 15, "lead", color=self.pri, min_size=11))
        side = s.get("bullets") or []
        if side:
            els.append(self.T(M, top + 64, 350, H - 56 - (top + 64), side, 11.5, "side", color=self.mut, bullet=self.pri,
                              space=6, min_size=9))
        els += self.img(s["image_id"], 420, 36, W - M - 420, 322, name="!!photo")
        els[-1]["radius"] = 12
        return els

    def l_table(self, s, top):
        header, rows = s["header"][:3], [r[:3] for r in (s.get("rows") or [])[:6]]
        cols = len(header)
        cw = (W - 2 * M) / cols
        rh = min(42, (H - 52 - top - 30) / max(1, len(rows)))
        els = [rect(M, top, W - 2 * M, 28, fill=mix(self.soft, self.pri, 0.08), radius=6)]
        for j, hd in enumerate(header):
            els.append(text(M + j * cw + 12, top, cw - 24, 28, hd, 11, "th", color=self.pri, bold=True, valign="middle", min_size=9))
        for i, r in enumerate(rows):
            y = top + 30 + i * rh
            els.append(rect(M, y + rh - 0.75, W - 2 * M, 0.75, fill=self.line_c))
            for j, cell in enumerate(r + [""] * (cols - len(r))):
                els.append(self.T(M + j * cw + 12, y + 2, cw - 24, rh - 4, cell, 12, "td", valign="middle", min_size=9))
        return els

    def l_hub(self, s, top):
        cards = (s.get("cards") or [])[:4]
        cx, cy = W / 2, top + (H - 48 - top) / 2
        els = [oval(cx - 82, cy - 82, 164, 164, fill=mix(self.soft, self.pri, 0.10), alpha=0.8),
               oval(cx - 62, cy - 62, 124, 124, fill=mix(self.soft, self.pri, 0.18), alpha=0.9),
               oval(cx - 46, cy - 46, 92, 92, fill="#ffffff", line=mix(self.pri, "#ffffff", 0.4), name="!!hub"),
               self.T(cx - 40, cy - 22, 80, 44, s.get("caption") or s.get("subtitle") or "", 11.5, "hub-center",
                      align="center", valign="middle", bold=True, min_size=8.5)]
        cw, chh = 178, 66
        spots = [(M + 10, top + 6), (W - M - 10 - cw, top + 6), (M + 10, H - 56 - chh), (W - M - 10 - cw, H - 56 - chh)]
        for i, c in enumerate(cards):
            x, y = spots[i]
            ex = x + cw if x < cx else x
            els.append(line(ex, y + chh / 2, cx + (-46 if x < cx else 46) * 0.92, cy + (-1 if y < cy else 1) * 18,
                            mix(self.pri, "#ffffff", 0.35), 0.75))
            els += [rect(x, y, cw, chh, fill="#ffffff", radius=8, line=self.line_c, shadow=True, name=f"!!card{i + 1}"),
                    self.T(x + 12, y + 8, cw - 54, 18, f"**{c['title']}**", 11, "hub-title", min_size=8.5),
                    text(x + cw - 40, y + 6, 28, 20, f"{i + 1:02d}", 13, "hub-num", color=self.pri, font=SERIF, italic=True, align="right"),
                    self.T(x + 12, y + 28, cw - 24, chh - 34, c["text"], 9, "hub-text", color=self.mut, min_size=7.5)]
        return els


def palette_preview(options: list[dict], out: Path, seed: int = 7) -> Path:
    """Ảnh xem trước các bảng màu đề xuất: dải mosaic + ô màu + tên, để người dùng chọn trước khi dựng."""
    from PIL import ImageFont

    w, row = 1200, 230
    im = Image.new("RGB", (w, row * len(options) + 20), "#ffffff")
    d = ImageDraw.Draw(im)
    try:
        f1 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 30)
        f2 = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 20)
    except OSError:
        f1 = f2 = ImageFont.load_default()
    for i, p in enumerate(options):
        y = 20 + i * row
        tmp = out.parent / f"_pv{i}.jpg"
        make_mosaic(tmp, p["mosaic"], seed + i)
        band = Image.open(tmp).resize((420, 190))
        im.paste(band, (20, y))
        tmp.unlink(missing_ok=True)
        d.text((470, y + 4), f"{i + 1}. {p['name']}", fill=p["ink"], font=f1)
        d.text((470, y + 44), p["reason"][:90], fill="#555555", font=f2)
        for k, key in enumerate(["primary", "secondary", "deep", "soft", "ink"]):
            x = 470 + k * 140
            d.rounded_rectangle([x, y + 84, x + 120, y + 154], 12, fill=p[key], outline="#dddddd")
            d.text((x, y + 160), f"{key}\n{p[key]}", fill="#333333", font=f2)
    im.save(out, quality=90)
    return out
