"""Laminate cut list: every piece of the wardrobe cut list with the laminate on face 1 / face 2,
laminate piece size (+10 mm each way for trimming), and sheets needed per laminate by packing on 8x4 (2440 x 1220)."""
import json, math, os, time
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "owner_cutlist.json")))
WHITE = "White laminate (code to confirm)"
GF_SWAP = {"27173 LV Seaglass": "DC687 Foliage Blue (Advance)", "21125 Sunburn": "21125 MR+ Sunburn (Merino)"}
ROOM = {"GF": "GF Bedroom", "1F Master": "1F M.Bedroom", "1F Bedroom 2": "1F Bedroom 2", "2F": "2F Bedroom"}
SW, SH, TRIM, KERF = 2440, 1220, 6, 4


def faces(room, g, part, mat):
    if g == "Shutters":
        col = part.rsplit(" - ", 1)[1].split(" (")[0]
        if room == "GF":
            col = GF_SWAP.get(col, col)
        if "Side cover" in part or "Wall-side strip" in part or "Skirting" in part:
            return col, None                       # back face is hidden (against carcass / wall / base)
        return col, WHITE                          # door: colour outside, white inside
    if mat.startswith("6 mm"):
        return WHITE, None
    return WHITE, WHITE                            # carcass, shelves, partitions, SIDE PANELS, drawer box, loft frame


def pack(pieces, trim_kerf=KERF):
    """MaxRects (best short side fit, rotation allowed) on 2440 x 1220; tries several orders, returns fewest sheets"""
    def run(order):
        bins = []
        for (L, W) in order:
            w0, h0 = L + trim_kerf, W + trim_kerf
            best = None
            for bi, free in enumerate(bins):
                for fr in free:
                    for (w, h) in ((w0, h0), (h0, w0)):
                        if w <= fr[2] and h <= fr[3]:
                            sc = min(fr[2] - w, fr[3] - h)
                            if best is None or sc < best[0]:
                                best = (sc, bi, fr[0], fr[1], w, h)
            if best is None:
                bins.append([(0, 0, SW, SH)])
                bi = len(bins) - 1
                w, h = (w0, h0) if w0 <= SW and h0 <= SH else (h0, w0)
                best = (0, bi, 0, 0, w, h)
            _, bi, x, y, w, h = best
            nf = []
            for fr in bins[bi]:
                fx, fy, fw, fh = fr
                if x >= fx + fw or x + w <= fx or y >= fy + fh or y + h <= fy:
                    nf.append(fr); continue
                if x > fx: nf.append((fx, fy, x - fx, fh))
                if x + w < fx + fw: nf.append((x + w, fy, fx + fw - x - w, fh))
                if y > fy: nf.append((fx, fy, fw, y - fy))
                if y + h < fy + fh: nf.append((fx, y + h, fw, fy + fh - y - h))
            bins[bi] = [a for a in nf if not any(a != b and a[0] >= b[0] and a[1] >= b[1] and a[0] + a[2] <= b[0] + b[2] and a[1] + a[3] <= b[1] + b[3] for b in nf)]
        return len(bins)
    orders = [sorted(pieces, key=k) for k in (lambda p: -p[0] * p[1], lambda p: -max(p), lambda p: -min(p), lambda p: -(p[0] + p[1]))]
    return min(run(o) for o in orders)


rows, need = [], {}
for room, v in D.items():
    for g, part, mat, q, L, W, cL, cW, edge, note in v["rows"]:
        f1, f2 = faces(room, g, part, mat)
        lp = (L + TRIM, W + TRIM)
        nm = part.rsplit(" - ", 1)[0] if g == "Shutters" and " - " in part else part
        rows.append([ROOM[room], g, nm, mat, q, cL, cW, f1, f2 or "-", f"{lp[0]:.0f} x {lp[1]:.0f}"])
        for f in (f1, f2):
            if f:
                need.setdefault(f, []).extend([lp] * q)

res = []
for lam, ps in sorted(need.items(), key=lambda kv: kv[0] == WHITE):
    area = sum(a * b for a, b in ps) / 92903.04
    res.append((lam, len(ps), round(area, 1), pack(ps)))

wb = Workbook(); ws = wb.active; ws.title = "Laminate summary"
dark = PatternFill("solid", fgColor="1F1A17"); thin = Side(style="thin", color="999999")
ws.append(["Mr. Manoker - 4 wardrobes - LAMINATE LIST (from the cut list) | Astra Interiors | " + time.strftime("%d-%m-%Y")]); ws["A1"].font = Font(bold=True, size=13)
ws.append(["Every piece counted: side panels, top/bottom, partitions, shelves, drawer box, loft frame = white both faces; 6 mm = white one face;"])
ws.append(["shutters = colour outside + white inside; side cover / 100 strip / skirting = colour one face. Laminate piece = cut size + 10 mm. Sheets = laid out on 8x4 (2440x1220)."])
ws.append([])
ws.append(["Laminate", "Faces (pieces)", "Area sq.ft", "Sheets 8x4 (laid out)"])
for c in ws[ws.max_row]: c.font, c.fill = Font(bold=True, color="FFFFFF"), dark
for r in res: ws.append(list(r))
ws.append(["TOTAL", sum(r[1] for r in res), round(sum(r[2] for r in res), 1), sum(r[3] for r in res)])
for c in ws[ws.max_row]: c.font = Font(bold=True)
for col, w in zip("ABCD", (44, 15, 12, 22)): ws.column_dimensions[col].width = w
cl = wb.create_sheet("Cut list + laminate")
cl.append(["Room", "Group", "Part", "Board", "Qty", "Cut L", "Cut W", "Laminate face 1", "Laminate face 2", "Lam piece (L x W)"])
for c in cl[1]: c.font, c.fill = Font(bold=True, color="FFFFFF"), dark
for r in rows:
    cl.append(r)
    for c in cl[cl.max_row]: c.border = Border(left=thin, right=thin, top=thin, bottom=thin)
for col, w in zip("ABCDEFGHIJ", (13, 16, 40, 12, 5, 8, 8, 30, 30, 16)): cl.column_dimensions[col].width = w
cl.freeze_panes = "A2"
out = os.path.join(HERE, "Mr. Manoker - Laminate List from Cut List.xlsx")
for cand in (out, out.replace(".xlsx", time.strftime(" (%H%M).xlsx"))):
    try:
        wb.save(cand); out = cand; break
    except PermissionError:
        continue
print("saved", out)
for r in res: print(r)
print("TOTAL sheets", sum(r[3] for r in res))
