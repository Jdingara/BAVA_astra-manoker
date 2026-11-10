"""One Excel: Summary + 4 bedroom cut lists + LED groove + Plywood & Laminate (copied from the two generated workbooks)."""
import os, time
from copy import copy
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment

HERE = os.path.dirname(os.path.abspath(__file__))
wb = load_workbook(os.path.join(HERE, "Owner Drawings - Wardrobe Cut List (500 depth).xlsx"))
mw = load_workbook(os.path.join(HERE, "Owner Drawings - Plywood and Laminate List.xlsx")).active
ms = wb.create_sheet("Plywood + Laminate")
for row in mw.iter_rows():
    for c in row:
        n = ms.cell(row=c.row, column=c.column, value=c.value)
        if c.has_style:
            n.font, n.fill, n.alignment = copy(c.font), copy(c.fill), copy(c.alignment)
for k, dim in mw.column_dimensions.items():
    ms.column_dimensions[k].width = dim.width
thin = Side(style="thin", color="999999")
fills = {"Cupboard box": "FFFFFF", "Loft frame 90 mm": "EEF3FA", "Inside": "FFFFFF", "Back panels 6 mm": "F5F5F5", "Drawers": "FFF7EC", "Shutters": "F3EEF8"}
for name in ["GF", "1F Master", "1F Bedroom 2", "2F"]:
    ws = wb[name]
    for r in ws.iter_rows(min_row=2):
        if r[0].value is None and r[2].value is None:
            continue
        for c in r[:11]:
            c.border = Border(left=thin, right=thin, top=thin, bottom=thin)
        g = r[1].value
        if g in fills:
            for c in r[:11]:
                c.fill = PatternFill("solid", fgColor=fills[g])
    ws.page_setup.orientation = "landscape"; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = "2:2"
out = os.path.join(HERE, "Mr. Manoker - Wardrobe Cut List FINAL.xlsx")
for cand in (out, out.replace(".xlsx", " (updated).xlsx"), out.replace(".xlsx", time.strftime(" (%H%M%S).xlsx"))):
    try:
        wb.save(cand); out = cand; break
    except PermissionError:
        continue
print("saved", out); print(wb.sheetnames)
