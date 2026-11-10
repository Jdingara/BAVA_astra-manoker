"""Picture only: inside of each wardrobe for the 5-door version - partitions at door joints (2 + 1 + 2 doors),
no dressing table, only shelves with 305 clear spacing; 2 drawers kept."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
T, BASE, BOX, SP, DRW = 18, 80, 2000, 305, 400
ROOMS = [("GF BEDROOM", 2526, 2857, 1), ("1ST FLOOR M.BEDROOM", 2349, 2905, 1),
         ("1ST FLOOR BEDROOM 2", 2319, 2895, 2), ("2ND FLOOR BEDROOM", 2349, 2825, 2)]   # last = drawer section index (0,1,2)
CAR, SH, DR, FR = "#ece4d2", "#d9cdb3", "#c9a87c", "#9fb6d0"


def draw(ax, title, W, H, dsec):
    ax.add_patch(Rectangle((0, 0), W, H, fc="#f7f4ee", ec="none"))
    # carcass
    ax.add_patch(Rectangle((0, 0), T, BOX, fc=CAR, ec="#555")); ax.add_patch(Rectangle((W - T, 0), T, BOX, fc=CAR, ec="#555"))
    ax.add_patch(Rectangle((T, BASE), W - 2 * T, T, fc=CAR, ec="#555")); ax.add_patch(Rectangle((T, BOX - T), W - 2 * T, T, fc=CAR, ec="#555"))
    inner = W - 2 * T - 2 * T
    unit = inner / 5                                    # 2 + 1 + 2 doors
    secs = [2 * unit, unit, 2 * unit]
    x = T; z0, z1 = BASE + T, BOX - T
    clear = z1 - z0
    info = []
    for i, w in enumerate(secs):
        if i:
            ax.add_patch(Rectangle((x, z0), T, clear, fc=CAR, ec="#555")); x += T
        z = z0
        if i == dsec:
            for k in range(2):
                ax.add_patch(Rectangle((x + 4, z + k * DRW / 2 + 3), w - 8, DRW / 2 - 6, fc=DR, ec="#7a5a30"))
            ax.text(x + w / 2, z + DRW / 2, "2 drawers", ha="center", va="center", fontsize=7)
            z += DRW; ax.add_patch(Rectangle((x, z), w, T, fc=SH, ec="#666")); z += T
        n = 0
        while z + SP + T <= z1 - 150:                   # shelves at 305 clear, keep >=150 top space
            z += SP
            ax.add_patch(Rectangle((x, z), w, T, fc=SH, ec="#666")); n += 1
            if n == 1:
                ax.annotate("", (x + w - 40, z), (x + w - 40, z - SP), arrowprops=dict(arrowstyle="<->", lw=.6))
                ax.text(x + w - 60, z - SP / 2, "305", rotation=90, ha="right", va="center", fontsize=7)
            z += T
        top = z1 - z
        ax.text(x + w / 2, z + top / 2, f"top {top:.0f}", ha="center", va="center", fontsize=6.5, color="#777")
        ax.text(x + w / 2, -90, f"{w:.0f}", ha="center", fontsize=8, weight="bold")
        info.append((round(w), n + (1 if i == dsec else 0)))
        x += w
    # loft frame
    for xx in (0, W - T):
        ax.add_patch(Rectangle((xx, BOX), T, H - BOX, fc=FR, ec="#555"))
    ax.add_patch(Rectangle((T, BOX), W - 2 * T, T, fc=FR, ec="#555")); ax.add_patch(Rectangle((T, H - T), W - 2 * T, T, fc=FR, ec="#555"))
    ax.text(W / 2, BOX + (H - BOX) / 2, "LOFT (90 mm frame)", ha="center", va="center", fontsize=8, color="#555")
    ax.text(W / 2, -260, title, ha="center", fontsize=12, weight="bold")
    ax.text(W / 2, -400, "inside, 5 doors (2 + 1 + 2)  ·  shelves 305 apart  ·  no dressing table", ha="center", fontsize=8)
    ax.set_xlim(-120, W + 120); ax.set_ylim(-480, H + 80); ax.set_aspect("equal"); ax.axis("off")
    return info


fig, axs = plt.subplots(1, 4, figsize=(26, 9.5))
for ax, r in zip(axs, ROOMS):
    print(r[0], draw(ax, *r))
fig.suptitle("Mr. Manoker – 5-door wardrobes: INSIDE (picture only)", fontsize=16, weight="bold")
fig.savefig(os.path.join(HERE, "All Bedrooms - 5 doors INSIDE (picture).png"), dpi=130, bbox_inches="tight")
