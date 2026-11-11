"""5-door design 2D drawing per bedroom from "boards (5-door).json" (run make_5door_boards.py first).
Left: inside front view with all measurements. Right: doors front view with laminate colours (shades approximate).
-> "2D 5 doors - <room>.png" + "Mr. Manoker - 5 doors 2D drawing.pdf"."""
import json
import os
import time
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
B = json.load(open(os.path.join(HERE, "boards (5-door).json")))
T, GLASS_BORDER, MIRROR_H = 18, 90, 700
TITLES = {"GF": "GF BEDROOM", "1F Master": "1ST FLOOR M.BEDROOM", "1F Bedroom 2": "1ST FLOOR BEDROOM 2", "2F": "2ND FLOOR BEDROOM"}
COVER_SIDE = {"GF": "left", "1F Master": "left", "1F Bedroom 2": "right", "2F": "left"}
# (main, accent, accent doors 1-based, accent loft doors) - same pattern as the 5-door customer pictures
COL = {"GF": ("DC687 Foliage Blue (Advance)", "21125 MR+ Sunburn (Merino)", [2, 4], [2, 4]),
       "1F Master": ("27292 LV Mink", "27262 LV Peacock", [2, 5], []),
       "1F Bedroom 2": ("21433 SF Neo Banana Leaf", "21457 SF Aspen Gold", [2, 4], []),
       "2F": ("21462 SF Lavendura", "21452 SF Prism Violet", [2, 4], [])}
HEX = {"DC687": "#46707a", "21125": "#9b6638", "27292": "#d9cdd2", "27262": "#075f7f",
       "21433": "#035f33", "21457": "#f7cd0b", "21462": "#a994c7", "21452": "#5c2568"}
PLY, PLY_E, DRW_C, TOP_C, MIR = "#dec49e", "#5a4630", "#c9a87c", "#b98d5a", "#cfe3ea"


def ink(h):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return "#111" if 0.299 * r + 0.587 * g + 0.114 * b > 140 else "#fff"


def dv(ax, x, a, b, txt=None, fs=7, side="left", color="#222"):
    ax.annotate("", (x, a), (x, b), arrowprops=dict(arrowstyle="<->", lw=.6, color=color))
    ax.text(x + (-12 if side == "left" else 12), (a + b) / 2, txt or f"{b - a:.0f}", rotation=90,
            ha="right" if side == "left" else "left", va="center", fontsize=fs, color=color)


def dh(ax, a, b, y, txt=None, fs=7, color="#222"):
    ax.annotate("", (a, y), (b, y), arrowprops=dict(arrowstyle="<->", lw=.6, color=color))
    ax.text((a + b) / 2, y + 15, txt or f"{b - a:.0f}", ha="center", va="bottom", fontsize=fs, color=color)


def inside(ax, room, d):
    m = d["meta"]
    X0, X1 = m["x"]; Y0, Y1 = m["y_floor"], m["y_top"]
    yb, mt = m["y_bot"], m["main_top"]
    ax.add_patch(Rectangle((X0, Y0), X1 - X0, Y1 - Y0, fc="#faf8f3", ec="none"))
    for y, a, b in d["h"]:
        c = TOP_C if abs(y - (m["dress_y"] or -1)) < .1 else PLY
        ax.add_patch(Rectangle((a, y), b - a, T, fc=c, ec=PLY_E, lw=.6))
    for x, a, b in d["v"]:
        ax.add_patch(Rectangle((x, a), T, b - a, fc=PLY, ec=PLY_E, lw=.6))
    ax.add_patch(Rectangle((X0 + T, Y0), X1 - X0 - 2 * T, yb - Y0, fc="#e8e2d6", ec=PLY_E, lw=.4))
    ax.text((X0 + X1) / 2, Y0 + 40, "base 80", ha="center", va="center", fontsize=6, color="#777")
    cup = Y0 + 2000
    ax.text((X0 + X1) / 2, (cup + Y1) / 2, f"LOFT  ·  90 mm frame only  ·  {Y1 - cup:.0f} high", ha="center", va="center", fontsize=8, color="#555")
    for s in m["sections"]:
        xa, xb = s["x"]; w = xb - xa
        lev = [yb + T] + [y + T for y in s["shelves"]]
        tops = s["shelves"] + [mt]
        # gap dims on the right inside each section
        for k, (lo, hi) in enumerate(zip(lev, tops)):
            dv(ax, xb - 25, lo, hi, fs=6.5)
        if s["drawers"]:
            for k, (lo, hi) in enumerate(zip(lev[:2], tops[:2])):
                ax.add_patch(Rectangle((xa + 8, lo + 6), w - 70, hi - lo - 12, fc=DRW_C, ec="#7a5a30", lw=.6))
                ax.text(xa + (w - 45) / 2, (lo + hi) / 2, f"drawer {k + 1}", ha="center", va="center", fontsize=6.5)
        if s["dressing"]:
            zt = m["dress_y"] + T
            ax.add_patch(Rectangle((xa + 30, zt + 100), w - 110, MIRROR_H, fc=MIR, ec="#557", lw=.7))
            ax.plot([xa + 60, xa + w * .4], [zt + 160, zt + MIRROR_H], color="white", lw=4, alpha=.8)
            ax.text(xa + 30 + (w - 110) / 2, zt + 100 + MIRROR_H / 2, f"MIRROR\n{w - 110:.0f} x {MIRROR_H}", ha="center", va="center", fontsize=6.5)
            ax.plot([xa + 25, xa + w - 60], [zt + 100 + MIRROR_H + 30] * 2, color="#e6a800", lw=2.5)
            ax.text(xa + (w - 35) / 2, zt + 100 + MIRROR_H + 8, "LED", ha="center", fontsize=6, color="#a07800")
            ax.text(xa + (w - 35) / 2, m["dress_y"] - 15, f"DRESSING TOP\n{m['dress_y'] - Y0:.0f} from floor", ha="center", va="top", fontsize=6.5, weight="bold", color="#6b4423")
            dv(ax, xa - 40 if False else X0 - 60, Y0, m["dress_y"], f"{m['dress_y'] - Y0:.0f} dressing top", fs=6.5, color="#6b4423")
        ax.text(xa + w / 2, Y0 - 70, "DRESSING" if s["dressing"] else ("SHELVES + 2 DRAWERS" if s["drawers"] else "SHELVES"),
                ha="center", va="top", fontsize=7, weight="bold", color="#6b4423" if s["dressing"] else "#444")
        dh(ax, xa, xb, Y0 - 230, f"{s['clear']} clear", fs=7.5)
    # overall dims
    dh(ax, X0, X1, Y1 + 60, f"{X1 - X0:.0f} overall", fs=8.5)
    dv(ax, X0 - 200, Y0, Y1, f"{Y1 - Y0:.0f} overall", fs=8.5)
    dv(ax, X0 - 130, Y0, cup, "2000 box", fs=8)
    dv(ax, X0 - 130, cup, Y1, f"{Y1 - cup:.0f} loft", fs=8)
    if m["split"]:
        s0, s1 = m["split"]
        dh(ax, X0, s0 + T, Y0 - 340, f"box 1: {s0 + T - X0:.0f}", fs=7.5, color="#c0392b")
        dh(ax, s1 - T, X1, Y0 - 340, f"box 2: {X1 - s1 + T:.0f}", fs=7.5, color="#c0392b")
        ax.text((s0 + s1) / 2, Y0 - 395, "2 boxes joint", ha="center", va="top", fontsize=6.5, color="#c0392b")
    ax.text((X0 + X1) / 2, Y1 + 200, "INSIDE (doors removed)", ha="center", fontsize=10, weight="bold")
    ax.set_xlim(X0 - 300, X1 + 80); ax.set_ylim(Y0 - 460, Y1 + 260); ax.set_aspect("equal"); ax.axis("off")


def front(ax, room, d):
    m = d["meta"]
    X0, X1 = m["x"]; Y0, Y1 = m["y_floor"], m["y_top"]
    main, acc, acc_doors, acc_loft = COL[room]
    cm, ca = HEX[main.split()[0]], HEX[acc.split()[0]]
    dw, eg = m["door_w"], m["end_gap"]
    ax.add_patch(Rectangle((X0 - 40, Y0 - 10), X1 - X0 + 80, Y1 - Y0 + 20, fc="#2b2b2b"))
    ax.add_patch(Rectangle((X0, Y0), X1 - X0, 79, fc=cm, ec="#111", lw=.5))
    ax.text((X0 + X1) / 2, Y0 + 40, "skirting 80", ha="center", va="center", fontsize=6, color=ink(cm))
    xs = [X0 + eg + k * (dw + 2) for k in range(5)]
    f0, cup = Y0 + 80 + 1, Y0 + 2000
    dsec = next(i for i, s in enumerate(m["sections"]) if s["drawers"])
    drw_doors = [3] if dsec == 1 else [4, 5]
    d_top = m["y_bot"] + 391 + T / 2 + 1                     # door above drawers starts here
    for i, x in enumerate(xs, 1):
        a = i in acc_doors
        if i in drw_doors and len(drw_doors) == 2:            # L-shape: door 4 above drawers = accent
            a = i == 4
        c = ca if a else cm
        lo = d_top if i in drw_doors else f0
        hgt = cup - 1 - lo
        ax.add_patch(Rectangle((x, lo), dw, hgt, fc=c, ec="#111", lw=.6))
        if i == 3:                                            # centre glass door
            ax.add_patch(Rectangle((x + GLASS_BORDER, lo + GLASS_BORDER), dw - 2 * GLASS_BORDER, hgt - 2 * GLASS_BORDER, fc="#b9d0d6", ec="#555", lw=.7))
            ax.plot([x + GLASS_BORDER + 30, x + dw * .55], [lo + GLASS_BORDER + 60, lo + hgt - GLASS_BORDER - 60], color="white", lw=4, alpha=.6)
            ax.text(x + dw / 2, lo + hgt / 2, f"GLASS\n{dw - 2 * GLASS_BORDER:.0f} x {hgt - 2 * GLASS_BORDER:.0f}\n(90 border)", ha="center", va="center", fontsize=6)
        else:
            nm = (acc if a else main).split(" (")[0]
            ax.text(x + dw / 2, lo + hgt / 2, nm.replace(" ", "\n", 1), ha="center", va="center", fontsize=6.5, color=ink(c))
        ax.text(x + dw / 2, lo + 40, f"{dw} x {hgt:.0f}", ha="center", va="bottom", fontsize=6, color=ink(c))
        ax.text(x + dw / 2, Y0 - 70, f"door {i}", ha="center", va="top", fontsize=7)
    # drawer fronts (accent)
    xa = xs[drw_doors[0] - 1]; xb = xs[drw_doors[-1] - 1] + dw
    lo = f0
    for k in range(2):
        hi = lo + 198
        ax.add_patch(Rectangle((xa, lo), xb - xa, 198, fc=ca, ec="#111", lw=.6))
        ax.text((xa + xb) / 2, lo + 99, f"drawer front {xb - xa:.0f} x 198", ha="center", va="center", fontsize=6, color=ink(ca))
        lo = hi + 2
    # loft doors
    lh = Y1 - cup - 2
    for i, x in enumerate(xs, 1):
        c = ca if i in acc_loft else cm
        ax.add_patch(Rectangle((x, cup + 1), dw, lh, fc=c, ec="#111", lw=.6))
        ax.text(x + dw / 2, cup + 1 + lh / 2, f"loft\n{dw} x {lh:.0f}", ha="center", va="center", fontsize=6, color=ink(c))
    dh(ax, X0, X1, Y1 + 60, f"{X1 - X0:.0f} overall  ·  5 doors x {dw}  ·  gaps 2 between, {eg:g} at ends", fs=8)
    ax.text((X0 + X1) / 2, Y0 - 200, f"side cover 518 deep on the {COVER_SIDE[room].upper()}  ·  100 strip on the other end",
            ha="center", va="top", fontsize=7)
    ax.text((X0 + X1) / 2, Y0 - 300, f"{main}  +  {acc} (accent)", ha="center", va="top", fontsize=7.5, weight="bold")
    ax.text((X0 + X1) / 2, Y1 + 200, "FRONT (doors closed)", ha="center", fontsize=10, weight="bold")
    ax.set_xlim(X0 - 120, X1 + 120); ax.set_ylim(Y0 - 460, Y1 + 260); ax.set_aspect("equal"); ax.axis("off")


def save_png(fig, name):
    for n in (name, name.replace(".png", " (updated).png"), name.replace(".png", time.strftime(" (%H%M%S).png"))):
        try:
            fig.savefig(os.path.join(HERE, n), dpi=150, bbox_inches="tight"); return n
        except PermissionError:
            continue


figs = []
for room, d in B.items():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(16.5, 9.6))
    inside(a1, room, d); front(a2, room, d)
    fig.suptitle(f"Mr. Manoker – {TITLES[room]} wardrobe – 5 doors (2 + 1 + 2) – 2D drawing (all mm)", fontsize=14, weight="bold")
    fig.text(.5, .02, "Depth 500. Partitions behind the door joints. Shelves 305 clear. Dressing in the centre door (glass). "
             "Colours on screen are approximate (DC687 shade not verified). Astra Interiors", ha="center", fontsize=8, color="#555")
    print(save_png(fig, f"2D 5 doors - {TITLES[room].title()}.png"))
    figs.append(fig)
pdf = "Mr. Manoker - 5 doors 2D drawing.pdf"
for n in (pdf, pdf.replace(".pdf", " (updated).pdf"), pdf.replace(".pdf", time.strftime(" (%H%M%S).pdf"))):
    try:
        with PdfPages(os.path.join(HERE, n)) as p:
            for f in figs:
                p.savefig(f, bbox_inches="tight")
        print(n); break
    except PermissionError:
        continue
