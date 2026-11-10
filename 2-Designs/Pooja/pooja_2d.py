"""Mr. Manoker pooja unit - 2D: front (doors closed, CNC jali like the owner's reference), front (doors open), side section."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Ellipse, PathPatch
from matplotlib.path import Path
import numpy as np

W, H, D, KD = 1040, 2720, 405, 100
TU = D - KD
LAM, PANEL, IN, CUT = "#8a5a36", "#6b4429", "#f1e7d3", "#ffcf6b"   # CUT = warm LED glow through the jali


def R(a, x, y, w, h, fc, ec="#222", lw=.8, t="", tc="w", fs=8, ls="-"):
    a.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, ls=ls))
    if t: a.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color=tc)


def dimv(a, y0, y1, x, t):
    a.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", lw=.7)); a.text(x + 25, (y0 + y1) / 2, t, va="center", fontsize=8)


def dimh(a, x0, x1, y, t):
    a.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", lw=.7)); a.text((x0 + x1) / 2, y - 70, t, ha="center", fontsize=8)


def bell(a, cx, top, s=1.0):
    a.add_patch(Polygon([(cx - 8 * s, top), (cx + 8 * s, top), (cx + 14 * s, top - 45 * s), (cx + 24 * s, top - 70 * s),
                         (cx - 24 * s, top - 70 * s), (cx - 14 * s, top - 45 * s)], fc=CUT, ec=CUT))
    a.add_patch(Ellipse((cx, top - 76 * s), 10 * s, 10 * s, fc=CUT))


def chain(a, cx, y0, y1):
    y = y0
    while y > y1:
        a.add_patch(Rectangle((cx - 13, y - 30), 6, 30, fc=CUT)); a.add_patch(Rectangle((cx + 7, y - 30), 6, 30, fc=CUT))
        y -= 42


def trunk(a, cx, ytop, mirror=1, sc=1.0):
    m = mirror
    verts = [(cx, ytop), (cx + 60 * m, ytop - 40 * sc), (cx + 30 * m, ytop - 150 * sc), (cx + 10 * m, ytop - 260 * sc),
             (cx - 10 * m, ytop - 380 * sc), (cx - 20 * m, ytop - 520 * sc), (cx + 10 * m, ytop - 560 * sc)]
    a.add_patch(PathPatch(Path(verts, [Path.MOVETO] + [Path.CURVE4] * 6), fc="none", ec=CUT, lw=4))
    a.add_patch(Ellipse((cx + 15 * m, ytop - 565 * sc), 30, 30, fc="none", ec=CUT, lw=3))
    for k in range(3):                                                    # ear lines / crown
        a.add_patch(Ellipse((cx - 5 * m + k * 10 * m, ytop + 25 + k * 22), 90 - k * 20, 12, angle=-20 * m, fc=CUT))
    a.add_patch(Ellipse((cx + 35 * m, ytop - 70), 50, 18, angle=-25 * m, fc=CUT))   # eye


def lotus(a, cx, cy):
    for ang, l in ((0, 110), (-28, 95), (28, 95), (-55, 75), (55, 75)):
        a.add_patch(Ellipse((cx + np.sin(np.radians(ang)) * l * 0.45, cy + np.cos(np.radians(ang)) * l * 0.45), 34, l, angle=-ang, fc=CUT))
    a.add_patch(Ellipse((cx, cy - 25), 120, 22, fc=CUT))


def door_jali_short(a, x, w, y0, y1, mirror=1):
    """CNC design for the upper (pooja niche) door: chains + bells at top, Ganesha motif, small lotus"""
    for k, f in enumerate((0.2, 0.5, 0.8)):
        cx = x + w * f; top = y1 - 50; ln = 200 if k != 1 else 140
        chain(a, cx, top, top - ln); bell(a, cx, top - ln - 10, 0.85)
    trunk(a, x + w * (0.55 if mirror == 1 else 0.45), y1 - 400, mirror, sc=0.68)
    lotus(a, x + w / 2, y0 + 110)


def door_jali(a, x, w, y0, y1, mirror=1):
    """CNC cut design on one door: 3 chains with bells, Ganesha trunk motif, lotus"""
    for k, f in enumerate((0.2, 0.5, 0.8)):
        cx = x + w * f
        top = y1 - 70
        ln = 330 if k != 1 else 250
        chain(a, cx, top, top - ln)
        bell(a, cx, top - ln - 10)
    trunk(a, x + w * (0.55 if mirror == 1 else 0.45), y1 - 620, mirror)
    lotus(a, x + w / 2, y0 + 200)


def kalasam(a, cx, y):
    a.add_patch(Rectangle((cx - 28, y), 56, 14, fc="#b8860b", ec="#7a5a00"))
    a.add_patch(Ellipse((cx, y + 55), 70, 80, fc="#d4a017", ec="#7a5a00"))
    a.add_patch(Rectangle((cx - 10, y + 92), 20, 35, fc="#d4a017", ec="#7a5a00"))
    a.add_patch(Ellipse((cx, y + 140), 26, 26, fc="#d4a017", ec="#7a5a00"))


def top_part(a):
    R(a, 0, 1905, W, 228, LAM)
    for cx in (W * 0.14, W * 0.32, W * 0.5, W * 0.68, W * 0.86):
        kalasam(a, cx, 1915)
    R(a, 0, 2135, W / 2 - 1, H - 2137, LAM, t="top door", fs=8); R(a, W / 2 + 1, 2135, W / 2 - 1, H - 2137, LAM, t="top door", fs=8)


fig, (ax, ox, bx) = plt.subplots(1, 3, figsize=(20, 13), gridspec_kw={"width_ratios": [1.4, 1.4, 0.9]})
# ---- FRONT, doors closed
R(ax, W, 0, 18, H, PANEL)
R(ax, 0, 0, W, 80, LAM, t="skirting 80", fs=7)
for k in range(2):
    x = k * (W / 2 + 1)
    R(ax, x, 80, W / 2 - 1, 678, LAM, t="plain door", fs=8)                       # lower plain doors
    R(ax, x, 762, W / 2 - 1, 1905 - 762, LAM)                                     # upper CNC doors (cover the pull-out)
    door_jali_short(ax, x, W / 2 - 1, 762, 1905, 1 if k == 0 else -1)
top_part(ax)
dimv(ax, 0, H, -300, "2720"); dimv(ax, 0, 80, W + 40, "80"); dimv(ax, 80, 760, W + 40, "680 plain doors"); dimv(ax, 760, 1905, W + 40, "1145 CNC doors\n(pull-out 90 + niche 1055 inside)")
dimv(ax, 1905, 2133, W + 40, "228"); dimv(ax, 2133, H, W + 40, "587"); dimh(ax, 0, W, -60, "1040")
ax.set_title("FRONT – CNC doors (cover pull-out + niche), plain doors below", fontsize=12, weight="bold")
ax.set_xlim(-460, W + 300); ax.set_ylim(-250, H + 100); ax.set_aspect("equal"); ax.axis("off")
# ---- FRONT, doors open (inside)
R(ox, 0, 0, W, 80, LAM, t="skirting 80", fs=7)
R(ox, 0, 80, W, 680, "#e8dcc6", ec="#555", t="storage (shelf inside)", tc="#333")
R(ox, 0, 760, W, 90, "#a8774f", t="pull-out shelf 90 (behind CNC doors, pooja time)", fs=7)
R(ox, 0, 850, W, 1055, IN, ec=LAM, lw=2, t="POOJA NICHE\n1055 high × 405 deep", tc="#5a3a22", fs=10)
top_part(ox)
dimv(ox, 80, 760, W + 40, "680"); dimv(ox, 760, 850, W + 40, "90"); dimv(ox, 850, 1905, W + 40, "1055")
ox.set_title("FRONT – doors open (inside)", fontsize=12, weight="bold")
ox.set_xlim(-200, W + 300); ox.set_ylim(-250, H + 100); ox.set_aspect("equal"); ox.axis("off")
# ---- SIDE SECTION
R(bx, 0, 0, D, 80, LAM, t="80", fs=7)
R(bx, 0, 80, D, 680, "#e8dcc6", ec="#555", t="storage", tc="#333")
R(bx, 0, 760, D, 90, "#a8774f", t="pull-out 90", fs=7)
R(bx, 0, 850, D, 1055, IN, ec=LAM, lw=2, t="POOJA\nNICHE", tc="#5a3a22")
R(bx, -18, 80, 18, 680, LAM); R(bx, -18, 762, 18, 1143, LAM)
R(bx, 0, 1905, KD, 228, "#d4a017", ec="#7a5a00", t="kalasam\n100", tc="#222", fs=7)
R(bx, KD, 1905, TU, 228, "#ddd", ec="#555", t="dummy\n305", tc="#333", fs=7, ls="--")
R(bx, KD, 2133, TU, H - 2133, "#e8dcc6", ec="#555", t="TOP UNIT\n305 deep", tc="#333")
R(bx, KD - 18, 2133, 18, H - 2133, LAM)
bx.add_patch(Rectangle((D, 0), 30, H, fc="#bbb", ec="#777")); bx.text(D + 50, H / 2, "WALL", rotation=90, va="center", fontsize=8)
dimh(bx, 0, D, -60, "405"); dimh(bx, 0, KD, 2850, "100"); dimh(bx, KD, D, 2850, "305")
bx.set_title("SIDE SECTION", fontsize=12, weight="bold")
bx.set_xlim(-150, D + 200); bx.set_ylim(-250, H + 300); bx.set_aspect("equal"); bx.axis("off")
fig.suptitle("Mr. Manoker – POOJA unit  ·  1040 W × 2720 H × 405 D  ·  10225 SF (Merino)  ·  CNC doors (niche) + plain doors (below) + 5 kalasam + LED behind jali + side panel RIGHT", fontsize=14, weight="bold")
fig.savefig("Pooja unit - 2D drawing.png", dpi=130, bbox_inches="tight"); fig.savefig("Pooja unit - 2D drawing.pdf", bbox_inches="tight")
print("ok")
