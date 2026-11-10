"""Front view of each wardrobe with the Merino laminate on every shutter (doors, drawer fronts, loft doors, skirting)."""
import json, os, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import owner_cutlist as oc

HERE = os.path.dirname(os.path.abspath(__file__))
B = json.load(open(os.path.join(HERE, "boards.json")))
T = 18.0
HEX = {"27173": "#77a99b", "21125": "#9b6638", "27292": "#d9cdd2", "27262": "#075f7f",
       "21433": "#035f33", "21457": "#f7cd0b", "21462": "#a994c7", "21452": "#5c2568"}
TITLE = {"GF": "GF BEDROOM", "1F Master": "1ST FLOOR M.BEDROOM", "1F Bedroom 2": "1ST FLOOR BEDROOM 2", "2F": "2ND FLOOR BEDROOM"}


def hexof(c):
    return HEX[c.split()[0]]


def ink(h):
    r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
    return "#111" if 0.299 * r + 0.587 * g + 0.114 * b > 150 else "#fff"


def label(c):
    p = c.replace(" (", "|").rstrip(")").split("|")[0].split()
    return p[0] + (" " + p[1] if p[1] in ("LV", "SF") else "") + "\n" + "\n".join(x for x in p[1:] if x not in ("LV", "SF"))


def shapes(name):
    d = B[name]
    hb = [tuple(b) for b in d["h"]]; vb = [tuple(b) for b in d["v"]]
    y_floor = min(b[1] for b in vb)
    tall_top = max(b[2] for b in vb)
    x_min = min(b[0] for b in vb)
    width = max(b[0] + T for b in vb) - x_min
    y_bot = min(b[0] for b in hb)
    main_top = min(b[0] for b in hb if b[0] > y_bot + 1500 and b[2] - b[1] >= 0.6 * width)
    cols = sorted({x for x, a, b in vb if a <= y_bot + T + 5 and b >= main_top - 5})
    groups = []
    for x in cols:
        if groups and x - groups[-1][-1] < 40: groups[-1].append(x)
        else: groups.append([x])
    edges = [min(groups[0])] + [(min(g) + max(g) + T) / 2 for g in groups[1:-1]] + [max(groups[-1]) + T]
    f_bot, f_top = y_bot, main_top + T
    col = oc.DOOR_COLOURS[name]; lcol = oc.LOFT_COLOURS[name]
    out = []   # (x, y, w, h, colour, kind)
    nd = 2 * (len(edges) - 1)
    dw = math.floor((edges[-1] - edges[0] - 2 * oc.GAP_END - (nd - 1) * oc.GAP_JOINT) / nd)
    xs = [edges[0] + oc.GAP_END + k * (dw + oc.GAP_JOINT) for k in range(nd)]
    for i, (xa, xb) in enumerate(zip(edges, edges[1:])):
        drw = [dd for dd in oc.DRAWERS[name] if xa - 5 <= dd[0] and dd[1] <= xb + 5]
        z0 = f_bot
        if drw:
            x1, x2, n, dh, lab = drw[0]
            divs = sorted(y for y, a, b in hb if a <= x1 + 5 and b >= x2 - 5 and y_bot + 1 < y < y_bot + 30 + n * (dh + T) + 40)[:n]
            cuts = [f_bot] + [y + T / 2 for y in divs]
            for k_, (lo, hi) in enumerate(zip(cuts, cuts[1:])):
                g0 = oc.GAP_EDGE if k_ == 0 else oc.GAP_JOINT / 2
                out.append((xs[2 * i], lo + g0, 2 * dw + oc.GAP_JOINT, hi - lo - g0 - oc.GAP_JOINT / 2, oc.DRAWER_COLOUR[name], "drawer"))
            z0 = cuts[-1]
        for j in range(2):
            x = xs[2 * i + j]
            gb = oc.GAP_JOINT / 2 if drw else oc.GAP_EDGE
            out.append((x, z0 + gb, dw, f_top - z0 - gb - oc.GAP_JOINT / 2, col[2 * i + j], "door"))
            out.append((x, f_top + oc.GAP_JOINT / 2, dw, tall_top - f_top - oc.GAP_JOINT / 2 - oc.GAP_EDGE, lcol[2 * i + j], "loft"))
    out.append((edges[0], y_floor, edges[-1] - edges[0], y_bot - y_floor, oc.SKIRT_COLOUR[name], "skirting"))
    for xc in (edges[0] - T, edges[-1]):   # cover on one side, 100 strip on the other: both show 18 mm from the front
        out.append((xc, y_floor, T, f_top - y_floor - 1.5, oc.SKIRT_COLOUR[name], "cover"))
        out.append((xc, f_top + 1.5, T, tall_top - f_top - 1.5, oc.SKIRT_COLOUR[name], "cover"))
    return out, (edges[0] - T, y_floor, edges[-1] + T, tall_top)


def draw(ax, name):
    sh, (X0, Y0, X1, Y1) = shapes(name)
    ax.add_patch(Rectangle((X0 - 30, Y0 - 20), X1 - X0 + 60, Y1 - Y0 + 40, fc="#2b2b2b", ec="none"))
    for x, y, w, h, c, k in sh:
        hx = hexof(c)
        ax.add_patch(Rectangle((x, y), w, h, fc=hx, ec="#1a1a1a", lw=0.6))
        if k not in ("skirting", "cover"):
            txt = label(c) + f"\n{h:.0f} × {w:.0f}" if k != "drawer" else label(c).replace("\n", " ") + f"  ·  {h:.0f} × {w:.0f}"
            ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center",
                    fontsize=6.5 if k != "drawer" else 6, color=ink(hx))
    ax.text((X0 + X1) / 2, Y0 - 160, TITLE[name], ha="center", fontsize=12, weight="bold")
    used = []
    for s in sh:
        if s[4] not in used: used.append(s[4])
    ax.text((X0 + X1) / 2, Y0 - 300, "   +   ".join(u.replace(" (", "  (") for u in used), ha="center", fontsize=8.5)
    ax.text((X0 + X1) / 2, Y1 + 80, f"{X1 - X0:.0f} W × {Y1 - Y0:.0f} H × 500 D  ·  6 doors + 6 loft doors + skirting + side cover {oc.COVER_SIDE[name]} (518 deep) + 100 strip other side", ha="center", fontsize=8.5)
    ax.set_xlim(X0 - 150, X1 + 150); ax.set_ylim(Y0 - 380, Y1 + 160); ax.set_aspect("equal"); ax.axis("off")


if __name__ == "__main__":
    names = ["GF", "1F Master", "1F Bedroom 2", "2F"]
    for n in names:
        fig, ax = plt.subplots(figsize=(8, 10)); draw(ax, n)
        fig.savefig(os.path.join(HERE, f"shutters_{n}.png"), dpi=170, bbox_inches="tight"); plt.close(fig)
    fig, axs = plt.subplots(1, 4, figsize=(26, 9.5))
    for ax, n in zip(axs, names): draw(ax, n)
    fig.suptitle("Mr. Manoker – Wardrobe shutters with Merino laminates (Astra Interiors)", fontsize=16, weight="bold")
    import time
    for nm in ("All Bedrooms - Laminate Shutters.png", "All Bedrooms - Laminate Shutters (updated).png", time.strftime("All Bedrooms - Laminate Shutters (%H%M%S).png")):
        try:
            fig.savefig(os.path.join(HERE, nm), dpi=130, bbox_inches="tight"); print("saved", nm); break
        except OSError:
            continue
    print("ok")
