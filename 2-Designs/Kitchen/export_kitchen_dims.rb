# Astra Interiors - export the open SketchUp model's geometry (mm) to JSON so the kitchen can be designed from it.
# Ruby Console:  load 'C:/Users/Home/Manoker/2-Designs/Kitchen/export_kitchen_dims.rb'
require 'json'
module AstraExport
  OUT = 'C:/Users/Home/Manoker/2-Designs/Kitchen/sketchup_kitchen_export.json'
  def self.mm(v) (v.to_f * 25.4).round(1) end
  def self.pt(p, t) q = p.transform(t); [mm(q.x), mm(q.y), mm(q.z)] end
  def self.walk(ents, t, path, out)
    ents.each do |e|
      case e
      when Sketchup::Group, Sketchup::ComponentInstance
        name = e.name.to_s
        name = e.definition.name.to_s if name.empty? && e.respond_to?(:definition)
        tt = t * e.transformation
        bb = Geom::BoundingBox.new
        e.definition.entities.grep(Sketchup::Face).each { |f| f.vertices.each { |v| bb.add(v.position.transform(tt)) } } rescue nil
        out[:groups] << { path: (path + [name]).join('/'), layer: e.layer.name,
                          min: [mm(bb.min.x), mm(bb.min.y), mm(bb.min.z)], max: [mm(bb.max.x), mm(bb.max.y), mm(bb.max.z)] } unless bb.empty?
        walk(e.definition.entities, tt, path + [name], out)
      when Sketchup::Face
        out[:faces] << { path: path.join('/'), normal: [e.normal.transform(t).x.round(3), e.normal.transform(t).y.round(3), e.normal.transform(t).z.round(3)],
                         pts: e.outer_loop.vertices.map { |v| pt(v.position, t) } }
      when Sketchup::DimensionLinear
        out[:dims] << { path: path.join('/'), text: e.text.to_s, start: (pt(e.start[1], t) rescue nil), end: (pt(e.end[1], t) rescue nil) }
      when Sketchup::Text
        out[:texts] << { path: path.join('/'), text: e.text.to_s, point: (pt(e.point, t) rescue nil) }
      end
    end
  end
  def self.run
    m = Sketchup.active_model
    out = { model: m.title, path: m.path, groups: [], faces: [], dims: [], texts: [] }
    walk(m.entities, Geom::Transformation.new, [], out)
    File.write(OUT, JSON.pretty_generate(out))
    msg = "Astra export: #{out[:groups].size} groups, #{out[:faces].size} faces, #{out[:dims].size} dims -> #{OUT}"
    puts msg
    UI.messagebox(msg)
  end
end
AstraExport.run
