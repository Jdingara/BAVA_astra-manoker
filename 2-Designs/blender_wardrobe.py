# Astra Interiors - render any wardrobe from its "<name> - data.json" (made by wardrobe_gen.py).
# Run: blender -b --python blender_wardrobe.py -- "<path to data.json>" [samples]
import json
import math
import os
import sys

import bpy
import mathutils

args = sys.argv[sys.argv.index("--") + 1:]
DATA = json.load(open(args[0]))
SAMPLES = int(args[1]) if len(args) > 1 else 160
OUT = os.path.dirname(os.path.abspath(args[0]))
NAME = DATA["name"]
g = DATA["geom"]
W, H, D, L, P, T, SH, GAP, SW = (g[k] for k in ("W", "H", "D", "L", "P", "T", "SH", "GAP", "SW"))
MAIN_B, MAIN_T = P, H - L
CEIL = H + 120.0
mm = lambda v: v / 1000.0

# laminate colours by name in the colour label (screen approximations of the shade cards)
SHADES = {"light": "#c9bcc4", "teal": "#1d6f82", "green": "#2f6a3b", "yellow": "#f2c200", "lilac": "#b7a3d6",
          "purple": "#5a2a6f", "sage": "#7fa597"}


def shade(label):
    for k, v in SHADES.items():
        if k in label.lower():
            return v
    return "#cccccc"


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
col = scene.collection


def setin(node, names, value):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = value
            return


def principled(name, color, rough=0.5, metal=0.0, coat=0.0, emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    setin(b, ["Base Color"], srgb(color))
    setin(b, ["Roughness"], rough)
    setin(b, ["Metallic"], metal)
    if coat:
        setin(b, ["Coat Weight"], coat)
        setin(b, ["Coat Roughness"], 0.05)
    if emission:
        setin(b, ["Emission Color"], srgb(emission))
        setin(b, ["Emission Strength"], strength)
    return m


def marble(name):
    m = principled(name, "#e8ded0", 0.12)
    nt = m.node_tree
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 12.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = srgb("#d8cbb8")
    ramp.color_ramp.elements[1].color = srgb("#efe7dc")
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], nt.nodes.get("Principled BSDF").inputs["Base Color"])
    return m


COLS = DATA["colours"]
MAT = {}
for k, v in COLS.items():
    glossy = "gloss" in v.lower()
    MAT[k] = principled(f"{k} {v}", DATA.get("shades", {}).get(k) or shade(v), rough=0.08 if glossy else 0.42, coat=1.0 if glossy else 0.15)
FLUTED = {k for k, v in COLS.items() if "fluted" in v.lower()}
MAT.update({
    "carcass": principled("Carcass liner", "#efe8dc", 0.6),
    "gold": principled("Handle gold", "#d9b07a", 0.22, metal=1.0),
    "chrome": principled("Rod chrome", "#d0d0d0", 0.15, metal=1.0),
    "wall": principled("Wall", "#efe8de", 0.9),
    "ceiling": principled("Ceiling", "#fbf8f3", 0.9),
    "floor": marble("Floor marble"),
    "skirt": principled("Tile skirting", "#e3d8c8", 0.2),
    "door": principled("Room door", "#6e4a2e", 0.45),
    "black": principled("Black", "#1e1e1e", 0.4),
    "sheet": principled("Bed sheet", "#efe9df", 0.85),
    "throw": principled("Throw", DATA.get("shades", {}).get("B") or shade(COLS["B"]), 0.95),
    "knit": principled("Knit", "#b39b80", 0.98),
    "rug": principled("Rug", "#cfc3b0", 1.0),
    "glass": principled("Glass shelf", "#e8f3f2", 0.02),
    "spot": principled("Downlight", "#ffffff", 0.3, emission="#ffe2b8", strength=25.0),
    "headboard": principled("Headboard", "#c8bfb4", 0.9),
})
setin(MAT["glass"].node_tree.nodes.get("Principled BSDF"), ["Transmission Weight"], 0.9)


def box(name, x, y, z, w, d, h, mat, bevel=0.0, parent=None):
    x0, y0, z0, x1, y1, z1 = mm(x), mm(y), mm(z), mm(x + w), mm(y + d), mm(z + h)
    me = bpy.data.meshes.new(name)
    me.from_pydata([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], [],
                   [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)])
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    col.objects.link(ob)
    if bevel:
        bv = ob.modifiers.new("Bevel", "BEVEL")
        bv.width, bv.segments = mm(bevel), 3
        for p in me.polygons:
            p.use_smooth = True
    if parent is not None:
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
    return ob


def empty(name, x):
    e = bpy.data.objects.new(name, None)
    e.location = (mm(x), 0, 0)
    col.objects.link(e)
    bpy.context.view_layer.update()
    return e


mx = lambda m: T + m * SW
# ---------------------------------------------------------------- carcass + inside
box("Side L", 0, 0, P, T, D, H - P, MAT["A"], 1)
box("Side R", W - T, 0, P, T, D, H - P, MAT["A"], 1)
for z in (MAIN_B, MAIN_T - T, MAIN_T, H - T):
    box("Horizontal", T, 0, z, W - 2 * T, D, T, MAT["carcass"])
for x in g["part_x"]:
    box("Partition", x, 0, MAIN_B + T, T, D - 6, MAIN_T - MAIN_B - 2 * T, MAT["carcass"])
    box("Loft partition", x, 0, MAIN_T + T, T, D - 6, L - 2 * T, MAT["carcass"])
box("Back", T, D - 6, P + T, W - 2 * T, 6, H - P - 2 * T, MAT["carcass"])
box("Base", T, 40, 0, W - 2 * T, T, P, MAT["A"])
for a, b, z, kind in g["shelves"]:
    box("Shelf", a, 24, z, b - a, D - 30, T, MAT["carcass"])
for a, b, z in g["glass"]:
    box("Glass shelf", a + 2, 30, z, b - a - 4, D - 40, 8, MAT["glass"])
MIRROR = principled("Mirror", "#e8eef0", 0.02, metal=1.0)
LED = principled("LED strip", "#ffffff", 0.3, emission="#ffe6c4", strength=12.0)
for x1, x2, z1, z2 in g.get("mirrors", []):
    box("Dressing mirror", x1, D - 12, z1, x2 - x1, 5, z2 - z1, MIRROR, 1)
for x1, x2, z in g.get("leds", []):
    box("LED strip", x1, 30, z - 6, x2 - x1, 12, 6, LED)
    led = bpy.data.lights.new("Dressing LED", "AREA")
    led.energy, led.size, led.color = 25, mm(x2 - x1), (1.0, 0.88, 0.7)
    lo = bpy.data.objects.new("Dressing LED", led)
    lo.location = (mm((x1 + x2) / 2), mm(120), mm(z) - 0.01)
    col.objects.link(lo)
for x, z1, z2 in g["vparts"]:
    box("Inner partition", x, 0, z1, T, D - 6, z2 - z1, MAT["carcass"])
for a, b, z in g["rods"]:
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=mm(b - a - 8), location=(mm((a + b) / 2), mm(D / 2), mm(z)), rotation=(0, math.pi / 2, 0))
    bpy.context.active_object.data.materials.append(MAT["chrome"])

# ---------------------------------------------------------------- doors / drawers
doors, drawer_objs = [], []
dz_of = {}
for m1, m2, colr, n, dz in g["drawers"]:
    for m in range(int(m1), int(math.ceil(m2))):
        dz_of[m] = dz
for m, colr, bh, hinge in g.get("bottom_doors", []):
    dz_of[m] = bh


def door(name, x1, x2, z1, z2, colr, hinge, handle, short=False, parent=None):
    w, h = x2 - x1, z2 - z1
    piv = parent or empty(name, x1 if hinge == "L" else x2)
    if colr in FLUTED:
        box(name + " base", x1, -SH + 3, z1, w, SH - 3, h, MAT[colr], 1, piv)
        nfl = max(1, round(w / 22))
        pitch = w / nfl
        for i in range(nfl):
            box(name + " flute", x1 + i * pitch + pitch * 0.12, -SH, z1, pitch * 0.76, 4, h, MAT[colr], 1.6, piv)
    else:
        box(name, x1, -SH, z1, w, SH, h, MAT[colr], 1.2, piv)
    if handle == "H":
        ln = min(w * 0.35, 400)
        hx = x1 + (w - ln) / 2
        box("Handle", hx, -SH - 32, z1 + h / 2 - 6, ln, 12, 12, MAT["gold"], 2.5, piv)
        for lx in (hx + 12, hx + ln - 24):
            box("Leg", lx, -SH - 20, z1 + h / 2 - 5, 12, 20, 10, MAT["gold"], 1, piv)
    elif handle in ("L", "R"):
        ln = min(h * 0.5, 160) if short else min(h * 0.28, 600)
        hx = x2 - 46 if handle == "R" else x1 + 34
        zc = z1 + (0.25 if short else 0.5) * h
        box("Handle", hx, -SH - 32, zc - ln / 2, 12, 12, ln, MAT["gold"], 2.5, piv)
        for lz in (zc - ln / 2 + 12, zc + ln / 2 - 22):
            box("Leg", hx + 1, -SH - 20, lz, 10, 20, 10, MAT["gold"], 1, piv)
    if parent is None:
        doors.append((piv, hinge))


for ld in g["loft_doors"]:
    m1, m2, hinge = ld[:3]
    door("Loft door", mx(m1) + GAP / 2, mx(m2) - GAP / 2, MAIN_T + GAP / 2, H - GAP / 2, ld[3] if len(ld) > 3 else g["loft_colour"], hinge, "R" if hinge == "L" else "L", short=True)
# inside drawers (behind the doors): plain board fronts
for idr in g.get("int_drawers", []):
    x1, x2, n, dz = idr[:4]
    zb = idr[4] if len(idr) > 4 else MAIN_B + T
    for k in range(n):
        z1 = zb + k * dz / n + 3
        box("Inside drawer front", x1 + 3, 6, z1, x2 - x1 - 6, T, dz / n - 6, MAT["carcass"], 1)
        box("Inside drawer box", x1 + 13, 6 + T, z1 + 15, x2 - x1 - 26, D - 80, dz / n - 70, MAT["carcass"])
        box("Inside drawer pull", (x1 + x2) / 2 - 60, 0, z1 + dz / n - 40, 120, 6, 14, MAT["chrome"], 1)
for m, colr, hinge, handle in g["main_doors"]:
    door("Door", mx(m) + GAP / 2, mx(m + 1) - GAP / 2, MAIN_B + dz_of.get(m, 0) + GAP / 2, MAIN_T - GAP / 2, colr, hinge, handle)
for m, colr, bh, hinge in g.get("bottom_doors", []):
    door("Bottom door", mx(m) + GAP / 2, mx(m + 1) - GAP / 2, MAIN_B + GAP / 2, MAIN_B + bh - GAP / 2, colr, hinge, "R" if hinge == "L" else "L", short=True)
for m1, m2, colr, n, dz in g["drawers"]:
    for k in range(n):
        e = empty("Drawer", 0)
        z1 = MAIN_B + k * dz / n + GAP / 2
        door("Drawer front", mx(m1) + GAP / 2, mx(m2) - GAP / 2, z1, z1 + dz / n - GAP, colr, "L", "H", short=True, parent=e)
        box("Drawer box", mx(m1) + 30, 0, z1 + 20, (m2 - m1) * SW - 60, D - 60, dz / n - 70, MAT["carcass"], 0, e)
        drawer_objs.append((e, k, n))

# ---------------------------------------------------------------- room (door on the right like the references)
RX1, RX2 = -1500.0, W + 1300.0
box("Floor", RX1, -5200, -20, RX2 - RX1, 5200 + D + 60, 20, MAT["floor"])
box("Back wall", RX1, D, 0, RX2 - RX1, 120, CEIL, MAT["wall"])
box("Left wall", RX1 - 120, -5200, 0, 120, 5200 + D + 120, CEIL, MAT["wall"])
box("Right wall", RX2, -5200, 0, 120, 5200 + D + 120, CEIL, MAT["wall"])
box("Ceiling", RX1, -5200, CEIL, RX2 - RX1, 5200 + D + 120, 80, MAT["ceiling"])
box("Tile skirting L", RX1, D - 10, 0, -RX1, 10, 100, MAT["skirt"])
box("Tile skirting R", W, D - 10, 0, RX2 - W, 10, 100, MAT["skirt"])
box("Room door frame", W + 250, D - 40, 0, 1000, 50, 2150, MAT["door"], 2)
box("Room door", W + 300, D - 20, 0, 900, 40, 2100, MAT["door"], 2)
box("Room door lever", W + 380, D - 45, 1000, 130, 22, 22, MAT["black"], 4)
for i in range(9):  # slatted wall panel on the left like the references
    box(f"Slat {i}", -1250 + i * 70, D - 60, 0, 40, 60, CEIL, MAT["door"], 3)
# bed with headboard on the left wall, foot towards the right (as in the reference pictures)
by1, by2 = -3300.0, -1500.0
box("Headboard", RX1, by1 - 40, 0, 90, by2 - by1 + 80, 1150, MAT["headboard"], 30)
box("Bed base", RX1 + 90, by1, 0, 2100, by2 - by1, 380, MAT["sheet"], 20)
box("Mattress", RX1 + 100, by1 + 20, 380, 2080, by2 - by1 - 40, 230, MAT["sheet"], 60)
box("Throw", RX1 + 1500, by1 + 10, 600, 600, by2 - by1 - 20, 60, MAT["throw"], 25)
box("Rug", 900, -2700, 0, 1600, 1300, 8, MAT["rug"], 3)

# ---------------------------------------------------------------- lights
for i, xx in enumerate([W * 0.2, W * 0.5, W * 0.8, -700, W + 700]):
    ld = bpy.data.lights.new(f"Spot {i}", "SPOT")
    ld.energy, ld.color, ld.spot_size, ld.spot_blend, ld.shadow_soft_size = (60 if i < 3 else 40), (1.0, 0.83, 0.63), math.radians(75), 0.8, 0.03
    lo = bpy.data.objects.new(f"Spot {i}", ld)
    lo.location, lo.rotation_euler = (mm(xx), mm(-350), mm(CEIL) - 0.01), (math.radians(-12), 0, 0)
    col.objects.link(lo)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.004, location=(mm(xx), mm(-350), mm(CEIL) - 0.002))
    bpy.context.active_object.data.materials.append(MAT["spot"])
pend = bpy.data.lights.new("Pendant", "POINT")
pend.energy, pend.color, pend.shadow_soft_size = 40, (1.0, 0.8, 0.55), 0.12
po = bpy.data.objects.new("Pendant", pend)
po.location = (mm(-900), mm(-700), 1.3)
col.objects.link(po)
cove = bpy.data.lights.new("Cove", "AREA")
cove.energy, cove.size, cove.color = 110, 3.0, (1.0, 0.85, 0.65)
co = bpy.data.objects.new("Cove", cove)
co.location, co.rotation_euler = (mm(W / 2), mm(-1200), mm(CEIL) - 0.05), (0, 0, 0)
col.objects.link(co)
fill = bpy.data.lights.new("Fill", "AREA")
fill.energy, fill.size, fill.color = 120, 3.0, (1.0, 0.93, 0.85)
fo = bpy.data.objects.new("Fill", fill)
fo.location, fo.rotation_euler = (mm(W / 2), mm(-4300), mm(2400)), (math.radians(70), 0, 0)
col.objects.link(fo)
world = bpy.data.worlds.new("World")
world.use_nodes = True
world.node_tree.nodes.get("Background").inputs["Color"].default_value = srgb("#e9e2d8")
world.node_tree.nodes.get("Background").inputs["Strength"].default_value = 0.25
scene.world = world

# ---------------------------------------------------------------- camera / render
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
cam.data.lens = 22
col.objects.link(cam)
scene.camera = cam


def look(eye, target):
    e, t = mathutils.Vector(eye), mathutils.Vector(target)
    cam.location = e
    cam.rotation_euler = (t - e).to_track_quat("-Z", "Y").to_euler()


scene.render.engine = "CYCLES"
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "CUDA"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = d.type == "CUDA"
    scene.cycles.device = "GPU"
except Exception as ex:  # noqa: BLE001
    print("ASTRA: GPU unavailable, CPU render:", ex)
scene.cycles.samples = SAMPLES
scene.cycles.use_adaptive_sampling = True
scene.cycles.use_denoising = True
try:
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
except Exception:  # noqa: BLE001
    pass
scene.render.resolution_x, scene.render.resolution_y = 1600, 1200
scene.render.image_settings.file_format = "PNG"
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = -0.9

# angled view like the reference pictures
look((mm(W * 0.15), mm(-3300), mm(1450)), (mm(W * 0.58), mm(0), mm(1350)))
scene.render.filepath = os.path.join(OUT, f"{NAME} - Render.png")
bpy.ops.render.render(write_still=True)
print("ASTRA: rendered closed")
for piv, hinge in doors:
    piv.rotation_euler = (0, 0, math.radians(-100 if hinge == "L" else 100))
for e, k, n in drawer_objs:
    if k == n - 1:
        e.location = (0, mm(-280), 0)
look((mm(W * 0.85), mm(-2900), mm(1450)), (mm(W * 0.45), mm(120), mm(1300)))
scene.render.filepath = os.path.join(OUT, f"{NAME} - Render Open.png")
bpy.ops.render.render(write_still=True)
print("ASTRA: rendered open")
