"""Recolour the kitchen reference renders: bottom = Advance 626 Dream Green, top = Advance 676 Aqua Green (approx shades)."""
import os, sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = sys.argv[1:3]
BOTTOM, TOP = "#357a50", "#86c0ae"          # approx: 626 Dream Green, 676 Aqua Green
TOP_REG = [lambda yy, xx: ((yy < 428) & (xx < 1295)) | ((xx < 292) & (yy < 605)), lambda yy, xx: (yy < 438)]
BOT_REG = [lambda yy, xx: (yy > 560 + np.maximum(0, xx - 1150) * 0.27) & (xx < 1495) & (xx > 295), lambda yy, xx: (yy > 568 + np.maximum(0, 520 - xx) * 0.13)]


CLOSE = 3


def recolour(a, region, target):
    f = a / 255.0
    mx, mn = f.max(2), f.min(2)
    s = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    green = (g > r * 1.03) & (g >= b * 0.95) & (s > 0.07) & (mx > 0.05)
    h, w, _ = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    m = green & region(yy, xx)
    im = Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.MaxFilter(CLOSE)).filter(ImageFilter.MinFilter(CLOSE))
    im = Image.fromarray((np.array(im) * region(yy, xx)).astype("uint8"))
    m = np.array(im.filter(ImageFilter.GaussianBlur(0.8))) / 255.0
    L = a @ np.array([0.299, 0.587, 0.114])
    Lm = np.median(L[m > 0.5]) if (m > 0.5).any() else 60
    shade = np.clip(L / Lm, 0.25, 1.7)[..., None]
    base = np.array([int(target[i:i + 2], 16) for i in (1, 3, 5)], float)[None, None, :]
    return a * (1 - m[..., None]) + np.clip(base * shade, 0, 255) * m[..., None]


for i, p in enumerate(IMG):
    a = np.array(Image.open(p).convert("RGB")).astype(float)
    globals()["CLOSE"] = 3 if i == 0 else 41
    a = recolour(a, TOP_REG[i], TOP)
    a = recolour(a, BOT_REG[i], BOTTOM)
    Image.fromarray(a.astype("uint8")).save(os.path.join(HERE, f"Kitchen - Advance 626 Dream Green + 676 Aqua Green - view {i + 1}.jpg"), quality=92)
print("ok")
