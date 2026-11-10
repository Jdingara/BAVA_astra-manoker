"""Astra Interiors - kitchen gas unit 2060 x 710 x 540 for Mr. Manoker.
Basket sections: inside width = basket 600 mm + 24 mm telescopic channels = 624 mm. Balance width = gas cylinder with 2 doors.
Writes AutoCAD DXF, Excel cut list (with basket order list) and PDF. Sizes in mm."""
import math
import os
import sys
import time

import ezdxf
from ezdxf.enums import TextEntityAlignment
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from wardrobe_sheets import make_sheets  # noqa: E402

NAME = "Kitchen Gas Unit 2060"
TITLE = "Kitchen gas unit 2060 (2 basket sections 600 mm + gas cylinder with 2 doors)"
W, H, D = 2060.0, 710.0, 540.0
T, GAP, BACK = 18.0, 3.0, 6.0
IN = 25.4
BASKET_W, CHANNEL = 600.0, 24.0          # basket width + telescopic channel allowance (both sides together)
# optional: python make_unit_2060.py 21   -> all baskets 21 inch (533.4 mm)
VARIANT = ""
if len(sys.argv) > 1:
    w_in = float(sys.argv[1])
    BASKET_W = round(w_in * 25.4, 1)
    VARIANT = f" - {w_in:g} inch baskets"
BASKET_D = 500.0                          # basket depth (market 20 in ~ 500-508)
# baskets per section from BOTTOM to TOP: (type, height inch)
BASKET_SECTIONS = [
    [("Plate basket", 8), ("Cup & saucer basket", 6), ("Cutlery basket", 4)],
    [("Utility basket", 10), ("Utility / thali basket", 8)],
]
DOORS = 2
COLS = {"A": "Front laminate (code to be given)"}


def _locked(path):
    if not os.path.exists(path):
        return False
    try:
        with open(path, "a"):
            return False
    except PermissionError:
        return True


NAME = NAME + VARIANT
TITLE = TITLE.replace("600 mm", f"{BASKET_W:.0f} mm")
if any(_locked(os.path.join(HERE, f"{NAME} - {x}")) for x in ("AutoCAD 2D.dxf", "Cut List.xlsx", "Drawing & Cut List.pdf", "Drawing.png")):
    NAME = NAME + time.strftime(" (%H%M)")

# ---------------------------------------------------------------- layout
SEC_W = BASKET_W + CHANNEL
clears = [SEC_W] * len(BASKET_SECTIONS)
door_clear = W - 2 * T - len(clears) * T - sum(clears)
assert door_clear >= 360, f"gas section too narrow: {door_clear:.0f} mm"
clears.append(door_clear)
NS = len(clears)
xs, x = [], T
for c in clears:
    xs.append(x)
    x += c + T
part_x = [xs[i] - T for i in range(1, NS)]
bounds = [0.0] + [px + T / 2 for px in part_x] + [W]
BOT, TOP = T, H - T
inner_h = TOP - BOT

# ---------------------------------------------------------------- DXF
doc = ezdxf.new("R2010", setup=True)
doc.units = ezdxf.units.MM
doc.header["$INSUNITS"] = 4
msp = doc.modelspace()
for n, c in {"0-OUTLINE": 7, "1-CARCASS": 7, "2-FRONTS": 3, "3-BASKETS": 5, "4-HANDLE": 40, "5-INTERNAL": 8,
             "7-DIM": 1, "8-TEXT": 7, "10-TITLE": 7}.items():
    doc.layers.add(n, color=c)
ds = doc.dimstyles.get("EZDXF")
ds.dxf.dimtxt, ds.dxf.dimasz, ds.dxf.dimexe, ds.dxf.dimexo, ds.dxf.dimgap = 26, 20, 12, 8, 8


def rect(x, y, w, h, layer, ox=0.0, oy=0.0):
    msp.add_lwpolyline([(ox + x, oy + y), (ox + x + w, oy + y), (ox + x + w, oy + y + h), (ox + x, oy + y + h)], close=True, dxfattribs={"layer": layer})


def text(s, x, y, h=28, layer="8-TEXT", align=TextEntityAlignment.MIDDLE_CENTER):
    msp.add_text(s, height=h, dxfattribs={"layer": layer, "style": "OpenSans"}).set_placement((x, y), align=align)


def dimh(x1, x2, y, base_y, label=None, ox=0.0):
    msp.add_linear_dim(base=(ox + x1, base_y), p1=(ox + x1, y), p2=(ox + x2, y), dimstyle="EZDXF",
                       text=label or f"{abs(x2 - x1):.0f}", dxfattribs={"layer": "7-DIM"}).render()


def dimv(y1, y2, x, base_x, label=None, ox=0.0):
    msp.add_linear_dim(base=(ox + base_x, y1), p1=(ox + x, y1), p2=(ox + x, y2), angle=90, dimstyle="EZDXF",
                       text=label or f"{abs(y2 - y1):.0f}", dxfattribs={"layer": "7-DIM"}).render()


fronts, basket_rows = [], []
rect(0, 0, W, H, "0-OUTLINE")
for si, baskets in enumerate(BASKET_SECTIONS):
    x0, x1 = bounds[si], bounds[si + 1]
    weights = [b[1] + 2 for b in baskets]                  # basket height + ~2 in clearance
    tot = sum(weights)
    z = 0.0
    for k, ((bname, b_in), wgt) in enumerate(zip(baskets, weights)):
        fh = H * wgt / tot
        rect(x0 + GAP / 2, z + GAP / 2, x1 - x0 - GAP, fh - GAP, "2-FRONTS")
        ln = min((x1 - x0) * 0.4, 260)
        rect((x0 + x1) / 2 - ln / 2, z + fh - 45, ln, 10, "4-HANDLE")
        text(f"{bname} {BASKET_W:.0f} x {BASKET_D:.0f} x {b_in}\"", (x0 + x1) / 2, z + fh / 2, 20)
        fronts.append(("Basket front", x1 - x0 - GAP, fh - GAP))
        basket_rows.append([si + 1, k + 1, bname, f"{BASKET_W:.0f} W x {BASKET_D:.0f} D mm x {b_in} in H", round(SEC_W),
                            round(D - BACK), round(z), round(fh)])
        dimv(z, z + fh, x1, x1 + 40)
        z += fh
xd0, xd1 = bounds[-2], bounds[-1]
dw = (xd1 - xd0) / DOORS
for k in range(DOORS):
    xx = xd0 + k * dw
    rect(xx + GAP / 2, GAP / 2, dw - GAP, H - GAP, "2-FRONTS")
    rect(xx + dw - 40 if k == 0 else xx + 30, H * 0.45, 10, 250, "4-HANDLE")
    fronts.append(("Door", dw - GAP, H - GAP))
text("GAS CYLINDER", (xd0 + xd1) / 2, H * 0.3, 26)
dimh(0, W, 0, -150, f"{W:.0f}")
for si in range(NS):
    dimh(bounds[si], bounds[si + 1], H, H + 80)
dimv(0, H, 0, -150, f"{H:.0f}")
text("FRONT ELEVATION", W / 2, -320, 48)
text("CARCASS & FRONTS: 18 mm PLY   |   BACK PANELS: 6 mm PLY   |   EDGE BAND: fronts 2 mm, carcass 0.5 mm", W / 2, -400, 28)

IX = W + 700
rect(0, 0, W, H, "0-OUTLINE", IX)
rect(0, 0, T, H, "1-CARCASS", IX)
rect(W - T, 0, T, H, "1-CARCASS", IX)
rect(T, 0, W - 2 * T, T, "1-CARCASS", IX)
rect(T, H - T, W - 2 * T, T, "1-CARCASS", IX)
for px in part_x:
    rect(px, BOT, T, inner_h, "1-CARCASS", IX)
for si, baskets in enumerate(BASKET_SECTIONS):
    a = xs[si]
    z = BOT
    weights = [b[1] + 2 for b in baskets]
    tot = sum(weights)
    for (bname, b_in), wgt in zip(baskets, weights):
        slot = inner_h * wgt / tot
        rect(a + CHANNEL / 2, z + 15, BASKET_W, b_in * IN, "3-BASKETS", IX)
        text(bname, IX + a + SEC_W / 2, z + 15 + b_in * IN / 2 + 10, 20)
        text(f"{BASKET_W:.0f} x {BASKET_D:.0f} x {b_in} in", IX + a + SEC_W / 2, z + 15 + b_in * IN / 2 - 22, 18)
        z += slot
    dimh(a, a + SEC_W, BOT, -110, f"{SEC_W:.0f} ({BASKET_W:.0f} + {CHANNEL:.0f})", ox=IX)
dimh(xs[-1], xs[-1] + clears[-1], BOT, -110, f"{clears[-1]:.0f}", ox=IX)
text("GAS CYLINDER", IX + xs[-1] + clears[-1] / 2, H * 0.55, 28)
text("(open inside, 2 doors)", IX + xs[-1] + clears[-1] / 2, H * 0.45, 22)
text(f"INSIDE ELEVATION - baskets {BASKET_W:.0f} mm + {CHANNEL:.0f} mm telescopic channel", IX + W / 2, -320, 40)

SY = -1400.0
rect(0, 0, D, H, "1-CARCASS", 0, SY)
rect(D - BACK - 6, T, BACK, H - 2 * T, "5-INTERNAL", 0, SY)
rect(-T, 0, T, H, "2-FRONTS", 0, SY)
rect(10, T + 15, BASKET_D, 8 * IN, "3-BASKETS", 0, SY)
dimh(10, 10 + BASKET_D, SY + T + 15 + 8 * IN, SY + H - 50, f"basket {BASKET_D:.0f}")
dimh(0, D, SY, SY - 110, f"{D:.0f}")
dimv(SY, SY + H, D, D + 90, f"{H:.0f}")
text("SIDE SECTION", D / 2, SY - 280, 48)

TBX, TBY, TBW = -200, -2050, 2 * W + 900
rect(TBX, TBY, TBW, 300, "10-TITLE")
for i, (k, v) in enumerate([("PROJECT", "Mr. Manoker - kitchen gas unit"), ("UNIT", f"{W:.0f} L x {H:.0f} H x {D:.0f} D"),
                            ("PLY / BASKETS", f"18 mm ply, 6 mm back | 2 x ({BASKET_W:.0f}+{CHANNEL:.0f}), gas {door_clear:.0f}"), ("BY", "ASTRA INTERIORS  +91 97911 82789")]):
    xx = TBX + i * TBW / 4
    if i:
        msp.add_line((xx, TBY), (xx, TBY + 300), dxfattribs={"layer": "10-TITLE"})
    text(k, xx + 25, TBY + 230, 28, "10-TITLE", TextEntityAlignment.LEFT)
    text(v, xx + 25, TBY + 100, 36, "10-TITLE", TextEntityAlignment.LEFT)
DXF_PATH = os.path.join(HERE, f"{NAME} - AutoCAD 2D.dxf")
doc.saveas(DXF_PATH)

# ---------------------------------------------------------------- cut list
C18, B6, FA = "18 mm ply", "6 mm back ply", "18 mm ply front - A (code to be given)"
cut = []


def add(group, part, mat, qty, Lmm, Wmm, edge):
    eb = 2.0 if edge == "4 sides" else 0.5 if edge == "1 long" else 0.0
    cL = Lmm - 2 * eb if edge == "4 sides" else Lmm
    cW = Wmm - 2 * eb if edge == "4 sides" else Wmm - eb
    cut.append([group, part, mat, qty, round(Lmm, 1), round(Wmm, 1), round(cL, 1), round(cW, 1),
                {"4 sides": "2 mm, 4 sides", "1 long": "0.5 mm, 1 long"}.get(edge, edge)])


add("Carcass", "Side panel L/R", C18, 2, H, D, "1 long")
add("Carcass", "Top", C18, 1, W - 2 * T, D, "1 long")
add("Carcass", "Bottom", C18, 1, W - 2 * T, D, "1 long")
add("Carcass", "Partition", C18, NS - 1, inner_h, D - BACK, "1 long")
for si, c in enumerate(clears):
    add("Carcass", f"Back panel section {si + 1}", B6, 1, inner_h + 12, c + 12, "-")
grp = {}
for kind, fw, fh in fronts:
    key = (kind, round(fw, 1), round(fh, 1))
    grp[key] = grp.get(key, 0) + 1
for (kind, fw, fh), q in grp.items():
    add("Fronts", kind, FA, q, fh if kind == "Door" else fw, fw if kind == "Door" else fh, "4 sides")

sqft = lambda r: r[3] * r[4] * r[5] / 92903.04
by = {}
for r in cut:
    by[r[2]] = by.get(r[2], 0) + sqft(r)
mats = [[m, round(by.get(m, 0), 1), math.ceil(by.get(m, 0) * 1.15 / 32)] for m in (C18, B6, FA)]
mats.append(["Inner liner laminate (front backs)", round(by.get(FA, 0), 1), math.ceil(by.get(FA, 0) * 1.15 / 32)])
mats.append(["Edge band 2 mm (fronts)", f"{math.ceil(sum(r[3] * 2 * (r[4] + r[5]) for r in cut if r[8].startswith('2 mm')) / 1000 * 1.1)} m", ""])
mats.append(["Edge tape 0.5 mm (carcass fronts)", f"{math.ceil(sum(r[3] * r[4] for r in cut if r[8].startswith('0.5')) / 1000 * 1.1)} m", ""])
n_b = sum(len(b) for b in BASKET_SECTIONS)
hardware = [[f"SS basket: {r[2]} {r[3]} (section {r[0]}, {r[1]} from bottom)", 1] for r in basket_rows]
hardware += [["Telescopic channel pairs for baskets (24 mm total allowance)", n_b],
             ["Soft-close hinges (gas doors)", 2 * DOORS], ["Handles (baskets + doors)", n_b + DOORS],
             ["Shelf pins / minifix", "as required"], ["Legs or base (if needed)", "optional"]]

wb = Workbook()
gold = PatternFill("solid", fgColor="EFE6DA")
ws = wb.active
ws.title = "Basket order list"
ws.append(["Section", "Position (from bottom)", "Basket type", "Basket size", "Inside width (mm)", "Inside depth (mm)",
           "Front from floor (mm)", "Front height (mm)"])
for c in ws[1]:
    c.font, c.fill = Font(bold=True), gold
for r in basket_rows:
    ws.append(r)
ws.append([])
ws.append([f"Each basket section: inside width {SEC_W:.0f} mm = basket {BASKET_W:.0f} mm + {CHANNEL:.0f} mm telescopic channels. "
           f"Balance {door_clear:.0f} mm = gas cylinder section with {DOORS} doors."])
for col, wdt in zip("ABCDEFGH", (9, 20, 24, 30, 16, 16, 18, 16)):
    ws.column_dimensions[col].width = wdt
cl = wb.create_sheet("Cut list")
cl.append([f"{TITLE} - Mr. Manoker - cut list (mm) | {W:.0f} x {H:.0f} x {D:.0f} | Astra Interiors"])
cl.append(["No", "Group", "Part", "Material", "Qty", "Finished L", "Finished W", "Cut L", "Cut W", "Edge band", "Sq.ft"])
for c in cl[2]:
    c.font, c.fill = Font(bold=True), gold
for i, r in enumerate(cut, 1):
    cl.append([i] + r + [round(sqft(r), 1)])
cl.append([])
cl.append(["", "", "Total pieces", "", sum(r[3] for r in cut)])
for col, wdt in zip("ABCDEFGHIJK", (5, 14, 26, 36, 6, 11, 11, 10, 10, 15, 8)):
    cl.column_dimensions[col].width = wdt
for title, rows, hdr in (("Materials", mats, ["Material", "Area sq.ft / length", "8x4 sheets (15% waste)"]), ("Hardware", hardware, ["Item", "Qty"])):
    s = wb.create_sheet(title)
    s.append(hdr)
    for r in rows:
        s.append(r)
    for c in s[1]:
        c.font, c.fill = Font(bold=True), gold
    s.column_dimensions["A"].width, s.column_dimensions["B"].width, s.column_dimensions["C"].width = 64, 20, 22
XLSX_PATH = os.path.join(HERE, f"{NAME} - Cut List.xlsx")
wb.save(XLSX_PATH)

data = {"name": NAME, "title": TITLE, "colours": COLS, "cut": cut, "sqft": [round(sqft(r), 1) for r in cut],
        "mats": mats, "hardware": hardware, "geom": {"W": W, "H": H, "DT": D, "P": 0}}
make_sheets(HERE, data)
print("DXF:", DXF_PATH)
print("sections inside:", [round(c) for c in clears], "| front edges:", [round(b) for b in bounds])
for r in basket_rows:
    print("  ", r)
for r in cut:
    print("  ", r)
