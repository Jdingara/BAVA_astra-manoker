"""Make the drawing preview PNG and the carpenter PDF (drawing + cut list + materials + hardware)."""
import html
import os
import pathlib

import ezdxf
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from ezdxf.addons.drawing import Frontend, RenderContext  # noqa: E402
from ezdxf.addons.drawing.config import BackgroundPolicy, ColorPolicy, Configuration  # noqa: E402
from ezdxf.addons.drawing.matplotlib import MatplotlibBackend  # noqa: E402

CSS = """
@page { size: A4 landscape; margin: 8mm; }
body { font-family: "Segoe UI", system-ui, sans-serif; color: #1f1a17; margin: 0; font-size: 9pt; }
.page { page-break-after: always; }
.page:last-child { page-break-after: auto; }
.bar { display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 2px solid #c9a46a; padding-bottom: 4px; margin-bottom: 6px; }
.bar h1 { margin: 0; font-size: 15pt; }
.bar span { color: #6f655c; }
.bar b { color: #a9834a; letter-spacing: .14em; }
img.dwg { width: 100%; max-height: 172mm; object-fit: contain; }
table { width: 100%; border-collapse: collapse; }
th, td { border: 1px solid #ddd2c4; padding: 2.2px 5px; text-align: left; }
th { background: #efe6da; }
td.n, th.n { text-align: right; white-space: nowrap; }
td.cut { font-weight: 700; }
tr.grp td { background: #f7f2eb; font-weight: 700; color: #a9834a; }
.cols { display: grid; grid-template-columns: 1.2fr 1fr; gap: 8mm; margin-top: 5mm; }
.note { color: #6f655c; margin-top: 4mm; line-height: 1.5; }
"""


def make_sheets(out, data):
    name = data["name"]
    dxf = os.path.join(out, f"{name} - AutoCAD 2D.dxf")
    doc = ezdxf.readfile(dxf)
    fig = plt.figure(figsize=(16, 11))
    ax = fig.add_axes([0, 0, 1, 1])
    Frontend(RenderContext(doc), MatplotlibBackend(ax),
             config=Configuration(background_policy=BackgroundPolicy.WHITE, color_policy=ColorPolicy.BLACK)).draw_layout(doc.modelspace())
    png = os.path.join(out, f"{name} - Drawing.png")
    fig.savefig(png, dpi=220)
    plt.close(fig)

    cols = "  |  ".join(f"{k} = {v}" for k, v in data["colours"].items())
    g = data["geom"]
    head = lambda t: f'<div class="bar"><h1>{html.escape(t)}</h1><span><b>ASTRA INTERIORS</b> · Mr. Manoker · {html.escape(data["title"])} · {g["W"]:.0f} × {g["H"]:.0f} × {g["DT"]:.0f} mm · {html.escape(cols)}</span></div>'
    rows, last = [], None
    for i, (r, sq) in enumerate(zip(data["cut"], data["sqft"]), 1):
        if r[0] != last:
            rows.append(f'<tr class="grp"><td colspan="10">{html.escape(r[0])}</td></tr>')
            last = r[0]
        rows.append(f'<tr><td>{i}</td><td>{html.escape(r[1])}</td><td>{html.escape(r[2])}</td><td class="n">{r[3]}</td>'
                    f'<td class="n">{r[4]:g}</td><td class="n">{r[5]:g}</td><td class="n cut">{r[6]:g}</td><td class="n cut">{r[7]:g}</td>'
                    f'<td>{html.escape(r[8])}</td><td class="n">{sq}</td></tr>')
    total = sum(r[3] for r in data["cut"])
    mats = "".join(f"<tr><td>{html.escape(str(m[0]))}</td><td class='n'>{m[1]}</td><td class='n'>{m[2]}</td></tr>" for m in data["mats"])
    hw = "".join(f"<tr><td>{html.escape(str(h[0]))}</td><td class='n'>{h[1]}</td></tr>" for h in data["hardware"])
    doc_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<section class="page">{head(f"{data['title']} wardrobe - 2D drawing")}<img class="dwg" src="{pathlib.Path(png).as_uri()}"></section>
<section class="page">{head("Cut list (mm)")}
<table><tr><th>#</th><th>Part</th><th>Material</th><th class="n">Qty</th><th class="n">Finished L</th><th class="n">Finished W</th>
<th class="n">Cut L</th><th class="n">Cut W</th><th>Edge band</th><th class="n">Sq.ft</th></tr>{''.join(rows)}
<tr><td></td><td><b>Total pieces</b></td><td></td><td class="n"><b>{total}</b></td><td colspan="6"></td></tr></table>
<div class="cols"><div><table><tr><th>Material (8 × 4 ft sheets, 15% waste)</th><th class="n">Sq.ft / length</th><th class="n">Sheets</th></tr>{mats}</table></div>
<div><table><tr><th>Hardware</th><th class="n">Qty</th></tr>{hw}</table></div></div>
<div class="note">Finished = size after edge banding. <b>Cut = panel-saw size</b> (doors &amp; drawer fronts minus 2 mm edge band each side; carcass minus 0.5 mm tape on the front edge).
Panels longer than 2400 are cut in 2 and joined at a partition. Base {g["P"]:.0f} mm sits above the 100 mm wall tile skirting. Confirm site sizes before cutting.</div>
</section></body></html>"""
    h = os.path.join(out, "_sheet.html")
    open(h, "w", encoding="utf-8").write(doc_html)
    from playwright.sync_api import sync_playwright
    pdf = os.path.join(out, f"{name} - Drawing & Cut List.pdf")
    with sync_playwright() as p:
        b = p.chromium.launch(channel="msedge")
        pg = b.new_page()
        pg.goto(pathlib.Path(h).as_uri())
        pg.wait_for_timeout(500)
        tmp_pdf = os.path.join(out, "_tmp_sheet.pdf")
        pg.pdf(path=tmp_pdf, prefer_css_page_size=True, print_background=True)
        b.close()
    import time
    for cand in (pdf, pdf.replace(".pdf", " (updated).pdf"), pdf.replace(".pdf", time.strftime(" (%H%M%S).pdf"))):
        try:
            os.replace(tmp_pdf, cand)
            pdf = cand
            break
        except PermissionError:  # open in a PDF viewer
            continue
    os.remove(h)
    print("   sheets:", os.path.basename(png), "|", os.path.basename(pdf))
