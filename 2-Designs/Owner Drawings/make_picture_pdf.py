"""Pictures-only PDF for the customer: 4 bedroom fronts (5 doors) + 2 kitchen views. One picture per page, small heading."""
import os, time
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import render_5door as r5

HERE = os.path.dirname(os.path.abspath(__file__))
KD = os.path.join(os.path.dirname(HERE), "Kitchen")
r5.HEX["DC687"] = "#46707a"
r5.ROOMS[0] = ("GF BEDROOM", 2526, 2857, "DC687 Foliage Blue (Advance)", "21125 MR+ Sunburn (Merino)", [2, 4], [3], False)
out = os.path.join(HERE, time.strftime("Mr. Manoker - Pictures (wardrobes + kitchen) %H%M.pdf"))
pdf = PdfPages(out)
for r in r5.ROOMS:
    fig = plt.figure(figsize=(11.7, 16.5))
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.85]); r5.draw(ax, *r)
    fig.text(0.5, 0.95, f"Mr. Manoker – {r[0].title()}", ha="center", fontsize=20, weight="bold")
    pdf.savefig(fig); plt.close(fig)
for k in (1, 2):
    fig = plt.figure(figsize=(16.5, 11.7))
    ax = fig.add_axes([0.03, 0.08, 0.94, 0.8])
    ax.imshow(plt.imread(os.path.join(KD, f"Kitchen - Advance 626 Dream Green + 676 Aqua Green - view {k}.jpg"))); ax.axis("off")
    fig.text(0.5, 0.93, f"Mr. Manoker – Kitchen (view {k})", ha="center", fontsize=20, weight="bold")
    fig.text(0.5, 0.04, "Top: 676 Aqua Green  ·  Bottom: 626 DG Dream Green  (Advance)", ha="center", fontsize=12)
    pdf.savefig(fig); plt.close(fig)
pdf.close()
print("saved", out)
