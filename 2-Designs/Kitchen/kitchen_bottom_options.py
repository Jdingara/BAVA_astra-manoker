"""Recolour only the TOP units (wall cabinets + tall unit) of the kitchen reference renders with Merino contrast laminates.
Bottom stays dark green (27183 LV Camouflage). Shading of the original is kept (multiply)."""
import os, sys, colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = sys.argv[1:3]                    # reference renders (front U view, side view)
WOOD = sys.argv[3]                     # 37380 LV Antique Walnut swatch crop
OPTIONS = [("27111 LV Ivory White", "#ebe5d6"), ("27247 LV Stone", "#b8b3ae"),
           ("37380 LV Antique Walnut", "wood"), ("27184 LV Hazel", "#dcc3ab")]
# where the base cabinets are (below the counter): per image a function y_min(x)
# top-unit region per image: (yy, xx) -> bool
LINES = [lambda yy, xx: (yy < 428) | ((xx < 292) & (yy < 605)),
         lambda yy, xx: (yy < 438)]


def mask_for(a, line):
    h, w, _ = a.shape
    f = a / 255.0
    mx, mn = f.max(2), f.min(2)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    green = (g > r * 1.03) & (g >= b * 0.95) & (s > 0.07) & (mx > 0.18)
    yy, xx = np.mgrid[0:h, 0:w]
    m = green & line(yy, xx)
    im = Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    return np.array(im.filter(ImageFilter.GaussianBlur(0.8))) / 255.0


def recolour(path, line, target, wood):
    src = Image.open(path).convert("RGB"); a = np.array(src).astype(float)
    m = mask_for(a, line)
    L = a @ np.array([0.299, 0.587, 0.114])
    Lm = np.median(L[m > 0.5]) if (m > 0.5).any() else 60
    shade = np.clip(L / Lm, 0.25, 2.6)[..., None]
    if target == "wood":
        tex = Image.open(wood).convert("RGB")
        tw, th = tex.size
        tex = tex.crop((4, int(th * 0.27), int(tw * 0.5), int(th * 0.92))).resize((180, 360))
        tile = Image.new("RGB", src.size)
        for x in range(0, src.size[0], 180):
            for y in range(0, src.size[1], 360):
                tile.paste(tex, (x, y))
        base = np.array(tile).astype(float)
    else:
        base = np.array([int(target[i:i + 2], 16) for i in (1, 3, 5)], float)[None, None, :]
    new = np.clip(base * shade, 0, 255)
    out = a * (1 - m[..., None]) + new * m[..., None]
    return Image.fromarray(out.astype("uint8"))


def font(sz, bold=False):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf", sz)
    except OSError:
        return ImageFont.load_default()


sheets = []
for k, (name, tgt) in enumerate(OPTIONS):
    ims = [recolour(p, LINES[i], tgt, WOOD) for i, p in enumerate(IMG)]
    for i, im in enumerate(ims):
        im.save(os.path.join(HERE, f"Kitchen option {k + 1} - {name} - view {i + 1}.jpg"), quality=92)
    sheets.append((name, tgt, ims))

# comparison board: 4 options x 2 views
W, H = 3508, 2480
bd = Image.new("RGB", (W, H), (250, 247, 242)); d = ImageDraw.Draw(bd)
d.rectangle([0, 0, W, 170], fill=(31, 26, 23))
d.text((80, 35), "ASTRA INTERIORS", font=font(60, True), fill=(169, 131, 74))
d.text((W - 80, 40), "Mr. Manoker – Kitchen: TOP unit colour options", font=font(60, True), fill=(255, 255, 255), anchor="ra")
d.text((W - 80, 118), "Bottom: 27183 LV Camouflage (green)  ·  Top: Merino contrast colour", font=font(32), fill=(220, 210, 195), anchor="ra")
cw, chh = (W - 160 - 60) // 2, 0
for k, (name, tgt, ims) in enumerate(sheets):
    col, row = k % 2, k // 2
    x0 = 80 + col * (cw + 60); y0 = 210 + row * 1110
    a_ = ims[0].copy(); a_.thumbnail((cw, 900)); bd.paste(a_, (x0, y0 + 70))
    sw = "#6b5340" if tgt == "wood" else tgt
    d.rectangle([x0, y0, x0 + 60, y0 + 55], fill=sw, outline=(60, 60, 60), width=2)
    d.text((x0 + 80, y0 + 2), f"Option {k + 1}: {name}", font=font(44, True), fill=(31, 26, 23))
d.text((80, H - 70), "Colours shown on the reference image for comparison – check the real Merino sample before final. LV = Luvih matte finish.", font=font(30), fill=(110, 104, 98))
bd.save(os.path.join(HERE, "Kitchen - TOP colour options (Merino).jpg"), quality=92)
print("done")
