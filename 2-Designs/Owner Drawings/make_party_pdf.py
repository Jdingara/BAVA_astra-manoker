"""Customer PDF: 4 bedrooms, 5-door design, GF in DC687 Foliage Blue + 21125 MR+ Sunburn. Page 1 all four, then one page each (front + inside)."""
import os, time
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Rectangle
import render_5door as r5
import render_5door_inside as ri

HERE = os.path.dirname(os.path.abspath(__file__))
r5.HEX["DC687"] = "#46707a"          # approx Foliage Blue
r5.ROOMS[0] = ("GF BEDROOM", 2526, 2857, "DC687 Foliage Blue (Advance)", "21125 MR+ Sunburn (Merino)", [2, 4], [3], False)
IN = {r[0]: r for r in ri.ROOMS}
GOLD, INK = "#a9834a", "#1f1a17"


def header(fig, title, sub):
    fig.patches.append(Rectangle((0, 0.93), 1, 0.07, transform=fig.transFigure, fc=INK, zorder=0))
    fig.text(0.03, 0.958, "ASTRA INTERIORS", color=GOLD, fontsize=20, weight="bold", va="center")
    fig.text(0.97, 0.965, title, color="white", fontsize=16, weight="bold", ha="right", va="center")
    fig.text(0.97, 0.942, sub, color="#ddd2c0", fontsize=9, ha="right", va="center")
    fig.text(0.03, 0.02, "Astra Interiors · No 2, KVK Nagar, IAF Road, Selaiyur, Chennai 600073 · +91 97911 82789   |   "
             "Colours are for visual reference – final shade as per laminate sample.   " + time.strftime("%d-%m-%Y"), fontsize=7.5, color="#777")


def swatches(fig, y, main, acc):
    for k, c in enumerate((main, acc)):
        code = c.split()[0] if c.split()[0] != "626" else "626"
        fig.patches.append(Rectangle((0.06 + k * 0.33, y), 0.025, 0.035, transform=fig.transFigure, fc=r5.HEX[code], ec="#333"))
        fig.text(0.092 + k * 0.33, y + 0.017, c, fontsize=11, va="center")


out = os.path.join(HERE, time.strftime("Mr. Manoker - Wardrobes 5 doors (for customer) %H%M.pdf"))
for cand in (out, out.replace(".pdf", time.strftime(" (%H%M%S).pdf"))):
    try:
        pdf = PdfPages(cand); out = cand; break
    except PermissionError:
        continue
# page 1: all four
fig, axs = plt.subplots(1, 4, figsize=(16.5, 11.7))
plt.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.08, wspace=0.08)
for ax, r in zip(axs, r5.ROOMS):
    r5.draw(ax, *r); ax.texts[-1].set_fontsize(5.5); ax.texts[-1].set_text(ax.texts[-1].get_text().replace("  ·  ", "\n", 2))
header(fig, "Mr. Manoker – Wardrobes (4 bedrooms)", "5-door design · laminates as shown")
pdf.savefig(fig); plt.close(fig)
# one page per bedroom: front + inside
for r in r5.ROOMS:
    title, W, H, main, acc = r[:5]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(16.5, 11.7))
    plt.subplots_adjust(left=0.03, right=0.97, top=0.86, bottom=0.14, wspace=0.08)
    r5.draw(a1, *r); a1.set_title("FRONT (doors closed)", fontsize=13, weight="bold")
    ri.draw(a2, *IN[title]); a2.set_title("INSIDE (doors removed)", fontsize=13, weight="bold")
    header(fig, f"Mr. Manoker – {title.title()}", f"{W + 36} W × {H} H × 500 D  ·  5 doors + 5 loft doors + 2 drawers")
    fig.text(0.03, 0.105, "Laminates:", fontsize=11, weight="bold")
    swatches(fig, 0.06, main, acc)
    pdf.savefig(fig); plt.close(fig)
# kitchen page: Advance 626 Dream Green (bottom) + 676 Aqua Green (top)
r5.HEX["626"], r5.HEX["676"] = "#357a50", "#86c0ae"
KD = os.path.join(os.path.dirname(HERE), "Kitchen")
fig = plt.figure(figsize=(16.5, 11.7))
for k in (1, 2):
    ax = fig.add_axes([0.03 + (k - 1) * 0.48, 0.2, 0.46, 0.62])
    ax.imshow(plt.imread(os.path.join(KD, f"Kitchen - Advance 626 Dream Green + 676 Aqua Green - view {k}.jpg"))); ax.axis("off")
header(fig, "Mr. Manoker – Kitchen", "Top unit + bottom unit laminates (Advance)")
fig.text(0.03, 0.15, "Laminates:", fontsize=11, weight="bold")
swatches(fig, 0.09, "676 Aqua Green (Advance) – TOP unit", "626 DG Dream Green (Advance) – BOTTOM unit")
fig.text(0.03, 0.055, "Colours applied on the reference kitchen design for comparison – actual layout as per site measurements.", fontsize=9, color="#555")
pdf.savefig(fig); plt.close(fig)
pdf.close()
print("saved", out)
