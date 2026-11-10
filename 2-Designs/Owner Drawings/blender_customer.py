"""Customer 3D renders: wardrobe with doors closed in the Merino laminate colours.
blender -b -P blender_customer.py -- <room> <samples>"""
import bpy, json, os, sys, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index("--") + 1:]
ROOM, SAMPLES = args[0], int(args[1]) if len(args) > 1 else 96
D = json.load(open(os.path.join(HERE, "model_parts.json")))
SH = json.load(open(os.path.join(HERE, "shutter_shapes.json")))[ROOM]
R = D["rooms"][ROOM]
parts = [p for p in D["parts"] if p[0] == ROOM]
COVER = {"GF": "#77a99b", "1F Master": "#d9cdd2", "1F Bedroom 2": "#035f33", "2F": "#a994c7"}[ROOM]
MM = 0.001
TITLE = {"GF": "GF Bedroom", "1F Master": "1F M.Bedroom", "1F Bedroom 2": "1F Bedroom 2", "2F": "2F Bedroom"}[ROOM]


def rgb(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c] + [1]


MATS = {}


def mat(hexc, rough=0.5, emit=0.0):
    key = (hexc, rough, emit)
    if key in MATS:
        return MATS[key]
    m = bpy.data.materials.new(hexc); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgb(hexc); b.inputs["Roughness"].default_value = rough
    if emit:
        b.inputs["Emission Color"].default_value = rgb(hexc); b.inputs["Emission Strength"].default_value = emit
    MATS[key] = m
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
sc.render.resolution_x, sc.render.resolution_y = 1600, 1600
sc.view_settings.view_transform = "AgX"
sc.view_settings.exposure = -0.9


def box(x, y, z, w, d, h, m, bevel=0.0008):
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.scale = (w * MM, d * MM, h * MM)
    o.location = ((x + w / 2) * MM, (y + d / 2) * MM, (z + h / 2) * MM)
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 2
    o.data.materials.append(m)
    return o


carcass = mat("#ece4d2", 0.6)
for _, part, mt, x, y, z, w, d, h in parts:
    if mt in ("drawer",):
        continue                                     # drawer fronts come from the shutter list
    m = mat(COVER, 0.5) if mt == "cover" else carcass
    box(x - R["x_off"], y, z, w, d, h, m)
# shutters (doors, loft doors, drawer fronts, skirting) in front of the carcass: y = -18 .. 0
for x, z, w, h, hexc, kind, name in SH:
    box(x, -18, z, w, 18, h, mat(hexc, 0.45), bevel=0.0006)

W, H, Dp = R["width"], R["tall"], R["depth"]
cx = W / 2
# room: floor, back wall, side walls, ceiling
fl = mat("#e9e3da", 0.25); wl = mat("#f3efe8", 0.8)
bpy.ops.mesh.primitive_plane_add(size=12, location=(cx * MM, -2.5, 0)); bpy.context.active_object.data.materials.append(fl)
bpy.ops.mesh.primitive_plane_add(size=12, location=(cx * MM, (Dp + 5) * MM, 3), rotation=(math.radians(90), 0, 0)); bpy.context.active_object.data.materials.append(wl)
bpy.ops.mesh.primitive_plane_add(size=12, location=(cx * MM, -2.5, H * MM + 0.03)); bpy.context.active_object.data.materials.append(wl)
# lights: two ceiling spots above the wardrobe + soft fill
for xs in (W * 0.25, W * 0.75):
    bpy.ops.object.light_add(type="SPOT", location=(xs * MM, -0.35, H * MM - 0.02))
    L = bpy.context.active_object; L.data.energy = 120; L.data.spot_size = math.radians(70); L.data.spot_blend = 0.6
    L.rotation_euler = (math.radians(12), 0, 0); L.data.color = (1.0, 0.92, 0.8)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.045, depth=0.005, location=(xs * MM, -0.35, H * MM + 0.028))
    bpy.context.active_object.data.materials.append(mat("#fff4dc", 0.3, emit=8))
bpy.ops.object.light_add(type="AREA", location=(cx * MM, -3.2, 1.6)); F = bpy.context.active_object
F.data.energy = 140; F.data.size = 3.5; F.rotation_euler = (math.radians(90), 0, 0)
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[0].default_value = (0.85, 0.86, 0.9, 1)
sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.15

bpy.ops.object.camera_add(); cam = bpy.context.active_object; sc.camera = cam


def aim(loc, tgt, lens):
    cam.location = loc; cam.data.lens = lens
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()


def render(fn):
    sc.render.filepath = os.path.join(HERE, fn); bpy.ops.render.render(write_still=True); print("wrote", fn)


# front view (straight, like the customer pictures)
dist = 1.3 * H * MM
aim((cx * MM, -dist, H * MM / 2), (cx * MM, 0, H * MM / 2), 35)
render(f"Customer 3D - {TITLE} - front.png")
# 3/4 view
aim((cx * MM + 1.6, -dist * 1.0, 1.45), (cx * MM, 0.1, H * MM / 2 - 0.05), 33)
render(f"Customer 3D - {TITLE} - 3-4 view.png")
