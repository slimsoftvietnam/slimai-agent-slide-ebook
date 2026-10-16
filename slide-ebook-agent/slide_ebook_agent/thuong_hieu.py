"""Bộ nhận diện SlimAI: đọc từ skill tai-lieu-slimai (nguồn duy nhất), chuẩn bị icon PNG và mã QR."""
from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

def _skill_dir() -> Path:
    """Bộ nhận diện: SLIMAI_SKILL_DIR > ~/.claude/skills/tai-lieu-slimai > bản đóng kèm cạnh thư mục mã (gói skill độc lập)."""
    if os.environ.get("SLIMAI_SKILL_DIR"):
        return Path(os.environ["SLIMAI_SKILL_DIR"]).expanduser()
    home = Path.home() / ".claude/skills/tai-lieu-slimai"
    bundled = Path(__file__).resolve().parent.parent / "tai-lieu-slimai"
    return home if (home / "assets" / "brand.json").exists() or not bundled.exists() else bundled


SKILL_DIR = _skill_dir()
ASSETS = SKILL_DIR / "assets"
EBOOK_TEMPLATE = SKILL_DIR / "templates" / "ebook"


@lru_cache(maxsize=1)
def brand() -> dict:
    path = ASSETS / "brand.json"
    if not path.exists():
        raise SystemExit(f"Không thấy bộ nhận diện: {path}. Cài skill tai-lieu-slimai hoặc đặt SLIMAI_SKILL_DIR.")
    return json.loads(path.read_text())


def logo(key: str) -> Path:
    return ASSETS / brand()["logos"][key]["file"]


def hex_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def social_pngs(out_dir: Path, page) -> dict[str, Path]:
    """Chuyển icon SVG mạng xã hội sang PNG (PPTX không nhận SVG). `page` là trang Playwright đang mở."""
    out_dir.mkdir(parents=True, exist_ok=True)
    result = {}
    for s in brand()["social"]:
        target = out_dir / f"{s['key']}.png"
        if not target.exists():
            svg = (ASSETS / "logos" / f"{s['key']}.svg").read_text()
            if s.get("boxed"):
                inner = svg.replace("<svg ", '<svg fill="#fff" width="84" height="84" ', 1)
                html = (f'<div id="i" style="width:112px;height:112px;border-radius:24px;background:{s["color"]};'
                        f'display:flex;align-items:center;justify-content:center">{inner}</div>')
            else:
                inner = svg.replace("<svg ", f'<svg fill="{s["color"]}" width="112" height="112" ', 1)
                html = f'<div id="i" style="width:112px;height:112px">{inner}</div>'
            page.set_content(f'<html><body style="margin:0;background:transparent">{html}</body></html>')
            page.locator("#i").screenshot(path=str(target), omit_background=True)
        result[s["key"]] = target
    return result


def qr_png(url: str, target: Path) -> Path:
    import qrcode

    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        img = qrcode.make(url, box_size=12, border=1)
        img.save(target)
    return target
