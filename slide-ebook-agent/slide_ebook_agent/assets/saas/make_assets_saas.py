"""Bộ ảnh cho phong cách 'saas' (xanh dương, giống landing mặc định): nền sáng có quầng xanh, quầng sáng, nền navy có vệt sáng,
6 thẻ giao diện nhỏ kiểu kính (thay khối lập phương). Chạy lại: .venv/bin/python slide_ebook_agent/assets/saas/make_assets_saas.py"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

OUT = Path(__file__).resolve().parent
W, H = 1920, 1080


def lin(c0, c1, w, h):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / (h - 1)
        d.line([(0, y), (w, y)], fill=tuple(int(c0[i] * (1 - t) + c1[i] * t) for i in range(3)))
    return im


def glow(im, cx, cy, r, color, alpha, blur):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([cx - r, cy - r, cx + r, cy + r], fill=color + (alpha,))
    lay = lay.filter(ImageFilter.GaussianBlur(blur))
    return Image.alpha_composite(im.convert("RGBA"), lay)


def rings(im, cx, cy, radii, color, alpha):
    lay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    for r in radii:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color + (alpha,), width=2)
    return Image.alpha_composite(im.convert("RGBA"), lay)


# nền sáng
bg = lin((255, 255, 255), (234, 241, 255), W, H)
bg = glow(bg, 120, 1080, 520, (122, 165, 255), 150, 160)
bg = glow(bg, 1820, 1000, 520, (143, 220, 255), 150, 160)
bg = rings(bg, W // 2, 2100, [1250, 1450, 1650], (47, 107, 255), 26)
bg.convert("RGB").save(OUT / "bg.png")

# quầng sáng (PNG trong suốt)
for name, col in (("orb_a", (91, 140, 255)), ("orb_b", (56, 198, 244))):
    s = 600
    im = Image.new("RGBA", (s, s), col + (0,))
    px = im.load()
    for y in range(s):
        for x in range(s):
            dd = math.hypot(x - s / 2, y - s / 2) / (s / 2)
            px[x, y] = col + (int(max(0.0, 1 - dd) ** 2.0 * 110),)
    im.save(OUT / f"{name}.png")

# nền navy có quầng + vệt sáng (slide mở chương, số liệu, trích dẫn)
dk = lin((18, 35, 94), (8, 17, 47), W, H)
dk = glow(dk, 1350, 380, 420, (56, 140, 255), 150, 170)
dk = glow(dk, 1700, 180, 260, (64, 220, 255), 120, 120)
beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
ImageDraw.Draw(beam).polygon([(1180, -100), (1420, -100), (980, 1200), (740, 1200)], fill=(120, 190, 255, 60))
dk = Image.alpha_composite(dk.convert("RGBA"), beam.filter(ImageFilter.GaussianBlur(40)))
stars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(stars)
for x, y in ((380, 300), (1340, 650), (770, 860), (1630, 270), (190, 760), (1050, 140), (560, 520)):
    sd.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 255, 255, 120))
Image.alpha_composite(dk, stars).convert("RGB").save(OUT / "dark.png")

# thẻ giao diện kiểu kính — vẽ bằng HTML trong Chromium (nền trong suốt)
CARDS = {
    "w_chart": '<div class="c" style="width:300px;height:220px;padding:26px 24px;display:flex;align-items:flex-end;gap:12px">'
               + "".join(f'<span style="flex:1;height:{h}%;border-radius:8px 8px 3px 3px;background:linear-gradient(180deg,{c})"></span>'
                         for h, c in ((42, "#a9c3ff,#7FA6FF"), (68, "#4b7dff,#1F5BFF"), (52, "#a9c3ff,#7FA6FF"), (88, "#4b7dff,#1F5BFF"), (64, "#a9c3ff,#7FA6FF"))) + "</div>",
    "w_tile": '<div style="width:150px;height:150px;border-radius:40px;background:linear-gradient(135deg,#5b8cff,#2f6bff 55%,#38c6f4);'
              'box-shadow:0 30px 50px -20px rgba(47,107,255,.85),inset 0 2px 0 rgba(255,255,255,.35);display:grid;place-items:center">'
              '<svg width="70" height="70" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6 9 17l-5-5"/></svg></div>',
    "w_stat": '<div class="c" style="width:260px;padding:22px 24px"><div style="display:flex;gap:12px;align-items:center">'
              '<span style="width:46px;height:46px;border-radius:14px;background:linear-gradient(135deg,#5b8cff,#2f6bff);display:grid;place-items:center">'
              '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.4" stroke-linecap="round"><path d="M22 7 13.5 15.5l-5-5L2 17"/><path d="M16 7h6v6"/></svg></span>'
              '<div style="flex:1"><i style="display:block;height:10px;width:70%;border-radius:5px;background:#dfe6f5"></i>'
              '<i style="display:block;height:16px;width:50%;border-radius:5px;background:#0d1838;margin-top:9px"></i></div></div></div>',
    "w_list": '<div class="c" style="width:270px;padding:24px">' + "".join(
              '<div style="display:flex;gap:12px;align-items:center;margin:9px 0"><span style="width:24px;height:24px;border-radius:50%;background:#2f6bff;display:grid;place-items:center">'
              '<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="3.5" stroke-linecap="round"><path d="M20 6 9 17l-5-5"/></svg></span>'
              f'<i style="height:10px;width:{w}%;border-radius:5px;background:#dfe6f5"></i></div>' for w in (78, 60, 70)) + "</div>",
    "w_blur": '<div style="width:150px;height:150px;border-radius:40px;background:linear-gradient(135deg,#7aa5ff,#2f6bff);filter:blur(7px);opacity:.75"></div>',
    "w_dot": '<div style="width:130px;height:130px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ffffff,#bfe6ff 45%,#38c6f4);filter:blur(5px);opacity:.8"></div>',
}
CSS = (".c{background:rgba(255,255,255,.92);border:1.5px solid #fff;border-radius:26px;"
       "box-shadow:0 34px 60px -26px rgba(31,73,170,.55),0 0 0 1px rgba(214,226,250,.8)}")
if __name__ == "__main__":
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        try:
            b = p.chromium.launch()
        except Exception:
            b = p.chromium.launch(channel="chrome")
        pg = b.new_page(device_scale_factor=2)
        for name, inner in CARDS.items():
            pg.set_content(f'<html><body style="margin:0;background:transparent"><style>{CSS}</style>'
                           f'<div id="w" style="display:inline-block;padding:50px">{inner}</div></body></html>')
            pg.locator("#w").screenshot(path=str(OUT / f"{name}.png"), omit_background=True)
        b.close()
    print(sorted(x.name for x in OUT.glob("*.png")))
