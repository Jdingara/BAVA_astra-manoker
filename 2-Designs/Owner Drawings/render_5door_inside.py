"""Picture only: inside of each wardrobe for the 5-door version - partitions at door joints (2 + 1 + 2 doors).
Owner: dressing table ONLY in the centre (1-door) section; the other sections get shelves 305 apart; 2 drawers kept.
GF / 1F Master: 2 drawers at the bottom of the centre section (below the dressing top).
1F Bed 2 / 2F: 2 drawers in the right section (L-shape), centre = dressing with a shelf below."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
T, BASE, BOX, SP, DRW = 18, 80, 2000, 305, 400
DRESS_OPEN, MIRROR_H = 850, 700                       # clear space above the dressing top, mirror height
# title, box width, total height, drawer section index (0,1,2), dressing top height from floor (GF 50 lower)
ROOMS = [("GF BEDROOM", 2526, 2857, 1, 750), ("1ST FLOOR M.BEDROOM", 2349, 2905, 1, 800),
         ("1ST FLOOR BEDROOM 2", 2319, 2895, 2, 800), ("2ND FLOOR BEDROOM", 2349, 2825, 2, 800)]
CAR, SH, DR, FR, TOP, MIR = "#ece4d2", "#d9cdb3", "#c9a87c", "#9fb6d0", "#b98d5a", "#cfe3ea"


def shelf(ax, x, z, w):
    ax.add_patch(Rectangle((x, z), w, T, fc=SH, ec="#666"))


def dim(ax, x, za, zb, txt):
    ax.annotate("", (x, zb), (x, za), arrowprops=dict(arrowstyle="<->", lw=.6))
    ax.text(x - 18, (za + zb) / 2, txt, rotation=90, ha="right", va="center", fontsize=6.5)


def shelves_up(ax, x, z, w, z1, mark=True):
    n = 0
    while z + SP + T <= z1 - 150:                     # shelves at 305 clear, keep >=150 top space
        if n == 0 and mark:
            dim(ax, x + w - 40, z, z + SP, "305")
        z += SP; shelf(ax, x, z, w); n += 1; z += T
    ax.text(x + w / 2, (z + z1) / 2, f"top {z1 - z:.0f}", ha="center", va="center", fontsize=6.5, color="#777")
    return n


def dressing(ax, x, z, w, z1, ztop, has_drw):
    """centre section: (drawers) + dressing top + mirror/LED + shelves above"""
    n = 0
    if has_drw:
        for k in range(2):
            ax.add_patch(Rectangle((x + 4, z + k * DRW / 2 + 3), w - 8, DRW / 2 - 6, fc=DR, ec="#7a5a30"))
        ax.text(x + w / 2, z + DRW / 2, "2 drawers", ha="center", va="center", fontsize=7)
        z += DRW; shelf(ax, x, z, w); z += T; n += 1
        ax.text(x + w / 2, (z + ztop - 60) / 2, f"open {ztop - z:.0f}", ha="center", va="center", fontsize=6.5, color="#777")
    else:
        mid = round((z + ztop - T) / 2)
        shelf(ax, x, mid, w); n += 1
        ax.text(x + w / 2, (z + mid) / 2, "storage", ha="center", va="center", fontsize=6.5, color="#777")
        ax.text(x + w / 2, (mid + T + ztop) / 2, "storage", ha="center", va="center", fontsize=6.5, color="#777")
    # dressing top
    ax.add_patch(Rectangle((x - 2, ztop), w + 4, T, fc=TOP, ec="#5a3d1e", lw=1))
    ax.text(x + w / 2, ztop - 30, f"DRESSING TOP @ {ztop}", ha="center", va="top", fontsize=6.5, weight="bold", color="#5a3d1e")
    zt = ztop + T
    # mirror + LED on the back panel
    ax.add_patch(Rectangle((x + 40, zt + 100), w - 110, MIRROR_H, fc=MIR, ec="#557", lw=.8))
    ax.plot([x + 70, x + w * .45], [zt + 160, zt + MIRROR_H], color="white", lw=4, alpha=.7)
    ax.text(x + 40 + (w - 110) / 2, zt + 100 + MIRROR_H / 2, f"MIRROR\n{w - 110:.0f} x {MIRROR_H}", ha="center", va="center", fontsize=6.5)
    ax.plot([x + 30, x + w - 30], [zt + 100 + MIRROR_H + 25] * 2, color="#ffcc33", lw=3)
    ax.text(x + w / 2, zt + 100 + MIRROR_H + 40, "LED", ha="center", fontsize=6, color="#a07800")
    dim(ax, x + w - 15, zt, zt + DRESS_OPEN, f"{DRESS_OPEN}")
    z = zt + DRESS_OPEN; shelf(ax, x, z, w); z += T; n += 1
    return n + shelves_up(ax, x, z, w, z1, mark=False)


def draw(ax, title, W, H, dsec, ztop):
    ax.add_patch(Rectangle((0, 0), W, H, fc="#f7f4ee", ec="none"))
    # carcass
    ax.add_patch(Rectangle((0, 0), T, BOX, fc=CAR, ec="#555")); ax.add_patch(Rectangle((W - T, 0), T, BOX, fc=CAR, ec="#555"))
    ax.add_patch(Rectangle((T, BASE), W - 2 * T, T, fc=CAR, ec="#555")); ax.add_patch(Rectangle((T, BOX - T), W - 2 * T, T, fc=CAR, ec="#555"))
    inner = W - 2 * T - 2 * T
    unit = inner / 5                                    # 2 + 1 + 2 doors
    secs = [2 * unit, unit, 2 * unit]
    x = T; z0, z1 = BASE + T, BOX - T
    info = []
    for i, w in enumerate(secs):
        if i:
            ax.add_patch(Rectangle((x, z0), T, z1 - z0, fc=CAR, ec="#555")); x += T
        z = z0
        if i == 1:                                      # centre door = dressing
            n = dressing(ax, x, z, w, z1, ztop, dsec == 1)
            ax.text(x + w / 2, -150, "DRESSING", ha="center", fontsize=7, color="#5a3d1e", weight="bold")
        else:
            n = 0
            if i == dsec:
                for k in range(2):
                    ax.add_patch(Rectangle((x + 4, z + k * DRW / 2 + 3), w - 8, DRW / 2 - 6, fc=DR, ec="#7a5a30"))
                ax.text(x + w / 2, z + DRW / 2, "2 drawers", ha="center", va="center", fontsize=7)
                z += DRW; shelf(ax, x, z, w); z += T; n += 1
            n += shelves_up(ax, x, z, w, z1)
            ax.text(x + w / 2, -150, "SHELVES", ha="center", fontsize=7, color="#555")
        ax.text(x + w / 2, -90, f"{w:.0f}", ha="center", fontsize=8, weight="bold")
        info.append((round(w), n))
        x += w
    # height marks on the left
    for zz in (BASE, ztop, BOX):
        ax.plot([-60, 0], [zz, zz], color="#999", lw=.5)
        ax.text(-70, zz, f"{zz}", ha="right", va="center", fontsize=6.5)
    # loft frame
    for xx in (0, W - T):
        ax.add_patch(Rectangle((xx, BOX), T, H - BOX, fc=FR, ec="#555"))
    ax.add_patch(Rectangle((T, BOX), W - 2 * T, T, fc=FR, ec="#555")); ax.add_patch(Rectangle((T, H - T), W - 2 * T, T, fc=FR, ec="#555"))
    ax.text(W / 2, BOX + (H - BOX) / 2, "LOFT (90 mm frame)", ha="center", va="center", fontsize=8, color="#555")
    ax.text(W / 2, -300, title, ha="center", fontsize=12, weight="bold")
    ax.text(W / 2, -430, f"5 doors (2 + 1 + 2)  ·  dressing in centre (top @ {ztop})  ·  other sections shelves 305 apart", ha="center", fontsize=8)
    ax.set_xlim(-260, W + 120); ax.set_ylim(-500, H + 80); ax.set_aspect("equal"); ax.axis("off")
    return info


def save(fig, name):
    for n in (name, name.replace(".png", " (updated).png")):
        try:
            fig.savefig(os.path.join(HERE, n), dpi=130, bbox_inches="tight"); return n
        except PermissionError:
            continue
    import time
    n = name.replace(".png", time.strftime(" (%H%M%S).png")); fig.savefig(os.path.join(HERE, n), dpi=130, bbox_inches="tight"); return n


fig, axs = plt.subplots(1, 4, figsize=(26, 9.5))
for ax, r in zip(axs, ROOMS):
    print(r[0], draw(ax, *r))
fig.suptitle("Mr. Manoker – 5-door wardrobes: INSIDE 2D (dressing in centre door, shelves in others) – picture only", fontsize=16, weight="bold")
print(save(fig, "All Bedrooms - 5 doors INSIDE with dressing (2D).png"))
