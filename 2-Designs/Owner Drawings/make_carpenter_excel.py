"""Carpenter list: one sheet, bedroom by bedroom - pieces (with where it goes), hardware, LED grooves, fitting notes."""
import json, os, time, math
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
import owner_cutlist as oc
from openpyxl.drawing.image import Image as XLImage
from PIL import Image as PILImage
from openpyxl.worksheet.pagebreak import Break

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "owner_cutlist.json")))
TITLE = {"GF": "GF BEDROOM", "1F Master": "1ST FLOOR M.BEDROOM", "1F Bedroom 2": "1ST FLOOR BEDROOM 2", "2F": "2ND FLOOR BEDROOM"}
GNAME = {"Cupboard box": "CARCASS (18 mm, Ivory White)", "Loft frame 90 mm": "LOFT FRAME 90 mm", "Inside": "SHELVES",
         "Back panels 6 mm": "BACK PANELS 6 mm", "Drawers": "DRAWER BOX", "Shutters": "SHUTTERS / COVER / SKIRTING (colour laminate + backer)"}
dark = PatternFill("solid", fgColor="1F1A17"); band = PatternFill("solid", fgColor="EFE6DA"); thin = Side(style="thin", color="999999")


def where(g, part, note, room):
    if "Side panel (cupboard" in part: return "box ends; 6 mm back groove inner face; LED groove (see below)"
    if "full height, doors fixed" in part: return "between sections, doors hinge here; back groove both faces"
    if "Partition (inside)" in part: return "dressing / bangle column (stands on shelf, in front of back panel)"
    if part in ("Bottom panel", "Top panel"): return "box " + part.split()[0].lower()
    if "Frame upright" in part: return "loft frame - at ends and partitions"
    if "Top rail" in part: return "loft frame top, fix to ceiling"
    if "Bottom rail" in part: return "loft frame bottom, on cupboard top"
    if part == "Shelf": return "set back 20 mm from front"
    if "back panel" in part: return "slides in 6 mm groove (sides / partitions / top / bottom)"
    if "drawer side" in part or "front/back inner" in part: return "groove for bottom: leave 12, 8 W x 10 D"
    if "drawer bottom" in part: return "slides in the 10 mm groove"
    if "Drawer outside front" in part: return "screw to drawer box front; handle"
    if "Door above drawers" in part: return "doors above the drawers; 4 hinges"
    if "Door (full height)" in part: return "5 hinges each"
    if "Loft door" in part: return "on loft frame; same width as door below"
    if "Skirting" in part: return "front of base 80"
    if "Side cover" in part: return f"{oc.COVER_SIDE[room].upper()} end, 518 deep (flush with door front); joint at 2000"
    if "Wall-side strip" in part: return ("RIGHT" if oc.COVER_SIDE[room] == "left" else "LEFT") + " end at front, flush with doors; joint at 2000"
    return note


T3 = {"GF": "GF Bedroom", "1F Master": "1F M.Bedroom", "1F Bedroom 2": "1F Bedroom 2", "2F": "2F Bedroom"}


def add_images(ws, room, h_px=520, row_px=20):
    pairs = [((f"drawing_{room}.png", "2D drawing (inside, measurements)"), (f"shutters_{room}.png", "2D shutters with laminate codes")),
             ((f"3D - {T3[room]} - assembled (no doors).png", "3D - assembled box, no doors"), (f"3D - {T3[room]} - exploded pieces.png", "3D - exploded pieces"))]
    for pair in pairs:
        ws.row_breaks.append(Break(id=ws._current_row))     # each picture pair on its own printed page
        ws.append(["", pair[0][1], "", "", pair[1][1]])
        for c in ws[ws.max_row]: c.font = Font(bold=True, color="A9834A")
        top = ws._current_row + 1
        for (fn, cap), col in zip(pair, ("A", "E")):
            fp = os.path.join(HERE, fn)
            if not os.path.exists(fp):
                continue
            w0, h0 = PILImage.open(fp).size
            img = XLImage(fp); img.height = h_px; img.width = min(590, int(w0 * h_px / h0))
            if img.width == 590: img.height = int(h0 * 590 / w0)
            ws.add_image(img, f"{col}{top}")
        for _ in range(int(h_px / row_px) + 2):
            ws.append([])


def build(ws, rooms, title):
    ws.append([title]); ws["A1"].font = Font(bold=True, size=13)
    ws.append(["Sizes = CUT size (mm). Gaps: 2 mm between doors, 3 mm+ at ends (next to side cover / strip), 2 mm cupboard-to-loft door, 1 mm bottom and top."])
    n = 0
    for room in rooms:
        v = D[room]; inf = v["info"]
        if ws._current_row > 3:
            ws.row_breaks.append(Break(id=ws._current_row))      # each bedroom starts on a new page
        ws.append([])
        ws.append([f"{TITLE[room]}  -  box {inf['width']} W x {inf['height']} H x 500 D  (+ side cover {oc.COVER_SIDE[room]} + 100 strip = {inf['width'] + 36} W)"])
        ws.merge_cells(start_row=ws.max_row, start_column=1, end_row=ws.max_row, end_column=8)
        c = ws.cell(ws.max_row, 1); c.font, c.fill = Font(bold=True, size=12, color="FFFFFF"), dark
        last = None
        for r in v["rows"]:
            g, part, mat, q, L, W, cL, cW, edge, note = r
            if g != last:
                ws.append(["", GNAME.get(g, g)]); 
                for c in ws[ws.max_row]: c.font, c.fill = Font(bold=True), band
                ws.append(["No", "Part", "Laminate", "Qty", "Cut L", "Cut W", "Edge tape", "Where / fitting"])
                for c in ws[ws.max_row]: c.font = Font(bold=True, size=9)
                last = g
            n += 1
            lam = part.rsplit(" - ", 1)[1].split(" (")[0] if g == "Shutters" and " - " in part else ("Ivory White" if not mat.startswith("6") else "Ivory White 1 side")
            nm = part.rsplit(" - ", 1)[0] if g == "Shutters" and " - " in part else part
            nm = nm.replace("Bottom drawers (right section): ", "").replace("Bottom drawers: ", "")
            ws.append([n, nm, lam, q, cL, cW, edge, where(g, part, note, room)])
            for c in ws[ws.max_row]: c.border = Border(left=thin, right=thin, top=thin, bottom=thin)
            ws.cell(ws.max_row, 5).font = ws.cell(ws.max_row, 6).font = Font(bold=True)
        # hardware + LED
        ws.append(["", "HARDWARE"]); 
        for c in ws[ws.max_row]: c.font, c.fill = Font(bold=True), band
        for h in v["hardware"]:
            ws.append(["", h[0], "", h[1]])
        ws.append(["", "Skirting / cover screws, minifix / dowels, hinge plates as needed"])
        ws.append(["", "LED GROOVE (12 W x 8 D, 100 mm from front)"]); 
        for c in ws[ws.max_row]: c.font, c.fill = Font(bold=True), band
        for gx in inf["led"]:
            ws.append(["", f"Section {gx['section']} ({gx['opening']} wide): {gx['panel']}, right face", "", "", f"start {gx['start']} mm  ·  groove length {gx['length']} mm  ·  LED strip {gx['strip']} mm"])
        add_images(ws, room)
    for col, w in zip("ABCDEFGH", (5, 44, 22, 6, 9, 9, 14, 58)): ws.column_dimensions[col].width = w
    ws.page_setup.orientation = "landscape"; ws.page_setup.paperSize = 9
    ws.sheet_properties.pageSetUpPr.fitToPage = True; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0


if __name__ == "__main__":
    wb = Workbook()
    build(wb.active, list(D), "Mr. Manoker - 4 wardrobes - CARPENTER LIST | Astra Interiors | " + time.strftime("%d-%m-%Y"))
    wb.active.title = "ALL - one page"
    for room in D:
        build(wb.create_sheet(room), [room], f"{TITLE[room]} - CARPENTER LIST | Astra Interiors")
    out = os.path.join(HERE, "Mr. Manoker - CARPENTER List.xlsx")
    for cand in (out, out.replace(".xlsx", " (updated).xlsx"), out.replace(".xlsx", time.strftime(" (%H%M%S).xlsx"))):
        try: wb.save(cand); out = cand; break
        except PermissionError: continue
    print("saved", out); print(wb.sheetnames)
