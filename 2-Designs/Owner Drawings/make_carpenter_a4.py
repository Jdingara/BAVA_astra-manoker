"""A4 portrait printout for the carpenter: per bedroom - 2D page, 3D page, cut list (readable font), hardware, LED, notes."""
import json, os, time
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor
import owner_cutlist as oc
from make_carpenter_excel import where, GNAME, TITLE, T3

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "owner_cutlist.json")))
GOLD = RGBColor(0xA9, 0x83, 0x4A)


def shade(cell, fill):
    pr = cell._tc.get_or_add_tcPr(); s = OxmlElement("w:shd")
    s.set(qn("w:val"), "clear"); s.set(qn("w:color"), "auto"); s.set(qn("w:fill"), fill); pr.append(s)


def hdr_repeat(row):
    pr = row._tr.get_or_add_trPr(); e = OxmlElement("w:tblHeader"); e.set(qn("w:val"), "true"); pr.append(e)


def txt(cell, t, bold=False, size=8.5, color=None, align=None):
    cell.text = ""; p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0); p.paragraph_format.space_before = Pt(0)
    if align is not None: p.alignment = align
    r = p.add_run(str(t)); r.bold = bold; r.font.size = Pt(size)
    if color is not None: r.font.color.rgb = color


def heading(doc, t, size=14, color=GOLD):
    p = doc.add_paragraph(); r = p.add_run(t); r.bold = True; r.font.size = Pt(size); r.font.color.rgb = color
    p.paragraph_format.space_after = Pt(4)


def pagebreak(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def picture(doc, fn, cap, h):
    fp = os.path.join(HERE, fn)
    if not os.path.exists(fp):
        return
    c = doc.add_paragraph(); r = c.add_run(cap); r.bold = True; r.font.size = Pt(10); r.font.color.rgb = GOLD
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(fp, height=Mm(h))


doc = Document()
sec = doc.sections[0]
sec.page_width, sec.page_height = Mm(210), Mm(297)
sec.left_margin = sec.right_margin = Mm(10); sec.top_margin = sec.bottom_margin = Mm(10)
doc.styles["Normal"].font.name = "Calibri"; doc.styles["Normal"].font.size = Pt(9)
fp = sec.footer.paragraphs[0]
fp.text = "ASTRA INTERIORS - Mr. Manoker wardrobes - Carpenter list - " + time.strftime("%d-%m-%Y")
fp.runs[0].font.size = Pt(7.5); fp.alignment = WD_ALIGN_PARAGRAPH.CENTER

# ---- cover page
heading(doc, "ASTRA INTERIORS", 20)
heading(doc, "Mr. Manoker - 4 wardrobes - CARPENTER LIST", 15, RGBColor(0, 0, 0))
rules = [
    "All sizes are CUT sizes in mm (edge tape already deducted).",
    "Box: 2000 high, 500 deep. Loft above = 90 mm frame only (uprights + top/bottom rails).",
    "Sides, top, bottom and full partitions 500 (cut 499). Inside partitions 494 (cut 493). Shelves 474 (cut 473), set back 20 mm.",
    "Back panel 6 mm in 6 mm groove on sides, full partitions, top and bottom (size = opening + 12).",
    "Drawers: 2 bottom drawers per bedroom, opening 173, box 150 high, 450 soft-close channel (13 mm each side). "
    "Drawer bottom groove: leave 12 mm from bottom, 8 mm wide x 10 mm deep.",
    "LED profile groove: 12 W x 8 D, 100 mm from the FRONT edge, vertical, on panel face inside the section. 10 mm wire hole through top panel.",
    "Shutters: 18 mm ply, colour laminate outside, WHITE laminate inside (no liner), 2 mm edge tape 4 sides.",
    "5 DOORS (2 + 1 + 2): full partitions behind the door joints. Centre door = DRESSING: top 750 from floor (GF) / 800 (others), mirror + LED above, shelf over it.",
    "GF centre door: GLASS panel, 90 mm laminate border all round (CNC cut-out after laminate + edge tape). Other rooms: plain centre door.",
    "GAPS: 2 mm between doors | 3 mm+ next to side cover / strip | 2 mm cupboard door to loft door | 1 mm bottom and top.",
    "Side cover (518 deep = 500 + door, full height, 2 pieces joined at 2000) on ONE side; 100 mm strip on the other side. 2 mm tape on front edge only.",
    "Skirting 80 high, 0.5 mm tape on top edge.",
    "Carcass laminate: WHITE both faces (code to confirm). 6 mm: same white one face. No liner."
]
for r_ in rules:
    p = doc.add_paragraph(r_, style="List Bullet"); p.runs[0].font.size = Pt(10)
doc.add_paragraph()
t = doc.add_table(rows=1, cols=5); t.style = "Table Grid"
for c, h in zip(t.rows[0].cells, ["Bedroom", "Total width", "Height", "Side cover", "Colours (main + accent)"]):
    txt(c, h, bold=True, size=9.5); shade(c, "EFE6DA")
for room, v in D.items():
    inf = v["info"]
    codes = []
    for r in v["rows"]:
        if r[0] == "Shutters" and " - " in r[1]:
            c_ = r[1].rsplit(" - ", 1)[1].split(" (")[0]
            if c_ not in codes:
                codes.append(c_)
    cells = t.add_row().cells
    for c, val in zip(cells, [TITLE[room], f"{inf['width'] + 36} (box {inf['width']})", inf["height"], f"{oc.COVER_SIDE[room]} side", " + ".join(codes)]):
        txt(c, val, size=9.5)

COLS = ["No", "Part", "Laminate", "Qty", "Cut L", "Cut W", "Edge tape", "Where / fitting"]
WID = [Mm(8), Mm(44), Mm(27), Mm(9), Mm(13), Mm(13), Mm(20), Mm(56)]
n = 0
for room, v in D.items():
    inf = v["info"]
    pagebreak(doc)
    heading(doc, f"{TITLE[room]} - 2D", 15)
    doc.add_paragraph(f"Box {inf['width']} W x {inf['height']} H x 500 D  |  with side cover ({oc.COVER_SIDE[room]}) + 100 strip = {inf['width'] + 36} W").runs[0].font.size = Pt(10)
    picture(doc, f"drawing_{room}.png", "2D drawing - inside, measurements", 108)
    picture(doc, f"shutters_{room}.png", "2D shutters - laminate code and size on each door", 108)
    pagebreak(doc)
    heading(doc, f"{TITLE[room]} - 3D", 15)
    picture(doc, f"3D - {T3[room]} - assembled (no doors).png", "3D - assembled box, without doors", 108)
    picture(doc, f"3D - {T3[room]} - exploded pieces.png", "3D - exploded pieces", 108)
    pagebreak(doc)
    heading(doc, f"{TITLE[room]} - cut list", 15)
    tb = doc.add_table(rows=1, cols=len(COLS)); tb.style = "Table Grid"; tb.alignment = WD_TABLE_ALIGNMENT.CENTER
    for c, h, w in zip(tb.rows[0].cells, COLS, WID):
        txt(c, h, bold=True, size=8.5, color=RGBColor(255, 255, 255)); shade(c, "1F1A17"); c.width = w
    hdr_repeat(tb.rows[0])
    last = None
    for r in v["rows"]:
        g, part, mat, q, L, W, cL, cW, edge, note = r
        if g != last:
            gc = tb.add_row().cells; m = gc[0].merge(gc[-1]); txt(m, GNAME.get(g, g), bold=True, size=9, color=GOLD); shade(m, "F7F2EB"); last = g
        n += 1
        lam = part.rsplit(" - ", 1)[1].split(" (")[0] if g == "Shutters" and " - " in part else ("White" if not mat.startswith("6") else "White 1 side")
        nm = (part.rsplit(" - ", 1)[0] if g == "Shutters" and " - " in part else part).replace("Bottom drawers (right section): ", "").replace("Bottom drawers: ", "")
        cells = tb.add_row().cells
        for j, (c, val, w) in enumerate(zip(cells, [n, nm, lam, q, cL, cW, edge, where(g, part, note, room)], WID)):
            txt(c, val, bold=j in (4, 5), size=8.5, align=WD_ALIGN_PARAGRAPH.RIGHT if j in (0, 3, 4, 5) else None); c.width = w
    doc.add_paragraph()
    heading(doc, "Hardware", 11)
    for h in v["hardware"]:
        doc.add_paragraph(f"{h[0]}: {h[1]}", style="List Bullet").runs[0].font.size = Pt(9.5)
    heading(doc, "LED groove (12 W x 8 D, 100 mm from front)", 11)
    for gx in inf["led"]:
        doc.add_paragraph(f"Section {gx['section']} ({gx['opening']} wide): {gx['panel']}, right face - start {gx['start']} mm, groove {gx['length']} mm, LED strip {gx['strip']} mm",
                          style="List Bullet").runs[0].font.size = Pt(9.5)

out = os.path.join(HERE, "Mr. Manoker - CARPENTER A4 Printout.docx")
for cand in (out, out.replace(".docx", " (updated).docx"), out.replace(".docx", time.strftime(" (%H%M%S).docx"))):
    try:
        doc.save(cand); out = cand; break
    except PermissionError:
        continue
print("saved", out)
