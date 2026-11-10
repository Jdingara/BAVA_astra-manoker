"""One file with all wardrobes: overview page + every wardrobe's customer pages, plus a single overview JPG."""
import os
import pathlib

import pymupdf
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

ROOT = r"C:\Users\Home\Manoker"
D2 = os.path.join(ROOT, "2-Designs")
ITEMS = [  # title, render image, customer pdf, colours
    ("GF Bedroom", os.path.join(D2, "GF Bedroom", "GF Bedroom Wardrobe - Render.png"), "GF Bedroom Wardrobe - Design for Mr. Manoker.pdf",
     "Sage green gloss + fluted walnut"),
    ("1F Master Bedroom", os.path.join(D2, "1F Master Bedroom", "1F Master Bedroom Wardrobe - Render.png"),
     "1F Master Bedroom Wardrobe - Design for Mr. Manoker.pdf", "27292 LV Mink + 27262 LV Peacock"),
    ("1F 2nd Bedroom", os.path.join(D2, "1F 2nd Bedroom", "1F 2nd Bedroom Wardrobe - Render.png"),
     "1F 2nd Bedroom Wardrobe - Design for Mr. Manoker.pdf", "21433 SF Neo Banana Leaf + 21457 SF Aspen Gold"),
    ("2F Bedroom", os.path.join(D2, "2F Bedroom", "2F Bedroom Wardrobe - Render.png"),
     "2F Bedroom Wardrobe - Design for Mr. Manoker.pdf", "21462 SF Lavendura + 21452 SF Prism Violet"),
]
tmp = os.path.join(D2, "_all_tmp")
os.makedirs(tmp, exist_ok=True)

# ---- overview JPG (2 x 2)
tiles = []
for title, img, _, cols in ITEMS:
    im = Image.open(img).convert("RGB")
    im.thumbnail((1200, 900))
    tiles.append((title, cols, im))
TW, TH, BAR = 1200, 900, 110
sheet = Image.new("RGB", (2 * TW + 30, 2 * (TH + BAR) + 30 + 160), "#1f1a17")
dr = ImageDraw.Draw(sheet)
try:
    f_big = ImageFont.truetype("segoeuib.ttf", 64)
    f_t = ImageFont.truetype("segoeuib.ttf", 44)
    f_s = ImageFont.truetype("segoeui.ttf", 30)
except OSError:
    f_big = f_t = f_s = ImageFont.load_default()
dr.text((30, 40), "ASTRA INTERIORS  ·  Mr. Manoker  ·  Wardrobe designs", font=f_big, fill="#c9a46a")
for k, (title, cols, im) in enumerate(tiles):
    x = 10 + (k % 2) * (TW + 10)
    y = 160 + (k // 2) * (TH + BAR + 10)
    sheet.paste(im, (x, y))
    dr.rectangle([x, y + TH, x + TW, y + TH + BAR], fill="#2b241f")
    dr.text((x + 24, y + TH + 10), title, font=f_t, fill="#ffffff")
    dr.text((x + 24, y + TH + 64), cols, font=f_s, fill="#d9cfc3")
jpg = os.path.join(ROOT, "All Wardrobes - Mr. Manoker.jpg")
try:
    sheet.save(jpg, quality=88)
except PermissionError:
    jpg = jpg.replace(".jpg", " (updated).jpg")
    sheet.save(jpg, quality=88)

# ---- overview page (HTML -> PDF) then append every customer PDF
cards = "".join(
    f'<div class="c"><img src="{pathlib.Path(img).as_uri()}"><div><b>{i + 1}. {t}</b><span>{cols}</span></div></div>'
    for i, (t, img, _, cols) in enumerate(ITEMS))
html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>
@page {{ size: A4 landscape; margin: 0; }} body {{ margin: 0; font-family: "Segoe UI", sans-serif; background: #1f1a17; color: #fff; }}
.p {{ width: 297mm; height: 210mm; padding: 9mm 12mm; box-sizing: border-box; }}
h1 {{ margin: 0 0 1mm; color: #c9a46a; letter-spacing: .12em; font-size: 20pt; }}
p.s {{ margin: 0 0 5mm; color: #d9cfc3; font-size: 10.5pt; }}
.g {{ display: grid; grid-template-columns: 1fr 1fr; gap: 5mm; }}
.c {{ background: #2b241f; border-radius: 2.5mm; overflow: hidden; }}
.c img {{ width: 100%; height: 66mm; object-fit: cover; display: block; }}
.c div {{ padding: 2mm 4mm 3mm; }} .c b {{ display: block; font-size: 12pt; }} .c span {{ font-size: 9pt; color: #d9cfc3; }}
</style></head><body><div class="p"><h1>ASTRA INTERIORS</h1>
<p class="s">Wardrobe designs for Mr. Manoker · each bedroom has its own design and colours · details on the following pages · +91 97911 82789</p>
<div class="g">{cards}</div></div></body></html>"""
hp = os.path.join(tmp, "o.html")
open(hp, "w", encoding="utf-8").write(html)
cover = os.path.join(tmp, "cover.pdf")
with sync_playwright() as p:
    b = p.chromium.launch(channel="msedge")
    pg = b.new_page()
    pg.goto(pathlib.Path(hp).as_uri())
    pg.wait_for_timeout(1500)
    pg.pdf(path=cover, print_background=True, prefer_css_page_size=True)
    b.close()
out = pymupdf.open(cover)
for _, _, pdf, _ in ITEMS:
    src = os.path.join(ROOT, pdf)
    upd = src.replace(".pdf", " (updated).pdf")
    if os.path.exists(upd) and os.path.getmtime(upd) > os.path.getmtime(src):
        src = upd
    out.insert_pdf(pymupdf.open(src))
dst = os.path.join(ROOT, "All Wardrobes - Mr. Manoker.pdf")
import time
for cand in (dst, dst.replace(".pdf", " (updated).pdf"), dst.replace(".pdf", time.strftime(" (%H%M%S).pdf"))):
    try:
        out.save(cand, garbage=3, deflate=True)
        dst = cand
        break
    except Exception:  # open in a PDF viewer
        continue
pages = out.page_count
out.close()
for f in os.listdir(tmp):
    os.remove(os.path.join(tmp, f))
os.rmdir(tmp)
print("PDF:", dst, pages, "pages", os.path.getsize(dst) // 1024, "KB")
print("JPG:", jpg, os.path.getsize(jpg) // 1024, "KB")
