"""Blender: each wardrobe without doors - assembled + exploded view. Run:
blender -b -P blender_owner_model.py -- <room> <samples>"""
import bpy, json, os, sys, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index("--") + 1:]
ROOM, SAMPLES = args[0], int(args[1]) if len(args) > 1 else 64
D = json.load(open(os.path.join(HERE, "model_parts.json")))
CL = json.load(open(os.path.join(HERE, "owner_cutlist.json")))[ROOM]
R = D["rooms"][ROOM]
parts = [p for p in D["parts"] if p[0] == ROOM]
DRAWER_HEX = {"GF": "#9b6638", "1F Master": "#075f7f", "1F Bedroom 2": "#f7cd0b", "2F": "#5c2568"}
COL = {"carcass": "#ece4d2", "shelf": "#f2ebdc", "back": "#e2d9c4", "frame": "#e6dcc6",
       "drawer": DRAWER_HEX[ROOM], "drawerbox": "#e9e0cc",
       "cover": {"GF": "#77a99b", "1F Master": "#d9cdd2", "1F Bedroom 2": "#035f33", "2F": "#a994c7"}[ROOM]}
MM = 0.001


def rgb(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c] + [1]


def mat(name, hexc, emit=0.0, rough=0.55):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgb(hexc); b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = rgb(hexc); b.inputs["Emission Strength"].default_value = emit
    return m


bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.engine = "CYCLES"
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "CUDA"; prefs.get_devices()
    for d in prefs.devices: d.use = True
    sc.cycles.device = "GPU"
except Exception as e:
    print("GPU fail", e)
sc.cycles.samples = SAMPLES; sc.cycles.use_denoising = True
sc.render.resolution_x, sc.render.resolution_y = 1600, 1400
sc.view_settings.view_transform = "Standard"
sc.view_settings.exposure = -0.3
sc.render.use_freestyle = True
sc.render.line_thickness = 1.1
M = {k: mat(k, v) for k, v in COL.items()}
M["led"] = mat("led", "#ffd27a", emit=3.0)
M["floor"] = mat("floor", "#b9b2a6", rough=0.4); M["wall"] = mat("wall", "#c9c6c0")
edge = mat("edge", "#b9ab8e")

W, H, Dp = R["width"], R["tall"], R["depth"]
cx, cz = W / 2, H / 2
objs = []


def box(name, x, y, z, w, d, h, m):
    # model: X = width, Y = depth (front y=0 -> Blender -Y is front), Z = height
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object; o.name = name
    o.scale = (w * MM, d * MM, h * MM)
    o.location = ((x + w / 2) * MM, (y + d / 2) * MM, (z + h / 2) * MM)
    bpy.ops.object.transform_apply(scale=True)
    bev = o.modifiers.new("b", "BEVEL"); bev.width = 0.0012; bev.segments = 2
    o.data.materials.append(m)
    return o


for _, part, mt, x, y, z, w, d, h in parts:
    o = box(part, x - R["x_off"], y, z, w, d, h, M[mt]); o["kind"] = mt; objs.append(o)
# LED strips in the grooves (100 mm from front, right face of the panel)
for g in CL["info"]["led"]:
    x = g["x"] - R["x_min"] + 18 - 4
    z = (R["y_bot"] - R["y_floor"]) + 18 + g["start"]
    o = box("LED strip", x, 100, z, 5, 12, g["length"], M["led"]); o["kind"] = "led"; objs.append(o)

# room
bpy.ops.mesh.primitive_plane_add(size=30, location=(cx * MM, 0, 0)); bpy.context.active_object.data.materials.append(M["floor"])
bpy.ops.mesh.primitive_plane_add(size=30, location=(cx * MM, 2.2, 0), rotation=(math.radians(90), 0, 0))
WALL = bpy.context.active_object
bpy.context.active_object.data.materials.append(M["wall"])
# lights
bpy.ops.object.light_add(type="AREA", location=(cx * MM - 1.2, -3.2, 3.2)); L = bpy.context.active_object
L.data.energy = 260; L.data.size = 3; L.rotation_euler = (math.radians(55), 0, math.radians(-20))
bpy.ops.object.light_add(type="AREA", location=(cx * MM + 2.5, -2.0, 1.6)); L2 = bpy.context.active_object
L2.data.energy = 90; L2.data.size = 2; L2.rotation_euler = (math.radians(70), 0, math.radians(50))
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.75, 0.76, 0.8, 1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.35

bpy.ops.object.camera_add(); cam = bpy.context.active_object; sc.camera = cam
cam.data.lens = 35


def aim(loc, tgt):
    cam.location = loc
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


def frame_ortho(rot_deg, pad=1.12):
    cam.data.type = "ORTHO"
    cam.rotation_euler = [math.radians(a) for a in rot_deg]
    bpy.context.view_layer.update()
    mw = cam.matrix_world.inverted()
    pts = [mw @ (o.matrix_world @ Vector(c)) for o in objs for c in o.bound_box]
    xs = [p.x for p in pts]; ys = [p.y for p in pts]
    cxl, cyl = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    cam.location = cam.matrix_world @ Vector((cxl, cyl, 0))
    asp = sc.render.resolution_x / sc.render.resolution_y
    cam.data.ortho_scale = max(max(xs) - min(xs), (max(ys) - min(ys)) * asp) * pad


def render(fn):
    sc.render.filepath = os.path.join(HERE, fn); bpy.ops.render.render(write_still=True); print("wrote", fn)


title = {"GF": "GF Bedroom", "1F Master": "1F M.Bedroom", "1F Bedroom 2": "1F Bedroom 2", "2F": "2F Bedroom"}[ROOM]
cam.location = (cx * MM, -8, 1.5)
frame_ortho((72, 0, 22))
render(f"3D - {title} - assembled (no doors).png")

# exploded
for o in objs:
    k = o["kind"]; p = o.location
    dx = (p.x - cx * MM) * 0.7; dz = (p.z - cz * MM) * 0.35; dy = 0
    if k == "back": dy = 0.9
    elif k == "shelf": dy = -0.35
    elif k == "drawer": dy = -1.0
    elif k == "drawerbox": dy = -0.7
    elif k == "frame": dz += 0.35
    elif k == "led": dy = -0.15
    elif k == "cover": dx = (0.6 if p.x > cx * MM else -0.6)
    if o.name.startswith("Top panel"): dz += 0.25
    if o.name.startswith("Bottom panel"): dz -= 0.15
    o.location = (p.x + dx, p.y + dy, p.z + dz + 0.15)
frame_ortho((68, 0, 28), pad=1.08)
render(f"3D - {title} - exploded pieces.png")
