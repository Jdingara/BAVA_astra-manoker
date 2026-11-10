"""Customer pages (A4 landscape, 300 dpi-ish): per bedroom - 3/4 view (big), front view, inside view, laminate swatches.
Writes JPG per bedroom + one PDF with all 4 + a cover."""
import json, os, time
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
D = json.load(open(os.path.join(HERE, "owner_cutlist.json")))
import owner_cutlist as oc
W, H = 3508, 2480
GOLD = (169, 131, 74); INK = (31, 26, 23); GREY = (110, 104, 98)
T3 = {"GF": "GF Bedroom", "1F Master": "1F M.Bedroom", "1F Bedroom 2": "1F Bedroom 2", "2F": "2F Bedroom"}
TITLE = {"GF": "GF Bedroom", "1F Master": "1st Floor Master Bedroom", "1F Bedroom 2": "1st Floor Bedroom 2", "2F": "2nd Floor Bedroom"}
HEX = {"27173": "#77a99b", "21125": "#9b6638", "27292": "#d9cdd2", "27262": "#075f7f",
       "21433": "#035f33", "21457": "#f7cd0b", "21462": "#a994c7", "21452": "#5c2568"}


def font(sz, bold=False):
    for f in (("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"), "C:/Windows/Fonts/arial.ttf"):
        try:
            return ImageFont.truetype(f, sz)
        except OSError:
            continue
    return ImageFont.load_default()


def fit(img, w, h):
    im = img.copy(); im.thumbnail((w, h), Image.LANCZOS); return im


def header(d, title, sub):
    d.rectangle([0, 0, W, 190], fill=INK)
    d.text((90, 40), "ASTRA INTERIORS", font=font(64, True), fill=GOLD)
    d.text((90, 118), "Interior Designers & Decorators · Chennai · +91 97911 82789", font=font(34), fill=(220, 210, 195))
    d.text((W - 90, 50), title, font=font(70, True), fill=(255, 255, 255), anchor="ra")
    d.text((W - 90, 132), sub, font=font(34), fill=(220, 210, 195), anchor="ra")


def footer(d, txt):
    d.line([90, H - 110, W - 90, H - 110], fill=(210, 200, 185), width=3)
    d.text((90, H - 90), txt, font=font(30), fill=GREY)
    d.text((W - 90, H - 90), time.strftime("%d-%m-%Y"), font=font(30), fill=GREY, anchor="ra")


pages = []
for room, v in D.items():
    inf = v["info"]
    pg = Image.new("RGB", (W, H), (250, 247, 242)); d = ImageDraw.Draw(pg)
    header(d, f"Mr. Manoker – {TITLE[room]}", f"Wardrobe {inf['width'] + 36} W × {inf['height']} H mm  ·  6 doors + loft  ·  2 drawers")
    big = Image.open(os.path.join(HERE, f"Customer 3D - {T3[room]} - 3-4 view.png")).convert("RGB")
    front = Image.open(os.path.join(HERE, f"Customer 3D - {T3[room]} - front.png")).convert("RGB")
    inside = Image.open(os.path.join(HERE, f"3D - {T3[room]} - assembled (no doors).png")).convert("RGB")
    b = fit(big, 1950, 1950); pg.paste(b, (90, 240))
    d.text((90 + b.width // 2, 240 + b.height + 20), "3D view", font=font(38, True), fill=INK, anchor="ma")
    x2 = 90 + 1950 + 80; cw = W - 90 - x2
    f_ = fit(front, cw, 900); pg.paste(f_, (x2, 240))
    d.text((x2 + f_.width // 2, 240 + f_.height + 12), "Front view (doors closed)", font=font(34, True), fill=INK, anchor="ma")
    i_ = fit(inside, cw, 760); y3 = 240 + f_.height + 80; pg.paste(i_, (x2, y3))
    d.text((x2 + i_.width // 2, y3 + i_.height + 12), "Inside (without doors) – off-white inside, LED strips", font=font(34, True), fill=INK, anchor="ma")
    # laminate swatches
    codes = []
    for r in v["rows"]:
        if r[0] == "Shutters" and " - " in r[1]:
            c = r[1].rsplit(" - ", 1)[1].split(" (")[0]
            if c not in codes: codes.append(c)
    y = 240 + 1950 + 90
    d.text((90, y), "Laminates (Merino):", font=font(40, True), fill=INK)
    xx = 520
    for c in codes:
        d.rectangle([xx, y - 5, xx + 90, y + 55], fill=HEX[c.split()[0]], outline=(60, 60, 60), width=2)
        d.text((xx + 110, y), c, font=font(38), fill=INK); xx += 110 + int(d.textlength(c, font=font(38))) + 80
    d.rectangle([xx, y - 5, xx + 90, y + 55], fill="#ece4d2", outline=(60, 60, 60), width=2)
    d.text((xx + 110, y), "27111 LV Ivory White (inside)", font=font(38), fill=INK)
    footer(d, "3D images are for visual reference – actual laminate shade as per Merino sample. Handles / profile as finalised.")
    fn = os.path.join(HERE, f"Customer - {TITLE[room]} - 3D.jpg"); pg.save(fn, quality=92); pages.append(pg); print("wrote", fn)

# cover: all 4 together
cv = Image.new("RGB", (W, H), (250, 247, 242)); d = ImageDraw.Draw(cv)
header(d, "Mr. Manoker – Wardrobes", "4 bedrooms · 3D design with Merino laminates")
cw, ch = (W - 180 - 80) // 2, 960
for k, room in enumerate(D):
    im = fit(Image.open(os.path.join(HERE, f"Customer 3D - {T3[room]} - 3-4 view.png")).convert("RGB"), cw, ch)
    col, row = k % 2, k // 2
    x = 90 + col * (cw + 80); y = 240 + row * (ch + 110)
    cv.paste(im, (x, y))
    d.text((x + im.width + 30, y + 30), TITLE[room], font=font(48, True), fill=INK)
    codes = []
    for r in D[room]["rows"]:
        if r[0] == "Shutters" and " - " in r[1]:
            c = r[1].rsplit(" - ", 1)[1].split(" (")[0]
            if c not in codes: codes.append(c)
    for j, c in enumerate(codes):
        yy = y + 120 + j * 80
        d.rectangle([x + im.width + 30, yy, x + im.width + 90, yy + 55], fill=HEX[c.split()[0]], outline=(60, 60, 60), width=2)
        d.text((x + im.width + 110, yy + 5), c, font=font(34), fill=INK)
footer(d, "Astra Interiors · No 2, KVK Nagar, IAF Road, Selaiyur, Chennai 600073")
cv.save(os.path.join(HERE, "Customer - All Wardrobes - 3D.jpg"), quality=92)
out = os.path.join(HERE, "Mr. Manoker - Wardrobes 3D (for customer).pdf")
for cand in (out, out.replace(".pdf", time.strftime(" (%H%M%S).pdf"))):
    try:
        cv.save(cand, save_all=True, append_images=pages, resolution=300); out = cand; break
    except PermissionError:
        continue
print("saved", out)
