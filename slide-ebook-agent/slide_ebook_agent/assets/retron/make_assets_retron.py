"""Asset phong cách Retron: khối lập phương tím bóng, cột 3D, nền, đốm màu."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

OUT = "assets2/"
SS = 3  # supersample
SHADOW_RGB = "4A2BC2"


def hexrgb(h):
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32)


def to_img(arr):
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8))


def poly_mask(W, H, pts):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon([tuple(p) for p in pts], fill=255)
    return np.array(m, np.float32) / 255


def lin_grad(W, H, p0, p1, c0, c1):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.array(p1, np.float32) - np.array(p0, np.float32)
    t = ((x - p0[0]) * d[0] + (y - p0[1]) * d[1]) / (d @ d)
    t = np.clip(t, 0, 1)[..., None]
    return hexrgb(c0) * (1 - t) + hexrgb(c1) * t


def round_mask(m, r):
    """Bo tròn góc lồi: làm mờ rồi cắt ngưỡng."""
    img = to_img(m * 255).filter(ImageFilter.GaussianBlur(r))
    a = np.array(img, np.float32) / 255
    return np.clip((a - 0.5) * 6 + 0.5, 0, 1)


def edge_line(W, H, p0, p1, width, blur):
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).line([tuple(p0), tuple(p1)], fill=255, width=width)
    return np.array(m.filter(ImageFilter.GaussianBlur(blur)), np.float32) / 255


def prism(name, s, height, pal, gloss=0.28, out_w=None):
    """Lăng trụ isometric đáy vuông cạnh s, cao `height` (đơn vị px trước supersample)."""
    s, height = s * SS, height * SS
    w, h = s * math.cos(math.radians(30)), s * 0.5
    pad = int(0.12 * s)
    W = int(2 * w + 2 * pad)
    H = int(2 * h + height + 2 * pad)
    cx, top = W / 2, pad
    T = np.array([cx, top]); R = np.array([cx + w, top + h])
    B = np.array([cx, top + 2 * h]); L = np.array([cx - w, top + h])
    dn = np.array([0, height])

    top_m = poly_mask(W, H, [T, R, B, L])
    left_m = poly_mask(W, H, [L, B, B + dn, L + dn])
    right_m = poly_mask(W, H, [B, R, R + dn, B + dn])
    sil = np.clip(top_m + left_m + right_m, 0, 1)
    sil_r = round_mask(sil, s * 0.035)

    col = np.zeros((H, W, 3), np.float32) + hexrgb(pal["left1"]) * 0.5 + hexrgb(pal["top1"]) * 0.5
    ctop = lin_grad(W, H, T, B, pal["top0"], pal["top1"])
    cleft = lin_grad(W, H, L, B + dn, pal["left0"], pal["left1"])
    cright = lin_grad(W, H, R, B + dn, pal["right0"], pal["right1"])
    for m, c in ((top_m, ctop), (left_m, cleft), (right_m, cright)):
        col = col * (1 - m[..., None]) + c * m[..., None]

    # bóng loáng: dải sáng chéo trên mặt trái và mặt trên
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    band = np.exp(-(((x - (cx - w * 0.45)) + (y - (top + h + height * 0.25)) * 0.35) ** 2) / (2 * (w * 0.16) ** 2))
    col += 255 * (band * left_m * gloss)[..., None]
    col += 255 * (top_m * 0.18 * np.exp(-((x - cx) ** 2 + (y - (top + h * 0.6)) ** 2) / (2 * (w * 0.5) ** 2)))[..., None]

    # viền sáng
    lw = max(2, int(s * 0.012))
    hl = np.zeros((H, W), np.float32)
    for a, b, k in ((L, B, 0.9), (B, R, 0.75), (B, B + dn, 0.65), (T, L, 0.55), (T, R, 0.45)):
        hl = np.maximum(hl, edge_line(W, H, a, b, lw, lw * 0.8) * k)
    col = col * (1 - hl[..., None]) + 255 * hl[..., None]

    rgba = np.zeros((H, W, 4), np.float32)
    rgba[..., :3] = col
    rgba[..., 3] = sil_r * 255
    img = Image.fromarray(rgba.clip(0, 255).astype(np.uint8))
    img = img.resize((W // SS, H // SS), Image.LANCZOS)
    img.save(OUT + name)
    return img


VIOLET = dict(top0="EDE6FF", top1="B9A3FF", left0="9B7DFB", left1="6E48EE", right0="6A44E6", right1="4524B8")
LAVENDER = dict(top0="FFFFFF", top1="EEE8FF", left0="F1ECFF", left1="D9CDFF", right0="CDBEFF", right1="A993FA")
DEEP = dict(top0="C9B8FF", top1="8E6CFA", left0="7651F2", left1="4E2BD0", right0="4A27C4", right1="2E1690")


def background():
    W, H = 1920, 1080
    arr = lin_grad(W, H, (0, 0), (W, H), "FAF9FE", "F1EEFB")
    to_img(arr).save(OUT + "bg.png")


def blob(name, color, size=900, alpha=0.7):
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    c = size / 2
    d = np.sqrt((x - c) ** 2 + (y - c) ** 2) / c
    a = np.clip(1 - d, 0, 1) ** 1.7 * alpha
    rgba = np.zeros((size, size, 4), np.float32)
    rgba[..., :3] = hexrgb(color)
    rgba[..., 3] = a * 255
    to_img(rgba).save(OUT + name)


def soft_shadow(name):
    W, H = 900, 260
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    a = np.clip(1 - d, 0, 1) ** 2 * 0.5
    rgba = np.zeros((H, W, 4), np.float32)
    rgba[..., :3] = hexrgb(SHADOW_RGB)
    rgba[..., 3] = a * 255
    to_img(rgba).save(OUT + name)


if __name__ == "__main__":
    import os
    os.makedirs(OUT, exist_ok=True)
    background()
    blob("blob_violet.png", "B9A3FF")
    blob("blob_pink.png", "E9C8FF")
    soft_shadow("shadow.png")
    c = prism("cube.png", 300, 300, VIOLET)
    c.convert("RGBa").filter(ImageFilter.GaussianBlur(7)).convert("RGBA").save(OUT + "cube_blur.png")
    prism("cube_lav.png", 300, 300, LAVENDER, gloss=0.1)
    prism("cube_deep.png", 300, 300, DEEP)
    # cột 3D cho 4 cấp độ
    for i, hh in enumerate([150, 300, 450, 600]):
        prism(f"bar{i}.png", 220, hh, LAVENDER if i % 2 == 0 else VIOLET, gloss=0.18 if i % 2 else 0.08)
    for f in sorted(os.listdir(OUT)):
        print(f, Image.open(OUT + f).size)
