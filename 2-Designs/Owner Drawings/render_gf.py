"""Render GF Bedroom wardrobe 2D drawing (front elevation) from boards.json (owner's updated AutoCAD drawing)."""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "boards.json")))["GF"]
T = 18
fig, ax = plt.subplots(figsize=(11, 12))
for y, a, b in d["h"]:
    ax.add_patch(Rectangle((a, y), b - a, T, fc="#dec49e", ec="#5a4630", lw=0.8))
for x, a, b in d["v"]:
    ax.add_patch(Rectangle((x, a), T, b - a, fc="#dec49e", ec="#5a4630", lw=0.8))
x0 = min(v[0] for v in d["v"]); x1 = max(v[0] + T for v in d["v"])
y0 = min(v[1] for v in d["v"]); y1 = max(v[2] for v in d["v"])
cup_top = 2848.5 + T
ax.axhline(cup_top, color="#c0392b", lw=1, ls="--")
ax.text(x1 + 40, cup_top + 15, "cupboard box top = 2000\nloft above: 90 mm frame only", color="#c0392b", fontsize=9, va="bottom")
def dim_h(a, b, y, txt=None):
    ax.annotate("", (a, y), (b, y), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text((a + b) / 2, y + 20, txt or f"{b - a:.0f}", ha="center", fontsize=9)
def dim_v(x, a, b, txt=None):
    ax.annotate("", (x, a), (x, b), arrowprops=dict(arrowstyle="<->", lw=0.7))
    ax.text(x - 20, (a + b) / 2, txt or f"{b - a:.0f}", ha="right", va="center", rotation=90, fontsize=9)
dim_h(x0, x1, y1 + 120, f"{x1 - x0:.0f} overall")
dim_h(1508.3, 3156.3, 700, "box 1: 1648 inside")
dim_v(2300, 1404.5, 1548.5, "144 open")
ax.text(2023, 1580, "dressing top 600 (50 lower)", ha="center", fontsize=7, color="#c0392b")
dim_h(3192.3, 3998.3, 700, "box 2: 806 inside")
dim_h(1508.3, 1705.3, 2620, "197"); dim_h(1723.3, 2323.3, 2620, "600"); dim_h(2341.3, 3156.3, 2620, "815")
dim_v(x0 - 120, y0, y1, f"{y1 - y0:.0f} overall")
dim_v(x0 - 40, y0, cup_top, "2000")
dim_v(x0 - 40, y0, 946.5, "80")
dim_v(x0 - 40, cup_top, y1, f"{y1 - cup_top:.0f}")
ax.text(2748, 1240, "BOTTOM DRAWERS 2 (opening 173, box 150)", ha="center", fontsize=8, color="#7a4a2a")
ax.text(2023, 1470, "open space (no drawer)", ha="center", fontsize=8, color="#7a4a2a")
ax.text((x0 + x1) / 2, y0 - 230, "GF BEDROOM – front view (depth 500 mm) · from owner's updated AutoCAD drawing",
        ha="center", fontsize=11, weight="bold")
ax.set_xlim(x0 - 300, x1 + 500); ax.set_ylim(y0 - 300, y1 + 250)
ax.set_aspect("equal"); ax.axis("off")
fig.savefig(os.path.join(HERE, "drawing_GF.png"), dpi=150, bbox_inches="tight")
print("ok")
