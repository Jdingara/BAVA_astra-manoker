"""Pieces sheet for the carpenter: every cut-list row drawn to scale (one rectangle per row, x qty), numbered as in Excel."""
import json, os, re, textwrap
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "owner_cutlist.json")))
HEX = {"DC687": "#46707a", "27173": "#77a99b", "21125": "#9b6638", "27292": "#d9cdd2", "27262": "#075f7f",
       "21433": "#035f33", "21457": "#f7cd0b", "21462": "#a994c7", "21452": "#5c2568"}
GC = {"Cupboard box": "#ece4d2", "Loft frame 90 mm": "#dfe8f3", "Inside": "#f4eedf", "Back panels 6 mm": "#e3dccb", "Drawers": "#f3e3c8"}
TITLE = {"GF": "GF BEDROOM", "1F Master": "1ST FLOOR M.BEDROOM", "1F Bedroom 2": "1ST FLOOR BEDROOM 2", "2F": "2ND FLOOR BEDROOM"}


def ink(h):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return "#111" if 0.299 * r + 0.587 * g + 0.114 * b > 140 else "#fff"


for room, v in D.items():
    rows = [(i, r) for i, r in enumerate(v["rows"], 1)]
    items = []
    for i, r in rows:
        g, part, mat, q, L, W, cL, cW, edge, note = r
        if g == "Shutters":
            fc = HEX.get(part.split(" - ")[-1].split()[0], "#ccc")
        else:
            fc = GC.get(g, "#eee")
        a, b = (cL, cW)
        # lay long side horizontal
        w, h = (a, b) if a >= b else (b, a)
        items.append((i, g, part, mat, q, cL, cW, w, h, fc))
    # shelf packing, width limit
    LIM = 5600.0; GAP = 120.0
    items.sort(key=lambda t: -t[8])
    x = y = rowh = 0.0
    place = []
    for it in items:
        w, h = it[7], max(it[8], 140)
        if x + w > LIM:
            x = 0; y -= rowh + GAP; rowh = 0
        place.append((it, x, y - h, w, h))
        x += w + GAP; rowh = max(rowh, h)
    ymin = min(p[2] for p in place)
    fig, ax = plt.subplots(figsize=(16.5, 11.7))
    for (i, g, part, mat, q, cL, cW, w, h0, fc), px, py, w, h in place:
        ax.add_patch(Rectangle((px, py), w, h0, fc=fc, ec="#333", lw=0.7))
        name = part.replace("Bottom drawers (right section): ", "Drawer ").replace("Bottom drawers: ", "Drawer ")
        name = re.sub(r" \((green|brown|grey|teal blue|yellow|lavender|violet)\)", "", name)
        for a_, b_ in (("Door (full height)", "Door full"), (" - ", " · "), (" (cupboard, 2000 high)", ""), ("drawer ", ""),
                       ("(full height, doors fixed)", "(full)"), (" 6 mm (in groove)", " 6mm"), ("Skirting (front, base 80)", "Skirting"),
                       ("Drawer outside front", "Drawer front"), ("Bottom rail (front, on cupboard top)", "Loft bottom rail"),
                       ("Frame upright (end / partition)", "Loft upright"), ("Top rail", "Loft top rail")):
            name = name.replace(a_, b_)
        fs = 7.5 if w >= 700 and h0 >= 260 else 6.2
        cpl = max(8, int(w / (fs * 3.4)))
        size = f"{cL:g} × {cW:g}   ×{q}" + ("  (6 mm)" if mat.startswith("6 mm") else "")
        if h0 < 160:
            txt = f"#{i}  {cL:g}×{cW:g}  ×{q}"
        else:
            txt = "\n".join(textwrap.wrap(f"#{i} {name}", cpl)[:3]) + "\n" + size
        ax.text(px + w / 2, py + h0 / 2, txt, ha="center", va="center", fontsize=fs, color=ink(fc))
    ax.set_xlim(-100, LIM + 100); ax.set_ylim(ymin - 200, 600)
    ax.set_aspect("equal"); ax.axis("off")
    ax.text(0, 330, f"{TITLE[room]} – all pieces (cut sizes in mm, drawn to scale)\n# = row number in the Excel cut list   ·   ×qty = number of pieces",
            fontsize=12, weight="bold")
    lg = [("Cupboard box (off-white)", GC["Cupboard box"]), ("Loft frame 90", GC["Loft frame 90 mm"]), ("Shelves", GC["Inside"]),
          ("6 mm back / drawer bottom", GC["Back panels 6 mm"]), ("Drawer box", GC["Drawers"]), ("Shutters = laminate colour", "#ffffff")]
    for k, (t, c) in enumerate(lg):
        ax.add_patch(Rectangle((k * 950, 60), 80, 80, fc=c, ec="#333", lw=0.6)); ax.text(k * 950 + 110, 100, t, fontsize=7.5, va="center")
    fn = os.path.join(HERE, f"Pieces - {TITLE[room].title()}.png")
    fig.savefig(fn, dpi=150, bbox_inches="tight"); plt.close(fig); print("wrote", fn)
