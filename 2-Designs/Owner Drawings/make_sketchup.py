"""Build the owner's 4 wardrobes in SketchUp from boards.json (read from his AutoCAD drawing).
Writes a Ruby script; run it in SketchUp (Ruby console: load '<path>') or via -RubyStartup.
Rules = same as the cut list: cupboard box 2000 high, depth 457 (18 in), partitions 451, shelves 431,
6 mm back panels, loft = 90 mm frame only, GF = 2 boxes side by side."""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
T, BACK, FRAME = 18.0, 6.0, 90.0
DEPTHS = {"GF": 500.0, "1F Master": 500.0, "1F Bedroom 2": 500.0, "2F": 500.0}   # owner: all wardrobes 500 deep

SPLIT_X = {"GF": (3156.3, 3192.3)}
DRAWERS = {
    "GF": [(2341.3, 3156.3, 964.5, 173.0), (2341.3, 3156.3, 1155.5, 182.0)],
    "1F Master": [(5669.9, 6434.9, 931.0, 173.0), (5669.9, 6434.9, 1122.0, 182.0)],
    "1F Bedroom 2": [(10013.0, 10759.0, 873.4, 173.0), (10013.0, 10759.0, 1064.4, 182.0)],
    "2F": [(13384.8, 14140.8, 873.4, 173.0), (13384.8, 14140.8, 1064.4, 182.0)],
}
TITLES = {"GF": "GF BEDROOM", "1F Master": "1ST FLOOR M.BEDROOM", "1F Bedroom 2": "1ST FLOOR BEDROOM 2", "2F": "2ND FLOOR BEDROOM"}
boards = json.load(open(os.path.join(HERE, "boards.json")))

ROOMS = {}
parts = []   # (wardrobe, part name, material, x, y, z, w(x), d(y), h(z))  y = depth from front


def build(name, d, x_off):
    DEPTH = DEPTHS.get(name, 457.0)
    PART_D, SHELF_D = DEPTH - BACK, DEPTH - BACK - 20
    box_l = next(c for c in (550, 500, 450, 400, 350) if c <= DEPTH - BACK - 40)
    hb = [tuple(b) for b in d["h"]]
    vb = [tuple(b) for b in d["v"]]
    x_min = min(b[0] for b in vb)
    x_max = max(b[0] + T for b in vb)
    width = x_max - x_min
    tall = max(b[2] - b[1] for b in vb)
    y_floor = min(b[1] for b in vb)
    ys = [b[0] for b in hb]
    y_bot, y_top = min(ys), max(ys)
    main_top_y = min(b[0] for b in hb if b[0] > y_bot + 1500 and b[2] - b[1] >= 0.6 * width)
    box_h = main_top_y + T - y_floor
    X = lambda x: x - x_min + x_off
    Z = lambda y: y - y_floor
    sx = SPLIT_X.get(name)
    if sx:
        nh = []
        for y, a, b in hb:
            nh += [(y, a, sx[0]), (y, sx[1], b)] if a < sx[0] - 1 and b > sx[1] + 1 else [(y, a, b)]
        hb = nh

    def P(part, mat, x, y, z, w, dd, h):
        parts.append((name, part, mat, round(x, 1), round(y, 1), round(z, 1), round(w, 1), round(dd, 1), round(h, 1)))

    # vertical boards
    up_x = []
    for x, a, b in sorted(vb):
        L = b - a
        if L >= tall - 30:
            P("Side panel (cupboard)", "carcass", X(x), 0, 0, T, DEPTH, box_h)
            up_x.append(x)
        elif a >= main_top_y - 1:
            up_x.append(x)                                   # loft partition -> frame upright
        else:
            P("Partition", "carcass", X(x), 0, Z(a), T, DEPTH if L >= 1800 else PART_D, L)
    # horizontal boards inside the cupboard (loft boards are replaced by the frame)
    for y, a, b in sorted(hb):
        L = b - a
        if y <= y_bot + 1:
            P("Bottom panel", "carcass", X(a), 0, Z(y), L, DEPTH, T)
        elif abs(y - main_top_y) < 1 and L >= 0.3 * width / (2 if sx else 1):
            P("Top panel", "carcass", X(a), 0, Z(y), L, DEPTH, T)
        elif y > main_top_y + 1:
            continue
        else:
            P("Shelf", "shelf", X(a), 20, Z(y), L, SHELF_D, T)
    # 6 mm back panels (cupboard sections)
    z1, z2 = Z(y_bot) + T, Z(main_top_y)
    cols = sorted({x for x, a, b in vb if Z(a) <= z1 + 5 and Z(b) >= z2 - 5})
    for xa, xb in zip(cols, cols[1:]):
        w = xb - (xa + T)
        if w >= 60:
            P("Back panel 6 mm", "back", X(xa + T), DEPTH - BACK, z1, w, BACK, z2 - z1)
    # loft: 90 mm frame only
    loft_h = tall - box_h
    merged = []
    for x in sorted(up_x):
        if not merged or x - merged[-1] > 40:
            merged.append(x)
    for x in merged:
        P("Loft frame upright 90", "frame", X(x), 0, box_h, T, FRAME, loft_h)
    pieces = [(x_min + T, sx[0]), (sx[1], x_max - T)] if sx else [(x_min + T, x_max - T)]
    for a, b in pieces:
        P("Loft top rail 90", "frame", X(a), 0, box_h + loft_h - T, b - a, FRAME, T)
        P("Loft bottom rail 90", "frame", X(a), 0, box_h, b - a, FRAME, T)
    # drawers (box + front)
    for x1, x2, zb, dh in DRAWERS[name]:
        z = Z(zb)
        P("Drawer front (outside)", "drawer", X(x1) - T / 2 + 1.5, -T, z - T / 2 + 1.5, x2 - x1 + T - 3, T, dh + T - 3)
        P("Drawer box", "drawerbox", X(x1) + 13, 10 + T, z + 15, x2 - x1 - 26, box_l, 150.0)
    COVER_SIDE = {"GF": "left", "1F Master": "left", "1F Bedroom 2": "right", "2F": "left"}
    left_c = COVER_SIDE[name] == "left"
    P("Side cover panel", "cover", X(x_min) - T if left_c else X(x_min) + width, -T, 0, T, DEPTH + T, tall)
    P("Wall-side strip 100", "cover", X(x_min) + width if left_c else X(x_min) - T, -T, 0, T, 100.0, tall)
    ROOMS[name] = {"x_min": x_min, "y_floor": y_floor, "x_off": x_off, "y_bot": y_bot, "width": width, "tall": tall, "box_h": box_h, "depth": DEPTH}
    return width, tall, box_h


x = 0.0
meta = []
for k in ["GF", "1F Master", "1F Bedroom 2", "2F"]:
    w, h, bh = build(k, boards[k], x)
    meta.append((k, TITLES[k], x, w, h))
    x += w + 900

out_dir = HERE.replace("\\", "/")
rb = ["# Astra Interiors - owner's wardrobes built from his AutoCAD drawing (generated by make_sketchup.py)",
      "module AstraOwner", f"  OUT = '{out_dir}'", "  PARTS = ["]
for p in parts:
    rb.append(f"    [{p[0]!r}, {p[1]!r}, {p[2]!r}, {p[3]}, {p[4]}, {p[5]}, {p[6]}, {p[7]}, {p[8]}],".replace("'", '"'))
rb.append("  ]")
rb.append("  META = [")
for k, t, x0, w, h in meta:
    rb.append(f'    ["{k}", "{t}", {x0}, {w}, {h}],')
rb.append("  ]")
rb.append(r'''
  COLORS = { "carcass" => [222, 196, 158], "shelf" => [236, 214, 178], "back" => [176, 150, 116],
             "frame" => [120, 150, 190], "drawer" => [200, 120, 80], "drawerbox" => [210, 190, 160] }

  def self.defn(model, name, w, d, h, mat)
    key = "#{name} #{w.round(1)}x#{d.round(1)}x#{h.round(1)}"
    return model.definitions[key] if model.definitions[key]
    cd = model.definitions.add(key)
    pts = [[0, 0, 0], [w, 0, 0], [w, d, 0], [0, d, 0]].map { |p| Geom::Point3d.new(p[0].mm, p[1].mm, p[2].mm) }
    f = cd.entities.add_face(pts)
    f.reverse! if f.normal.z < 0
    f.pushpull(h.mm)
    cd.entities.grep(Sketchup::Face).each { |fc| fc.material = mat }
    cd
  end

  def self.build
    model = Sketchup.active_model
    model.start_operation('Astra owner wardrobes', true)
    model.entities.clear!
    model.options['UnitsOptions']['LengthUnit'] = 4
    mats = {}
    COLORS.each { |k, c| m = model.materials[k] || model.materials.add(k); m.color = Sketchup::Color.new(*c); mats[k] = m }
    groups = {}
    META.each do |k, title, x0, w, h|
      g = model.entities.add_group
      g.name = "#{title} wardrobe"
      groups[k] = g
      tg = model.entities.add_group
      tg.entities.add_3d_text(title, TextAlignLeft, 'Arial', true, false, 120.mm, 0, 0, true, 0)
      tg.transform!(Geom::Transformation.rotation(ORIGIN, X_AXIS, 90.degrees))
      tg.transform!(Geom::Transformation.translation(Geom::Vector3d.new(x0.mm, 0, (h + 150).mm)))
      tg.name = "Title #{title}"
    end
    PARTS.each do |k, part, mat, x, y, z, w, d, h|
      # SketchUp: X = width, Y = depth (front at -Y so the front faces the default Front view), Z = height
      cd = defn(model, part, w, d, h, mats[mat])
      t = Geom::Transformation.translation(Geom::Vector3d.new(x.mm, -(y + d).mm, z.mm))
      inst = groups[k].entities.add_instance(cd, t)
      inst.name = part
    end
    ro = model.rendering_options
    ro['EdgeColorMode'] = 0
    model.shadow_info['DisplayShadows'] = false
    model.pages.to_a.each { |pg| model.pages.erase(pg) }
    total_w = META.map { |m| m[2] + m[3] }.max
    cx = total_w / 2.0
    cams = {
      '1 Front (all)' => [[cx, -9000, 1450], [cx, 0, 1450], false],
      '2 3D view (all)' => [[cx + 3500, -7500, 4200], [cx, 0, 1300], true],
    }
    cams.each do |name, (eye, tgt, persp)|
      cam = Sketchup::Camera.new(Geom::Point3d.new(*eye.map(&:mm)), Geom::Point3d.new(*tgt.map(&:mm)), Z_AXIS, persp, 40)
      model.active_view.camera = cam
      model.active_view.zoom_extents
      model.pages.add(name)
    end
    META.each_with_index do |(k, title, x0, w, h), i|
      c = x0 + w / 2.0
      cam = Sketchup::Camera.new(Geom::Point3d.new((c + 1500).mm, -4200.mm, 2600.mm), Geom::Point3d.new(c.mm, 0, 1300.mm), Z_AXIS, true, 45)
      model.active_view.camera = cam
      bb = groups[k].bounds
      model.active_view.zoom(groups[k]) rescue nil
      model.pages.add("#{i + 3} #{title}")
    end
    model.pages.selected_page = model.pages[0]
    model.commit_operation
    model
  end

  def self.export
    model = Sketchup.active_model
    view = model.active_view
    model.options['PageOptions']['ShowTransition'] = false
    model.pages.each do |pg|
      model.pages.selected_page = pg
      view.refresh
      view.write_image(filename: "#{OUT}/SketchUp - #{pg.name}.png", width: 1920, height: 1080, antialias: true)
    end
    model.pages.selected_page = model.pages[0]
  end
end

AstraOwner.build
if defined?(ASTRA_OWNER_EXPORT) && ASTRA_OWNER_EXPORT
  AstraOwner.export
  Sketchup.active_model.save("#{AstraOwner::OUT}/Owner Wardrobes (from AutoCAD).skp")
end
puts "Astra owner wardrobes: #{AstraOwner::PARTS.size} parts"
''')
open(os.path.join(HERE, "Owner Wardrobes - SketchUp Builder.rb"), "w", encoding="utf-8").write("\n".join(rb))
print("parts", len(parts))
json.dump({"parts": parts, "rooms": ROOMS}, open(os.path.join(HERE, "model_parts.json"), "w"), indent=1)
