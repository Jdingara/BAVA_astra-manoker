# Astra Interiors - GF Bedroom wardrobe for Mr. Manoker
# Builds the wardrobe in SketchUp (all sizes in mm). Run in SketchUp: Extensions > Ruby Console, then:
#   load 'C:/Users/Home/Manoker/2-Designs/GF Bedroom Wardrobe - SketchUp Builder.rb'
# Change the sizes below and run again to rebuild.

module AstraWardrobe
  W   = 2564.0   # overall width
  H   = 2879.0   # overall height
  DT  = 450.0    # overall depth incl. back board and shutter
  L   = 500.0    # loft height
  DZ  = 400.0    # drawer zone (2 drawers)
  P   = 75.0     # skirting / plinth
  T   = 18.0     # board: 16 ply + 1 mm lam + 0.8 mm backer = 18 overall
  SH  = 18.0     # shutter thickness
  GAP = 3.0      # shutter gap
  ND  = 2        # drawers
  D   = DT - SH  # carcass depth
  SW  = (W - 2 * T) / 6.0
  MAIN_B = P
  MAIN_T = H - L
  OUT_DIR = 'C:/Users/Home/Manoker/2-Designs'
  NAME = 'GF Bedroom Wardrobe'

  def self.mat(model, name, rgb, alpha = 1.0)
    m = model.materials[name] || model.materials.add(name)
    m.color = Sketchup::Color.new(*rgb)
    m.alpha = alpha
    m
  end

  def self.tag(model, name)
    model.layers[name] || model.layers.add(name)
  end

  # Box from (x, y, z) with size (w, d, h). y = 0 is the carcass front, +y goes to the wall.
  def self.box(ents, name, x, y, z, w, d, h, material, layer = nil)
    g = ents.add_group
    g.name = name
    pts = [[x, y, z], [x + w, y, z], [x + w, y + d, z], [x, y + d, z]].map { |p| Geom::Point3d.new(p[0].mm, p[1].mm, p[2].mm) }
    f = g.entities.add_face(pts)
    f.reverse! if f.normal.z < 0
    f.pushpull(h.mm)
    g.material = material
    g.layer = layer if layer
    g
  end

  def self.rod(ents, x1, x2, y, z, material, layer)
    g = ents.add_group
    g.name = 'Hanging rod'
    c = g.entities.add_circle(Geom::Point3d.new(x1.mm, y.mm, z.mm), X_AXIS, 12.mm, 24)
    f = g.entities.add_face(c)
    f.reverse! if f.normal.x < 0
    f.pushpull((x2 - x1).mm)
    g.material = material
    g.layer = layer
    g
  end

  # One shutter (with handle) as a group. Fluted finish gets real 3 mm raised flutes.
  def self.shutter(ents, name, x1, x2, z1, z2, finish, mats, handle: nil)
    w = x2 - x1
    h = z2 - z1
    g = ents.add_group
    g.name = name
    e = g.entities
    if finish == :B
      box(e, 'Shutter base', x1, -SH + 3, z1, w, SH - 3, h, mats[:B])
      n = [(w / 24.0).round, 1].max
      pitch = w / n
      n.times do |i|
        box(e, 'Flute', x1 + i * pitch + pitch * 0.18, -SH, z1, pitch * 0.64, 3, h, mats[:B])
      end
    else
      box(e, 'Shutter', x1, -SH, z1, w, SH, h, mats[:A])
    end
    if handle
      side, at, horizontal = handle
      if horizontal
        len = [w * 0.35, 450].min
        box(e, 'Handle', x1 + (w - len) / 2, -SH - 30, z1 + h / 2 - 6, len, 12, 12, mats[:gold])
        [x1 + (w - len) / 2 + 15, x1 + (w + len) / 2 - 27].each { |hx| box(e, 'Handle leg', hx, -SH - 18, z1 + h / 2 - 5, 12, 18, 10, mats[:gold]) }
      else
        len = [h * 0.28, 600].min
        hx = side == :right ? x2 - 46 : x1 + 34
        zc = z1 + at * h
        box(e, 'Handle', hx, -SH - 30, zc - len / 2, 12, 12, len, mats[:gold])
        [zc - len / 2 + 15, zc + len / 2 - 25].each { |hz| box(e, 'Handle leg', hx + 1, -SH - 18, hz, 10, 18, 10, mats[:gold]) }
      end
    end
    g
  end

  def self.build
    model = Sketchup.active_model
    model.start_operation('Astra wardrobe', true)
    model.entities.clear!
    model.options['UnitsOptions']['LengthUnit'] = 4 # mm
    model.options['UnitsOptions']['LengthFormat'] = 0

    mats = {
      A: mat(model, 'A - Sage gloss acrylic (Merino code ___)', [143, 178, 166]),
      B: mat(model, 'B - Fluted wood (Merino code ___)', [140, 79, 40]),
      carcass: mat(model, 'Carcass liner', [239, 231, 218]),
      plinth: mat(model, 'Plinth', [111, 148, 136]),
      gold: mat(model, 'Handle - gold', [201, 164, 106]),
      rod: mat(model, 'Rod - chrome', [200, 200, 200]),
      wall: mat(model, 'Room - wall', [243, 236, 225]),
      floor: mat(model, 'Room - floor marble', [233, 223, 208]),
      ceiling: mat(model, 'Room - ceiling', [251, 248, 243]),
    }
    t_carcass = tag(model, 'Carcass')
    t_inside  = tag(model, 'Internals')
    t_closed  = tag(model, 'Shutters closed')
    t_open    = tag(model, 'Shutters open')
    t_room    = tag(model, 'Room')

    root = model.entities.add_group
    root.name = "#{NAME} #{W.round}x#{H.round}x#{DT.round}"
    ents = root.entities

    # ---- carcass ----
    box(ents, 'Side L (outer, A)', 0, 0, P, T, D, H - P, mats[:A], t_carcass)
    box(ents, 'Side R (outer, A)', W - T, 0, P, T, D, H - P, mats[:A], t_carcass)
    [[MAIN_B, 'Main bottom'], [MAIN_T - T, 'Main top'], [MAIN_T, 'Loft bottom'], [H - T, 'Loft top']].each do |z, n|
      box(ents, n, T, 0, z, W - 2 * T, D, T, mats[:carcass], t_carcass)
    end
    [1, 2, 4, 5].each do |i|
      x = T + i * SW - T / 2
      box(ents, "Partition #{i} main", x, 0, MAIN_B + T, T, D - 6, MAIN_T - MAIN_B - 2 * T, mats[:carcass], t_carcass)
      box(ents, "Partition #{i} loft", x, 0, MAIN_T + T, T, D - 6, L - 2 * T, mats[:carcass], t_carcass)
    end
    box(ents, 'Back panel 6 mm', T, D - 6, P + T, W - 2 * T, 6, H - P - 2 * T, mats[:carcass], t_carcass)
    box(ents, 'Plinth', T, 40, 0, W - 2 * T, T, P, mats[:plinth], t_carcass)

    # ---- internals ----
    bot = MAIN_B + T
    top = MAIN_T - T
    clear_h = top - bot
    sec = lambda do |s0, n|
      x1 = T + s0 * SW + (s0 > 0 ? T / 2 : 0)
      x2 = T + (s0 + n) * SW - (s0 + n < 6 ? T / 2 : 0)
      [x1, x2]
    end
    shelf = ->(x1, x2, z, n) { box(ents, n, x1, 24, z, x2 - x1, D - 30, T, mats[:carcass], t_inside) }
    [[0, 1], [5, 1]].each do |s0, n|
      x1, x2 = sec.call(s0, n)
      (1..4).each { |k| shelf.call(x1, x2, bot + clear_h * k / 5.0 - T / 2, "Shelf #{s0}-#{k}") }
    end
    [[1, 1], [4, 1]].each do |s0, n|
      x1, x2 = sec.call(s0, n)
      shelf.call(x1, x2, top - 300 - T, "Shelf over rod #{s0}")
      rod(ents, x1 + 5, x2 - 5, D / 2, top - 380, mats[:rod], t_inside)
    end
    x1, x2 = sec.call(2, 2)
    d_top = bot + DZ
    upper = top - d_top
    shelf.call(x1, x2, d_top, 'Drawer top shelf')
    shelf.call(x1, x2, d_top + upper / 3.0, 'Shelf middle 1')
    shelf.call(x1, x2, d_top + 2 * upper / 3.0, 'Shelf middle 2')

    # ---- shutters: closed set and open set ----
    loft_f = [:A, :B, :A, :A, :B, :A]
    specs = []
    6.times do |i|
      specs << ["Loft shutter #{i + 1} (#{loft_f[i]})", i, MAIN_T + GAP / 2, H - GAP / 2, loft_f[i], i < 3, nil]
    end
    y1 = MAIN_B + GAP / 2
    y2 = MAIN_T - GAP / 2
    h_top = MAIN_B + DZ
    specs << ['Shutter 1 (A)', 0, y1, y2, :A, true, [:right, 0.55]]
    specs << ['Shutter 2 (B)', 1, y1, y2, :B, true, [:right, 0.55]]
    specs << ['Shutter 3 (A)', 2, h_top + GAP / 2, y2, :A, true, [:right, 0.45]]
    specs << ['Shutter 4 (A)', 3, h_top + GAP / 2, y2, :A, false, [:left, 0.45]]
    specs << ['Shutter 5 (B)', 4, y1, y2, :B, false, [:left, 0.55]]
    specs << ['Shutter 6 (A)', 5, y1, y2, :A, false, [:left, 0.55]]

    [[t_closed, false], [t_open, true]].each do |layer, open|
      set = ents.add_group
      set.name = open ? 'Shutters OPEN' : 'Shutters CLOSED'
      set.layer = layer
      specs.each do |name, mod, z1, z2, fin, hinge_left, handle|
        sx1 = T + mod * SW + GAP / 2
        sx2 = T + (mod + 1) * SW - GAP / 2
        g = shutter(set.entities, name, sx1, sx2, z1, z2, fin, mats, handle: handle)
        next unless open
        hx = hinge_left ? sx1 : sx2
        ang = (hinge_left ? -100 : 100).degrees
        g.transform!(Geom::Transformation.rotation(Geom::Point3d.new(hx.mm, 0, 0), Z_AXIS, ang))
      end
      # drawers
      dx1 = T + 2 * SW + GAP / 2
      dx2 = T + 4 * SW - GAP / 2
      dh = DZ / ND
      ND.times do |k|
        z1 = MAIN_B + k * dh + GAP / 2
        z2 = z1 + dh - GAP
        dg = set.entities.add_group
        dg.name = "Drawer #{k + 1}"
        shutter(dg.entities, "Drawer front #{k + 1} (B)", dx1, dx2, z1, z2, :B, mats, handle: [:center, 0.5, true])
        box(dg.entities, 'Drawer box', dx1 + 30, 0, z1 + 20, dx2 - dx1 - 60, D - 60, dh - 70, mats[:carcass])
        dg.transform!(Geom::Transformation.translation(Geom::Vector3d.new(0, -300.mm, 0))) if open && k == 1
      end
    end

    # ---- room ----
    rx1 = -1200.0
    rx2 = W + 1200
    box(model.entities, 'Floor', rx1, -3500, -20, rx2 - rx1, 3500 + D + 100, 20, mats[:floor], t_room)
    box(model.entities, 'Back wall', rx1, D, 0, rx2 - rx1, 120, H + 150, mats[:wall], t_room)
    box(model.entities, 'Left wall', rx1 - 120, -3500, 0, 120, 3500 + D + 120, H + 150, mats[:wall], t_room)
    box(model.entities, 'Right wall', rx2, -3500, 0, 120, 3500 + D + 120, H + 150, mats[:wall], t_room)
    box(model.entities, 'Ceiling', rx1, -3500, H + 150, rx2 - rx1, 3500 + D + 120, 100, mats[:ceiling], t_room)
    [1, 4].each do |i|
      cx = T + i * SW + SW / 2
      box(model.entities, 'Spotlight (add V-Ray IES light here)', cx - 35, 200, H + 149, 70, 70, 1, mat(model, 'Spot glow', [255, 243, 214]), t_room)
    end

    # ---- view settings & scenes ----
    ro = model.rendering_options
    ro['EdgeDisplayMode'] = 0
    ro['DrawSilhouettes'] = false
    model.shadow_info['DisplayShadows'] = true
    model.shadow_info['Light'] = 80
    model.shadow_info['Dark'] = 55
    model.options['PageOptions']['ShowTransition'] = false
    model.pages.to_a.each { |pg| model.pages.erase(pg) }
    cz = H * 0.5
    cams = {
      '1 Front' => [[W / 2, -5400, cz], [W / 2, 0, cz]],
      '2 Angle' => [[W * 1.05, -5200, cz + 100], [W * 0.5, 0, cz]],
      '3 Open' => [[W * 0.95, -5000, cz + 100], [W * 0.5, 0, cz - 40]],
    }
    cams.each do |name, (eye, tgt)|
      t_closed.visible = !name.include?('Open')
      t_open.visible = name.include?('Open')
      cam = Sketchup::Camera.new(Geom::Point3d.new(*eye.map(&:mm)), Geom::Point3d.new(*tgt.map(&:mm)), Z_AXIS, true, 45)
      model.active_view.camera = cam
      model.pages.add(name)
    end
    t_closed.visible = true
    t_open.visible = false
    model.pages.selected_page = model.pages[0]
    model.commit_operation
    model
  end

  def self.export_images
    model = Sketchup.active_model
    view = model.active_view
    model.pages.each do |pg|
      model.pages.selected_page = pg
      view.refresh
      view.write_image(filename: "#{OUT_DIR}/#{NAME} - SketchUp #{pg.name}.png", width: 1920, height: 1200, antialias: true, transparent: false)
    end
    model.pages.selected_page = model.pages[0]
  end
end

model = AstraWardrobe.build
if defined?(ASTRA_AUTO_EXPORT) && ASTRA_AUTO_EXPORT
  AstraWardrobe.export_images
  model.save("#{AstraWardrobe::OUT_DIR}/#{AstraWardrobe::NAME}.skp")
end
puts "Astra wardrobe built: #{AstraWardrobe::W}x#{AstraWardrobe::H}x#{AstraWardrobe::DT} mm"
