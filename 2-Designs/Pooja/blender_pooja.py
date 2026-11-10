"""Mr. Manoker pooja unit - 3D render.  blender -b -P blender_pooja.py -- <samples>"""
import bpy, os, sys, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SAMPLES = int(args[0]) if args else 96
MM = 0.001
W, H, D, KD = 1040.0, 2720.0, 405.0, 100.0


def rgb(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c] + [1]


def mat(name, hexc, rough=0.45, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = rgb(hexc); b.inputs["Roughness"].default_value = rough; b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = rgb(hexc); b.inputs["Emission Strength"].default_value = emit
    return m


def door_mat(side):
    m = bpy.data.materials.new("door" + side); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    tc = nt.nodes.new("ShaderNodeTexImage"); tc.image = bpy.data.images.load(os.path.join(HERE, f"tex_door_{side}_colour.png"))
    tm = nt.nodes.new("ShaderNodeTexImage"); tm.image = bpy.data.images.load(os.path.join(HERE, f"tex_door_{side}_mask.png")); tm.image.colorspace_settings.name = "Non-Color"
    nt.links.new(tc.outputs["Color"], b.inputs["Base Color"])
    b.inputs["Emission Color"].default_value = rgb("#ffcf7a")
    mul = nt.nodes.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 18.0
    nt.links.new(tm.outputs["Color"], mul.inputs[0]); nt.links.new(mul.outputs[0], b.inputs["Emission Strength"])
    b.inputs["Roughness"].default_value = 0.45
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
sc.render.resolution_x, sc.render.resolution_y = 1400, 2000
sc.view_settings.view_transform = "AgX"; sc.view_settings.exposure = -1.6


def box(x, y, z, w, d, h, m, bevel=0.0007):
    """x across, y depth (0 = front face, + into wall), z up"""
    bpy.ops.mesh.primitive_cube_add(size=1)
    o = bpy.context.active_object
    o.scale = (w * MM, d * MM, h * MM)
    o.location = ((x + w / 2) * MM, (y + d / 2) * MM, (z + h / 2) * MM)
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        b = o.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = 2
    o.data.materials.append(m)
    return o


def uv_door(o):
    """front face (-y) gets full 0..1 UV so the texture fits the door"""
    me = o.data
    uv = me.uv_layers.active.data
    for poly in me.polygons:
        n = poly.normal
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            if n.y < -0.9:
                xs = [me.vertices[i].co.x for i in poly.vertices]; zs = [me.vertices[i].co.z for i in poly.vertices]
                uv[li].uv = ((v.x - min(xs)) / (max(xs) - min(xs)), (v.z - min(zs)) / (max(zs) - min(zs)))


LAM = mat("lam", "#5e3820", 0.5)                 # 10225 SF (approx wood brown)
PANEL = mat("panel", "#4e2e1a", 0.5)
INSIDE = mat("inside", "#efe5d1", 0.6)
GOLD = mat("brass", "#d4a017", 0.25, 1.0)
LED = mat("led", "#ffc46a", 0.5, emit=14)
# carcass shell (lower box 0..1905, 405 deep)
T = 18
box(0, 0, 0, W, D - 20, 80, LAM)                                   # skirting / plinth
box(0, 0, 80, T, D, 1905 - 80, LAM); box(W - T, 0, 80, T, D, 1905 - 80, LAM)
box(T, 18, 1905 - T, W - 2 * T, D - 18, T, LAM)                    # top of lower box (ledge for kalasam)
box(T, D - 6, 80, W - 2 * T, 6, 1825, INSIDE)                      # back
# doors (front face at y = -18 .. 0)
dl = (W - 3) / 2
for k in range(2):
    x = 1 + k * (dl + 1)
    box(x, -18, 81, dl, 18, 678, LAM)                              # plain lower doors
    d = box(x, -18, 762, dl, 18, 1141, door_mat("L" if k == 0 else "R"), bevel=0)
    uv_door(d)
    box(x + dl - 22 if k == 0 else x + 14, -24, 1280, 8, 6, 140, GOLD, bevel=0)      # brass handles at the centre joint
# LED strip behind the jali (inside, glowing)
box(T, 30, 770, W - 2 * T, 4, 1130, LED, bevel=0)
# kalasam band: dummy box recessed 100, ledge in front with 5 kalasam
box(T, KD, 1905, W - 2 * T, D - KD, 228, LAM)
for cx in (0.14, 0.32, 0.5, 0.68, 0.86):
    x = W * cx
    bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=0.016, location=(x * MM, 0.05, 1.913)); bpy.context.active_object.data.materials.append(GOLD)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.045, location=(x * MM, 0.05, 1.965)); o = bpy.context.active_object; o.scale.z = 1.05; o.data.materials.append(GOLD)
    bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.05, location=(x * MM, 0.05, 2.03)); bpy.context.active_object.data.materials.append(GOLD)
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.02, location=(x * MM, 0.05, 2.065)); bpy.context.active_object.data.materials.append(GOLD)
    bpy.ops.mesh.primitive_cone_add(radius1=0.012, depth=0.03, location=(x * MM, 0.05, 2.095)); bpy.context.active_object.data.materials.append(GOLD)
# top unit (recessed 100, 305 deep) with 2 doors
box(T, KD, 2133, W - 2 * T, D - KD, H - 2133, LAM)
for k in range(2):
    box(1 + k * (dl + 1), KD - 18, 2135, dl, 18, H - 2137, LAM)
# side colour panel - RIGHT
box(W, -18, 0, 18, D + 18, H, PANEL)
# room
fl = mat("floor", "#ece6dc", 0.15); wl = mat("wall", "#f2ece2", 0.85)
bpy.ops.mesh.primitive_plane_add(size=8, location=(W / 2 * MM, -1.5, 0)); bpy.context.active_object.data.materials.append(fl)
box(-2500, D, 0, W + 5000, 50, 3200, wl, bevel=0)                  # back wall
box(-1100, -3000, 0, 50, 3000 + D, 3200, wl, bevel=0); box(W + 1100, -3000, 0, 50, 3000 + D, 3200, wl, bevel=0)
box(-2500, -3000, 3150, W + 5000, 3000 + D + 50, 50, wl, bevel=0)  # ceiling
box(-1050, D - 60, 3100, W + 2150, 40, 20, mat("cove", "#ffe2b0", emit=6), bevel=0)   # cove light
bpy.ops.object.light_add(type="AREA", location=(W / 2 * MM, -2.2, 2.4)); L = bpy.context.active_object
L.data.energy = 140; L.data.size = 2.5; L.rotation_euler = (math.radians(65), 0, 0)
bpy.ops.object.light_add(type="AREA", location=(W / 2 * MM, -0.6, 3.0)); L2 = bpy.context.active_object
L2.data.energy = 120; L2.data.size = 1.2
sc.world = bpy.data.worlds.new("w"); sc.world.use_nodes = True
sc.world.node_tree.nodes["Background"].inputs[1].default_value = 0.1

bpy.ops.object.camera_add(); cam = bpy.context.active_object; sc.camera = cam


def shot(loc, tgt, lens, fn):
    cam.location = loc; cam.data.lens = lens
    cam.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(HERE, fn); bpy.ops.render.render(write_still=True); print("wrote", fn)


shot((W / 2 * MM, -3.4, 1.45), (W / 2 * MM, 0, 1.38), 32, "Pooja 3D - front.png")
shot((W / 2 * MM - 1.3, -3.0, 1.5), (W / 2 * MM, 0.1, 1.38), 32, "Pooja 3D - angle.png")
