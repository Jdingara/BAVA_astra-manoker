"""Factory cut list (panel saw / edge bander): one sheet per board type, cut sizes, edge banding per edge, grooves."""
import json, os, time
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "owner_cutlist.json")))
ROOM = {"GF": "GF Bedroom", "1F Master": "1F M.Bedroom", "1F Bedroom 2": "1F Bedroom 2", "2F": "2F Bedroom"}
OFF = "WHITE (code to confirm)"   # owner: no liner, one white laminate inside; code not fixed yet

def board(g, part, mat):
    if g == "Shutters":
        col = part.rsplit(" - ", 1)[1].split(" (")[0]
        return f"18 mm ply - {col} / white inside"
    if mat.startswith("6 mm"):
        return f"6 mm ply - {OFF} one side"
    return f"18 mm ply - {OFF} both sides"

def edges(edge, L, W):
    if edge == "2 mm, 4 sides":
        return "2 mm", "2 mm", "2 mm", "2 mm"
    if edge == "2 mm, 1 long":
        return "2 mm", "", "", ""
    if edge.startswith("0.5"):
        return "0.5 mm", "", "", ""
    return "", "", "", ""

def short(part):
    p = part.rsplit(" - ", 1)[0] if " - " in part and any(c.isdigit() for c in part.rsplit(" - ", 1)[1][:5]) else part
    return p.replace("Bottom drawers (right section): ", "Drawer ").replace("Bottom drawers (centre, under dressing): ", "Drawer ").replace("Bottom drawers: ", "Drawer ")

def machining(g, part, note):
    n = []
    if "Side panel" in part and g == "Cupboard box":
        n.append("no back groove (6 mm back screwed on)")
    if "full height, doors fixed" in part:
        n.append("back panel joint on back edge")
    if "groove" in note and g == "Drawers" and "bottom" not in part:
        n.append("drawer-bottom groove: leave 12, 8 W x 10 D")
    if g == "Shutters" and ("Door" in part):
        n.append("35 mm hinge cups")
    return "; ".join(n)

rows = {}
for room, v in D.items():
    led = {round(gx["x"], 1): gx for gx in v["info"]["led"]}
    for r in v["rows"]:
        g, part, mat, q, L, W, cL, cW, edge, note = r
        b = board(g, part, mat)
        m = machining(g, part, note)
        if g == "Cupboard box" and ("Side panel" in part or "Partition (full" in part):
            m += ("; " if m else "") + "LED groove 12x8 @100 from front (see LED sheet)"
        rows.setdefault(b, []).append([ROOM[room], short(part), cL, cW, q, *edges(edge, cL, cW), m])

wb = Workbook()
hdr = ["No", "Room", "Part", "Cut L (mm)", "Cut W (mm)", "Qty", "Edge L1", "Edge L2", "Edge W1", "Edge W2", "Machining / groove"]
gold = PatternFill("solid", fgColor="1F1A17"); thin = Side(style="thin", color="999999")
# summary
ss = wb.active; ss.title = "Summary"
ss.append(["Mr. Manoker - 4 wardrobes - FACTORY CUT LIST | Astra Interiors | " + time.strftime("%d-%m-%Y")]); ss["A1"].font = Font(bold=True, size=13)
ss.append(["Sizes are CUT sizes (edge band already deducted). L = grain/length direction. Edge L1 = front edge for carcass parts. Shutters 2 mm on 4 sides; side cover / 100 strip 2 mm front edge only; skirting 0.5 mm top edge."])
ss.append(["Board 8 x 4 (2440 x 1220). Max piece length 2400."])
ss.append([])
ss.append(["Board type", "Pieces", "Area sq.ft", "Sheets (packed)"])
for c in ss[5]: c.font, c.fill = Font(bold=True, color="FFFFFF"), gold
import math
_src = open(os.path.join(HERE, "make_laminate_cutlist.py")).read(); _ns = {}
exec(_src[_src.index("SW, SH, TRIM, KERF"):_src.index("rows, need = [], {}")], _ns)   # MaxRects packer
nsheets = lambda b: _ns["pack"]([(r[2], r[3]) for r in rows[b] for _ in range(r[4])])   # real sheet count (4 mm kerf), not area
order = sorted(rows, key=lambda b: (not b.endswith("both sides"), b.startswith("6 mm"), b))
for b in order:
    pcs = sum(r[4] for r in rows[b]); a = sum(r[2] * r[3] * r[4] for r in rows[b]) / 92903.04
    ss.append([b, pcs, round(a, 1), nsheets(b)])
ss.append(["TOTAL", sum(sum(r[4] for r in rows[b]) for b in order), "", sum(nsheets(b) for b in order)])
for c in ss[ss.max_row]: c.font = Font(bold=True)
ss.column_dimensions["A"].width = 52
for col in "BCD": ss.column_dimensions[col].width = 16
for b in order:
    name = b.replace("18 mm ply - ", "18 ").replace("6 mm ply - ", "6 ").replace(" / white inside", "").replace(" both sides", " 2S").replace(" one side", " 1S")[:31]
    ws = wb.create_sheet(name.replace("/", "-"))
    ws.append([f"BOARD: {b}"]); ws["A1"].font = Font(bold=True, size=12)
    ws.append(hdr)
    for c in ws[2]: c.font, c.fill = Font(bold=True, color="FFFFFF"), gold
    data = sorted(rows[b], key=lambda r: (-r[2], -r[3]))
    for i, r in enumerate(data, 1):
        ws.append([i] + r)
        for c in ws[ws.max_row]: c.border = Border(left=thin, right=thin, top=thin, bottom=thin)
        ws.cell(ws.max_row, 4).font = ws.cell(ws.max_row, 5).font = Font(bold=True)
    ws.append([]); ws.append(["", "", "Total pieces", "", "", sum(r[4] for r in data)])
    for col, w in zip("ABCDEFGHIJK", (5, 14, 44, 11, 11, 6, 9, 9, 9, 9, 48)): ws.column_dimensions[col].width = w
    ws.freeze_panes = "A3"; ws.print_title_rows = "2:2"
    ws.page_setup.orientation = "landscape"; ws.sheet_properties.pageSetUpPr.fitToPage = True; ws.page_setup.fitToHeight = 0
# ---- ONE PAGE: summary + all pieces of all boards on one sheet (first sheet)
one = wb.create_sheet("ALL - one page", 0)
one.append(["Mr. Manoker - 4 wardrobes - FACTORY CUT LIST (all boards) | Astra Interiors | " + time.strftime("%d-%m-%Y")]); one["A1"].font = Font(bold=True, size=13)
one.append(["CUT sizes (edge band already deducted). Edge L1 = front edge. Shutters 2 mm 4 sides; side cover / 100 strip 2 mm front edge only; skirting 0.5 mm top edge. Board 8x4."])
one.append([])
one.append(["", "Board type", "", "", "", "Pieces", "Sheets 8x4"])
for c in one[one.max_row]: c.font, c.fill = Font(bold=True, color="FFFFFF"), gold
for b in order:
    a_ = sum(r[2] * r[3] * r[4] for r in rows[b]) / 92903.04
    one.append(["", b, "", "", "", sum(r[4] for r in rows[b]), nsheets(b)])
one.append(["", "TOTAL", "", "", "", sum(sum(r[4] for r in rows[b]) for b in order),
            sum(nsheets(b) for b in order)])
for c in one[one.max_row]: c.font = Font(bold=True)
n_ = 0
band = PatternFill("solid", fgColor="EFE6DA")
for b in order:
    one.append([])
    one.append([f"BOARD: {b}"]); one.cell(one.max_row, 1).font = Font(bold=True, size=11)
    for c in one[one.max_row]: c.fill = band
    one.append(hdr)
    for c in one[one.max_row]: c.font, c.fill = Font(bold=True, color="FFFFFF"), gold
    for r in sorted(rows[b], key=lambda r: (-r[2], -r[3])):
        n_ += 1
        one.append([n_] + r)
        for c in one[one.max_row]: c.border = Border(left=thin, right=thin, top=thin, bottom=thin)
        one.cell(one.max_row, 4).font = one.cell(one.max_row, 5).font = Font(bold=True)
one.append([])
one.append(["LED profile groove: 12 W x 8 D, 100 mm from FRONT edge, on panel face inside the section (start above bottom panel)"]); one.cell(one.max_row, 1).font = Font(bold=True)
one.append(["", "Room", "Section / panel", "Start", "Length"])
for c in one[one.max_row]: c.font, c.fill = Font(bold=True, color="FFFFFF"), gold
for room, v in D.items():
    for gx in v["info"]["led"]:
        one.append(["", ROOM[room], f"Section {gx['section']} - {gx['panel']} ({gx['face']})", gx["start"], gx["length"]])
for col, w in zip("ABCDEFGHIJK", (5, 14, 44, 11, 11, 7, 9, 9, 9, 9, 46)): one.column_dimensions[col].width = w
one.page_setup.orientation = "landscape"; one.page_setup.paperSize = 9
one.sheet_properties.pageSetUpPr.fitToPage = True; one.page_setup.fitToWidth = 1; one.page_setup.fitToHeight = 0
one.freeze_panes = "A5"
wb.active = 0
# LED sheet
ls = wb.create_sheet("LED groove")
ls.append(["LED profile groove: 12 W x 8 D, 100 mm from FRONT edge, vertical, on panel face inside the section. Start = above bottom panel."])
ls.append(["Room", "Section", "Panel", "Face", "Start (mm)", "Groove length (mm)"])
for c in ls[2]: c.font, c.fill = Font(bold=True, color="FFFFFF"), gold
for room, v in D.items():
    for gx in v["info"]["led"]:
        ls.append([ROOM[room], gx["section"], gx["panel"], gx["face"], gx["start"], gx["length"]])
for col, w in zip("ABCDEF", (14, 9, 12, 28, 11, 18)): ls.column_dimensions[col].width = w
out = os.path.join(HERE, "Mr. Manoker - FACTORY Cut List.xlsx")
for cand in (out, out.replace(".xlsx", " (updated).xlsx"), out.replace(".xlsx", time.strftime(" (%H%M%S).xlsx"))):
    try: wb.save(cand); out = cand; break
    except PermissionError: continue
print("saved", out); print(wb.sheetnames)
for r in ss.iter_rows(min_row=6, values_only=True): print(r)
