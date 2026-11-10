# Astra Interiors - GF Bedroom wardrobe (Mr. Manoker) - photo-realistic render with Blender Cycles.
# Run:  blender -b --python "GF Bedroom Wardrobe - Blender Render.py"
# Sizes in mm, same as the 2D drawing / SketchUp model.
import math
import os

import bpy

OUT = r"C:\Users\Home\Manoker\2-Designs"
W, H, DT = 2564.0, 2879.0, 450.0
L, DZ, P = 500.0, 400.0, 75.0
T, SH, GAP, ND = 18.0, 18.0, 3.0, 2
D = DT - SH
SW = (W - 2 * T) / 6.0
MAIN_B, MAIN_T = P, H - L
CEIL = H + 120.0
SAMPLES = int(os.environ.get("ASTRA_SAMPLES", "256"))
RES = (1600, 1200)

mm = lambda v: v / 1000.0


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


# ---------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
col = scene.collection


def setin(node, names, value):
    for n in names:
        if n in node.inputs:
            node.inputs[n].default_value = value
            return


def principled(name, color, rough=0.5, metal=0.0, coat=0.0, coat_rough=0.03, emission=None, strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    setin(b, ["Base Color"], srgb(color) if isinstance(color, str) else color)
    setin(b, ["Roughness"], rough)
    setin(b, ["Metallic"], metal)
    if coat:
        setin(b, ["Coat Weight", "Clearcoat"], coat)
        setin(b, ["Coat Roughness", "Clearcoat Roughness"], coat_rough)
    if emission:
        setin(b, ["Emission Color", "Emission"], srgb(emission))
        setin(b, ["Emission Strength"], strength)
    return m


def wood(name, light, dark, rough=0.45, scale=(18.0, 18.0, 0.35)):
    m = principled(name, light, rough)
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 6.0
    nz.inputs["Detail"].default_value = 8.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = srgb(dark)
    ramp.color_ramp.elements[1].color = srgb(light)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    nt.links.new(mp.outputs["Vector"], nz.inputs["Vector"])
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return m


def marble(name):
    m = principled(name, "#e8ded0", 0.12)
    nt = m.node_tree
    b = nt.nodes.get("Principled BSDF")
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.0
    brick.inputs["Scale"].default_value = 1.25
    brick.inputs["Mortar Size"].default_value = 0.004
    brick.inputs["Brick Width"].default_value = 1.0
    brick.inputs["Row Height"].default_value = 1.0
    nz = nt.nodes.new("ShaderNodeTexNoise")
    nz.inputs["Scale"].default_value = 3.0
    nz.inputs["Detail"].default_value = 12.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = srgb("#d8cbb8")
    ramp.color_ramp.elements[1].color = srgb("#efe7dc")
    nt.links.new(nz.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], brick.inputs["Color1"])
    nt.links.new(ramp.outputs["Color"], brick.inputs["Color2"])
    brick.inputs["Mortar"].default_value = srgb("#bfb2a0")
    nt.links.new(ramp.outputs["Color"], b.inputs["Base Color"])
    return m


MAT = {
    "A": principled("A sage gloss acrylic", "#7fa597", rough=0.06, coat=1.0, coat_rough=0.02),
    "B": wood("B fluted wood", "#7f4626", "#4f2a14", rough=0.5),
    "carcass": principled("Carcass liner", "#efe8dc", 0.6),
    "gold": principled("Handle gold", "#d9b07a", 0.22, metal=1.0),
    "chrome": principled("Rod chrome", "#d0d0d0", 0.15, metal=1.0),
    "wall": principled("Wall", "#f1ebe1", 0.9),
    "ceiling": principled("Ceiling", "#fbf8f3", 0.9),
    "floor": marble("Floor marble"),
    "skirt": principled("Wall skirting", "#e0d3bf", 0.4),
    "door": wood("Room door", "#a8743f", "#7a4f28", 0.45, scale=(30.0, 30.0, 0.4)),
    "black": principled("Window frame", "#1e1e1e", 0.4),
    "glass": principled("Glass", "#ffffff", 0.0),
    "blind": principled("Roman blind linen", "#cdbfa7", 0.95),
    "sheet": principled("Bed sheet", "#efe9df", 0.85),
    "throw": principled("Throw green", "#55624a", 0.95),
    "knit": principled("Knit blanket", "#b39b80", 0.98),
    "rug": principled("Rug", "#d9cbb3", 1.0),
    "spot": principled("Downlight", "#ffffff", 0.3, emission="#ffe2b8", strength=25.0),
    "pot": principled("Plant pot", "#f3efe8", 0.3),
    "leaf": principled("Leaf", "#3f6b3a", 0.6),
}
glass = MAT["glass"].node_tree.nodes.get("Principled BSDF")
setin(glass, ["Transmission Weight", "Transmission"], 1.0)


# ---------------------------------------------------------------- geometry helpers
def box(name, x, y, z, w, d, h, mat, bevel=0.0, parent=None):
    """Axis-aligned box in mm; x right, y back (to the wall), z up. Front of carcass is y = 0."""
    x0, y0, z0 = mm(x), mm(y), mm(z)
    x1, y1, z1 = mm(x + w), mm(y + d), mm(z + h)
    verts = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    faces = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    ob = bpy.data.objects.new(name, me)
    ob.data.materials.append(mat)
    col.objects.link(ob)
    if bevel:
        bv = ob.modifiers.new("Bevel", "BEVEL")
        bv.width = mm(bevel)
        bv.segments = 3
        bv.limit_method = "ANGLE"
        for p in me.polygons:
            p.use_smooth = True
    if parent is not None:
        ob.parent = parent
        ob.matrix_parent_inverse = parent.matrix_world.inverted()
    return ob


def empty(name, x, y, z):
    e = bpy.data.objects.new(name, None)
    e.location = (mm(x), mm(y), mm(z))
    col.objects.link(e)
    bpy.context.view_layer.update()
    return e


def cylinder_x(name, x1, x2, y, z, r, mat):
    bpy.ops.mesh.primitive_cylinder_add(radius=mm(r), depth=mm(x2 - x1), location=(mm((x1 + x2) / 2), mm(y), mm(z)), rotation=(0, math.pi / 2, 0))
    ob = bpy.context.active_object
    ob.name = name
    ob.data.materials.append(mat)
    return ob


# ---------------------------------------------------------------- wardrobe carcass
box("Side L", 0, 0, P, T, D, H - P, MAT["A"], 1)
box("Side R", W - T, 0, P, T, D, H - P, MAT["A"], 1)
for z, n in [(MAIN_B, "Main bottom"), (MAIN_T - T, "Main top"), (MAIN_T, "Loft bottom"), (H - T, "Loft top")]:
    box(n, T, 0, z, W - 2 * T, D, T, MAT["carcass"])
for i in (1, 2, 4, 5):
    x = T + i * SW - T / 2
    box(f"Partition {i}", x, 0, MAIN_B + T, T, D - 6, MAIN_T - MAIN_B - 2 * T, MAT["carcass"])
    box(f"Loft partition {i}", x, 0, MAIN_T + T, T, D - 6, L - 2 * T, MAT["carcass"])
box("Back", T, D - 6, P + T, W - 2 * T, 6, H - P - 2 * T, MAT["carcass"])
box("Plinth", T, 40, 0, W - 2 * T, T, P, MAT["A"])

bot, top = MAIN_B + T, MAIN_T - T
clear_h = top - bot


def sec(s0, n):
    return T + s0 * SW + (T / 2 if s0 else 0), T + (s0 + n) * SW - (T / 2 if s0 + n < 6 else 0)


for s0 in (0, 5):
    a, b = sec(s0, 1)
    for k in range(1, 5):
        box(f"Shelf {s0}-{k}", a, 24, bot + clear_h * k / 5 - T / 2, b - a, D - 30, T, MAT["carcass"])
for s0 in (1, 4):
    a, b = sec(s0, 1)
    box(f"Shelf rod {s0}", a, 24, top - 300 - T, b - a, D - 30, T, MAT["carcass"])
    cylinder_x(f"Rod {s0}", a + 4, b - 4, D / 2, top - 380, 12, MAT["chrome"])
a, b = sec(2, 2)
d_top = bot + DZ
upper = top - d_top
for z, n in [(d_top, "Drawer top"), (d_top + upper / 3, "Mid shelf 1"), (d_top + 2 * upper / 3, "Mid shelf 2")]:
    box(n, a, 24, z, b - a, D - 30, T, MAT["carcass"])

# ---------------------------------------------------------------- shutters / drawers
doors, drawers = [], []


def shutter(name, x1, x2, z1, z2, fin, hinge_left, handle=None, parent=None):
    w, h = x2 - x1, z2 - z1
    piv = parent or empty(name + " hinge", x1 if hinge_left else x2, 0, 0)
    if fin == "B":
        box(name + " base", x1, -SH + 3, z1, w, SH - 3, h, MAT["B"], 1, piv)
        n = max(1, round(w / 22))
        pitch = w / n
        for i in range(n):
            box(name + f" flute {i}", x1 + i * pitch + pitch * 0.12, -SH, z1, pitch * 0.76, 4, h, MAT["B"], 1.6, piv)
    else:
        box(name, x1, -SH, z1, w, SH, h, MAT["A"], 1.2, piv)
    if handle:
        side, at, horizontal = handle
        if horizontal:
            ln = min(w * 0.35, 450)
            hx = x1 + (w - ln) / 2
            box(name + " handle", hx, -SH - 32, z1 + h / 2 - 6, ln, 12, 12, MAT["gold"], 2.5, piv)
            for lx in (hx + 12, hx + ln - 24):
                box(name + " leg", lx, -SH - 20, z1 + h / 2 - 5, 12, 20, 10, MAT["gold"], 1, piv)
        else:
            ln = min(h * 0.28, 600)
            hx = x2 - 46 if side == "right" else x1 + 34
            zc = z1 + at * h
            box(name + " handle", hx, -SH - 32, zc - ln / 2, 12, 12, ln, MAT["gold"], 2.5, piv)
            for lz in (zc - ln / 2 + 12, zc + ln / 2 - 22):
                box(name + " leg", hx + 1, -SH - 20, lz, 10, 20, 10, MAT["gold"], 1, piv)
    if parent is None:
        doors.append((piv, hinge_left))
    return piv


loft_f = ["A", "B", "A", "A", "B", "A"]
for i in range(6):
    shutter(f"Loft {i + 1}", T + i * SW + GAP / 2, T + (i + 1) * SW - GAP / 2, MAIN_T + GAP / 2, H - GAP / 2, loft_f[i], i < 3)
y1, y2, h_top = MAIN_B + GAP / 2, MAIN_T - GAP / 2, MAIN_B + DZ
main = [(0, y1, "A", True, ("right", 0.55)), (1, y1, "B", True, ("right", 0.55)), (2, h_top + GAP / 2, "A", True, ("right", 0.45)),
        (3, h_top + GAP / 2, "A", False, ("left", 0.45)), (4, y1, "B", False, ("left", 0.55)), (5, y1, "A", False, ("left", 0.55))]
for mod, z1, fin, hl, hd in main:
    shutter(f"Shutter {mod + 1}", T + mod * SW + GAP / 2, T + (mod + 1) * SW - GAP / 2, z1, y2, fin, hl, (hd[0], hd[1], False))
dx1, dx2 = T + 2 * SW + GAP / 2, T + 4 * SW - GAP / 2
dh = DZ / ND
for k in range(ND):
    z1 = MAIN_B + k * dh + GAP / 2
    e = empty(f"Drawer {k + 1}", 0, 0, 0)
    shutter(f"Drawer {k + 1} front", dx1, dx2, z1, z1 + dh - GAP, "B", True, ("c", 0.5, True), parent=e)
    box(f"Drawer {k + 1} box", dx1 + 30, 0, z1 + 20, dx2 - dx1 - 60, D - 60, dh - 70, MAT["carcass"], 0, e)
    drawers.append(e)

# ---------------------------------------------------------------- room
RX1, RX2 = -1350.0, W + 1450.0
box("Floor", RX1, -5200, -20, RX2 - RX1, 5200 + D + 60, 20, MAT["floor"])
box("Back wall L", RX1, D, 0, -1150 - RX1, 120, CEIL, MAT["wall"])  # left of door
box("Back wall", -150, D, 0, W + 400, 120, CEIL, MAT["wall"])
box("Wall above door", -1150, D, 2150, 1000, 120, CEIL - 2150, MAT["wall"])
box("Back wall R1", W + 250, D, 0, 1100, 120, 950, MAT["wall"])  # below window
box("Back wall R2", W + 250, D, 2250, 1100, 120, CEIL - 2250, MAT["wall"])  # above window
box("Back wall R3", W + 1350, D, 0, RX2 - W - 1350 + 50, 120, CEIL, MAT["wall"])
box("Left wall", RX1 - 120, -5200, 0, 120, 5200 + D + 120, CEIL, MAT["wall"])
box("Right wall", RX2, -5200, 0, 120, 5200 + D + 120, CEIL, MAT["wall"])
box("Ceiling", RX1, -5200, CEIL, RX2 - RX1, 5200 + D + 120, 80, MAT["ceiling"])
box("Skirting L", RX1, D - 12, 0, -150 - RX1 - 1000, 12, 90, MAT["skirt"])
box("Skirting R", W + 250, D - 12, 0, RX2 - W - 250, 12, 90, MAT["skirt"])
# room door (left)
box("Door frame L", -1150, D - 40, 0, 50, 60, 2150, MAT["door"], 2)
box("Door frame R", -200, D - 40, 0, 50, 60, 2150, MAT["door"], 2)
box("Door frame top", -1150, D - 40, 2100, 1000, 60, 50, MAT["door"], 2)
box("Door leaf", -1100, D - 10, 0, 900, 40, 2100, MAT["door"], 2)
box("Door lever", -300, D - 40, 1000, 140, 22, 22, MAT["black"], 4)
# window (right) with roman blind
box("Window sill", W + 250, D - 60, 950, 1100, 240, 30, MAT["wall"], 3)
box("Win frame b", W + 250, D + 60, 980, 1100, 60, 50, MAT["black"])
box("Win frame t", W + 250, D + 60, 2200, 1100, 60, 50, MAT["black"])
box("Win frame l", W + 250, D + 60, 980, 50, 60, 1270, MAT["black"])
box("Win frame r", W + 1300, D + 60, 980, 50, 60, 1270, MAT["black"])
box("Win frame m", W + 775, D + 60, 980, 50, 60, 1270, MAT["black"])
for i in range(5):
    box(f"Grill {i}", W + 300 + i * 210, D + 40, 980, 12, 12, 1270, MAT["black"])
box("Glass", W + 300, D + 85, 1030, 1000, 6, 1170, MAT["glass"])
box("Blind", W + 230, D - 90, 1650, 1140, 40, 600, MAT["blind"], 8)
for i in range(3):
    box(f"Blind fold {i}", W + 230, D - 105, 1650 + i * 190, 1140, 30, 60, MAT["blind"], 12)
# bed + throw + blanket in the foreground, rug
bx1, bx2 = -700.0, 1500.0
box("Bed base", bx1, -3900, 0, bx2 - bx1, 2100, 380, MAT["sheet"], 20)
box("Mattress", bx1 + 20, -3880, 380, bx2 - bx1 - 40, 2060, 230, MAT["sheet"], 60)
box("Knit blanket", bx1 + 10, -2250, 570, bx2 - bx1 - 20, 450, 70, MAT["knit"], 30)
box("Throw", bx1 + 10, -2150, 600, bx2 - bx1 - 20, 300, 60, MAT["throw"], 25)
box("Rug", 1600, -1300, 0, 1500, 900, 8, MAT["rug"], 3)

# ---------------------------------------------------------------- lights
for i, xx in enumerate([T + SW * 1.5, T + SW * 3.0, T + SW * 4.5, -650, W + 800]):
    ld = bpy.data.lights.new(f"Spot {i}", "SPOT")
    ld.energy = 55 if i < 3 else 35
    ld.color = (1.0, 0.83, 0.63)
    ld.spot_size = math.radians(70)
    ld.spot_blend = 0.8
    ld.shadow_soft_size = 0.03
    lo = bpy.data.objects.new(f"Spot {i}", ld)
    lo.location = (mm(xx), mm(-330), mm(CEIL) - 0.01)
    lo.rotation_euler = (math.radians(-12), 0, 0)
    col.objects.link(lo)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.04, depth=0.004, location=(mm(xx), mm(-330), mm(CEIL) - 0.002))
    bpy.context.active_object.data.materials.append(MAT["spot"])
# daylight through the window
win = bpy.data.lights.new("Window light", "AREA")
win.energy = 260
win.size = 1.0
win.color = (0.95, 0.97, 1.0)
wo = bpy.data.objects.new("Window light", win)
wo.location = (mm(W + 800), mm(D + 200), mm(1600))
wo.rotation_euler = (math.radians(90), 0, 0)
col.objects.link(wo)
sun = bpy.data.lights.new("Sun", "SUN")
sun.energy = 2.0
sun.angle = math.radians(3)
so = bpy.data.objects.new("Sun", sun)
so.rotation_euler = (math.radians(-60), math.radians(25), math.radians(-150))
col.objects.link(so)
fill = bpy.data.lights.new("Fill", "AREA")
fill.energy = 120
fill.size = 3.0
fill.color = (1.0, 0.93, 0.85)
fo = bpy.data.objects.new("Fill", fill)
fo.location = (mm(W / 2), mm(-4300), mm(2400))
fo.rotation_euler = (math.radians(70), 0, 0)
col.objects.link(fo)

world = bpy.data.worlds.new("World")
world.use_nodes = True
bg = world.node_tree.nodes.get("Background")
bg.inputs["Color"].default_value = srgb("#dfe9f2")
bg.inputs["Strength"].default_value = 0.35
scene.world = world

# ---------------------------------------------------------------- camera & render settings
cam_d = bpy.data.cameras.new("Camera")
cam_d.lens = 22
cam = bpy.data.objects.new("Camera", cam_d)
col.objects.link(cam)
scene.camera = cam


def look(cam_obj, eye, target):
    import mathutils
    e, t = mathutils.Vector(eye), mathutils.Vector(target)
    cam_obj.location = e
    cam_obj.rotation_euler = (t - e).to_track_quat("-Z", "Y").to_euler()


scene.render.engine = "CYCLES"
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for dev_type in ("CUDA",):  # OptiX fails with the installed driver
        try:
            prefs.compute_device_type = dev_type
            prefs.get_devices()
            if any(d.type == dev_type for d in prefs.devices):
                for d in prefs.devices:
                    d.use = d.type == dev_type
                scene.cycles.device = "GPU"
                print("ASTRA: rendering on", dev_type)
                break
        except Exception as ex:  # noqa: BLE001
            print("ASTRA: device", dev_type, "unavailable:", ex)
except Exception as ex:  # noqa: BLE001
    print("ASTRA: GPU setup failed, using CPU:", ex)
scene.cycles.samples = SAMPLES
scene.cycles.use_adaptive_sampling = True
scene.cycles.use_denoising = True
try:
    scene.cycles.denoiser = "OPENIMAGEDENOISE"
except Exception:  # noqa: BLE001
    pass
scene.render.resolution_x, scene.render.resolution_y = RES
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
try:
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
except Exception:  # noqa: BLE001
    pass
scene.view_settings.exposure = -0.45

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT, "GF Bedroom Wardrobe - Blender Scene.blend"))

# 1) closed, front view like the reference
look(cam, (mm(W / 2 + 120), mm(-3700), mm(1480)), (mm(W / 2 + 60), mm(0), mm(1330)))
scene.render.filepath = os.path.join(OUT, "GF Bedroom Wardrobe - Render Front.png")
bpy.ops.render.render(write_still=True)
print("ASTRA: rendered front")

# 2) doors open, angle view
for piv, hinge_left in doors:
    piv.rotation_euler = (0, 0, math.radians(-100 if hinge_left else 100))
drawers[1].location = (0, mm(-300), 0)
look(cam, (mm(W * 0.92), mm(-2900), mm(1450)), (mm(W * 0.45), mm(120), mm(1320)))
scene.render.filepath = os.path.join(OUT, "GF Bedroom Wardrobe - Render Open.png")
bpy.ops.render.render(write_still=True)
print("ASTRA: rendered open")
