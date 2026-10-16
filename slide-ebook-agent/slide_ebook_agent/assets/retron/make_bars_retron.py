"""5 cột 3D tím dùng chung cho layout 'bậc thang' của phong cách retron (slide_ebook_agent)."""
import os
import make_assets_retron as m

m.OUT = OUT = "./"
os.makedirs(OUT, exist_ok=True)
for i, hh in enumerate([150, 255, 360, 465, 570]):
    pal, g = [(m.LAVENDER, 0.08), (m.VIOLET, 0.18), (m.LAVENDER, 0.08), (m.VIOLET, 0.18), (m.DEEP, 0.28)][i]
    m.prism(f"bar{i}.png", 220, hh, pal, gloss=g)
print(sorted(os.listdir(OUT)))
