"""Agent tạo Slide và Ebook: tài liệu thô -> bộ slide (.pptx sửa được + .pdf) và ebook (.pdf) đồng bộ, nhận diện SlimAI.

Lệnh:
  dan-y <nguồn...>   đọc nguồn + biên tập -> ban-thao.json / ban-thao.md, DỪNG để người dùng duyệt
  dung <thư-mục>     dựng ebook + slide từ ban-thao.json đã duyệt, rồi kiểm định
  chay <nguồn...>    chạy liền dan-y + dung (không dừng duyệt)
  landing <thư-mục>  làm landing page (một tệp HTML, có form đăng ký) từ ban-thao.json
  doc <nguồn...>     chỉ đọc nguồn -> nguon.md + anh/ (không cần API key; AI trong Claude Code/Codex tự soạn ban-thao.json)
  kiem <thư-mục>     kiểm tra ban-thao.json đúng cấu trúc, tạo lại ban-thao.md để duyệt
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
OUT_BASE = Path.cwd() / "output" / "slide-ebook"   # kết quả nằm trong thư mục đang làm việc
sys.path.insert(0, str(HERE))


def load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    for env in (Path.cwd() / ".env", ROOT / ".env"):   # thư mục làm việc trước, rồi thư mục dự án/skill
        if env.exists():
            load_dotenv(env)


def slug(text: str) -> str:
    t = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^A-Za-z0-9]+", "-", t).strip("-").lower()[:60] or "tai-lieu"


def file_title(text: str) -> str:
    t = unicodedata.normalize("NFD", text.replace("đ", "d").replace("Đ", "D"))
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^A-Za-z0-9 ,&()-]+", "", t).strip()[:80]


def launch(p):
    """Chromium của Playwright; nếu chưa cài (hoặc bị xoá khi dọn ổ đĩa) thì dùng Google Chrome có sẵn trên máy."""
    for kw in ({}, {"channel": "chromium"}, {"channel": "chrome"}):
        try:
            return p.chromium.launch(**kw)
        except Exception as exc:
            last = exc
    raise RuntimeError(f"Không mở được Chromium/Chrome: {last}. Cài bằng: .venv/bin/python -m playwright install chromium")


def step(msg: str) -> None:
    print(f"▶ {msg}", flush=True)


def cmd_dan_y(args) -> Path:
    import bien_tap
    import nguon

    first = args.nguon[0]
    work = Path(args.dau_ra or OUT_BASE / (args.ten or slug(Path(first).stem if "://" not in first else first)))
    work.mkdir(parents=True, exist_ok=True)
    step(f"Đọc {len(args.nguon)} nguồn → {work}")
    markdown, catalog = nguon.read_sources(args.nguon, work)
    print(f"  · {len(markdown):,} ký tự, {len(catalog)} ảnh minh hoạ")
    step(f"Biên tập bản thảo chung (mô hình {bien_tap.model()})")
    doc = bien_tap.draft(markdown, catalog, args.doi_tuong, args.ghi_cong, args.so_slide, args.mau)
    doc["course_enabled"] = not args.khong_khoa_hoc
    (work / "ban-thao.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    (work / "ban-thao.md").write_text(bien_tap.to_markdown(doc))
    if doc.get("palette"):
        from phong_cach_visual import palette_preview
        palette_preview([doc["palette"]], work / "bang-mau.png")
    n_sl = sum(len(c["slides"]) for c in doc["chapters"])
    print(f"  · «{doc['title']}»: {len(doc['chapters'])} chương, {len(doc['appendix'])} phụ lục, {n_sl} slide nội dung")
    for w in doc.get("warnings", []):
        print(f"  ⚠ {w}")
    p = doc.get("palette")
    print(f"\n🎨 Bảng màu {'theo yêu cầu' if args.mau else 'agent tự chọn'}: "
          + (f"{p['name']} — {p['reason']} (xem bang-mau.png)" if p else "màu SlimAI mặc định"))
    if doc.get("palette_question"):
        print(f"❓ Cần bạn trả lời: {doc['palette_question']}\n   Trả lời bằng: dung \"{work}\" --mau \"…\" hoặc --bang-mau \"5 mã màu\"")
    print(f"\nBản thảo để duyệt: {work / 'ban-thao.md'}\nSửa nội dung trong {work / 'ban-thao.json'} rồi chạy:\n"
          f"  slide_ebook_agent/.venv/bin/python slide_ebook_agent/agent.py dung \"{work}\"")
    return work


def cmd_dung(args, work: Path | None = None) -> int:
    from playwright.sync_api import sync_playwright

    import bien_tap
    import dung_ebook
    import kiem_dinh
    import thiet_ke_slide

    work = Path(work or args.thu_muc).expanduser().resolve()
    draft_path = work / "ban-thao.json"
    if not draft_path.exists():
        print(f"Không thấy {draft_path}. Chạy lệnh dan-y trước.", file=sys.stderr)
        return 2
    doc = json.loads(draft_path.read_text())
    if getattr(args, "khong_khoa_hoc", False):
        doc["course_enabled"] = False
    choice = getattr(args, "bang_mau", None)
    wish = getattr(args, "mau", None)
    if wish and not choice:   # đổi màu bằng lời: mô hình dựng bảng màu đầy đủ
        doc["palette"] = bien_tap.palette_from_wish(wish, doc["title"], doc.get("audience", ""))
        doc["color_wish"], doc["palette_question"] = wish, None
        draft_path.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    if choice:
        if re.fullmatch(r"(#[0-9a-fA-F]{6},){4}#[0-9a-fA-F]{6}", choice.replace(" ", "")):
            pri, sec, deep, soft, ink = choice.replace(" ", "").split(",")
            doc["palette"] = {"name": "Tuỳ chọn", "reason": "Người dùng chỉ định", "primary": pri, "secondary": sec,
                              "deep": deep, "soft": soft, "ink": ink, "mosaic": [soft, sec, pri, deep, ink]}
        else:
            print("--bang-mau phải là 5 mã màu 'chính,phụ,đậm,nền,chữ', vd '#0f7c86,#ef7d32,#0b2e36,#eef8f8,#11191b'.", file=sys.stderr)
            return 2
        draft_path.write_text(json.dumps(doc, ensure_ascii=False, indent=1))
    style = getattr(args, "phong_cach", "saas")
    saved_palette = doc.get("palette")
    if style in ("retron", "saas"):   # bảng màu của phong cách dùng cho cả slide lẫn ebook, trừ khi người dùng đã yêu cầu màu
        from phong_cach_retron import RETRON, explicit_palette
        from phong_cach_saas import SAAS
        if not explicit_palette(doc):
            doc["palette"] = SAAS if style == "saas" else RETRON
    if style == "visual" and not doc.get("palette"):
        print("  ⚠ Chưa có bảng màu: dùng màu SlimAI mặc định. Muốn đổi: thêm --mau \"mô tả màu\".", flush=True)
    catalog = json.loads((work / "anh.json").read_text()) if (work / "anh.json").exists() else []
    images = {c["id"]: work / "anh" / c["file"] for c in catalog}
    name = file_title(doc["title"])
    out = Path(args.xuat).expanduser() if getattr(args, "xuat", None) else work
    out.mkdir(parents=True, exist_ok=True)
    want_slide = args.loai in ("ca-hai", "slide")
    want_ebook = args.loai in ("ca-hai", "ebook")
    pptx = out / f"SlimAI - {name} (Slide).pptx"
    slide_pdf = out / f"SlimAI - {name} (Slide).pdf"
    ebook_pdf = out / f"SlimAI - {name} (Ebook).pdf"
    present = out / f"SlimAI - {name} (Trinh chieu).html"

    deck, overflow, ebook_info = None, [], None
    t0 = time.time()
    with sync_playwright() as p:
        browser = launch(p)
        page = browser.new_page()
        if want_slide:
            step("Thiết kế slide: dàn trang, đo chữ, đồng bộ cỡ chữ")
            shorten = lambda s, probs: bien_tap.shorten_slide(s, probs, doc["title"])
            res = thiet_ke_slide.render(doc, work, images, pptx, slide_pdf, page, shorten=shorten, style=style,
                                        out_html=present)
            doc, deck, overflow = res["doc"], res["deck"], res["overflow"]
            draft_path.write_text(json.dumps({**doc, "palette": saved_palette}, ensure_ascii=False, indent=1))   # lưu bản đã rút gọn, giữ màu gốc
            print(f"  · {len(deck.slides)} slide ({style}) → {pptx.name} + {slide_pdf.name} + {present.name}")
        browser.close()
    if want_ebook:
        step("Dựng ebook A4")
        ebook_info = dung_ebook.build(doc, work, catalog, ebook_pdf)
        print(f"  · {ebook_info['stdout'].splitlines()[-1] if ebook_info['stdout'] else ebook_pdf}")
    step("Kiểm định")
    report, n_err = kiem_dinh.check(doc, deck, overflow, ebook_pdf if want_ebook else None,
                                    slide_pdf if want_slide else None, pptx if want_slide else None,
                                    ebook_info, work / "qa")
    (work / "bao-cao-qa.md").write_text(report)
    print(report.split("## Đồng bộ")[0].strip())
    print(f"\nXong sau {time.time() - t0:.0f}s. Báo cáo: {work / 'bao-cao-qa.md'}")
    for f in (pptx, slide_pdf, present, ebook_pdf):
        if f.exists():
            print(f"  📄 {f}")
    return 1 if n_err else 0


def cmd_doc(args) -> int:
    import nguon

    first = args.nguon[0]
    work = Path(args.dau_ra or OUT_BASE / (args.ten or slug(Path(first).stem if "://" not in first else first)))
    work.mkdir(parents=True, exist_ok=True)
    step(f"Đọc {len(args.nguon)} nguồn → {work}")
    markdown, catalog = nguon.read_sources(args.nguon, work)
    print(f"  · {len(markdown):,} ký tự → {work / 'nguon.md'}; {len(catalog)} ảnh → {work / 'anh'} (danh mục anh.json)")
    print("Tiếp theo: soạn ban-thao.json theo cấu trúc trong slide_ebook_agent/BAN_THAO.md, rồi chạy lệnh kiem.")
    return 0


def check_draft(doc: dict) -> list[str]:
    """Kiểm cấu trúc bản thảo theo JSON Schema của bien_tap (kiểu, trường bắt buộc, enum)."""
    import bien_tap

    errs: list[str] = []

    def walk(v, sch, where):
        if "anyOf" in sch:
            if not any(not _errs(v, s) for s in sch["anyOf"]):
                errs.append(f"{where}: không khớp dạng cho phép")
            return
        t = sch.get("type")
        types = t if isinstance(t, list) else [t]
        py = {"object": dict, "array": list, "string": str, "boolean": bool, "null": type(None),
              "integer": int, "number": (int, float)}
        if t and not any(isinstance(v, py[x]) for x in types):
            errs.append(f"{where}: cần {'/'.join(types)}, đang là {type(v).__name__}")
            return
        if "enum" in sch and v not in sch["enum"]:
            errs.append(f"{where}: '{v}' không thuộc {sch['enum']}")
        if isinstance(v, dict) and "properties" in sch:
            for k in sch.get("required", []):
                if k not in v:
                    errs.append(f"{where}.{k}: thiếu")
            for k, s in sch["properties"].items():
                if k in v:
                    walk(v[k], s, f"{where}.{k}")
        if isinstance(v, list) and "items" in sch:
            for i, x in enumerate(v):
                walk(x, sch["items"], f"{where}[{i}]")

    def _errs(v, s):
        before = len(errs)
        walk(v, s, "")
        bad = len(errs) > before
        del errs[before:]
        return bad

    top = {k: doc[k] for k in bien_tap.OUTLINE["properties"] if k in doc}
    if top.get("palette") is None:   # null = dùng màu của phong cách (saas/retron)
        top.pop("palette", None)
    walk(top | {"chapters": [
        {k: c.get(k) for k in bien_tap.OUTLINE["properties"]["chapters"]["items"]["properties"]} for c in doc.get("chapters", [])]},
        {**bien_tap.OUTLINE, "required": [k for k in bien_tap.OUTLINE["required"] if k not in ("appendix_plan", "palette")]}, "ban_thao")   # appendix_plan chỉ dùng lúc soạn
    for i, c in enumerate(doc.get("chapters", [])):
        walk({k: c.get(k) for k in bien_tap.CHAPTER["properties"]}, bien_tap.CHAPTER, f"chapters[{i}]")
    walk({"items": doc.get("appendix", [])}, bien_tap.APPENDIX, "appendix")
    return errs


def cmd_kiem(args) -> int:
    import bien_tap

    work = Path(args.thu_muc).expanduser().resolve()
    p = work / "ban-thao.json"
    if not p.exists():
        print(f"Không thấy {p}.", file=sys.stderr)
        return 2
    try:
        doc = json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        print(f"ban-thao.json không phải JSON hợp lệ: {exc}", file=sys.stderr)
        return 2
    errs = check_draft(doc)
    ids = {c["id"] for c in (json.loads((work / "anh.json").read_text()) if (work / "anh.json").exists() else [])}
    used = set(re.findall(r'"image_id":\s*"([^"]+)"', json.dumps(doc, ensure_ascii=False)))
    errs += [f"image_id '{x}' không có trong anh.json" for x in sorted(used - ids)]
    if errs:
        print(f"❌ {len(errs)} lỗi cấu trúc:")
        for e in errs[:40]:
            print("  -", e)
        return 1
    (work / "ban-thao.md").write_text(bien_tap.to_markdown(doc))
    n = sum(len(c["slides"]) for c in doc["chapters"])
    print(f"✅ Bản thảo hợp lệ: {len(doc['chapters'])} chương, {n} slide nội dung, {len(doc.get('appendix', []))} phụ lục → {work / 'ban-thao.md'}")
    return 0


def cmd_landing(args) -> int:
    import landing_page

    work = Path(args.thu_muc).expanduser().resolve()
    draft_path = work / "ban-thao.json"
    if not draft_path.exists():
        print(f"Không thấy {draft_path}. Chạy lệnh dan-y trước.", file=sys.stderr)
        return 2
    doc = json.loads(draft_path.read_text())
    out_dir = Path(args.xuat).expanduser() if args.xuat else work
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"SlimAI - {file_title(doc['title'])} (Landing).html"
    step("Dựng landing page (phong cách mặc định saas-soft)")
    landing_page.build(doc, work, out, form_action=args.form_action or "", cta_text=args.cta or "")
    print(f"  📄 {out} ({out.stat().st_size / 1e6:.1f} MB)")
    if not args.form_action:
        print("  ⚠ Form chưa nối nơi nhận dữ liệu: thêm --form-action <URL nhận POST> (CRM, Google Apps Script, webhook…).")
    return 0


def main() -> int:
    load_env()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="lenh", required=True)

    def source_args(sp):
        sp.add_argument("nguon", nargs="+", help="Tệp PDF/DOCX/PPTX/MD/TXT/HTML hoặc URL")
        sp.add_argument("--ten", help="Tên thư mục dự án (mặc định theo tên tệp đầu tiên)")
        sp.add_argument("--dau-ra", help="Thư mục dự án (mặc định output/slide-ebook/<tên>)")
        sp.add_argument("--doi-tuong", help="Đối tượng đọc, vd 'chủ doanh nghiệp SME'")
        sp.add_argument("--ghi-cong", choices=["author", "compile", "translate"], help="Biên soạn / sưu tầm / biên dịch")
        sp.add_argument("--so-slide", type=int, default=24, help="Số slide mong muốn (mặc định 24)")
        sp.add_argument("--khong-khoa-hoc", action="store_true", help="Không thêm CTA và trang khoá học AI Agent")
        sp.add_argument("--mau", help="Yêu cầu màu bằng lời, vd 'xanh navy và vàng'; bỏ trống = agent tự chọn theo chủ đề")

    def build_args(sp):
        sp.add_argument("--loai", choices=["ca-hai", "ebook", "slide"], default="ca-hai")
        sp.add_argument("--phong-cach", choices=["saas", "retron", "visual", "co-dien"], default="saas",
                        help="saas: xanh dương đồng bộ slide/ebook/landing, Morph (mặc định, xem design_system.md); retron: tím gradient + khối 3D; visual: Visual-First theo bảng màu tài liệu; "
                             "co-dien: kiểu ebook SlimAI")
        sp.add_argument("--bang-mau", help="5 mã màu chính xác 'chính,phụ,đậm,nền,chữ' (ghi đè bảng màu)")
        sp.add_argument("--xuat", help="Thư mục lưu file thành phẩm (vd ~/Downloads); mặc định thư mục dự án")

    source_args(sub.add_parser("dan-y", help="Đọc nguồn + biên tập bản thảo, dừng để duyệt"))
    d = sub.add_parser("dung", help="Dựng slide + ebook từ ban-thao.json")
    d.add_argument("thu_muc")
    d.add_argument("--khong-khoa-hoc", action="store_true")
    d.add_argument("--mau", help="Đổi bảng màu bằng lời trước khi dựng, vd 'tông xanh lá tươi'")
    build_args(d)
    dp = sub.add_parser("doc", help="Chỉ đọc nguồn -> nguon.md + anh/ (không cần API key)")
    dp.add_argument("nguon", nargs="+")
    dp.add_argument("--ten")
    dp.add_argument("--dau-ra")
    kp = sub.add_parser("kiem", help="Kiểm tra ban-thao.json và tạo ban-thao.md")
    kp.add_argument("thu_muc")
    lp = sub.add_parser("landing", help="Làm landing page có form đăng ký từ ban-thao.json")
    lp.add_argument("thu_muc")
    lp.add_argument("--xuat", help="Thư mục lưu tệp HTML (mặc định thư mục dự án)")
    lp.add_argument("--form-action", help="URL nhận dữ liệu form (POST FormData). Bỏ trống = bản xem trước, không gửi đi")
    lp.add_argument("--cta", help="Chữ trên nút kêu gọi (mặc định 'Nhận tài liệu miễn phí')")
    c = sub.add_parser("chay", help="Chạy liền: đọc nguồn → biên tập → dựng → kiểm định")
    source_args(c)
    build_args(c)
    args = ap.parse_args()
    try:
        if args.lenh == "dan-y":
            cmd_dan_y(args)
            return 0
        if args.lenh == "dung":
            return cmd_dung(args)
        if args.lenh == "landing":
            return cmd_landing(args)
        if args.lenh == "doc":
            return cmd_doc(args)
        if args.lenh == "kiem":
            return cmd_kiem(args)
        work = cmd_dan_y(args)
        q = json.loads((work / "ban-thao.json").read_text()).get("palette_question")
        if q and not args.mau and not args.bang_mau:   # chỉ dừng khi agent thật sự cần hỏi màu
            print(f"\nDừng trước khi dựng vì cần bạn chọn màu: {q}")
            return 3
        return cmd_dung(args, work)
    except (RuntimeError, OSError) as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
