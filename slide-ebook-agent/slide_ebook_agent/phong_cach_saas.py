"""Phong cách 'saas' (xanh dương, đồng bộ với landing mặc định và ebook): dùng lại bố cục Retron nhưng đổi chất liệu —
nền sáng có quầng xanh/cyan, thẻ kính trắng bóng xanh, tiêu đề Be Vietnam Pro chữ nhấn xanh #2F6BFF,
panel gradient xanh→cyan, slide nền navy có quầng sáng và vệt sáng, thẻ giao diện nhỏ lơ lửng thay khối lập phương.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image

from phong_cach_retron import ASSETS as RETRON_ASSETS, DeckRetron, explicit_palette, hue, mix, tint
from thiet_ke_slide import H, W, image, rect

ASSETS = Path(__file__).resolve().parent / "assets" / "saas"

SAAS = {"name": "SaaS xanh dương", "reason": "Đồng bộ slide, ebook và landing: xanh dương #2F6BFF, cyan, navy",
        "primary": "#2F6BFF", "secondary": "#38C6F4", "deep": "#0D1838", "soft": "#EEF4FF", "ink": "#0D1838",
        "mosaic": ["#EEF4FF", "#BFD4FF", "#5B8CFF", "#2F6BFF", "#1D47C8"],
        # CSS thêm cho ebook (mẫu tai-lieu-slimai) để cùng chất liệu với slide/landing
        "ebook_css": (
            ":root{--navy:#0d1838;--ink:#1c2745;--muted:#5f6c8c;--line:#e4e9f5;--soft:#eef4ff;"
            "--grad:linear-gradient(90deg,#2f6bff,#5b8cff 45%,#38c6f4)}"
            "h1,h2,h3,h4{letter-spacing:-.01em}h2{font-weight:700}b,strong{color:#1d47c8}"
            ".box{border-radius:12pt!important;box-shadow:0 8pt 22pt -16pt rgba(31,73,170,.45)}"
            ".opener{border-radius:16pt!important;background:#08112f!important}.opener img{opacity:.95!important}"
            ".opener .num{color:#9cc4ff!important}"
            "table th{background:#2f6bff!important;color:#fff!important}"
            ".prompt{background:#0d1838!important;border-left-color:#38c6f4!important}"
            "figure img{border-radius:12pt!important;box-shadow:0 14pt 30pt -22pt rgba(31,73,170,.6)}")}

WIDGETS = ["w_chart", "w_tile", "w_stat", "w_list", "w_blur", "w_dot"]
SCALE = [1.1, 0.85, 1.35, 1.3, 0.8, 0.7]     # thẻ giao diện cần to hơn khối lập phương một chút để đọc được


class DeckSaas(DeckRetron):
    head = "Be Vietnam Pro"
    font_links = ["https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700&display=swap"]
    cube_names = WIDGETS

    def __init__(self, doc, work, images, social):
        super().__init__(doc, work, images, social)
        if not explicit_palette(doc):
            self.a1 = self.a2 = "#2F6BFF"
            self.a5, self.ink = "#1D47C8", "#0D1838"
            self.grad = ["#1D47C8", "#2F6BFF", "#38B8FF"]
            self.dark_bg = "#08112F"
            self.a3, self.a4 = "#DCE7FF", "#EEF3FF"
            self.mut = mix(self.ink, "#ffffff", 0.38)
            self.sh_panel, self.sh_card = "#1D47C8/0.30", "#1F49AA/0.16"
        out = work / "saas"
        out.mkdir(exist_ok=True)
        shift = (hue(self.a1) - hue("#6D4AEE")) % 1.0
        self.A.update({n: ASSETS / f"{n}.png" for n in WIDGETS})
        self.A.update({"bg": ASSETS / "bg.png", "blob_violet": ASSETS / "orb_a.png", "blob_pink": ASSETS / "orb_b.png",
                       "dark": ASSETS / "dark.png"})
        for i in range(5):   # cột bậc thang: xoay sắc độ bộ cột tím sang xanh
            self.A[f"bar{i}"] = tint(RETRON_ASSETS / f"bar{i}.png", out / f"bar{i}-{self.a1.lstrip('#')}.png", shift)
        self._ratio = {}
        for n in WIDGETS:
            with Image.open(self.A[n]) as im:
                self._ratio[n] = im.height / im.width

    def cube_ratio(self, i):
        return self._ratio[self.cube_names[i]]

    def cubes(self, spots):
        spots = [[x, y, w * SCALE[i], rot * 0.25] for i, (x, y, w, rot) in enumerate(spots)]
        return super().cubes(spots)

    def panel(self, x, y, w, h, shape="round"):
        if shape == "full":   # nền navy + quầng/vệt sáng (giống khối 'Điểm chính' của landing)
            return [rect(0, 0, W, H, fill=self.dark_bg, name="!!panel"), image(0, 0, W, H, self.A["dark"], name="!!glow")]
        return super().panel(x, y, w, h, shape)

    def cover(self):
        super().cover()
        d = self.doc
        words = d["title"].split()
        cut = min(range(1, len(words)), key=lambda c: max(len(" ".join(words[:c])), len(" ".join(words[c:])))) if len(words) > 1 else 1
        for e in self.slides[-1]["elements"]:
            if e.get("name") == "!!title":   # tiêu đề câu thường, nửa sau màu nhấn (như hero landing)
                e["paras"] = [" ".join(words[:cut]), f"[[{self.a2}|{' '.join(words[cut:])}]]"]
                e["size"] = e["min"] = round(e["size"] * 1.0, 2)
                e["min"] = round(e["size"] * 0.6, 2)
