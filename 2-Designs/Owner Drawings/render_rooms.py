"""Render 1F Master / 1F Bedroom 2 / 2F front elevations from boards.json (after the dressing/drawer change)."""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
HERE = os.path.dirname(os.path.abspath(__file__))
B = json.load(open(os.path.join(HERE, "boards.json")))
T = 18
CFG = {"1F Master": ("1ST FLOOR M.BEDROOM", 913.0, 5669.9, 6269.9, 6434.9),
       "1F Bedroom 2": ("1ST FLOOR BEDROOM 2", 855.4, 10013.0, 10594.0, 10759.0),
       "2F": ("2ND FLOOR BEDROOM", 855.4, 13384.8, 13975.8, 14140.8)}
for k, (title, b0, x1, xp, x2) in CFG.items():
    d = B[k]
    fig, ax = plt.subplots(figsize=(11, 12))
    for y, a, b in d["h"]:
        ax.add_patch(Rectangle((a, y), b - a, T, fc="#dec49e", ec="#5a4630", lw=0.8))
    for x, a, b in d["v"]:
        ax.add_patch(Rectangle((x, a), T, b - a, fc="#dec49e", ec="#5a4630", lw=0.8))
    X0 = min(v[0] for v in d["v"]); X1 = max(v[0] + T for v in d["v"])
    Y0 = min(v[1] for v in d["v"]); Y1 = max(v[2] for v in d["v"])
    cup = Y0 + 2000
    ax.axhline(cup, color="#c0392b", lw=1, ls="--")
    ax.text(X1 + 40, cup + 15, "cupboard box top = 2000\nloft above: 90 mm frame only", color="#c0392b", fontsize=9)
    def dh(a, b, y, t):
        ax.annotate("", (a, y), (b, y), arrowprops=dict(arrowstyle="<->", lw=0.7)); ax.text((a + b) / 2, y + 20, t, ha="center", fontsize=9)
    def dv(x, a, b, t):
        ax.annotate("", (x, a), (x, b), arrowprops=dict(arrowstyle="<->", lw=0.7)); ax.text(x - 20, (a + b) / 2, t, ha="right", va="center", rotation=90, fontsize=9)
    dh(X0, X1, Y1 + 120, f"{X1 - X0:.0f} overall")
    dv(X0 - 160, Y0, Y1, f"{Y1 - Y0:.0f} overall")
    dv(X0 - 60, Y0, cup, "2000")
    dv(x2 + 60, b0 + T, b0 + 191, "173"); dv(x2 + 60, b0 + 209, b0 + 391, "182")
    dv(x2 + 60, b0 + 409, b0 + 509, "100 open"); dv(xp + 60, b0 + 409, b0 + 409 + 1493, "1493")
    ax.text((x1 + x2) / 2, b0 + 80, "drawer 1 (box 150)", ha="center", fontsize=8, color="#7a4a2a")
    ax.text((x1 + x2) / 2, b0 + 280, "drawer 2 (box 150)", ha="center", fontsize=8, color="#7a4a2a")
    ax.text((x1 + xp) / 2, b0 + 420, "open space", ha="center", fontsize=8, color="#7a4a2a")
    ax.text((x1 + xp) / 2, b0 + 545, "dressing top 600 (50 lower)", ha="center", fontsize=7, color="#c0392b")
    ax.text((X0 + X1) / 2, Y0 - 230, f"{title} – front view (depth 500 mm) · from owner's AutoCAD drawing", ha="center", fontsize=11, weight="bold")
    ax.set_xlim(X0 - 350, X1 + 500); ax.set_ylim(Y0 - 300, Y1 + 250); ax.set_aspect("equal"); ax.axis("off")
    fig.savefig(os.path.join(HERE, f"drawing_{k}.png"), dpi=150, bbox_inches="tight"); plt.close(fig)
print("ok")
