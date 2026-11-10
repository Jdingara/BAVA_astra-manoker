"""Printable Word cut list (A4) for the owner's 4 wardrobe drawings, from owner_cutlist.json."""
import json
import os
import time

from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(HERE, "owner_cutlist.json")))
TITLES = {"GF": "GF Bedroom", "1F Master": "1st Floor M.Bedroom", "1F Bedroom 2": "1st Floor Bedroom 2", "2F": "2nd Floor Bedroom"}
GOLD = RGBColor(0xA9, 0x83, 0x4A)


def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def repeat_header(row):
    trPr = row._tr.get_or_add_trPr()
    el = OxmlElement("w:tblHeader")
    el.set(qn("w:val"), "true")
    trPr.append(el)


def cell_text(cell, text, bold=False, size=8.5, align=None, color=None):
    cell.text = ""
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    if align:
        p.alignment = align
    r = p.add_run(str(text))
    r.bold = bold
    r.font.size = Pt(size)
    if color:
        r.font.color.rgb = color


doc = Document()
sec = doc.sections[0]
sec.orientation = WD_ORIENT.LANDSCAPE
sec.page_width, sec.page_height = Mm(297), Mm(210)
for side in ("left_margin", "right_margin"):
    setattr(sec, side, Mm(10))
sec.top_margin, sec.bottom_margin = Mm(10), Mm(10)
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(9)

# footer
fp = sec.footer.paragraphs[0]
fp.text = "ASTRA INTERIORS · No 2, KVK Nagar, IAF Road, Selaiyur, Chennai 600073 · +91 97911 82789 · Cut list from owner's AutoCAD drawing (manoker bedroom 2d model.dwg)"
fp.runs[0].font.size = Pt(7.5)
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER

# ---- cover / summary
h = doc.add_paragraph()
r = h.add_run("ASTRA INTERIORS")
r.bold, r.font.size, r.font.color.rgb = True, Pt(20), GOLD
h2 = doc.add_paragraph()
r = h2.add_run("Mr. Manoker – Wardrobe cut list (4 bedrooms)")
r.bold, r.font.size = True, Pt(14)
doc.add_paragraph(time.strftime("Date: %d-%m-%Y")).runs[0].font.size = Pt(9)

t = doc.add_table(rows=1, cols=9)
t.style = "Table Grid"
t.alignment = WD_TABLE_ALIGNMENT.CENTER
hdr = ["Wardrobe", "Width", "Height", "Cupboard box", "Loft", "Pieces", "18 mm sheets", "6 mm sheets", "LED strip"]
for c, txt in zip(t.rows[0].cells, hdr):
    cell_text(c, txt, bold=True, size=9)
    shade(c, "EFE6DA")
for k in ["GF", "1F Master", "1F Bedroom 2", "2F"]:
    d = data[k]
    inf = d["info"]
    cells = t.add_row().cells
    vals = [TITLES[k], inf["width"], inf["height"], f"{inf['box_h']} mm", f"90 mm frame, {inf['height'] - inf['box_h']} H",
            sum(r[3] for r in d["rows"]), d["mats"][0][2], d["mats"][1][2], f"{inf['grooves']} pcs / {inf['led_m']} m"]
    for c, v in zip(cells, vals):
        cell_text(c, v, size=9)

doc.add_paragraph()
notes = [
    "Board: 18 mm ply for all carcass, shelves and drawers.  Back panels: 6 mm ply in a 6 mm groove all round (size includes +12 mm).",
    "Depth: all wardrobes 500 mm (side / top / bottom). Full-height partitions = 500 (same as side panel, doors are fixed on them; 6 mm back-panel groove on both faces). Inside partitions (dressing / bangle column) = 494. Shelves = 474 (set back 20 mm).",
    "Every wardrobe is a CUPBOARD BOX 2000 mm high (an 8 ft ply sheet is only 2400 mm long).",
    "LOFT above the cupboard = 90 mm FRAME ONLY: 90 mm uprights at the ends and partitions + 90 mm top and bottom rails. No loft box, no loft back panel. Loft floor = cupboard top panel.",
    "GF Bedroom is wider than 2400 mm, so it has 2 cupboard boxes side by side and the loft rails are in 2 pieces – no piece is longer than 2400 mm.",
    "LED strip-light groove: one vertical groove per cupboard section, 12 mm wide × 8 mm deep, 100 mm from the front edge, on the side / partition face.",
    "Drawers: bottom 2 drawers only in every bedroom, opening 173, drawer box 150 high. 18 mm frame (sides + front/back inner) with an 8 mm wide x 10 mm deep groove: leave 12 mm from the bottom edge, groove from 12 to 20 mm; the 6 mm drawer bottom slides into the groove (size = inside + 18 mm: 10 mm groove each side, 1 mm play).",
    "Cut L / Cut W = panel-saw size (front edge minus 0.5 mm edge tape). Add saw kerf when marking out.",
    "Shutters: 6 doors per bedroom (2 per section), 18 mm ply + laminate, full overlay; gaps 2 mm between doors, 3 mm next to side cover / strip, 2 mm cupboard-to-loft door, 1 mm bottom and top; 2 mm edge tape on 4 sides (Cut = finished - 4 mm). Drawer section: doors only above the drawers; the 2 drawers have outside fronts in shutter material.",
]
for n in notes:
    p = doc.add_paragraph(n, style="List Bullet")
    p.runs[0].font.size = Pt(9)

# ---- one section per wardrobe
for k in ["GF", "1F Master", "1F Bedroom 2", "2F"]:
    d = data[k]
    inf = d["info"]
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
    hp = doc.add_paragraph()
    r = hp.add_run(f"{TITLES[k]} wardrobe")
    r.bold, r.font.size, r.font.color.rgb = True, Pt(15), GOLD
    sp = doc.add_paragraph(f"{inf['width']} W × {inf['height']} H × {inf['depth']:.0f} D  ·  cupboard box {inf['box_h']} mm + loft 90 mm frame only  ·  "
                           f"cupboard clear {inf['main_clear']} mm")
    sp.runs[0].font.size = Pt(9.5)
    img = os.path.join(HERE, f"drawing_{k}.png")
    if os.path.exists(img):
        ip = doc.add_paragraph()
        ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ip.add_run().add_picture(img, height=Mm(140))
        cp = doc.add_paragraph(f"2D drawing (owner's AutoCAD): cupboard box {inf['box_h']} mm high; loft above = 90 mm frame only "
                               f"(uprights + top/bottom rails). LED strip groove in each cupboard section.")
        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cp.runs[0].font.size = Pt(9)
        cp.runs[0].italic = True
        simg = os.path.join(HERE, f"shutters_{k}.png")
        if os.path.exists(simg):
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            sp_ = doc.add_paragraph()
            r4 = sp_.add_run(f"{TITLES[k]} – shutters with Merino laminate")
            r4.bold, r4.font.size, r4.font.color.rgb = True, Pt(13), GOLD
            ip2 = doc.add_paragraph()
            ip2.alignment = WD_ALIGN_PARAGRAPH.CENTER
            ip2.add_run().add_picture(simg, height=Mm(150))
        T3 = {"GF": "GF Bedroom", "1F Master": "1F M.Bedroom", "1F Bedroom 2": "1F Bedroom 2", "2F": "2F Bedroom"}[k]
        TP = {"GF": "Gf Bedroom", "1F Master": "1St Floor M.Bedroom", "1F Bedroom 2": "1St Floor Bedroom 2", "2F": "2Nd Floor Bedroom"}[k]
        for fn_, cap_, hmm in ((f"3D - {T3} - assembled (no doors).png", "3D model – assembled box without doors (off-white carcass, LED strips, drawer fronts)", 150),
                               (f"3D - {T3} - exploded pieces.png", "3D model – exploded view of the pieces", 150),
                               (f"Pieces - {TP}.png", "All pieces drawn to scale – # = row number in the cut list", 150)):
            fp_ = os.path.join(HERE, fn_)
            if not os.path.exists(fp_):
                continue
            doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            hq = doc.add_paragraph(); rq = hq.add_run(f"{TITLES[k]} – {cap_}")
            rq.bold, rq.font.size, rq.font.color.rgb = True, Pt(12), GOLD
            iq = doc.add_paragraph(); iq.alignment = WD_ALIGN_PARAGRAPH.CENTER
            iq.add_run().add_picture(fp_, height=Mm(hmm))
        doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
        hp2 = doc.add_paragraph()
        r2 = hp2.add_run(f"{TITLES[k]} wardrobe – cut list")
        r2.bold, r2.font.size, r2.font.color.rgb = True, Pt(13), GOLD
    cols = ["#", "Group", "Part", "Material", "Qty", "Finished L", "Finished W", "Cut L", "Cut W", "Edge band", "Machining / note"]
    widths = [Mm(8), Mm(24), Mm(60), Mm(22), Mm(10), Mm(18), Mm(18), Mm(16), Mm(16), Mm(22), Mm(63)]
    tb = doc.add_table(rows=1, cols=len(cols))
    tb.style = "Table Grid"
    for c, txt, w in zip(tb.rows[0].cells, cols, widths):
        cell_text(c, txt, bold=True, size=8.5)
        shade(c, "1F1A17")
        c.paragraphs[0].runs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        c.width = w
    repeat_header(tb.rows[0])
    last = None
    for i, rr in enumerate(d["rows"], 1):
        group, part, mat, qty, L, W, cL, cW, edge, note = rr
        if group != last:
            gc = tb.add_row().cells
            m = gc[0].merge(gc[-1])
            cell_text(m, group, bold=True, size=8.5, color=GOLD)
            shade(m, "F7F2EB")
            last = group
        cells = tb.add_row().cells
        vals = [i, group, part, mat, qty, f"{L:g}", f"{W:g}", f"{cL:g}", f"{cW:g}", edge, note]
        for j, (c, v, w) in enumerate(zip(cells, vals, widths)):
            cell_text(c, v, bold=j in (7, 8), size=8.5,
                      align=WD_ALIGN_PARAGRAPH.RIGHT if j in (0, 4, 5, 6, 7, 8) else None)
            c.width = w
    tot = tb.add_row().cells
    cell_text(tot[2], "Total pieces", bold=True)
    cell_text(tot[4], sum(r[3] for r in d["rows"]), bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT)

    doc.add_paragraph()
    mt = doc.add_table(rows=1, cols=4)
    mt.style = "Table Grid"
    for c, txt in zip(mt.rows[0].cells, ["Material", "Area sq.ft / length", "8×4 sheets (15% waste)", "Hardware / item"]):
        cell_text(c, txt, bold=True)
        shade(c, "EFE6DA")
    n = max(len(d["mats"]), len(d["hardware"]))
    for i in range(n):
        cells = mt.add_row().cells
        if i < len(d["mats"]):
            m_ = d["mats"][i]
            cell_text(cells[0], m_[0])
            cell_text(cells[1], m_[1])
            cell_text(cells[2], m_[2])
        if i < len(d["hardware"]):
            h_ = d["hardware"][i]
            cell_text(cells[3], f"{h_[0]}: {h_[1]}")

    doc.add_paragraph()
    lp = doc.add_paragraph()
    r3 = lp.add_run("LED strip light – profile groove cutting")
    r3.bold, r3.font.size, r3.font.color.rgb = True, Pt(11), GOLD
    gp = doc.add_paragraph("Groove 12 mm wide × 8 mm deep, 100 mm from the front edge, vertical, on the panel face inside the section. "
                           "Start is measured from the top of the bottom panel; groove runs up to the underside of the top panel. "
                           "Drill a 10 mm wire hole through the top panel at the groove top. Keep shelf screws clear of the groove.")
    gp.runs[0].font.size = Pt(8.5)
    lt = doc.add_table(rows=1, cols=8)
    lt.style = "Table Grid"
    for c, txt in zip(lt.rows[0].cells, ["Section", "Opening W", "Panel", "Groove on", "From front", "Groove start", "Groove length", "Profile + strip"]):
        cell_text(c, txt, bold=True)
        shade(c, "EFE6DA")
    for g in inf["led"]:
        cells = lt.add_row().cells
        for c, v in zip(cells, [g["section"], g["opening"], g["panel"], g["face"], f"{g['from_front']} mm",
                                f"{g['start']} mm" + (" (above drawers)" if g["start"] else ""), f"{g['length']} mm", f"{g['strip']} mm"]):
            cell_text(c, v)
    cells = lt.add_row().cells
    cell_text(cells[0], "Total", bold=True)
    cell_text(cells[7], f"{inf['led_m']} m", bold=True)

out = os.path.join(HERE, "Mr. Manoker - Wardrobes Carpenter Pack (print).docx")
for cand in (out, out.replace(".docx", " (updated).docx"), out.replace(".docx", time.strftime(" (%H%M%S).docx"))):
    try:
        doc.save(cand)
        out = cand
        break
    except PermissionError:
        continue
print("saved", out)
