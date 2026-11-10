"""Mr. Manoker kitchen - 3D render from kitchen_parts.json.  blender -b -P blender_kitchen.py -- <samples>"""
import bpy, json, os, sys, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
args = [a for a in (sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []) if a != "--corner"]
SAMPLES = int(args[0]) if args else 96
TOP_OVERRIDE = args[1] if len(args) > 1 else None          # e.g. "27292 LV Mink:#d8ccd1"
SUFFIX = args[2] if len(args) > 2 else ""
D = json.load(open(os.path.join(HERE, "kitchen_parts.json")))
RX, RY, RH = D["room"]
MM = 0.001
LAM = {"27183 LV Camouflage": "#28644d", "27111 LV Ivory White": "#efe9dc"}


def rgb(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c] + [1]


MAT = {}


def mat(key, hexc, rough=0.5, metal=0.0, emit=0.0):
    if key in MAT:
        return MAT[key]
    m = bpy.data.materials.new(key); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgb(hexc); b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = rgb(hexc); b.inputs["Emission Strength"].default_value = emit
    MAT[key] = m
    return m


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
try:
    pr = bpy.context.preferences.addons["cycles"].preferences
    pr.compute_device_type = "CUDA"; pr.get_devices()
    for d in pr.devices: d.use = True
    sc.cycles.device = "GPU"
except Exception as e:
    print("GPU", e)
sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1920, 1200
sc.view_settings.view_transform = "AgX"; sc.view_settings.exposure = -1.3


def box(x, y, z, w, d, h, m, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.scale = (w * MM, d * MM, h * MM)
    o.location = ((x + w / 2) * MM, (y + d / 2) * MM, (z + h / 2) * MM)
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 2
    o.data.materials.append(m)
    return o


M = {"carcass": mat("carcass", "#ece4d2", 0.6), "shelf": mat("shelf", "#ece4d2", 0.6), "back": mat("back", "#e2d9c4", 0.7),
     "masonry": mat("masonry", "#f1ede6", 0.85), "granite": mat("granite", "#1d1d1f", 0.12),
     "rolling": mat("rolling", "#9aa1a6", 0.35, 0.7), "hob": mat("hob", "#0b0b0c", 0.05),
     "sink": mat("sink", "#c9ccd0", 0.2, 1.0), "window": mat("window", "#dff0ff", 0.2, emit=3.0)}
for p in D["parts"]:
    x, y, z, w, d, h = p["box"]
    k = p["kind"]
    if k == "front":
        col = LAM[p["colour"]]
        if TOP_OVERRIDE and p["colour"] == "27111 LV Ivory White":
            col = TOP_OVERRIDE.split(":")[1]
        m = mat("front-" + col, col, 0.35)
        box(x, y, z, w, d, h, m, bevel=0.0007)
    elif k == "profile":
        box(x, y, z, w, d, h, mat("alu", "#b9bdc1", 0.25, 1.0))
    elif k == "rolling":
        box(x, y, z, w, d, h, M["rolling"])
        for zz in range(int(z) + 25, int(z + h), 45):     # slats on the room side (+y)
            box(x + 2, y + d, zz, w - 4, 4, 6, mat("slat", "#5f666b", 0.35, 0.6))
        box(x - 8, y + d, z, 10, 25, h, mat("track", "#7d858a", 0.3, 0.8)); box(x + w - 2, y + d, z, 10, 25, h, mat("track", "#7d858a", 0.3, 0.8))
    else:
        box(x, y, z, w, d, h, M.get(k, M["carcass"]), bevel=0.0006 if k in ("granite",) else 0.0)
# tap at the sink
sx, sy = [p for p in D["parts"] if p["kind"] == "sink"][0]["box"][:2]
box(sx + 470, sy + 240, 847, 30, 30, 260, M["sink"]); box(sx + 330, sy + 245, 1080, 170, 20, 20, M["sink"])
# hob burners
hx, hy = [p for p in D["parts"] if p["kind"] == "hob"][0]["box"][:2]
for bx in (120, 330, 540):
    box(hx + bx, hy + 140, 855, 110, 110, 18, mat("burner", "#2a2a2a", 0.3, 0.8))

# room: floor, walls (south wall with entrance opening), ceiling
fl = mat("floor", "#ece8e2", 0.18); wl = mat("wall", "#f4f1ec", 0.85); tile = mat("dado", "#d9dadb", 0.4)
box(-200, -200, -20, RX + 400, RY + 400, 20, fl)
box(-150, -150, 0, 150, RY + 300, RH, wl)                      # west
box(RX, -150, 0, 150, RY + 300, RH, wl)                        # east
box(-150, RY, 0, RX + 300, 150, RH, wl)                        # north (window wall)
box(-150, -150, 0, 1900, 150, RH, wl); box(RX - 150, -150, 0, 300, 150, RH, wl); box(1750, -150, 2100, RX - 1900, 150, RH - 2100, wl)
box(-200, -200, RH, RX + 400, RY + 400, 20, wl)                # ceiling
# backsplash band (grey tile like site) above counter on N/E walls
box(0, RY - 3, 847, RX, 3, 600, tile); box(RX - 3, RY - 1500, 847, 3, 1500, 600, tile)
# lights
for (lx, ly) in ((RX * 0.3, RY * 0.65), (RX * 0.7, RY * 0.65), (RX * 0.5, RY * 0.3)):
    bpy.ops.object.light_add(type="AREA", location=(lx * MM, ly * MM, (RH - 30) * MM))
    L = bpy.context.active_object; L.data.energy = 60; L.data.size = 0.35; L.data.color = (1.0, 0.95, 0.88)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=0.004, location=(lx * MM, ly * MM, (RH - 2) * MM))
    bpy.context.active_object.data.materials.append(mat("downlight", "#fff6e6", 0.3, emit=10))
bpy.ops.object.light_add(type="AREA", location=((MD := 560) * MM + 1.2, (RY + 600) * MM, 1.4))   # daylight through window
Wd = bpy.context.active_object; Wd.data.energy = 250; Wd.data.size = 1.8; Wd.rotation_euler = (math.radians(90), 0, 0); Wd.data.color = (0.95, 0.98, 1.0)
# under-cabinet LED strips (warm) under top units
for p in D["parts"]:
    if p["kind"] == "carcass" and p["name"] == "tb" and abs(p["box"][2] - 1447) < 1:
        x, y, z, w, d, h = p["box"]
        box(x, y, z - 4, w, d, 4, mat("led", "#ffe2b0", 0.5, emit=4))
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.9, 0.92, 0.95, 1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.3

bpy.ops.object.camera_add(); cam = bpy.context.active_object; sc.camera = cam


def shot(loc, tgt, lens, fn):
    cam.location = [v * MM for v in loc]; cam.data.lens = lens
    cam.rotation_euler = (Vector([v * MM for v in tgt]) - Vector(cam.location)).to_track_quat("-Z", "Y").to_euler()
    if SUFFIX:
        fn = fn.replace(".png", f" - top {SUFFIX}.png")
    sc.render.filepath = os.path.join(HERE, fn); bpy.ops.render.render(write_still=True); print("wrote", fn)


CLOSEUP = "--corner" in sys.argv
if CLOSEUP:
    shot((RX - 1500, RY - 1700, 1100), (RX - 400, RY - 400, 450), 20, "Kitchen 3D - right corner close-up.png"); sys.exit(0)
shot((RX - 500, 80, 1650), (RX * 0.35, RY * 0.8, 1200), 17, "Kitchen 3D - view 1 (from entrance).png")
shot((1500, 2300, 1550), (350, 150, 1250), 20, "Kitchen 3D - view 2 (magic corner + garage).png")
shot((1300, 900, 1600), (RX - 200, RY - 700, 1250), 17, "Kitchen 3D - view 3 (sink side).png")
