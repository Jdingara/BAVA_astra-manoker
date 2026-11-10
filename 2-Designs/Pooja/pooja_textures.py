"""Door textures for the 3D: colour image + glow mask (cut-outs) for the left/right CNC doors."""
import os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pooja_2d as p2

HERE = os.path.dirname(os.path.abspath(__file__))
DW, DH = 519, 1143
for side, mirror in (("L", 1), ("R", -1)):
    for kind in ("colour", "mask"):
        fig = plt.figure(figsize=(DW / 100, DH / 100), dpi=200)
        ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, DW); ax.set_ylim(0, DH); ax.axis("off")
        p2.CUT = "#ffd27a" if kind == "colour" else "#ffffff"
        ax.add_patch(Rectangle((0, 0), DW, DH, fc="#5e3820" if kind == "colour" else "#000000"))
        p2.door_jali_short(ax, 0, DW, 0, DH, mirror)
        fig.savefig(os.path.join(HERE, f"tex_door_{side}_{kind}.png"), facecolor="black"); plt.close(fig)
print("ok")
