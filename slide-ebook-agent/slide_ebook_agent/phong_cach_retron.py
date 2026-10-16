"""Phong cách 'retron' (mặc định): bố cục kiểu mẫu Retron — panel gradient tím→lilac, khối lập phương 3D bóng lơ lửng,
tiêu đề Space Grotesk hai màu (đen + tím), thẻ trắng đổ bóng tím, slide mở chương nền tím phủ kín, nút tím chữ trắng.

Màu: mặc định TÍM Retron (đúng ảnh mẫu người dùng đã chọn). Chỉ đổi màu khi người dùng yêu cầu (--mau / --bang-mau):
khi đó accent theo bảng màu và ảnh khối/đốm/nền được xoay sắc độ (hue) sang màu chính.
Toạ độ viết theo inch của khung 13.333 x 7.5 in (giống bản dựng tay đã duyệt) rồi đổi sang pt (x54); cỡ chữ x0.75.
Phần tử tên '!!…' ghép cặp giữa các slide => Morph (PPTX) / View Transitions (HTML).
"""
from __future__ import annotations

import colorsys
import re
from pathlib import Path

from PIL import Image

from thiet_ke_slide import H, W, Deck, image, line, oval, qr_png, rect, text
from thuong_hieu import hex_rgb, logo

ASSETS = Path(__file__).resolve().parent / "assets" / "retron"
HEAD, SANS, MONO = "Space Grotesk", "Be Vietnam Pro", "Courier New"
K = W / (40 / 3)                  # 1 inch của khung 13.333 in = 54 pt
CUBE_R = 672 / 591
CUBES = ["cube", "cube_lav", "cube_deep", "cube_lav", "cube_blur", "cube_blur"]

RETRON = {"name": "Retron tím", "reason": "Phong cách Retron: tím gradient, khối 3D (mặc định đã chọn)",
          "primary": "#6D4AEE", "secondary": "#9479FA", "deep": "#4524B8", "soft": "#EFEAFF", "ink": "#17132B",
          "mosaic": ["#EFEAFF", "#C9B8FF", "#9479FA", "#6D4AEE", "#4524B8"]}


def I(v: float) -> float:
    return round(v * K, 2)


def F(v: float) -> float:
    return round(v * 0.75, 2)


def mix(a: str, b: str, t: float) -> str:
    ra, rb = hex_rgb(a), hex_rgb(b)
    return "#%02x%02x%02x" % tuple(int(ra[i] * (1 - t) + rb[i] * t) for i in range(3))


def hue(c: str) -> float:
    r, g, b = (x / 255 for x in hex_rgb(c))
    return colorsys.rgb_to_hsv(r, g, b)[0]


def explicit_palette(doc: dict) -> dict | None:
    """Bảng màu người dùng chủ động yêu cầu (lời hoặc mã màu); bảng agent tự chọn thì bỏ qua để giữ tím Retron."""
    p = doc.get("palette")
    if p and (doc.get("color_wish") or p.get("name") == "Tuỳ chọn"):
        return p
    return None


def tint(src: Path, out: Path, shift: float) -> Path:
    if out.exists():
        return out
    im = Image.open(src).convert("RGBA")
    a = im.getchannel("A")
    h, s, v = im.convert("RGB").convert("HSV").split()
    d = int(round(shift * 255))
    h = h.point(lambda x: (x + d) % 256)
    rgb = Image.merge("HSV", (h, s, v)).convert("RGB")
    rgb.putalpha(a)
    rgb.save(out)
    return out


# Vị trí khối lập phương (inch) theo từng bố cục — đặt ở mép, không đè chữ (lấy từ bản đã duyệt)
SPOTS = {
    "cover": [[7.55, 3.75, 1.4, 10], [7.95, 0.35, 0.7, -12], [11.3, 4.5, 1.0, 6], [5.9, 0.9, 0.5, 18], [12.2, 6.2, 0.75, 0], [0.35, 6.0, 0.55, -10]],
    "agenda": [[4.45, 0.45, 1.0, -8], [12.0, 5.8, 0.85, 12], [3.4, 5.4, 0.7, 4], [2.3, 4.6, 0.42, -16], [0.25, 0.55, 0.55, 0], [12.55, 0.25, 0.5, 0]],
    "bullets": [[4.45, 0.45, 1.0, -8], [12.0, 5.8, 0.85, 12], [4.2, 6.05, 0.55, 4], [3.3, 6.3, 0.35, -16], [0.25, 0.55, 0.55, 0], [12.55, 0.25, 0.5, 0]],
    "panelL": [[7.45, 0.5, 0.85, 14], [0.25, 5.95, 0.75, -6], [12.25, 6.0, 0.6, 8], [12.0, 0.55, 0.45, -14], [8.4, 6.55, 0.45, 0], [6.4, 0.3, 0.42, 0]],
    "band": [[11.9, 0.45, 0.9, -8], [12.6, 1.75, 0.45, 12], [0.3, 6.15, 0.5, 4], [10.7, 0.5, 0.4, -16], [8.4, 0.45, 0.38, 0], [9.6, 0.6, 0.35, 0]],
    "compare": [[12.05, 1.9, 0.85, 14], [6.3, 6.15, 0.5, -6], [0.3, 6.15, 0.5, 8], [12.1, 0.4, 0.45, -14], [12.7, 6.45, 0.42, 0], [10.6, 0.45, 0.42, 0]],
    "full": [[1.6, 0.9, 1.0, -10], [10.9, 1.0, 0.75, 12], [11.9, 2.6, 0.5, -6], [0.75, 2.55, 0.5, 14], [6.3, 0.2, 0.5, 0], [12.4, 6.3, 0.7, 0]],
    "image": [[12.05, 0.45, 0.8, 14], [6.5, 5.9, 0.6, -6], [12.2, 6.2, 0.55, 8], [0.3, 0.6, 0.42, -14], [6.3, 0.5, 0.4, 0], [0.4, 6.25, 0.45, 0]],
    "table": [[12.1, 0.45, 0.8, 14], [12.3, 2.0, 0.45, -8], [0.3, 6.25, 0.45, 8], [11.0, 0.6, 0.4, -14], [9.6, 0.5, 0.35, 0], [0.4, 0.95, 0.4, 0]],
    "course": [[7.3, 4.9, 1.1, 10], [7.4, 0.4, 0.6, -12], [12.1, 5.9, 0.75, 6], [6.2, 1.4, 0.45, 18], [12.3, 0.3, 0.5, 0], [0.35, 6.1, 0.5, -10]],
    "eco": [[11.7, 0.5, 0.8, -8], [0.6, 5.9, 0.6, 12], [12.3, 5.8, 0.55, 4], [0.5, 0.9, 0.42, -16], [10.9, 1.5, 0.4, 0], [1.6, 6.4, 0.4, 0]],
}
SECTION_SPOTS = [
    [[10.2, 1.2, 1.5, 10], [9.3, 4.4, 0.8, -12], [11.9, 3.6, 1.0, 6], [8.6, 0.6, 0.5, 18], [12.3, 6.1, 0.6, 0], [6.4, 6.2, 0.5, -10]],
    [[9.8, 3.4, 1.5, -8], [10.6, 0.9, 0.8, 12], [12.2, 4.9, 0.9, 6], [8.2, 1.2, 0.5, -14], [12.4, 0.4, 0.55, 0], [7.0, 6.2, 0.5, 10]],
    [[10.4, 1.4, 1.3, 12], [9.0, 4.6, 0.9, -8], [12.0, 3.9, 0.8, 4], [8.8, 0.7, 0.5, -16], [12.5, 0.5, 0.5, 0], [6.6, 6.3, 0.45, 0]],
    [[10.0, 2.6, 1.6, 6], [11.9, 0.8, 0.8, -12], [9.0, 5.0, 0.7, 10], [8.4, 1.0, 0.5, 18], [12.5, 5.6, 0.6, 0], [6.8, 6.3, 0.45, -10]],
]


class DeckRetron(Deck):
    sans = SANS
    head = HEAD                   # font tiêu đề (phong cách con có thể đổi)
    font_links = ["https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&family=Space+Grotesk:wght@500;700&display=swap"]
    transition = "morph"

    def __init__(self, doc, work, images, social):
        super().__init__(doc, work, images, social)
        p = explicit_palette(doc)
        if p:   # màu người dùng yêu cầu
            self.a1, self.a5, self.ink = p["primary"], p["deep"], p["ink"]
            self.a2 = mix(self.a1, "#ffffff", 0.25)
            self.grad = [mix(self.a1, "#000000", 0.06), self.a2, mix(self.a1, "#ffffff", 0.78)]
            self.dark_bg = mix(self.a1, "#ffffff", 0.15)
        else:
            self.a1, self.a2, self.a5, self.ink = "#6D4AEE", "#9479FA", "#4524B8", "#17132B"
            self.grad = ["#6440EC", "#9479FA", "#DCCFFF"]
            self.dark_bg = "#8466F6"
        self.a3 = mix(self.a1, "#ffffff", 0.62)      # lilac: viên tròn, nhãn
        self.a4 = mix(self.a1, "#ffffff", 0.88)      # lilac rất nhạt: pill
        self.mut = mix(self.ink, "#ffffff", 0.38)
        self.sh_panel = f"{self.a5}/0.22"
        self.sh_card = f"{self.a5}/0.16"
        # ảnh: dùng nguyên bộ tím; nếu đổi màu thì xoay hue sang màu chính
        names = CUBES[:4] + ["cube_blur", "blob_violet", "blob_pink", "bg", "shadow"] + [f"bar{i}" for i in range(5)]
        shift = (hue(self.a1) - hue("#6D4AEE")) % 1.0 if p else 0
        out = work / "retron"
        out.mkdir(exist_ok=True)
        self.A = {n: (tint(ASSETS / f"{n}.png", out / f"{n}-{self.a1.lstrip('#')}.png", shift) if shift else ASSETS / f"{n}.png")
                  for n in set(names)}
        self.ch_index = {c["id"]: i for i, c in enumerate(doc["chapters"])}

    # ---------------------------------------------------------- mảnh ghép
    def T(self, x, y, w, h, paras, size, role, **kw):
        """Toạ độ inch, cỡ chữ theo thang 960 (tự đổi). Chữ *nhấn* = màu tím, không nghiêng."""
        kw.setdefault("color", self.ink)
        kw.setdefault("accent", self.a2)
        kw.setdefault("accent_italic", False)
        kw.setdefault("font", SANS)
        if "min_size" in kw:
            kw["min_size"] = F(kw["min_size"])
        if "spacing_chars" in kw:
            kw["spacing_chars"] = F(kw["spacing_chars"])
        return text(I(x), I(y), I(w), I(h), paras, F(size), role, **kw)

    def bg(self):
        return [image(0, 0, W, H, self.A["bg"], name="!!bg")]

    def blobs(self, a, b):
        return [image(I(a[0]), I(a[1]), I(a[2]), I(a[2]), self.A["blob_violet"], name="!!blobA"),
                image(I(b[0]), I(b[1]), I(b[2]), I(b[2]), self.A["blob_pink"], name="!!blobB")]

    cube_names = CUBES

    def cube_ratio(self, i):
        return CUBE_R

    def cubes(self, spots):
        return [image(I(x), I(y), I(w), I(w * self.cube_ratio(i)), self.A[self.cube_names[i]], name=f"!!cube{i}", rot=rot)
                for i, (x, y, w, rot) in enumerate(spots)]

    def panel(self, x, y, w, h, shape="round"):
        if shape == "oval":
            e = oval(I(x), I(y), I(w), I(h), name="!!panel")
            e.update(grad=self.grad, grad_angle=40, shadow=self.sh_panel)
            return [e]
        full = shape == "full"
        return [rect(I(x), I(y), I(w), I(h), grad=self.grad, grad_angle=40, radius=0 if shape in ("full", "band") else I(0.35),
                     shadow=None if full or shape == "band" else self.sh_panel, name="!!panel")]

    def card(self, x, y, w, h, name, fill="#ffffff"):
        return [rect(I(x), I(y), I(w), I(h), fill=fill, radius=I(0.22), shadow=self.sh_card, name=name)]

    def label(self, txt, x=0.9, y=1.35, w=6, color=None, align="left"):
        return self.T(x, y, w, 0.3, txt, 13, "kicker", color=color or self.a1, bold=True, caps=True, spacing_chars=2,
                      font=self.head, align=align, name="!!label", min_size=10)

    def title2(self, a, b, x=0.9, y=1.75, w=6, h=1.6, size=44, inline=False, color=None, accent=None):
        b = f"[[{accent or self.a2}|{b}]]"
        paras = [f"{a} {b}"] if inline else [a, b]
        return self.T(x, y, w, h, paras, size, "title", color=color or self.ink, bold=True, font=self.head, min_size=size * 0.6,
                      name="!!title")

    def title_md(self, t, x=0.9, y=1.75, w=11.4, h=0.85, size=38, color=None, accent=None, align="left", valign="top"):
        return self.T(x, y, w, h, t, size, "title", color=color or self.ink, accent=accent or self.a2, bold=True, font=self.head,
                      min_size=22, align=align, valign=valign, name="!!title")

    def sub(self, t, x=0.9, y=3.55, w=5.0, h=0.7, color=None, size=15, align="left"):
        on_dark = color == "#ffffff"   # trên nền tím: chữ nhấn cũng trắng (tím trên tím sẽ chìm)
        return self.T(x, y, w, h, t, size, "sub", color=color or self.mut, accent="#ffffff" if on_dark else self.a2,
                      min_size=11, align=align, name="!!sub")

    def dot(self, x, y, d, label="", name="", fill=None, color=None, size=None):
        els = [oval(I(x), I(y), I(d), I(d), fill=fill or self.a3, name=name)]
        if label:
            els.append(self.T(x, y, d, d, label, size or d * 30, "dot", color=color or self.ink, bold=True, font=self.head,
                              align="center", valign="middle"))
        return els

    def chap_label(self, chapter_id):
        i = self.ch_index.get(chapter_id, 0)
        t = self.doc["chapters"][i]["title"]
        return f"{i + 1:02d} · {t if len(t) <= 44 else t[:42].rsplit(' ', 1)[0] + '…'}"

    def chrome(self, idx, s):
        if not s["footer"]:
            return []
        dark = s["dark"]
        fc = "#ffffff" if dark else self.mut
        y = H - 24
        return [image(I(0.9), I(0.32), I(1.5), I(0.42), logo("slimai_white" if dark else "slimai"), self.b["site"],
                      fit="contain-left", name="!!logo"),
                text(I(0.9), y, 200, 12, self.b["slogan"], 7.5, "footer", color=fc, bold=True, font=SANS),
                text(W / 2 - 60, y, 120, 12, self.b["site_label"], 7.5, "footer", color=fc, align="center", link=self.b["site"], font=SANS),
                text(W - I(0.9) - 60, y, 60, 12, f"{idx + 1:02d}", 7.5, "footer", color=fc, align="right", bold=True, font=SANS)]

    # ---------------------------------------------------------- slide tự động
    def cover(self):
        d = self.doc
        words = d["title"].split()
        # ngắt 2 dòng cân nhau theo số ký tự (tránh dòng cuối trơ một chữ)
        cut = min(range(1, len(words)), key=lambda c: max(len(" ".join(words[:c])), len(" ".join(words[c:])))) if len(words) > 1 else 1
        a, b = " ".join(words[:cut]), " ".join(words[cut:])
        credit = self.b["credit"][d["credit"]]
        els = self.bg() + self.blobs((-2.5, 3.2, 6.5), (9.5, 3.0, 6)) + self.panel(8.4, -0.6, 5.6, 3.9)
        els += [self.T(9.6, 0.5, 3.4, 0.35, d.get("series") or "SlimAI", 14, "panel-k", color="#ffffff", bold=True, caps=True,
                       spacing_chars=2, font=self.head, name="!!panelK", min_size=9),
                self.T(9.6, 0.85, 3.3, 1.15, f"{len(d['chapters']):02d}", 60, "panel-n", color="#ffffff", bold=True, font=self.head, name="!!panelN"),
                self.T(9.6, 1.95, 3.3, 0.6, "chương nội dung", 15, "panel-l", color="#ffffff", name="!!panelText")]
        els += self.cubes(SPOTS["cover"])
        els += [self.T(0.9, 1.4, 6.6, 0.3, d["kicker"], 13, "kicker", color=self.a1, bold=True, caps=True, spacing_chars=2, font=self.head,
                       name="!!label"),
                self.T(0.9, 1.8, 7.0, 2.5, [a.upper(), f"[[{self.a2}|{b.upper()}]]"], 50, "cover-title", bold=True, font=self.head,
                       min_size=28, valign="middle", name="!!title"),
                self.sub(d["subtitle"], y=4.45, w=6.2, h=0.85),
                rect(I(0.9), I(5.5), I(1.95), I(0.54), fill=self.a1, radius=I(0.27), name="!!btn"),
                self.T(0.9, 5.5, 1.95, 0.54, "Bắt đầu  →", 14, "button", color="#ffffff", bold=True, align="center", valign="middle",
                       name="!!btnText"),
                self.T(0.9, 6.3, 6.6, 0.5, [f"{credit} · {self.b['site_label']}", d.get("source_credit") or ""], 10, "cover-credit",
                       color=self.mut, min_size=8)]
        self.add("cover", els, title=d["title"], notes=d["subtitle"], bg="#f6f3ff")

    def agenda(self):
        chs = self.doc["chapters"]
        n = len(chs)
        els = self.bg() + self.blobs((-2.8, -2.5, 6.5), (2.0, 4.2, 6)) + self.panel(5.1, 0.85, 7.35, 5.8) + self.cubes(SPOTS["agenda"])
        els += [self.label("Nội dung"), self.title2(f"{n} chương", "của tài liệu", w=4.0),
                self.sub(["Lộ trình từ vấn đề", "đến hành động."], w=3.6)]
        rh = min(0.86, 5.0 / n)
        for k, c in enumerate(chs):
            y = 1.3 + k * rh
            els += [self.T(5.65, y, 0.8, rh * 0.62, f"{k + 1:02d}", 24, "agenda-num", color="#ffffff", bold=True, font=self.head, valign="middle",
                           name=f"!!rowNum{k}"),
                    self.T(6.55, y, 5.6, rh * 0.62, c["title"], 17, "agenda", color="#ffffff", bold=True, valign="middle", min_size=12,
                           name=f"!!rowTitle{k}")]
            if k < n - 1:
                els.append(rect(I(5.65), I(y + rh * 0.8), I(6.3), 0.6, fill=mix(self.a2, "#ffffff", 0.45), name=f"!!rule{k}"))
        self.add("agenda", els, title="Nội dung chính", notes="Lộ trình của bài trình bày.", bg="#f6f3ff")

    def section(self, i, ch):
        els = self.panel(0, 0, 13.333, 7.5, "full") + self.blobs((-2.2, 3.4, 6.5), (8.8, -2.6, 6.5))
        els += self.cubes(SECTION_SPOTS[i % len(SECTION_SPOTS)])
        els += [self.label(f"Chương {i + 1:02d}", y=1.45, color="#ffffff"),
                self.T(0.75, 1.6, 4.5, 2.35, f"{i + 1:02d}", 130, "section-num", color="#ffffff", bold=True, font=self.head, name="!!bigNum"),
                self.T(0.9, 3.95, 8.2, 1.5, ch["title"], 40, "section-title", color="#ffffff", bold=True, font=self.head, min_size=24,
                       name="!!title"),
                self.sub(ch["lead"], y=5.55, w=7.6, h=0.7, color="#ffffff", size=16)]
        self.add("section", els, dark=True, chapter=ch["id"], title=ch["title"], notes=ch["lead"], bg=self.dark_bg)

    def _panel_list(self, items, role="body", check=True):
        """Danh sách chữ trắng trong panel phải (x 5.4–12.55in), dấu ✓ trong viên trắng."""
        n = max(1, len(items))
        rh = min(1.0, 5.0 / n)
        els = []
        for k, it in enumerate(items):
            y = 1.3 + k * rh
            if check:
                els += self.dot(5.9, y + (rh * 0.7 - 0.38) / 2, 0.38, "✓", name=f"!!li{k}", fill="#ffffff", color=self.a1, size=14)
            els.append(self.T(6.5, y, 5.75, rh * 0.7, it, 20, role, color="#ffffff", bold=True, valign="middle", min_size=14,
                              name=f"!!rowTitle{k}"))
            if k < n - 1:
                els.append(rect(I(5.9), I(y + rh * 0.85), I(6.3), 0.6, fill=mix(self.a2, "#ffffff", 0.45), name=f"!!rule{k}"))
        return els

    def summary(self):
        chs = self.doc["chapters"]
        els = self.bg() + self.blobs((-2.8, -2.5, 6.5), (2.0, 4.2, 6)) + self.panel(5.4, 0.85, 7.15, 5.8) + self.cubes(SPOTS["agenda"])
        els += [self.label("Tổng kết"), self.title2("Điểm chính", "cần nhớ", w=4.4, h=1.4, size=40),
                self.sub("Mỗi chương một ý quan trọng nhất.", y=3.35, w=3.8, h=0.6)]
        els += self._panel_list([c["summary"][0] if c["summary"] else c["lead"] for c in chs], role="summary")
        self.add("summary", els, title="Điểm chính cần nhớ", notes="Nhắc lại thông điệp chính của từng chương.", bg="#f6f3ff")

    def course(self):
        c = self.b["course"]
        url = c["url"]
        qr = qr_png(url, self.work / "qr-khoa-hoc.png")
        els = self.bg() + self.blobs((-2.5, 3.2, 6.5), (9.5, 3.0, 6)) + self.panel(8.0, 0.85, 4.6, 5.8) + self.cubes(SPOTS["course"])
        els += [self.label("Bước tiếp theo"), self.title2("Để AI", "làm việc thay bạn", w=6.6, h=1.6, size=46),
                self.T(0.9, 3.6, 6.4, 0.45, c["name"], 20, "course-title", bold=True, font=self.head, min_size=14),
                self.T(0.9, 4.1, 6.2, 0.85, c["audience"], 14, "course-aud", color=self.mut, min_size=10),
                rect(I(0.9), I(5.2), I(2.6), I(0.56), fill=self.a1, radius=I(0.28), name="!!btn"),
                self.T(0.9, 5.2, 2.6, 0.56, "Xem khoá học  →", 15, "button", color="#ffffff", bold=True, align="center", valign="middle",
                       link=url, name="!!btnText"),
                self.T(0.9, 5.9, 5, 0.3, c["url_label"], 12, "url", color=self.a1, link=url),
                rect(I(8.85), I(1.6), I(2.9), I(2.9), fill="#ffffff", radius=I(0.2), name="!!qrCard"),
                image(I(9.05), I(1.8), I(2.5), I(2.5), qr, url, fit="contain", name="!!qr"),
                self.T(8.5, 4.85, 3.6, 0.9, ["Quét mã để xem", "lộ trình khoá học"], 18, "qr", color="#ffffff", bold=True, font=self.head,
                       align="center", name="!!panelText")]
        self.add("course", els, title=c["name"], notes="Giới thiệu khoá học AI Agent cho người đi làm.", bg="#f6f3ff")

    def ecosystem(self):
        b = self.b
        els = self.bg() + self.blobs((-2.8, -2.5, 6.5), (9.0, 3.6, 6)) + self.cubes(SPOTS["eco"])
        els += [image(I(4.67), I(0.7), I(4.0), I(1.3), logo("slimai"), b["site"], fit="contain", name="!!logo"),
                self.T(1.5, 2.05, 10.333, 0.4, self.slogan(), 16, "slogan", bold=True, font=self.head, align="center")]
        for k, e in enumerate(b["ecosystem"]):
            x, y, w = 1.25 + k * 3.75, 2.85, 3.45
            els += self.card(x, y, w, 2.45, f"!!card{k}")
            els += [image(I(x + 0.3), I(y + 0.3), I(2.0), I(0.55), logo(e["key"]), e["link"], fit="contain-left", name=f"!!ecoLogo{k}"),
                    self.T(x + 0.3, y + 1.0, w - 0.6, 0.3, e["label"], 13, "eco-url", color=self.a1, bold=True, link=e["link"]),
                    self.T(x + 0.3, y + 1.38, w - 0.6, 0.9, e["desc"], 13, "eco-desc", color=self.mut, min_size=10)]
        els.append(self.T(0, 5.55, 13.333, 0.3, "Theo dõi SlimAI", 13, "follow", color=self.a1, bold=True, caps=True,
                          spacing_chars=2, font=self.head, align="center"))
        n, dd, gap = len(b["social"]), 0.5, 0.5
        x0 = (13.333 - (n * dd + (n - 1) * gap)) / 2
        for k, s in enumerate(b["social"]):
            els.append(image(I(x0 + k * (dd + gap)), I(6.0), I(dd), I(dd), self.social[s["key"]], s["link"], fit="contain",
                             name=f"!!social{k}"))
        self.add("eco", els, title="Hệ sinh thái SlimAI", notes="Kênh và sản phẩm của SlimAI.", bg="#f6f3ff")

    # ---------------------------------------------------------- slide nội dung
    def content(self, s, chapter_id):
        from thiet_ke_slide import fn_ok

        lay = s["layout"] if fn_ok(s) and hasattr(self, f"l_{s['layout']}") else "bullets"
        if lay == "bullets" and s.get("image_id") in self.images:
            lay = "image"
        els, dark = getattr(self, f"l_{lay}")(s, self.chap_label(chapter_id))
        self.add(lay, els, chapter=chapter_id, title=s["title"], notes=s.get("notes") or "", dark=dark,
                 bg=self.dark_bg if dark else "#f6f3ff")

    def _head(self, s, lab, spots, blobs=((8.5, -2.8, 6.5), (-2.5, 3.5, 6))):
        """Nền sáng + tiêu đề một dòng ở trên; trả về (phần tử, y bắt đầu nội dung)."""
        els = self.bg() + self.blobs(*blobs)
        tail = [self.label(lab, w=10), self.title_md(s["title"])]
        top = 2.75
        if s.get("subtitle"):
            tail.append(self.sub(s["subtitle"], y=2.55, w=10.5, h=0.4))
            top = 3.1
        return els, tail, top

    def l_bullets(self, s, lab):
        els = self.bg() + self.blobs((-2.8, -2.5, 6.5), (2.0, 4.2, 6)) + self.panel(5.4, 0.85, 7.15, 5.8) + self.cubes(SPOTS["bullets"])
        els += [self.label(lab, w=4.3), self.title_md(s["title"], w=4.3, h=2.4, size=36)]
        if s.get("subtitle"):
            els.append(self.sub(s["subtitle"], y=4.3, w=4.0, h=1.0))
        els += self._panel_list(s.get("bullets") or [s.get("caption") or ""])
        return els, False

    def l_cards(self, s, lab):
        els, tail, top = self._head(s, lab, SPOTS["band"], blobs=((-2.8, -2.5, 6.5), (8.0, -2.0, 6)))
        els += self.panel(0, 4.5, 13.333, 2.2, "band") + self.cubes(SPOTS["band"]) + tail
        cards = (s.get("cards") or [])[:4]
        n = max(1, len(cards))
        gap = 0.3
        cw = (11.55 - gap * (n - 1)) / n
        ch = 6.25 - top
        for k, c in enumerate(cards):
            x = 0.9 + k * (cw + gap)
            els += self.card(x, top, cw, ch, f"!!card{k}")
            els += self.dot(x + 0.3, top + 0.3, 0.75, c.get("icon") or "•", name=f"!!dot{k}", size=20)
            els += [self.T(x + 0.3, top + 1.2, cw - 0.6, 0.45, c["title"], 19, "card-title", bold=True, font=self.head, min_size=14,
                           name=f"!!cardTitle{k}"),
                    self.T(x + 0.3, top + 1.7, cw - 0.6, ch - 1.9, c["text"], 15, "card-text", color=self.mut, min_size=11,
                           name=f"!!cardText{k}")]
        return els, False

    def l_steps(self, s, lab):
        steps = (s.get("steps") or [])[:5]
        self._n_steps = getattr(self, "_n_steps", 0) + 1
        if self._n_steps % 2 == 1:      # bậc thang: cột 3D trong panel trái, danh sách bên phải
            n = len(steps)
            els = self.bg() + self.blobs((8.5, -2.8, 6.5), (-2.5, 3.5, 6)) + self.panel(0.7, 1.0, 7.3, 5.6) + self.cubes(SPOTS["panelL"])
            gw = 6.6 / n
            bw = min(1.25, gw * 0.84)
            for k in range(n):
                idx = min(4, round(k * 4 / max(1, n - 1))) if n > 1 else 2
                bh = bw * (422 + idx * 105) / 433          # đúng tỉ lệ ảnh bar{idx}.png (433 x 422…842 px)
                x = 1.0 + k * gw + (gw - bw) / 2
                els.append(image(I(x), I(6.25 - bh), I(bw), I(bh), self.A[f"bar{idx}"], name=f"!!bar{k}"))
                els.append(self.T(x, 6.25 - bh - 0.55, bw, 0.45, f"{k + 1:02d}", 24, "bar-num", color="#ffffff", bold=True, font=self.head,
                                  align="center", name=f"!!barNum{k}"))
            els += [self.label(lab.split(" · ")[0].join(["Chương ", ""]), x=8.6, w=4.4), self.title_md(s["title"], x=8.6, w=4.4, h=1.45, size=34)]
            rh = min(0.78, 3.65 / max(1, n))
            for k, st in enumerate(steps):
                y = 3.3 + k * rh
                els += [self.T(8.6, y, 4.4, 0.3, f"[[{self.a1}|{k + 1:02d}]]  {st['title']}", 15, "step-title", bold=True, min_size=11,
                               name=f"!!lv{k}"),
                        self.T(8.6, y + 0.3, 4.4, rh - 0.33, st["text"], 12, "step-text", color=self.mut, min_size=9, name=f"!!lvSub{k}")]
            return els, False
        els, tail, top = self._head(s, lab, SPOTS["band"], blobs=((-2.8, -2.5, 6.5), (8.0, -2.0, 6)))
        els += self.panel(0, 4.35, 13.333, 2.35, "band") + self.cubes(SPOTS["band"]) + tail
        n = max(1, len(steps))
        gap = 0.17
        cw = (11.55 - gap * (n - 1)) / n
        top = max(top, 3.2)
        for k, st in enumerate(steps):
            x = 0.9 + k * (cw + gap)
            els += self.card(x, top, cw, 6.3 - top, f"!!card{k}")
            last = k == n - 1
            els += self.dot(x + 0.25, top + 0.28, 0.7, str(k + 1), name=f"!!dot{k}", fill=self.a1 if last else self.a3,
                            color="#ffffff" if last else self.ink, size=22)
            els += [self.T(x + 0.25, top + 1.15, cw - 0.4, 0.45, st["title"], 16, "step-title", bold=True, font=self.head, min_size=12,
                           name=f"!!cardTitle{k}"),
                    self.T(x + 0.25, top + 1.62, cw - 0.45, 6.15 - top - 1.62, st["text"], 13, "step-text", color=self.mut, min_size=10,
                           name=f"!!cardText{k}")]
        return els, False

    def l_stats(self, s, lab):
        stats = (s.get("stats") or [])[:3]
        n = max(1, len(stats))
        els = self.panel(0, 0, 13.333, 7.5, "full") + self.blobs((-2.0, -2.5, 6.5), (8.5, 3.5, 6.5)) + self.cubes(SPOTS["full"])
        els += [self.label(lab, x=0, w=13.333, color="#ffffff", align="center"),
                self.title_md(s["title"], x=1.2, y=1.75, w=10.93, h=1.0, size=36, color="#ffffff", accent="#ffffff", align="center")]
        gap = 0.35
        cw = min(3.6, (11.0 - gap * (n - 1)) / n)
        x0 = (13.333 - (n * cw + (n - 1) * gap)) / 2
        for k, st in enumerate(stats):
            x = x0 + k * (cw + gap)
            els += self.card(x, 3.05, cw, 2.55, f"!!card{k}")
            els += [self.T(x + 0.3, 3.3, cw - 0.6, 1.1, st["value"], 54, "stat-value", color=self.a1, bold=True, font=self.head, min_size=30,
                           name=f"!!statValue{k}"),
                    self.T(x + 0.3, 4.45, cw - 0.6, 0.95, st["label"], 14, "stat-label", color=self.mut, min_size=10, name=f"!!statLabel{k}")]
        if s.get("subtitle"):
            els.append(self.sub(s["subtitle"], x=1.2, y=5.95, w=10.93, h=0.45, color="#ffffff", size=14, align="center"))
        return els, True

    def l_compare(self, s, lab):
        els, tail, top = self._head(s, lab, SPOTS["compare"])
        top = max(top, 2.95)
        els += self.panel(6.95, top - 0.2, 5.6, 6.6 - top + 0.2) + self.cubes(SPOTS["compare"]) + tail
        L, R = s["left"], s["right"]
        els += self.card(0.9, top, 5.35, 6.4 - top, "!!card0")
        els += [self.T(1.25, top + 0.3, 4.6, 0.4, L["title"], 20, "compare-title", color=self.mut, bold=True, font=self.head, min_size=14,
                       name="!!cardTitle0"),
                self.T(1.25, top + 0.85, 4.65, 6.15 - top - 0.85, L["items"], 19, "compare-item", bullet=self.mut, space=6, min_size=12,
                       name="!!cardText0"),
                self.T(7.35, top + 0.1, 4.8, 0.4, R["title"], 20, "compare-title", color="#ffffff", bold=True, font=self.head, min_size=14,
                       name="!!cardTitle1"),
                self.T(7.35, top + 0.65, 4.85, 6.3 - top - 0.65, R["items"], 19, "compare-item", color="#ffffff", bullet="#ffffff",
                       space=6, min_size=12, bold=True, name="!!cardText1")]
        mid = top + (6.4 - top) / 2 - 0.31
        els += self.dot(6.27, mid, 0.62, "→", name="!!arrowDot", fill=self.a3, size=20)
        return els, False

    def l_quote(self, s, lab):
        els = self.panel(0, 0, 13.333, 7.5, "full") + self.blobs((-2.0, -2.5, 6.5), (8.5, 3.5, 6.5)) + self.cubes(SPOTS["full"])
        els += [self.label(s["title"].replace("*", ""), x=1.0, w=11.333, color="#ffffff", align="center"),
                self.T(5.97, 1.4, 1.4, 1.45, "“", 80, "quote-mark", color="#ffffff", bold=True, font=self.head, align="center", name="!!quoteIcon"),
                self.T(1.4, 2.85, 10.533, 2.3, s["quote"], 40, "quote", color="#ffffff", bold=True, font=self.head, align="center",
                       valign="middle", min_size=20, name="!!title")]
        if s.get("by"):
            els.append(self.sub(f"— {s['by']}", x=1.5, y=5.25, w=10.333, h=0.4, color="#ffffff", size=14, align="center"))
        return els, True

    def l_prompt(self, s, lab):
        els, tail, top = self._head(s, lab, SPOTS["table"])
        h = 5.0 - top + (0 if s.get("caption") else 1.2)
        box = rect(I(0.9), I(top), I(11.55), I(h), fill=mix(self.ink, self.a5, 0.35), radius=I(0.3), shadow=self.sh_panel, name="!!panel")
        els += [box] + self.cubes(SPOTS["table"]) + tail
        els += [self.T(1.3, top + 0.3, 6, 0.3, "Prompt mẫu", 12, "prompt-label", color=self.a3, bold=True, caps=True, spacing_chars=2,
                       font=self.head),
                self.T(1.3, top + 0.75, 10.75, h - 1.0, s["prompt"], 19, "prompt", color="#f4f1ff", font=MONO, min_size=12)]
        if s.get("caption"):
            els.append(self.sub(s["caption"], y=top + h + 0.25, w=11.4, h=0.7))
        return els, False

    def l_image(self, s, lab):
        els = self.bg() + self.blobs((8.5, -2.8, 6.5), (-2.5, 3.5, 6)) + self.panel(7.0, 1.0, 5.6, 5.6) + self.cubes(SPOTS["image"])
        els += [self.label(lab, w=5.6), self.title_md(s["title"], w=5.6, h=1.5, size=34)]
        y = 3.35
        if s.get("caption"):
            els.append(self.sub(s["caption"], y=y, w=5.6, h=0.8, color=self.a1, size=16))
            y += 0.95
        if s.get("bullets"):
            els.append(self.T(0.9, y, 5.6, 6.4 - y, s["bullets"], 19, "side", bullet=self.a1, space=6, min_size=11))
        pic = self.img(s["image_id"], I(7.25), I(1.25), I(5.1), I(5.1), name="!!photo")
        for p in pic:
            p["radius"] = I(0.22)
        return els + pic, False

    def l_table(self, s, lab):
        els, tail, top = self._head(s, lab, SPOTS["table"])
        els += self.cubes(SPOTS["table"]) + tail
        header, rows = s["header"][:3], [r[:3] for r in (s.get("rows") or [])[:6]]
        cols = len(header)
        top = max(top, 2.7)
        els += self.card(0.9, top, 11.55, 6.45 - top, "!!card0")
        els.append(rect(I(1.15), I(top + 0.25), I(11.05), I(0.5), fill=self.a1, radius=I(0.12), name="!!panel"))
        cw = 11.05 / cols
        for j, hd in enumerate(header):
            els.append(self.T(1.35 + j * cw, top + 0.25, cw - 0.3, 0.5, hd, 14, "th", color="#ffffff", bold=True, valign="middle", min_size=10))
        rh = min(0.62, (6.2 - top - 0.85) / max(1, len(rows)))
        for i, r in enumerate(rows):
            y = top + 0.85 + i * rh
            for j, cell in enumerate(r + [""] * (cols - len(r))):
                els.append(self.T(1.35 + j * cw, y, cw - 0.3, rh, cell, 14, "td", valign="middle", min_size=10,
                                  bold=(j == 0)))
            if i < len(rows) - 1:
                els.append(rect(I(1.15), I(y + rh), I(11.05), 0.6, fill=mix(self.a3, "#ffffff", 0.4)))
        return els, False

    def l_hub(self, s, lab):
        els, tail, top = self._head(s, lab, SPOTS["full"])
        cards = (s.get("cards") or [])[:4]
        cx, cy = 6.667, top + (6.45 - top) / 2
        els += self.panel(cx - 1.25, cy - 1.25, 2.5, 2.5, "oval") + self.cubes(SPOTS["table"]) + tail
        els.append(self.T(cx - 1.0, cy - 0.5, 2.0, 1.0, s.get("caption") or "", 17, "hub-center", color="#ffffff", bold=True, font=self.head,
                          align="center", valign="middle", min_size=11))
        cw, chh = 3.7, 1.35
        spots = [(0.9, top), (12.45 - cw, top), (0.9, 6.45 - chh), (12.45 - cw, 6.45 - chh)]
        for k, c in enumerate(cards):
            x, y = spots[k]
            left = x < cx
            els.append(line(I(x + cw if left else x), I(y + chh / 2), I(cx + (-1.2 if left else 1.2)), I(cy + (-0.35 if y < cy else 0.35)),
                            self.a3, 1.2))
            els += self.card(x, y, cw, chh, f"!!card{k}")
            els += [self.T(x + 0.25, y + 0.18, cw - 0.9, 0.4, c["title"], 16, "hub-title", bold=True, font=self.head, min_size=11,
                           name=f"!!cardTitle{k}"),
                    self.T(x + cw - 0.75, y + 0.15, 0.5, 0.4, f"{k + 1:02d}", 15, "hub-num", color=self.a1, bold=True, font=self.head, align="right"),
                    self.T(x + 0.25, y + 0.62, cw - 0.5, chh - 0.72, c["text"], 12.5, "hub-text", color=self.mut, min_size=9,
                           name=f"!!cardText{k}")]
        return els, False
