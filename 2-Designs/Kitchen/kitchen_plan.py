"""Mr. Manoker kitchen - overall plan (top view), schematic from the owner's measurements."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
D = 600                    # counter depth (granite) approx
P = 110                    # pillar
TD = 350                   # top unit depth
GREEN, IVORY, PIL, GRAN = "#2d6851", "#efe9dc", "#cfc8bd", "#3a3a3a"
# room (inside) - schematic
RX = D + P + 2080 + P + D          # window wall length  (left corner + gas run + right corner)
RY = 3000                          # left wall length (top unit 3000 runs full wall)

fig, ax = plt.subplots(figsize=(13, 13))
ax.add_patch(Rectangle((-150, -150), RX + 300, RY + 300, fc="#555", ec="none"))
ax.add_patch(Rectangle((0, 0), RX, RY, fc="#f7f4ee", ec="none"))


def blk(x, y, w, h, c, t="", rot=0, fs=8, tc="w"):
    ax.add_patch(Rectangle((x, y), w, h, fc=c, ec="#111", lw=.7))
    if t: ax.text(x + w / 2, y + h / 2, t, ha="center", va="center", fontsize=fs, color=tc, rotation=rot)


def dimx(x0, x1, y, t):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", lw=.6)); ax.text((x0 + x1) / 2, y + 40, t, ha="center", fontsize=8)


def dimy(y0, y1, x, t):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", lw=.6)); ax.text(x + 40, (y0 + y1) / 2, t, va="center", fontsize=8, rotation=90)


# ---- WINDOW wall (top): corner | P | 2080 gas unit | P | corner
y = RY - D
blk(0, y, D, D, GRAN, "corner", fs=7)
blk(D, y, P, D, PIL); blk(D + P, y, 557, D, GREEN, "3 pull-out\n4/6/8\"")
blk(D + P + 557 + 18, y, 557, D, GREEN, "2 pull-out\n8\"+8\"")
blk(D + P + 2 * 575, y, 2080 - 2 * 575, D, GREEN, "GAS\ncylinder\n2 doors")
blk(D + P + 2080, y, P, D, PIL); blk(RX - D, y, D, D, GRAN, "corner", fs=7)
dimx(D + P, D + P + 2080, RY - D - 120, "2080 open")
ax.add_patch(Rectangle((D + 300, RY), 1600, 150, fc="#9fd0ea", ec="#333")); ax.text(D + 1100, RY + 230, "WINDOW (no top unit)", ha="center", fontsize=9, weight="bold")

# ---- RIGHT wall: from window corner down: P | sink 668 | P
x = RX - D; yy = RY - D
blk(x, yy - P, D, P, PIL); blk(x, yy - P - 668, D, 668, GREEN, "SINK\n668\nframe +\n2 doors", fs=8)
blk(x, yy - 2 * P - 668, D, P, PIL)
dimy(yy - P - 668, yy - P, x - 110, "668")
# top unit right 1420 (dashed, from window corner?)
ax.add_patch(Rectangle((RX - TD, RY - 1420), TD, 1420, fc="none", ec="#c08a2a", lw=2.5, ls="--"))
ax.annotate("", (RX - TD - 60, RY), (RX - TD - 60, RY - 1420), arrowprops=dict(arrowstyle="<->", lw=.8, color="#a06a10"))
ax.text(RX - TD - 330, RY - 1420 + 80, "TOP 1420\n(wall → over sink)", ha="center", fontsize=8, color="#a06a10")

# ---- LEFT wall: from window corner down: P | 1050 (3 pull-out + door/shelf) | P | ... corner
x = 0; yy = RY - D
blk(x, yy - P, D, P, PIL)
blk(x, yy - P - 557, D, 557, GREEN, "3 pull-out\n4/6/8\"", fs=8)
blk(x, yy - P - 1050, D, 1050 - 557, GREEN, "door +\nshelf", fs=8)
blk(x, yy - 2 * P - 1050, D, P, PIL)
dimy(yy - P - 1050, yy - P, D + 60, "1050 open")
ax.add_patch(Rectangle((0, 0), TD, RY, fc="none", ec="#c08a2a", lw=2, ls="--"))
ax.text(TD / 2 + 10, RY / 2 - 300, "TOP 3000 (full wall ?)", rotation=90, ha="center", va="center", fontsize=8, color="#a06a10")

# ---- ENTRANCE / back wall (bottom): corner at LEFT-wall end (right end when facing it): blind 450 | magic 450 | wicker 536 | P
# 1490 opening starts AT THE CORNER (left wall): magic corner box sits in the corner, blind 450 into the corner
blk(0, 0, 468, D, "#3f7a63", "blind 450\n(in corner)", fs=8)
blk(468, 0, 468, D, GREEN, "MAGIC\nCORNER\ndoor 450", fs=8)
blk(936, 0, 554, D, "#b58b5a", "WICKER\n×3", fs=8, tc="#111")
blk(1490, 0, P, D, PIL)
ax.add_patch(Rectangle((0, 0), 936, D, fc="none", ec="#e0b000", lw=2.5))
ax.text(468, D + 60, "Ebco MAGIC CORNER box 900 (right-hand) – in the corner", ha="center", fontsize=8, color="#806000", weight="bold")
dimx(0, 1490, D + 160, "1490 open (from corner wall)")
# top: appliance garage 600 in the corner (on counter) + box 1120
ax.add_patch(Rectangle((0, 0), 600, TD, fc="none", ec="#7a8a90", lw=2, ls="--"))
ax.text(1250, 1150, "APPLIANCE GARAGE 600 (top, corner)\n(rolling shutter, top) ?", ha="center", fontsize=8, color="#555")
ax.add_patch(Rectangle((600, 0), 1120, TD, fc="none", ec="#c08a2a", lw=2, ls="--"))
ax.text(600 + 560, TD / 2 + 60, "TOP box 1120", ha="center", va="center", fontsize=8, color="#a06a10")
# door / entrance
ax.add_patch(Rectangle((1750, -150), RX - 1750 - 150, 150, fc="#f7f4ee", ec="none"))
ax.text(1750 + (RX - 1900) / 2, -260, "ENTRANCE (open)", ha="center", fontsize=9, weight="bold")

ax.text(RX / 2, RY / 2 + 200, "KITCHEN\n(plan – top view)", ha="center", va="center", fontsize=14, color="#888", weight="bold")
ax.text(-150, -500, "Green = bottom units (27183 LV Camouflage, 540 deep boxes in masonry openings)  ·  Grey = 110 pillars  ·  Dark = corners / granite\n"
        "Dashed gold = TOP units (27111 LV Ivory White, 350 deep, 1447–2857 from floor)  ·  '?' = position not confirmed – please mark on this picture",
        fontsize=9)
ax.set_xlim(-400, RX + 400); ax.set_ylim(-700, RY + 450); ax.set_aspect("equal"); ax.axis("off")
ax.set_title("Mr. Manoker kitchen – overall plan (schematic, please check)", fontsize=14, weight="bold")
fig.savefig(os.path.join(HERE, "Kitchen - overall plan (please check).png"), dpi=130, bbox_inches="tight")
print("ok")
