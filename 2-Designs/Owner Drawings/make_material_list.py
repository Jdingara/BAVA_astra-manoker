"""Plywood + laminate list for the 4 wardrobes, from owner_cutlist.json.
Laminate rules: shutters = colour outside + backer inside; carcass 18 mm pieces = off-white both faces;
6 mm backs / drawer bottoms = off-white one face (inside). Sheets 8x4 = 32 sq.ft, +15% waste."""
import json, math, os, time
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "owner_cutlist.json")))
OFF = "White laminate (inside: carcass both sides + 6 mm one side + shutter back) - Merino white, code to confirm"
BACKER = OFF   # owner: no liner, shutter back = same white laminate
TITLES = {"GF": "GF Bedroom", "1F Master": "1st Floor M.Bedroom", "1F Bedroom 2": "1st Floor Bedroom 2", "2F": "2nd Floor Bedroom"}
SQ = 92903.04
sheets = lambda a: math.ceil(a * 1.15 / 32)

res = {}
for k, v in d.items():
    ply = {"18 mm ply (carcass / shelves / drawers / loft frame)": 0.0, "18 mm ply (shutters)": 0.0, "6 mm ply (backs / drawer bottoms)": 0.0}
    lam = {}
    for g, part, mat, q, L, W, cL, cW, edge, note in v["rows"]:
        a = q * L * W / SQ
        if g == "Shutters":
            ply["18 mm ply (shutters)"] += a
            col = part.rsplit(" - ", 1)[1]
            lam[col] = lam.get(col, 0) + a
            lam[BACKER] = lam.get(BACKER, 0) + a           # shutter inside face = backer
        elif mat.startswith("6 mm"):
            ply["6 mm ply (backs / drawer bottoms)"] += a
            lam[OFF] = lam.get(OFF, 0) + a
        else:
            ply["18 mm ply (carcass / shelves / drawers / loft frame)"] += a
            lam[OFF] = lam.get(OFF, 0) + 2 * a
    res[k] = (ply, lam)

wb = Workbook(); ws = wb.active; ws.title = "Plywood + Laminate"
gold = PatternFill("solid", fgColor="EFE6DA")
ws.append(["Mr. Manoker - 4 wardrobes - Plywood and laminate list (8 x 4 sheets, 15% waste) | Astra Interiors"]); ws["A1"].font = Font(bold=True, size=12)
ws.append(["Laminate: shutters = colour outside + backer inside; carcass 18 mm = off-white both faces; 6 mm back / drawer bottom = off-white one face."])
ws.append([])
tot_ply, tot_lam = {}, {}
for k, (ply, lam) in res.items():
    ws.append([TITLES[k]]); ws.cell(ws.max_row, 1).font = Font(bold=True, size=11)
    ws.append(["Item", "Area sq.ft", "Sheets 8x4"])
    for c in ws[ws.max_row]: c.font, c.fill = Font(bold=True), gold
    for n, a in ply.items():
        ws.append([n, round(a, 1), sheets(a)]); tot_ply[n] = tot_ply.get(n, 0) + sheets(a)
    for n, a in sorted(lam.items(), key=lambda x: (x[0] == OFF, x[0] == BACKER)):
        ws.append(["Laminate " + n, round(a, 1), sheets(a)]); tot_lam[n] = tot_lam.get(n, 0) + sheets(a)
    ws.append([])
ws.append(["TOTAL - all 4 bedrooms"]); ws.cell(ws.max_row, 1).font = Font(bold=True, size=12)
ws.append(["Item", "", "Sheets 8x4"])
for c in ws[ws.max_row]: c.font, c.fill = Font(bold=True), gold
for n, s in tot_ply.items(): ws.append([n, "", s])
for n, s in sorted(tot_lam.items(), key=lambda x: (x[0] == OFF, x[0] == BACKER)): ws.append(["Laminate " + n, "", s])
ws.column_dimensions["A"].width = 62; ws.column_dimensions["B"].width = 12; ws.column_dimensions["C"].width = 12
out = os.path.join(HERE, "Owner Drawings - Plywood and Laminate List.xlsx")
for cand in (out, out.replace(".xlsx", " (updated).xlsx"), out.replace(".xlsx", time.strftime(" (%H%M%S).xlsx"))):
    try: wb.save(cand); out = cand; break
    except PermissionError: continue
print("saved", out)
for k, (ply, lam) in res.items():
    print(k, {n[:22]: (round(a, 1), sheets(a)) for n, a in ply.items()}, {n: (round(a, 1), sheets(a)) for n, a in lam.items()})
print(tot_ply); print(tot_lam)
