"""Picture only: each bedroom wardrobe with 5 doors (+5 loft doors) in the same colours / L-U pattern."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
HEX = {"27173": "#77a99b", "21125": "#9b6638", "27292": "#d9cdd2", "27262": "#075f7f",
       "21433": "#035f33", "21457": "#f7cd0b", "21462": "#a994c7", "21452": "#5c2568"}
# room: (title, box width, total height, main, accent, accent doors (1-based), drawer doors (under these), door above drawers accent?)
ROOMS = [
    ("GF BEDROOM", 2526, 2857, "27173 LV Seaglass", "21125 Sunburn", [2, 4], [3], False),
    ("1ST FLOOR M.BEDROOM", 2349, 2905, "27292 LV Mink", "27262 LV Peacock", [2, 5], [3], False),
    ("1ST FLOOR BEDROOM 2", 2319, 2895, "21433 SF Neo Banana Leaf", "21457 SF Aspen Gold", [2, 4], [4, 5], True),
    ("2ND FLOOR BEDROOM", 2349, 2825, "21462 SF Lavendura", "21452 SF Prism Violet", [2, 4], [4, 5], True),
]
BASE, BOX, DRAWER = 80, 2000, 400
GLASS_DOOR = 3          # owner: centre door = glass (aluminium frame)


def glass(ax, x, y, w, h, lam):
    """laminate door (colour = lam) with a glass panel inset; laminate border shows all round"""
    f = 90
    ax.add_patch(Rectangle((x, y), w, h, fc=lam, ec="#111", lw=.6))                    # laminate door
    ax.add_patch(Rectangle((x + f, y + f), w - 2 * f, h - 2 * f, fc="#b9d0d6", ec="#555", lw=.8))   # glass
    for k, a in ((0.15, .55), (0.35, .35)):
        ax.plot([x + f + (w - 2 * f) * k, x + f + (w - 2 * f) * (k + 0.3)], [y + f + 40, y + h - f - 40], color="white", lw=5 * a, alpha=.6)
    ax.text(x + w / 2, y + h / 2, "glass", ha="center", va="center", fontsize=6.5, color="#333")


def ink(h):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return "#111" if 0.299 * r + 0.587 * g + 0.114 * b > 140 else "#fff"


def draw(ax, title, W, H, main, acc, acc_doors, drw, above_acc):
    cm, ca = HEX[main.split()[0]], HEX[acc.split()[0]]
    ax.add_patch(Rectangle((-30, -20), W + 60, H + 40, fc="#2b2b2b"))
    n = 5; gap = 2; dw = (W - gap * (n + 1)) / n
    xs = [gap + k * (dw + gap) for k in range(n)]
    ax.add_patch(Rectangle((0, 0), W, BASE - 1, fc=cm, ec="#111", lw=.6))                 # skirting
    for i, x in enumerate(xs, 1):
        a = i in acc_doors
        if i in drw:
            continue
        c = ca if a else cm
        if i == GLASS_DOOR:
            glass(ax, x, BASE + 1, dw, BOX - BASE - 2, c); continue
        ax.add_patch(Rectangle((x, BASE + 1), dw, BOX - BASE - 2, fc=c, ec="#111", lw=.6))
        ax.text(x + dw / 2, BASE + (BOX - BASE) / 2, f"{(acc if a else main).split(' (')[0].replace(' LV ', chr(10) + 'LV ').replace(' SF ', chr(10) + 'SF ')}\n{dw:.0f} wide", ha="center", va="center", fontsize=6.5, color=ink(c))
    # drawer block + door(s) above
    xa, xb = xs[drw[0] - 1], xs[drw[-1] - 1] + dw
    for k in range(2):
        ax.add_patch(Rectangle((xa, BASE + 1 + k * DRAWER / 2), xb - xa, DRAWER / 2 - 2, fc=ca, ec="#111", lw=.6))
    ax.text((xa + xb) / 2, BASE + DRAWER / 2, "2 drawers", ha="center", va="center", fontsize=7, color=ink(ca))
    for j, i in enumerate(drw):
        x = xs[i - 1]
        a = (i in acc_doors) if not above_acc else (j == 0)
        c = ca if a else cm
        if i == GLASS_DOOR:
            glass(ax, x, BASE + DRAWER + 1, dw, BOX - BASE - DRAWER - 2, c); continue
        ax.add_patch(Rectangle((x, BASE + DRAWER + 1), dw, BOX - BASE - DRAWER - 2, fc=c, ec="#111", lw=.6))
    for i, x in enumerate(xs, 1):                                                         # loft doors
        c = ca if (title.startswith("GF") and i in acc_doors) else cm
        ax.add_patch(Rectangle((x, BOX + 1), dw, H - BOX - 2, fc=c, ec="#111", lw=.6))
    ax.text(W / 2, -230, title, ha="center", fontsize=12, weight="bold")
    ax.text(W / 2, -380, f"5 doors (centre door with glass panel) + 5 loft doors  ·  door {dw:.0f} wide  ·  {main} + {acc}", ha="center", fontsize=8)
    ax.set_xlim(-150, W + 150); ax.set_ylim(-450, H + 120); ax.set_aspect("equal"); ax.axis("off")


fig, axs = plt.subplots(1, 4, figsize=(26, 9.5))
for ax, r in zip(axs, ROOMS):
    draw(ax, *r)
fig.suptitle("Mr. Manoker – wardrobes with 5 doors (picture only, same colours)", fontsize=16, weight="bold")
fig.savefig(os.path.join(HERE, "All Bedrooms - 5 doors (picture).png"), dpi=130, bbox_inches="tight")
print("ok")
