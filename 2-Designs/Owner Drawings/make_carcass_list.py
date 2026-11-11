"""CARCASS ONLY cut list (box, partitions, shelves, dressing top, loft frame, 6 mm backs) - no shutters, no drawer boxes.
owner_cutlist.json -> "Mr. Manoker - CARCASS Cut List.xlsx" + ".pdf" (A4 landscape)."""
import html
import json
import math
import os
import time

import pymupdf
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "owner_cutlist.json")))
ROOM = {"GF": "GF Bedroom", "1F Master": "1F M.Bedroom", "1F Bedroom 2": "1F Bedroom 2", "2F": "2F Bedroom"}
GROUPS = ("Cupboard box", "Inside", "Loft frame 90 mm", "Back panels 6 mm")
BOARD = {"18 mm ply": "18 mm ply - WHITE both sides (code to confirm)", "6 mm back ply": "6 mm ply - WHITE one side (code to confirm)"}
COLS = ["No", "Room", "Part", "Cut L", "Cut W", "Qty", "Edge tape", "Note"]

rows = {}
for room, v in D.items():
    for g, part, mat, q, L, W, cl, cw, edge, note in v["rows"]:
        if g in GROUPS and q:
            rows.setdefault(BOARD[mat], []).append([ROOM[room], part, cl, cw, q, "0.5 mm front edge" if edge.startswith("0.5") else "-", note])
for b in rows:
    rows[b].sort(key=lambda r: (-r[2], -r[3], r[0]))


def sheets(rs):
    return math.ceil(sum(r[2] * r[3] * r[4] for r in rs) / (2440 * 1220) * 1.15)


title = f"Mr. Manoker - 4 wardrobes - CARCASS ONLY cut list | Astra Interiors | {time.strftime('%d-%m-%Y')}"
notes = ["CUT sizes (0.5 mm edge tape already deducted on the front edge). Board 8x4 (2440 x 1220).",
         "Total depth 500 = carcass 494 + 6 mm back. Back is OUTER TO OUTER, 2000 high, screwed on the back edges (no groove); joints on partition centres.",
         "NOT in this list: shutters / drawer fronts / skirting / side cover / 100 strip, and drawer boxes (they come in the next list)."]

# ---- Excel
wb = Workbook()
ws = wb.active
ws.title = "CARCASS"
gold = PatternFill("solid", fgColor="EFE6DA")
ws.append([title]); ws["A1"].font = Font(bold=True, size=12)
for n in notes:
    ws.append([n])
ws.append([])
ws.append(["Board", "", "Pieces", "Sheets 8x4 (+15%)"])
for c in ws[ws.max_row]:
    c.font, c.fill = Font(bold=True), gold
for b, rs in rows.items():
    ws.append([b, "", sum(r[4] for r in rs), sheets(rs)])
ws.append(["TOTAL", "", sum(r[4] for rs in rows.values() for r in rs), sum(sheets(rs) for rs in rows.values())])
ws[ws.max_row][0].font = Font(bold=True)
for b, rs in rows.items():
    ws.append([])
    ws.append([f"BOARD: {b}"]); ws[ws.max_row][0].font = Font(bold=True, size=11)
    ws.append(COLS)
    for c in ws[ws.max_row]:
        c.font, c.fill = Font(bold=True), gold
    for i, r in enumerate(rs, 1):
        ws.append([i] + r)
for col, w in zip("ABCDEFGH", (6, 14, 40, 8, 8, 5, 16, 60)):
    ws.column_dimensions[col].width = w
xl = os.path.join(HERE, "Mr. Manoker - CARCASS Cut List.xlsx")
for cand in (xl, xl.replace(".xlsx", " (updated).xlsx"), xl.replace(".xlsx", time.strftime(" (%H%M%S).xlsx"))):
    try:
        wb.save(cand); print("saved", os.path.basename(cand)); break
    except PermissionError:
        continue

# ---- PDF
th = lambda cs: "<tr style='background-color:#efe6da;'>" + "".join(f"<th>{html.escape(str(c))}</th>" for c in cs) + "</tr>"
td = lambda cs: "<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in cs) + "</tr>"
h = [f"<body style='font-family: sans-serif; font-size: 8pt;'><p style='font-weight:bold; font-size:11pt; color:#7a5a30;'>{html.escape(title)}</p>"]
h += [f"<p>{html.escape(n)}</p>" for n in notes]
h.append("<table border='1' cellpadding='3' style='border-collapse: collapse;'>" + th(["Board", "Pieces", "Sheets 8x4"]))
h += [td([b, sum(r[4] for r in rs), sheets(rs)]) for b, rs in rows.items()]
h.append(td(["TOTAL", sum(r[4] for rs in rows.values() for r in rs), sum(sheets(rs) for rs in rows.values())]) + "</table>")
for b, rs in rows.items():
    h.append(f"<p style='font-weight:bold; font-size:10pt; color:#7a5a30;'>BOARD: {html.escape(b)}</p>")
    h.append("<table border='1' cellpadding='2' style='border-collapse: collapse; width:100%;'>" + th(COLS))
    h += [td([i] + r) for i, r in enumerate(rs, 1)]
    h.append("</table>")
h.append("</body>")
story = pymupdf.Story("".join(h))
rect = pymupdf.paper_rect("a4-l")
pdf = os.path.join(HERE, "Mr. Manoker - CARCASS Cut List.pdf")
for cand in (pdf, pdf.replace(".pdf", " (updated).pdf"), pdf.replace(".pdf", time.strftime(" (%H%M%S).pdf"))):
    try:
        w = pymupdf.DocumentWriter(cand)
        more = True
        while more:
            dev = w.begin_page(rect)
            more, _ = story.place(rect + (28, 28, -28, -28))
            story.draw(dev)
            w.end_page()
        w.close()
        print("saved", os.path.basename(cand)); break
    except (PermissionError, RuntimeError):
        continue
for b, rs in rows.items():
    print(b, sum(r[4] for r in rs), "pcs", sheets(rs), "sheets")
