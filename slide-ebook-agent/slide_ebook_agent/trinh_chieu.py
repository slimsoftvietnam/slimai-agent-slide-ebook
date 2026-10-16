"""Bản trình chiếu HTML một tệp: cùng danh sách phần tử với PPTX/PDF, chuyển trang kiểu Morph bằng View Transitions.

- Phần tử tên '!!…' trùng nhau giữa 2 slide liên tiếp sẽ trượt/đổi kích thước sang vị trí mới (giống PowerPoint Morph).
- Phần tử còn lại xuất hiện lần lượt (fade + trồi nhẹ).
- Phím: → / Space / PageDown: tiếp; ← / PageUp: lùi; Home/End; F: toàn màn hình. Bấm nửa phải/trái màn hình để chuyển.
Ảnh được nhúng base64 nên gửi một tệp là đủ.
"""
from __future__ import annotations

import base64
import json
import re
import mimetypes
from pathlib import Path
from urllib.parse import unquote, urlparse

from thiet_ke_slide import CSS, H, W, head_links, slides_html

PRESENT_CSS = f"""
html,body{{height:100%;background:#0b0a10;overflow:hidden}}
.stage{{position:fixed;left:50%;top:50%;width:{W}pt;height:{H}pt;transform-origin:center;}}
.slide{{position:absolute;inset:0;display:none;break-after:auto;box-shadow:0 20px 60px rgba(0,0,0,.45)}}
.slide.on{{display:block}}
.slide.on .el:not([data-vt]){{animation:rise .7s cubic-bezier(.2,.7,.2,1) both;animation-delay:calc(var(--k,0) * 45ms + 120ms)}}
@keyframes rise{{from{{opacity:0;transform:translateY(10pt)}}to{{opacity:1}}}}
.slide.on .el[style*="rotate"]:not([data-vt]){{animation-name:fade}}
@keyframes fade{{from{{opacity:0}}to{{opacity:1}}}}
::view-transition-group(*){{animation-duration:.9s;animation-timing-function:cubic-bezier(.65,0,.35,1)}}
::view-transition-old(root),::view-transition-new(root){{animation-duration:.45s}}
.bar{{position:fixed;left:0;bottom:0;height:3px;background:linear-gradient(90deg,#e8318a,#8a4dea,#12b5e5);transition:width .5s;z-index:9}}
.hint{{position:fixed;right:14px;bottom:10px;font:12px/1 system-ui;color:#8b8799;z-index:9}}
@media print{{.bar,.hint{{display:none}}}}
"""

PRESENT_JS = """
const S=[...document.querySelectorAll('.slide')], bar=document.querySelector('.bar'), hint=document.querySelector('.hint');
S.forEach(s=>[...s.querySelectorAll('.el')].forEach((e,k)=>e.style.setProperty('--k',Math.min(k,14))));
let cur=-1;
function fit(){const st=document.querySelector('.stage');const k=Math.min(innerWidth/st.offsetWidth,innerHeight/st.offsetHeight)*0.96;
  st.style.transform=`translate(-50%,-50%) scale(${k})`;}
function names(i,on){S[i].querySelectorAll('[data-vt]').forEach(e=>e.style.viewTransitionName=on?e.dataset.vt:'none');}
function paint(i){S.forEach((s,j)=>{s.classList.toggle('on',j===i);});names(i,true);cur=i;
  bar.style.width=((i+1)/S.length*100)+'%';hint.textContent=(i+1)+' / '+S.length;history.replaceState(null,'','#'+(i+1));}
function go(i){i=Math.max(0,Math.min(S.length-1,i));if(i===cur)return;
  if(!document.startViewTransition||cur<0){if(cur>=0)names(cur,false);paint(i);return;}
  names(cur,true);S.forEach((s,j)=>{if(j!==cur)names(j,false);});
  document.startViewTransition(()=>{names(cur,false);paint(i);});}
addEventListener('keydown',e=>{if(['ArrowRight',' ','PageDown','Enter'].includes(e.key)){e.preventDefault();go(cur+1);}
  else if(['ArrowLeft','PageUp','Backspace'].includes(e.key)){e.preventDefault();go(cur-1);}
  else if(e.key==='Home')go(0);else if(e.key==='End')go(S.length-1);
  else if(e.key==='f'||e.key==='F'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();}});
addEventListener('click',e=>{if(e.target.closest('a'))return;go(e.clientX>innerWidth/2?cur+1:cur-1);});
addEventListener('resize',fit);fit();paint(Math.max(0,(parseInt(location.hash.slice(1))||1)-1));
"""


def write_presenter(deck, out: Path, title: str) -> Path:
    # Mỗi ảnh nhúng MỘT lần vào bảng ASSETS; thẻ <img> chỉ giữ mã (ảnh lặp trên nhiều slide không làm tệp phình to)
    ids: dict[str, str] = {}
    data: dict[str, str] = {}

    def embed(m: re.Match) -> str:
        uri = m.group(1)
        if uri not in ids:
            path = Path(unquote(urlparse(uri).path))
            mime = mimetypes.guess_type(path.name)[0] or "image/png"
            ids[uri] = f"a{len(ids)}"
            data[ids[uri]] = f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()
        return f'data-a="{ids[uri]}"'

    slides = [re.sub(r'src="(file://[^"]+)"', embed, sl) for sl in slides_html(deck, fit=False)]
    assets_js = "const ASSETS=" + json.dumps(data) + ";document.querySelectorAll('img[data-a]').forEach(i=>i.src=ASSETS[i.dataset.a]);"
    # Tên view-transition phải duy nhất trên trang -> chỉ gán khi slide đang hiện (JS), bỏ khỏi style tĩnh
    html = (f'<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{title}</title>{head_links(deck)}<style>{CSS}{PRESENT_CSS}</style></head>'
            f'<body><div class="stage">{"".join(slides)}</div><div class="bar"></div><div class="hint"></div>'
            f'<script>{assets_js}{PRESENT_JS}</script></body></html>')
    out.write_text(html)
    return out
