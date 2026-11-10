"""Mr. Manoker kitchen - wall elevations (bottom units in masonry openings + top units), proposal for confirmation."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
GREEN, IVORY, PIL, GRAN = "#2d6851", "#efe9dc", "#d9d2c6", "#222222"
OPEN_H, SLAB, GRANITE = 710, 110, 27          # 710 + 110 + 27 = 847 counter
CTR = OPEN_H + SLAB + GRANITE
TOP_BOT, TOP_H = CTR + 600, 1410              # top unit bottom 1447, top 2857


def pillar(ax, x, w=110):
    ax.add_patch(Rectangle((x, 0), w, OPEN_H, fc=PIL, ec="#777", lw=.6))


def front(ax, x, y, w, h, c, label="", fs=7, tc="w"):
    ax.add_patch(Rectangle((x + 1, y + 1), w - 2, h - 2, fc=c, ec="#111", lw=.6))
    if label:
        ax.text(x + w / 2, y + h / 2, label, ha="center", va="center", fontsize=fs, color=tc)


def baskets(ax, x, w, sizes):
    hs = {"4": 176, "6": 227, "8": 279, "8d": 344, "8d2": 344}
    y = 0
    for s in sizes[::-1]:
        h = OPEN_H * hs[s] / sum(hs[t] for t in sizes)
        front(ax, x, y, w, h, GREEN, f'{s[0]}" basket' if s != "8d2" else '8" basket'); y += h


def counter(ax, x0, x1):
    ax.add_patch(Rectangle((x0, OPEN_H), x1 - x0, SLAB, fc="#cfc8bd", ec="#777", lw=.5))
    ax.add_patch(Rectangle((x0 - 20, OPEN_H + SLAB), x1 - x0 + 40, GRANITE, fc=GRAN, ec=GRAN))


def top_unit(ax, x, w, n_doors, label):
    dw = w / n_doors
    for k in range(n_doors):
        front(ax, x + k * dw, TOP_BOT, dw, TOP_H, IVORY, "", tc="#333")
    ax.text(x + w / 2, TOP_BOT + TOP_H + 60, label, ha="center", fontsize=8, weight="bold")


def dim(ax, x0, x1, y, t):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", lw=.6)); ax.text((x0 + x1) / 2, y - 70, t, ha="center", fontsize=7.5)


fig, axs = plt.subplots(2, 2, figsize=(20, 13))
# 1 RIGHT wall - sink
ax = axs[0, 0]; x = 0
pillar(ax, x); x += 110; front(ax, x, 0, 334, OPEN_H, GREEN, "sink\ndoor"); front(ax, x + 334, 0, 334, OPEN_H, GREEN, "sink\ndoor"); dim(ax, x, x + 668, -40, "668"); x += 668; pillar(ax, x); x += 110
counter(ax, 0, x)
top_unit(ax, 0, 1420, 3, "TOP 1420 × 1410 × 350 (3 doors)")
ax.set_title("1. RIGHT wall – SINK (frame + 2 shutters, no box)", fontsize=11, weight="bold")
# 2 OPPOSITE (window) wall - gas unit 2080
ax = axs[0, 1]; x = 0
pillar(ax, x); x += 110; x0 = x
baskets(ax, x, 575, ["4", "6", "8"]); x += 575
baskets(ax, x, 575, ["8d", "8d2"]); x += 575
front(ax, x, 0, 465, OPEN_H, GREEN, "gas\ndoor"); front(ax, x + 465, 0, 465, OPEN_H, GREEN, "gas\ndoor"); x += 930
dim(ax, x0, x, -40, "2080 open"); pillar(ax, x); x += 110
counter(ax, 0, x)
ax.add_patch(Rectangle((300, CTR + 150), x - 600, 700, fc="#cfe3f0", ec="#555")); ax.text(x / 2, CTR + 500, "WINDOW – no top unit", ha="center", fontsize=9)
ax.set_title("2. OPPOSITE (window) wall – 3 pull-out (4/6/8\") + 2 pull-out + gas cylinder", fontsize=11, weight="bold")
# 3 LEFT wall - 1050 + top 3000
ax = axs[1, 0]; x = 0
pillar(ax, x); x += 110; x0 = x
baskets(ax, x, 575, ["4", "6", "8"]); x += 575
front(ax, x, 0, 475, OPEN_H, GREEN, "door +\nshelf"); x += 475
dim(ax, x0, x, -40, "1050 open"); pillar(ax, x); x += 110
counter(ax, 0, max(x, 3000))
top_unit(ax, 0, 3000, 6, "TOP 3000 × 1410 × 350 (2 boxes 1500, 6 doors)")
ax.set_title("3. LEFT wall – 3 pull-out + door/shelf  ·  top 3000", fontsize=11, weight="bold")
# 4 BACK wall - corner 1490 + top 1720 (garage 600 + box 1120)
ax = axs[1, 1]; x = 0
pillar(ax, x); x += 110; x0 = x
baskets(ax, x, 554, ["4", "6", "8"]); ax.texts[-1].set_text("wicker")
for t in ax.texts[-3:]: t.set_text("wicker")
for p in ax.patches[-3:]: p.set_facecolor("#b58b5a")
x += 554
front(ax, x, 0, 468, OPEN_H, GREEN, "MAGIC\nCORNER\ndoor 450"); x += 468
front(ax, x, 0, 468, OPEN_H, "#3f7a63", "blind\npanel 450"); x += 468
dim(ax, x0, x, -40, "1490 open (corner on RIGHT)")
counter(ax, 0, x)
# top: box 1120 (2 doors) + appliance garage 600 at the corner (right)
top_unit(ax, 0, 1120, 2, "TOP box 1120 (2 doors)")
gx = 1120
ax.add_patch(Rectangle((gx, CTR), 600, TOP_BOT + TOP_H - CTR, fc="#9aa3a8", ec="#111", lw=.8))
for yy in range(int(CTR) + 20, int(TOP_BOT + TOP_H), 40):
    ax.plot([gx + 10, gx + 590], [yy, yy], color="#6f777c", lw=.6)
ax.text(gx + 300, (CTR + TOP_BOT + TOP_H) / 2, "APPLIANCE\nGARAGE 600\nrolling shutter\n(counter to top)", ha="center", va="center", fontsize=8, color="#111",
        bbox=dict(fc="w", ec="none", alpha=.7))
ax.set_title("4. BACK wall – wicker ×3 + Ebco magic corner (RH)  ·  top 1120 + rolling garage 600", fontsize=11, weight="bold")
for a in axs.flat:
    a.axhline(0, color="#555", lw=1)
    a.text(-60, CTR, "847", ha="right", va="center", fontsize=7); a.text(-60, TOP_BOT, "1447", ha="right", va="center", fontsize=7)
    a.text(-60, TOP_BOT + TOP_H, "2857", ha="right", va="center", fontsize=7)
    a.set_xlim(-350, 3300); a.set_ylim(-250, 3100); a.set_aspect("equal"); a.axis("off")
fig.suptitle("Mr. Manoker kitchen – wall elevations (PROPOSAL)   ·   bottom 27183 LV Camouflage   ·   top 27111 LV Ivory White   ·   counter 847, top unit 1447–2857, depth 350",
             fontsize=13, weight="bold")
fig.savefig(os.path.join(HERE, "Kitchen - wall elevations (proposal).png"), dpi=130, bbox_inches="tight")
print("ok")
