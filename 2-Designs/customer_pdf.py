"""Customer design PDF (4 pages) for a wardrobe made by wardrobe_gen.py + blender_wardrobe.py.
Run: python customer_pdf.py "<folder>/<name> - data.json"
"""
import html
import json
import os
import pathlib
import sys

from PIL import Image
from playwright.sync_api import sync_playwright

SHADES = {"light": "#c9bcc4", "teal": "#1d6f82", "green": "#2f6a3b", "yellow": "#f2c200", "lilac": "#b7a3d6", "purple": "#5a2a6f"}
CSS = """
@page { size: A4 landscape; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; font-family: "Segoe UI", system-ui, sans-serif; color: #1f1a17; }
.page { width: 297mm; height: 210mm; position: relative; overflow: hidden; page-break-after: always; }
.page:last-child { page-break-after: auto; }
.hero { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; }
.shade { position: absolute; left: 0; right: 0; bottom: 0; height: 52mm; background: linear-gradient(transparent, rgba(20,16,13,.88)); }
.cover-text { position: absolute; left: 16mm; bottom: 12mm; color: #fff; }
.cover-text small { letter-spacing: .3em; color: #c9a46a; font-size: 10pt; font-weight: 600; }
.cover-text h1 { margin: 2mm 0 1mm; font-size: 30pt; font-weight: 600; }
.cover-text p { margin: 0; font-size: 12pt; opacity: .9; }
.brand { position: absolute; right: 16mm; bottom: 12mm; text-align: right; color: #fff; font-size: 10pt; line-height: 1.5; }
.brand b { display: block; font-size: 18pt; letter-spacing: .2em; color: #c9a46a; }
.bar { height: 16mm; display: flex; align-items: center; justify-content: space-between; padding: 0 14mm; border-bottom: 1.2mm solid #c9a46a; }
.bar h2 { margin: 0; font-size: 15pt; }
.bar span { font-size: 9.5pt; color: #6f655c; }
.bar b { letter-spacing: .18em; color: #a9834a; }
.two { display: grid; grid-template-columns: 1.55fr 1fr; gap: 10mm; padding: 9mm 14mm; height: calc(210mm - 28mm); }
.two img { width: 100%; height: 100%; object-fit: cover; border-radius: 3mm; }
ul { margin: 0; padding: 0; list-style: none; font-size: 11.5pt; line-height: 1.45; }
li { padding: 3mm 0 3mm 9mm; border-bottom: .3mm solid #eee5d8; position: relative; }
li::before { content: "\\2605"; color: #c9a46a; position: absolute; left: 0; top: 3mm; }
li b { display: block; font-size: 12pt; }
.full { padding: 5mm 14mm; height: calc(210mm - 28mm); display: flex; align-items: center; justify-content: center; }
.full img { max-width: 100%; max-height: 100%; }
.foot { position: absolute; left: 14mm; right: 14mm; bottom: 4mm; font-size: 8.5pt; color: #8a8077; display: flex; justify-content: space-between; }
.specs { display: grid; grid-template-columns: 1fr 1fr; gap: 10mm; padding: 9mm 14mm; }
.sw { display: flex; gap: 5mm; align-items: center; margin-bottom: 5mm; }
.chip { width: 30mm; height: 22mm; border-radius: 2mm; border: .3mm solid #ccc; flex-shrink: 0; }
.sw b { display: block; font-size: 12pt; }
.sw span { font-size: 10pt; color: #6f655c; }
table { width: 100%; border-collapse: collapse; font-size: 10.5pt; }
td { padding: 2.4mm 2mm; border-bottom: .3mm solid #eee5d8; vertical-align: top; }
td:first-child { color: #6f655c; width: 38%; }
.contact { margin-top: 7mm; background: #1f1a17; color: #fff; border-radius: 3mm; padding: 6mm 7mm; font-size: 10.5pt; line-height: 1.6; }
.contact b { color: #c9a46a; letter-spacing: .14em; font-size: 13pt; }
.note { font-size: 9pt; color: #8a8077; margin-top: 4mm; }
"""


def chip(label):
    for k, v in SHADES.items():
        if k in label.lower():
            return v
    return "#ccc"


def main(path):
    d = json.load(open(path))
    folder = os.path.dirname(os.path.abspath(path))
    name, title, g, cols = d["name"], d["title"], d["geom"], d["colours"]
    tmp = os.path.join(folder, "_tmp")
    os.makedirs(tmp, exist_ok=True)
    jp = {}
    for key, f in (("render", "Render.png"), ("open", "Render Open.png")):
        Image.open(os.path.join(folder, f"{name} - {f}")).convert("RGB").save(os.path.join(tmp, key + ".jpg"), quality=88)
        jp[key] = pathlib.Path(os.path.join(tmp, key + ".jpg")).as_uri()
    dw = Image.open(os.path.join(folder, f"{name} - Drawing.png")).convert("RGB")
    w, h = dw.size
    dw = dw.crop((int(w * 0.02), int(h * 0.03), int(w * 0.98), int(h * 0.58)))
    dw.save(os.path.join(tmp, "dwg.jpg"), quality=90)
    jp["dwg"] = pathlib.Path(os.path.join(tmp, "dwg.jpg")).as_uri()

    n_main, n_loft = len(g["main_doors"]), len(g["loft_doors"])
    n_drw = sum(x[3] for x in g["drawers"])
    feats = [("Full-height wardrobe with loft", f"{n_main} doors below and {n_loft} loft doors above for suitcases and seasonal items.")]
    if g.get("mirrors"):
        feats.append(("Inside dressing table", "Visible when the doors open: table top at 800 mm with a slim drawer just under it, mirror with LED light, glass shelves above."))
        feats.append(("Bangle & perfume shelves", "A 300 mm shelf column right beside the dressing table."))
    elif g["glass"]:
        feats.append(("Bangle & perfume column", "A 300 mm column with small shelves, plus glass shelves beside it for display."))
    feats.append(("Shelves at 305 mm spacing", "Easy-to-reach shelves for folded clothes."))
    if g["rods"]:
        feats.append(("Hanging space", "Coat / shirt hanging rod with full-length space."))
    if n_drw:
        feats.append((f"{n_drw} soft-close drawers", "Telescopic soft-close channels with gold bar handles."))
    feats.append(("Two-colour design", " + ".join(v for v in cols.values()) + " with champagne-gold handles."))
    li = "".join(f"<li><b>{html.escape(a)}</b>{html.escape(b)}</li>" for a, b in feats)
    chips = "".join(f'<div class="sw"><div class="chip" style="background:{d.get("shades", {}).get(k) or chip(v)}"></div><div><b>{k} &middot; {html.escape(v)}</b>'
                    f'<span>{"Main doors, loft doors, sides and base" if k == "A" else "Feature doors and drawer fronts"}</span></div></div>' for k, v in cols.items())
    head = lambda t: f'<div class="bar"><h2>{t}</h2><span><b>ASTRA INTERIORS</b> &middot; Mr. Manoker &middot; {html.escape(title)}</span></div>'
    doc = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<section class="page"><img class="hero" src="{jp['render']}"><div class="shade"></div>
<div class="cover-text"><small>DESIGN PROPOSAL</small><h1>{html.escape(title)} Wardrobe</h1>
<p>Prepared for Mr. Manoker &middot; {g['W']:.0f} &times; {g['H']:.0f} mm &middot; {html.escape(' + '.join(cols.values()))}</p></div>
<div class="brand"><b>ASTRA INTERIORS</b>Selaiyur, Chennai &middot; +91 97911 82789</div></section>
<section class="page">{head("Inside the wardrobe")}<div class="two"><img src="{jp['open']}"><ul>{li}</ul></div>
<div class="foot"><span>3D visual for design approval. Final colours as per the selected laminate shade card.</span><span>2</span></div></section>
<section class="page">{head("Design drawing with sizes")}<div class="full"><img src="{jp['dwg']}"></div>
<div class="foot"><span>All sizes in mm, to be confirmed at site before production.</span><span>3</span></div></section>
<section class="page">{head("Colours &amp; specification")}<div class="specs"><div>{chips}
<div class="sw"><div class="chip" style="background:linear-gradient(135deg,#f0d9b0,#c9a46a 50%,#a9834a)"></div><div><b>Champagne gold handles</b><span>Long bar handles on doors, short on loft, horizontal on drawers</span></div></div></div>
<div><table>
<tr><td>Size (W &times; H &times; D)</td><td>{g['W']:.0f} &times; {g['H']:.0f} &times; {g['DT']:.0f} mm (depth includes back panel &amp; door)</td></tr>
<tr><td>Board</td><td>18 mm ply (16 mm ply + 1 mm laminate + 0.8 mm backer)</td></tr>
<tr><td>Edge banding</td><td>Doors &amp; drawer fronts 2 mm all sides &middot; carcass 0.5 mm</td></tr>
<tr><td>Doors</td><td>{n_main} main + {n_loft} loft, soft-close hinges</td></tr>
<tr><td>Drawers</td><td>{n_drw} with soft-close channels</td></tr>
<tr><td>Base</td><td>{g['P']:.0f} mm, sits above the 100 mm wall tile skirting</td></tr>
</table>
<div class="contact"><b>ASTRA INTERIORS</b><br>Vengatachalam &middot; +91 97911 82789<br>No 2, KVK Nagar, IAF Road, Selaiyur, Chennai 600073<br>chennaistyle1@gmail.com</div>
<div class="note">Images are 3D visuals for design approval; colours on screen are approximate. Final sizes after site measurement.</div></div></div>
<div class="foot"><span>Thank you for choosing Astra Interiors.</span><span>4</span></div></section></body></html>"""
    hp = os.path.join(tmp, "c.html")
    open(hp, "w", encoding="utf-8").write(doc)
    out = os.path.join(os.path.dirname(folder), "..", f"{title} Wardrobe - Design for Mr. Manoker.pdf")
    out = os.path.normpath(out)
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge")
        pg = b.new_page()
        pg.goto(pathlib.Path(hp).as_uri())
        pg.wait_for_timeout(1200)
        tmp_pdf = os.path.join(tmp, "out.pdf")
        pg.pdf(path=tmp_pdf, print_background=True, prefer_css_page_size=True)
        b.close()
    import time
    for cand in (out, out.replace(".pdf", " (updated).pdf"), out.replace(".pdf", time.strftime(" (%H%M%S).pdf"))):
        try:
            os.replace(tmp_pdf, cand)
            out = cand
            break
        except PermissionError:  # open in a PDF viewer
            continue
    for f in os.listdir(tmp):
        os.remove(os.path.join(tmp, f))
    os.rmdir(tmp)
    print("customer PDF:", out, os.path.getsize(out) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1])
