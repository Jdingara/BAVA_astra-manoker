"""Astra Interiors - shared wardrobe generator.

build(cfg) writes, into cfg["out"]:
  <name> - AutoCAD 2D.dxf     front elevation, inside elevation, top plan, base section, title block
  <name> - Cut List.xlsx      cut list (finished + cut sizes), materials, hardware
  <name> - data.json          same data, used by the PDF and render scripts
All sizes in mm. Doors sit on modules of equal width; sections (bays) are module ranges.
"""
import json
import math
import os

import ezdxf
from ezdxf.enums import TextEntityAlignment
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

DEFAULTS = dict(T=18.0, SH=18.0, GAP=3.0, BACK=6.0, P=115.0, L=500.0, TILE_SKIRT=100.0,
                board="18 mm ply (16 + 1 lam + 0.8 backer)", back="6 mm back ply")


def build(cfg):
    c = dict(DEFAULTS, **cfg)
    W, H, DT, L, P = c["W"], c["H"], c["DT"], c["L"], c["P"]
    T, SH, GAP, BACK = c["T"], c["SH"], c["GAP"], c["BACK"]
    NM, NAME, OUT, COLS = c["modules"], c["name"], c["out"], c["colours"]
    D = DT - SH
    SW = (W - 2 * T) / NM
    MAIN_B, MAIN_T = P, H - L
    BOT, TOP = MAIN_B + T, MAIN_T - T
    SHELF_D = D - BACK - 24
    mx = lambda m: T + m * SW
    bay_mods = c["bays"]                                     # e.g. [(0, 2), (2, 5), (5, 7)]
    part_x = [mx(b[0]) - T / 2 for b in bay_mods[1:]]
    edges = [T] + [x + T for x in part_x]
    ends = part_x + [W - T]
    bays = list(zip(edges, ends))
    bay_w = [b - a for a, b in bays]
    drawers = c["drawers"]                                   # [(m1, m2, colour, count, zone_height)]
    drawer_zone = {}
    for m1, m2, col, n, dz in drawers:
        for m in range(int(m1), int(math.ceil(m2))):
            drawer_zone[m] = dz
    bottom_doors = c.get("bottom_doors", [])                  # [(module, colour, height, hinge)]
    for m, col, bh, hinge in bottom_doors:
        drawer_zone[m] = bh

    os.makedirs(OUT, exist_ok=True)
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    doc.header["$INSUNITS"] = 4
    msp = doc.modelspace()
    LAY = {k: f"2-DOOR-{k}-{''.join(v.split()[:2])}" for k, v in COLS.items()}
    layers = {"0-OUTLINE": 7, "1-CARCASS": 7, "4-HANDLE": 40, "5-INTERNAL": 8, "6-GLASS": 4, "7-DIM": 1,
              "8-TEXT": 7, "9-WALL": 9, "10-TITLE": 7}
    layers.update({v: (8 if k == "A" else 5) for k, v in LAY.items()})
    for n, col in layers.items():
        doc.layers.add(n, color=col)
    doc.layers.get("6-GLASS").dxf.linetype = "DASHED"
    ds = doc.dimstyles.get("EZDXF")
    ds.dxf.dimtxt, ds.dxf.dimasz, ds.dxf.dimexe, ds.dxf.dimexo, ds.dxf.dimgap = 45, 35, 20, 15, 12

    def rect(x, y, w, h, layer, ox=0.0, oy=0.0):
        msp.add_lwpolyline([(ox + x, oy + y), (ox + x + w, oy + y), (ox + x + w, oy + y + h), (ox + x, oy + y + h)],
                           close=True, dxfattribs={"layer": layer})

    def text(s, x, y, h=45, layer="8-TEXT", align=TextEntityAlignment.MIDDLE_CENTER):
        msp.add_text(s, height=h, dxfattribs={"layer": layer, "style": "OpenSans"}).set_placement((x, y), align=align)

    def dimh(x1, x2, y, base_y, label=None, ox=0.0):
        msp.add_linear_dim(base=(ox + x1, base_y), p1=(ox + x1, y), p2=(ox + x2, y), dimstyle="EZDXF",
                           text=label or f"{abs(x2 - x1):.0f}", dxfattribs={"layer": "7-DIM"}).render()

    def dimv(y1, y2, x, base_x, label=None, ox=0.0):
        msp.add_linear_dim(base=(ox + base_x, y1), p1=(ox + x, y1), p2=(ox + x, y2), angle=90, dimstyle="EZDXF",
                           text=label or f"{abs(y2 - y1):.0f}", dxfattribs={"layer": "7-DIM"}).render()

    def ftin(v):
        i = v / 25.4
        f, r = int(i // 12), round(i - int(i // 12) * 12)
        return f"{f + (r == 12)}'{0 if r == 12 else r}\""

    def door(x1, x2, z1, z2, col, handle=None, short=False):
        rect(x1, z1, x2 - x1, z2 - z1, LAY[col])
        text(col, (x1 + x2) / 2, z1 + (z2 - z1) * (0.5 if short else 0.85), 60)
        if handle == "H":
            ln = min((x2 - x1) * 0.35, 400)
            rect((x1 + x2) / 2 - ln / 2, (z1 + z2) / 2 - 6, ln, 12, "4-HANDLE")
        elif handle in ("L", "R"):
            ln = min((z2 - z1) * 0.28, 600) if not short else min((z2 - z1) * 0.5, 160)
            hx = x2 - 46 if handle == "R" else x1 + 34
            zc = z1 + (0.25 if short else 0.5) * (z2 - z1)
            rect(hx, zc - ln / 2, 12, ln, "4-HANDLE")

    # ------------------------------------------------ 1. FRONT ELEVATION
    rect(0, 0, W, H, "0-OUTLINE")
    rect(T, 0, W - 2 * T, P, "1-CARCASS")
    text(f"BASE {P:.0f}", W / 2, P / 2, 35)
    for ld in c["loft_doors"]:
        m1, m2, hinge = ld[:3]
        door(mx(m1) + GAP / 2, mx(m2) - GAP / 2, MAIN_T + GAP / 2, H - GAP / 2, ld[3] if len(ld) > 3 else c.get("loft_colour", "A"), "R" if hinge == "L" else "L", short=True)
    for m, col, hinge, handle in c["main_doors"]:
        z1 = MAIN_B + drawer_zone.get(m, 0) + GAP / 2
        door(mx(m) + GAP / 2, mx(m + 1) - GAP / 2, z1, MAIN_T - GAP / 2, col, handle)
    for m1, m2, col, n, dz in drawers:
        for k in range(n):
            z1 = MAIN_B + k * dz / n + GAP / 2
            door(mx(m1) + GAP / 2, mx(m2) - GAP / 2, z1, z1 + dz / n - GAP, col, "H", short=True)
    for m, col, bh, hinge in bottom_doors:
        door(mx(m) + GAP / 2, mx(m + 1) - GAP / 2, MAIN_B + GAP / 2, MAIN_B + bh - GAP / 2, col, "R" if hinge == "L" else "L", short=True)
    dimh(0, W, 0, -260, f"{W:.0f} ({ftin(W)})")
    for i in range(NM):
        dimh(mx(i), mx(i + 1), H, H + 140)
    dimv(0, H, 0, -260, f"{H:.0f} ({ftin(H)})")
    dimv(MAIN_T, H, W, W + 160)
    dimv(P, MAIN_T, W, W + 160)
    dimv(0, P, W, W + 160)
    if drawers:
        dimv(P, P + drawers[0][4], W, W + 340)
    text("FRONT ELEVATION", W / 2, -480, 80)
    text("   ".join(f"{k} = {v}" for k, v in COLS.items()), W / 2, -620, 55)

    # ------------------------------------------------ 2. INSIDE ELEVATION + cut data for internals
    IX = W + 1400

    def ir(x, z, w, h, layer="1-CARCASS"):
        rect(x, z, w, h, layer, IX)

    ir(0, 0, W, H, "0-OUTLINE")
    ir(0, P, T, H - P)
    ir(W - T, P, T, H - P)
    for z in (MAIN_B, MAIN_T - T, MAIN_T, H - T):
        ir(T, z, W - 2 * T, T)
    ir(T, 0, W - 2 * T, P, "5-INTERNAL")
    for x in part_x:
        ir(x, BOT, T, TOP - BOT)
        ir(x, MAIN_T + T, T, L - 2 * T)
    internals = []                      # (group, part, mat, qty, L, W, edge)
    shelves_3d = []                     # for renders: (x1, x2, z, kind)
    rods_3d, glass_3d, vparts_3d, drawer_boxes = [], [], [], []
    int_drawers = []                    # inside drawers (behind doors): (x1, x2, n, dz)
    mirrors_3d, leds_3d = [], []

    def fill_shelves(grp, x1, x2, z_from, z_to, comp=305.0, dim_x=None):
        """Board shelves with `comp` clear compartments from z_from (top of a board) upwards."""
        n_sh = int((z_to - z_from) // (comp + T))
        z = z_from
        dx = dim_x if dim_x is not None else x1
        for k in range(n_sh):
            ir(x1, z + comp, x2 - x1, T, "5-INTERNAL")
            shelves_3d.append((x1, x2, z + comp, "board"))
            dimv(z, z + comp, dx, dx + 80, f"{comp:.0f}", ox=IX)
            z += comp + T
        if n_sh:
            internals.append((grp, f"Shelf {x2 - x1:.0f} wide ({comp:.0f} spacing)", "board", n_sh, x2 - x1, SHELF_D, "1 long"))

    def vpart(grp, x, z1, z2, label="Inner partition"):
        ir(x, z1, T, z2 - z1)
        vparts_3d.append((x, z1, z2))
        internals.append((grp, label, "board", 1, z2 - z1, D - BACK, "1 long"))

    def drawer_block(grp, x1, x2, n, dz, a, b, inside):
        """n drawers between x1..x2 at the bottom, drawer-top shelf, partitions where not at a section side."""
        for px in ([x1 - T] if x1 > a + 1 else []) + ([x2] if x2 < b - 1 else []):
            vpart(grp, px, BOT, BOT + dz, "Partition beside drawers")
        ir(x1, BOT + dz, x2 - x1, T, "5-INTERNAL")
        shelves_3d.append((x1, x2, BOT + dz, "board"))
        internals.append((grp, "Drawer top shelf", "board", 1, x2 - x1, SHELF_D, "1 long"))
        for k in range(n):
            ir(x1 + 13, BOT + k * dz / n + 15, x2 - x1 - 26, dz / n - 30, "5-INTERNAL")
        text(f"{n} DRAWERS" + (" (INSIDE)" if inside else ""), IX + (x1 + x2) / 2, BOT + dz / 2, 30)
        drawer_boxes.append((x1, x2, n, dz))
        if inside:
            int_drawers.append((x1, x2, n, dz, BOT))
            internals.append((grp, "Inside drawer front", "board", n, x2 - x1 - 6, dz / n - 6, "4 sides"))
        return BOT + dz + T

    def ext_drawer_span(lay, a, b):
        dr = lay.get("drawers")
        if not dr:
            return None
        m1, m2, n, dz = dr
        x1 = a if mx(m1) <= a + T else mx(m1) + T / 2      # drawers start at the section side
        x2 = b if mx(m2) >= b - T else mx(m2) - T / 2      # drawers end at the section side
        return x1, x2, n, dz

    for bi, ((a, b), lay) in enumerate(zip(bays, c["inside"])):
        grp = f"Section {bi + 1} ({lay['type']})"
        if lay["type"] == "col_dressing":
            # inside dressing unit: table + mirror + LED, bangle/perfume shelf column beside it, glass shelves above
            side_w = lay.get("side_w", 300.0)
            ext = ext_drawer_span(lay, a, b)
            full_drawers = bool(ext) and ext[0] <= a + 1 and ext[1] >= b - 1
            z_base = drawer_block(grp, a, b, ext[2], ext[3], a, b, inside=False) if full_drawers else BOT
            sx1, sx2 = a, a + side_w
            gx1, gx2 = sx2 + T, b
            vpart(grp, sx2, z_base, TOP, "Bangle/perfume column partition")
            # side column: bangle & perfume shelves at 200 mm spacing
            fill_shelves(grp, sx1, sx2, z_base, TOP, comp=lay.get("side_comp", 200.0), dim_x=sx1)
            text("BANGLE &", IX + (sx1 + sx2) / 2, TOP - 120, 24)
            text("PERFUME", IX + (sx1 + sx2) / 2, TOP - 155, 24)
            # dressing table top at 800 from floor, drawers under it when there are no outside drawers
            table_top = lay.get("table_h", 800.0)
            tz = table_top - T
            if not full_drawers and lay.get("table_drawers", True):
                n_td = 2
                dz_td = min(400.0, tz - BOT - 40)
                drawer_block(grp, gx1, gx2, n_td, dz_td, a, b, inside=True)
            ir(gx1, tz, gx2 - gx1, T, "5-INTERNAL")
            shelves_3d.append((gx1, gx2, tz, "board"))
            internals.append((grp, "Dressing table top", "board", 1, gx2 - gx1, SHELF_D, "1 long"))
            # slim drawer right under the table top (combs, make-up)
            sdh = lay.get("slim_drawer_h", 150.0)
            sz = tz - sdh
            ir(gx1, sz - T, gx2 - gx1, T, "5-INTERNAL")
            shelves_3d.append((gx1, gx2, sz - T, "board"))
            internals.append((grp, "Shelf under slim drawer", "board", 1, gx2 - gx1, SHELF_D, "1 long"))
            ir(gx1 + 13, sz + 10, gx2 - gx1 - 26, sdh - 20, "5-INTERNAL")
            text("SLIM DRAWER", IX + (gx1 + gx2) / 2, sz + sdh / 2, 24)
            drawer_boxes.append((gx1, gx2, 1, sdh + 40))
            int_drawers.append((gx1, gx2, 1, sdh, sz))
            internals.append((grp, "Slim drawer front", "board", 1, gx2 - gx1 - 6, sdh - 6, "4 sides"))
            mir_h = lay.get("mirror_h", 1000.0)
            m_z1, m_z2 = table_top + 60, table_top + 60 + mir_h
            ir(gx1 + 40, m_z1, gx2 - gx1 - 80, mir_h, "6-GLASS")
            mirrors_3d.append((gx1 + 40, gx2 - 40, m_z1, m_z2))
            internals.append((grp, "Dressing mirror (on back panel)", "mirror", 1, mir_h, gx2 - gx1 - 80, "polished"))
            niche_top = m_z2 + 60
            ir(gx1, niche_top, gx2 - gx1, T, "5-INTERNAL")
            shelves_3d.append((gx1, gx2, niche_top, "board"))
            leds_3d.append((gx1 + 20, gx2 - 20, niche_top))
            internals.append((grp, "Shelf over dressing (LED below)", "board", 1, gx2 - gx1, SHELF_D, "1 long"))
            text("DRESSING", IX + (gx1 + gx2) / 2, (m_z1 + m_z2) / 2 + 30, 34)
            text("MIRROR + LED", IX + (gx1 + gx2) / 2, (m_z1 + m_z2) / 2 - 30, 28)
            dimv(0, table_top, gx2, gx2 - 70, f"TABLE {table_top:.0f}", ox=IX)
            # glass shelves above the dressing niche
            g_from = niche_top + T
            ng = max(1, int((TOP - g_from) // 300))
            for k in range(1, ng + 1):
                z = g_from + (TOP - g_from) / (ng + 1) * k - 4
                ir(gx1, z, gx2 - gx1, 8, "6-GLASS")
                glass_3d.append((gx1, gx2, z))
            internals.append((grp, "Glass shelf", "glass", ng, gx2 - gx1 - 4, SHELF_D - 10, "polished"))
            continue
        if lay["type"] == "col_glass":
            # glass shelves under the loft + a side column with shelves and drawers
            side_w = lay.get("side_w", 300.0)
            ext = ext_drawer_span(lay, a, b)
            if ext and ext[0] > a + 1:
                sx1, sx2 = a, ext[0] - T
            else:
                sx1, sx2 = a, a + side_w
            gx1, gx2 = sx2 + T, b
            full_drawers = bool(ext) and ext[0] <= a + 1 and ext[1] >= b - 1
            z_base = drawer_block(grp, a, b, ext[2], ext[3], a, b, inside=False) if full_drawers else BOT
            vpart(grp, sx2, z_base, TOP, "Side column partition")
            zone = lay.get("zone", 1000.0)
            ng = lay.get("glass", 3)
            g_bot = TOP - zone
            for k in range(1, ng + 1):
                z = g_bot + zone / (ng + 1) * k - 4
                ir(gx1, z, gx2 - gx1, 8, "6-GLASS")
                glass_3d.append((gx1, gx2, z))
            text("GLASS SHELVES", IX + (gx1 + gx2) / 2, TOP - zone / 2, 30)
            ir(gx1, g_bot - T, gx2 - gx1, T, "5-INTERNAL")
            shelves_3d.append((gx1, gx2, g_bot - T, "board"))
            internals.append((grp, "Shelf under glass zone", "board", 1, gx2 - gx1, SHELF_D, "1 long"))
            internals.append((grp, "Glass shelf", "glass", ng, gx2 - gx1 - 4, SHELF_D - 10, "polished"))
            z0 = z_base
            if ext and not full_drawers and ext[0] >= gx1 - 1:
                z0 = drawer_block(grp, gx1, gx2, ext[2], ext[3], a, b, inside=False)
            fill_shelves(grp, gx1, gx2, z0, g_bot - T, dim_x=gx2 - 90)
            zs = z_base
            if not lay.get("side_bottom_door") and not full_drawers:
                zs = drawer_block(grp, sx1, sx2, 2, lay.get("side_dz", 400.0), a, b, inside=True)
            fill_shelves(grp, sx1, sx2, zs, TOP, comp=lay.get("side_comp", 305.0), dim_x=sx1)
            text("SHELF +", IX + (sx1 + sx2) / 2, TOP - 150, 26)
            text("DRAWER", IX + (sx1 + sx2) / 2, TOP - 190, 26)
            continue
        if lay["type"] == "col_hang":
            # coat hanging at top, shelves in the middle, drawers at the bottom
            ext = ext_drawer_span(lay, a, b)
            if ext:
                z0 = drawer_block(grp, ext[0], ext[1], ext[2], ext[3], a, b, inside=False)
            else:
                z0 = drawer_block(grp, a, b, 2, lay.get("dz", 400.0), a, b, inside=True)
            hang = lay.get("hang", 1050.0)
            hs = TOP - hang - T
            ir(a, hs, b - a, T, "5-INTERNAL")
            shelves_3d.append((a, b, hs, "board"))
            internals.append((grp, "Shelf under hanging", "board", 1, b - a, SHELF_D, "1 long"))
            rz = TOP - 60
            msp.add_line((IX + a, rz), (IX + b, rz), dxfattribs={"layer": "5-INTERNAL"})
            msp.add_circle((IX + a + 40, rz), 14, dxfattribs={"layer": "5-INTERNAL"})
            rods_3d.append((a, b, rz))
            text("COAT HANGING", IX + (a + b) / 2, rz - 300, 34)
            dimv(hs + T, TOP, b, b - 80, f"{hang:.0f}", ox=IX)
            fill_shelves(grp, a, b, z0, hs, dim_x=a)
            continue
        if lay["type"] == "col_shelves":
            ext = ext_drawer_span(lay, a, b)
            z0 = BOT
            if ext:
                z0 = drawer_block(grp, ext[0], ext[1], ext[2], ext[3], a, b, inside=False)
                if ext[0] > a + 1 or ext[1] < b - 1:
                    xs = (a, ext[0] - T) if ext[0] > a + 1 else (ext[1] + T, b)
                    fill_shelves(grp, xs[0], xs[1], BOT, BOT + ext[3], dim_x=xs[0])
            fill_shelves(grp, a, b, z0, TOP, dim_x=a)
            text("FULL SHELVES", IX + (a + b) / 2, TOP - 150, 30)
            continue
        if lay["type"] == "bangle_glass":
            bw, zone, nb, ng, gap2 = lay.get("bangle_w", 300.0), lay.get("zone", 1000.0), lay.get("bangle_shelves", 4), lay.get("glass", 2), lay.get("gap2", 400.0)
            S1 = TOP - zone - T
            S2 = S1 - gap2 - T
            bx = a + bw
            ir(bx, S1 + T, T, TOP - S1 - T)
            vparts_3d.append((bx, S1 + T, TOP))
            for k in range(1, nb + 1):
                z = S1 + T + zone / (nb + 1) * k - T / 2
                ir(a, z, bw, T, "5-INTERNAL")
                shelves_3d.append((a, a + bw, z, "board"))
            gz = [S1 + T + zone / (ng + 1) * k - 4 for k in range(1, ng + 1)]
            for z in gz:
                ir(bx + T, z, b - bx - T, 8, "6-GLASS")
                glass_3d.append((bx + T, b, z))
            for z in (S1, S2):
                ir(a, z, b - a, T, "5-INTERNAL")
                shelves_3d.append((a, b, z, "board"))
            text("BANGLE /", IX + a + bw / 2, S1 + T + zone * 0.55, 32)
            text("PERFUME", IX + a + bw / 2, S1 + T + zone * 0.55 - 42, 32)
            text("GLASS", IX + (bx + T + b) / 2, gz[0] - 70, 32)
            text("OPEN STORAGE", IX + (a + b) / 2, (BOT + S2) / 2, 36)
            dimh(a, bx, S1 + T + 40, S1 + T + zone - 60, f"{bw:.0f}", ox=IX)
            dimv(S1 + T, TOP, b, b - 70, f"{zone:.0f}", ox=IX)
            internals += [(grp, "Shelf (full width)", "board", 2, b - a, SHELF_D, "1 long"),
                          (grp, "Bangle/perfume column partition", "board", 1, zone, D - BACK, "1 long"),
                          (grp, f"Bangle/perfume shelf ({bw:.0f} wide)", "board", nb, bw, SHELF_D, "1 long"),
                          (grp, "Glass shelf", "glass", ng, b - bx - T - 4, SHELF_D - 10, "polished")]
        elif lay["type"] == "shelves":
            comp = lay.get("comp", 305.0)
            dr = lay.get("drawers")                   # (m1, m2, count, zone) inside this bay
            z0 = BOT
            if dr:
                m1, m2, n, dz = dr
                dx2 = mx(m2) - T / 2 if mx(m2) - T / 2 < b - 1 else b
                dx1 = mx(m1) + T / 2 if mx(m1) + T / 2 > a + 1 else a
                ir(a, BOT + dz, b - a, T, "5-INTERNAL")
                shelves_3d.append((a, b, BOT + dz, "board"))
                internals.append((grp, "Drawer top shelf", "board", 1, b - a, SHELF_D, "1 long"))
                for px in ([dx2] if dx2 < b - 1 else []) + ([dx1 - T] if dx1 > a + 1 else []):
                    ir(px, BOT, T, dz)
                    vparts_3d.append((px, BOT, BOT + dz))
                    internals.append((grp, "Partition beside drawers", "board", 1, dz, D - BACK, "1 long"))
                for k in range(n):
                    ir(dx1 + 13, BOT + k * dz / n + 15, dx2 - dx1 - 26, dz / n - 30, "5-INTERNAL")
                text(f"{n} DRAWERS", IX + (dx1 + dx2) / 2, BOT + dz / 2, 34)
                drawer_boxes.append((dx1, dx2, n, dz))
                z0 = BOT + dz + T
            n_sh = int((TOP - z0) // (comp + T))
            for k in range(n_sh):
                z = z0 + k * (comp + T) + comp
                ir(a, z, b - a, T, "5-INTERNAL")
                shelves_3d.append((a, b, z, "board"))
                dimv(z - comp, z, a, a + 90, f"{comp:.0f}", ox=IX)
            internals.append((grp, f"Shelf ({comp:.0f} compartments)", "board", n_sh, b - a, SHELF_D, "1 long"))
        elif lay["type"] == "hanging":
            comp, ns = lay.get("comp", 305.0), lay.get("shelves", 3)
            z = BOT
            for k in range(ns):
                ir(a, z + comp, b - a, T, "5-INTERNAL")
                shelves_3d.append((a, b, z + comp, "board"))
                dimv(z, z + comp, b, b - 90, f"{comp:.0f}", ox=IX)
                z += comp + T
            rz = TOP - 60
            msp.add_line((IX + a, rz), (IX + b, rz), dxfattribs={"layer": "5-INTERNAL"})
            msp.add_circle((IX + a + 40, rz), 14, dxfattribs={"layer": "5-INTERNAL"})
            rods_3d.append((a, b, rz))
            text("HANGING", IX + (a + b) / 2, rz - 300, 36)
            text(f"{TOP - z:.0f} CLEAR", IX + (a + b) / 2, rz - 360, 30)
            internals.append((grp, f"Shelf ({comp:.0f} compartments)", "board", ns, b - a, SHELF_D, "1 long"))
    for (a, b) in bays:
        dimh(a, b, BOT, -170, f"{b - a:.0f}", ox=IX)
    text("INSIDE ELEVATION (DOORS REMOVED)", IX + W / 2, -480, 80)

    # ------------------------------------------------ 3. TOP PLAN
    PY = -2300.0
    rect(-300, PY + D, W + 600, 120, "9-WALL")
    text("WALL", W / 2, PY + D + 60, 40)
    rect(0, PY, W, D, "1-CARCASS")
    rect(T, PY + D - BACK, W - 2 * T, BACK, "5-INTERNAL")
    for x in part_x:
        rect(x, PY, T, D - BACK, "1-CARCASS")
    for m, col, hinge, handle in c["main_doors"]:
        x1, x2 = mx(m) + GAP / 2, mx(m + 1) - GAP / 2
        rect(x1, PY - SH, x2 - x1, SH, LAY[col])
        hx, r = (x1 if hinge == "L" else x2), x2 - x1
        msp.add_line((hx, PY - SH), (hx, PY - SH - r), dxfattribs={"layer": "5-INTERNAL"})
        msp.add_arc((hx, PY - SH), r, 270 if hinge == "L" else 180, 360 if hinge == "L" else 270, dxfattribs={"layer": "6-GLASS"})
    dimh(0, W, PY - SH, PY - SH - 520, f"{W:.0f}")
    dimv(PY - SH, PY + D, 0, -200, f"{DT:.0f}")
    dimv(PY, PY + D, W, W + 160, f"{D:.0f}")
    text("TOP PLAN", W / 2, PY - 900, 80)

    # ------------------------------------------------ 4. SECTION AT BASE
    SX, SY = IX + 300, PY - 600
    rect(D, 0, 120, 900, "9-WALL", SX, SY)
    rect(D - 10, 0, 10, c["TILE_SKIRT"], "9-WALL", SX, SY)
    text(f"TILE SKIRTING {c['TILE_SKIRT']:.0f}", SX + D + 300, SY + c["TILE_SKIRT"] / 2, 32, align=TextEntityAlignment.MIDDLE_LEFT)
    rect(0, P, D - 10, T, "1-CARCASS", SX, SY)
    rect(D - 10 - BACK, P + T, BACK, 700, "5-INTERNAL", SX, SY)
    rect(40, 0, T, P, "1-CARCASS", SX, SY)
    rect(-SH, P, SH, 700, LAY["A"], SX, SY)
    msp.add_line((SX - 300, SY), (SX + D + 200, SY), dxfattribs={"layer": "9-WALL"})
    dimv(SY, SY + P, SX, SX - 260, f"{P:.0f}")
    dimv(SY, SY + c["TILE_SKIRT"], SX + D, SX + D + 160, f"{c['TILE_SKIRT']:.0f}")
    text("SECTION AT BASE: carcass sits above the wall tile skirting", SX + D / 2, SY - 220, 40)

    TBX, TBY, TBW = -300, PY - 1500, 2 * W + 1700
    rect(TBX, TBY, TBW, 420, "10-TITLE")
    cells = [("PROJECT", f"Mr. Manoker - {c['title']}"), ("SIZE", f"{W:.0f} W x {H:.0f} H x {DT:.0f} D"),
             ("COLOURS", "  |  ".join(f"{k} {' '.join(v.split()[:2])}" for k, v in COLS.items())),
             ("BOARD / EDGE", "18 mm | doors 2 mm, carcass 0.5 mm"), ("BY", "ASTRA INTERIORS  +91 97911 82789")]
    cw = TBW / len(cells)
    for i, (k, v) in enumerate(cells):
        x = TBX + i * cw
        if i:
            msp.add_line((x, TBY), (x, TBY + 420), dxfattribs={"layer": "10-TITLE"})
        text(k, x + 30, TBY + 330, 40, "10-TITLE", TextEntityAlignment.LEFT)
        text(v, x + 30, TBY + 150, 50, "10-TITLE", TextEntityAlignment.LEFT)
    doc.saveas(os.path.join(OUT, f"{NAME} - AutoCAD 2D.dxf"))

    # ------------------------------------------------ CUT LIST
    MAXL = 2400.0
    C18, B6, GL = c["board"], c["back"], "8 mm toughened glass"
    DM = {k: f"18 mm door - {k} {v}" for k, v in COLS.items()}
    matmap = {"board": C18, "back": B6, "glass": GL, "mirror": "5 mm mirror"}
    cut = []

    def add(group, part, mat, qty, Lmm, Wmm, edge):
        if qty <= 0:
            return
        mat = matmap.get(mat, mat)
        if Lmm > MAXL and mat not in (GL, "5 mm mirror"):
            qty, Lmm, part = qty * 2, Lmm / 2, part + " (2 pcs, joint at partition)"
        eb = 2.0 if edge == "4 sides" else 0.5 if edge == "1 long" else 0.0
        cL = Lmm - 2 * eb if edge == "4 sides" else Lmm
        cW = Wmm - 2 * eb if edge == "4 sides" else Wmm - eb
        cut.append([group, part, mat, qty, round(Lmm, 1), round(Wmm, 1), round(cL, 1), round(cW, 1),
                    {"4 sides": "2 mm, 4 sides", "1 long": "0.5 mm, 1 long"}.get(edge, edge)])

    main_h = MAIN_T - MAIN_B
    add("Loft carcass", "Side panel L/R", C18, 2, L, D, "1 long")
    add("Loft carcass", "Top & bottom", C18, 2, W - 2 * T, D, "1 long")
    add("Loft carcass", "Partition", C18, len(part_x), L - 2 * T, D - BACK, "1 long")
    for i, bw in enumerate(bay_w):
        add("Loft carcass", f"Back panel loft {i + 1}", B6, 1, L - 2 * T + 12, bw + 12, "-")
    add("Main carcass", "Side panel L/R", C18, 2, main_h, D, "1 long")
    add("Main carcass", "Top & bottom", C18, 2, W - 2 * T, D, "1 long")
    add("Main carcass", "Partition (full height)", C18, len(part_x), TOP - BOT, D - BACK, "1 long")
    for i, bw in enumerate(bay_w):
        add("Main carcass", f"Back panel section {i + 1}", B6, 1, TOP - BOT + 12, bw + 12, "-")
    add("Base", f"Base front ({P:.0f} high)", C18, 1, W - 2 * T, P, "1 long")
    add("Base", "Base support / cross rail", C18, len(bays) + 2, D - 60, P, "-")
    for it in internals:
        add(*it)
    # doors grouped by size + colour
    groups = {}
    for ld in c["loft_doors"]:
        m1, m2 = ld[:2]
        k = ("Loft door", ld[3] if len(ld) > 3 else c.get("loft_colour", "A"), round(L - GAP, 1), round((m2 - m1) * SW - GAP, 1))
        groups[k] = groups.get(k, 0) + 1
    for m, col, hinge, handle in c["main_doors"]:
        k = ("Main door", col, round(main_h - drawer_zone.get(m, 0) - GAP, 1), round(SW - GAP, 1))
        groups[k] = groups.get(k, 0) + 1
    for m1, m2, col, n, dz in drawers:
        k = ("Drawer front", col, round((m2 - m1) * SW - GAP, 1), round(dz / n - GAP, 1))
        groups[k] = groups.get(k, 0) + n
    for m, col, bh, hinge in bottom_doors:
        k = ("Bottom door", col, round(bh - GAP, 1), round(SW - GAP, 1))
        groups[k] = groups.get(k, 0) + 1
    for (kind, col, a_, b_), q in groups.items():
        add("Doors & drawer fronts", f"{kind} {col}", DM[col], q, a_, b_, "4 sides")
    db_l = min(D - BACK - 40, 550)
    nbox = 0
    for a, b, n, dz in drawer_boxes:
        db_w, db_h = (b - a) - 26, dz / n - 70
        add("Drawer boxes", "Drawer side", C18, 2 * n, db_l, db_h, "1 long")
        add("Drawer boxes", "Drawer front/back (inner)", C18, 2 * n, db_w - 2 * T, db_h, "1 long")
        add("Drawer boxes", "Drawer bottom", B6, n, db_l, db_w, "-")
        nbox += n

    sqft = lambda r: r[3] * r[4] * r[5] / 92903.04
    by_mat = {}
    for r in cut:
        by_mat[r[2]] = by_mat.get(r[2], 0) + sqft(r)
    SHEET, WASTE = 32.0, 1.15
    mats = [[m, round(by_mat.get(m, 0), 1), math.ceil(by_mat.get(m, 0) * WASTE / SHEET)] for m in [C18, B6] + list(DM.values())]
    door_area = sum(by_mat.get(v, 0) for v in DM.values())
    mats.append(["Inner liner laminate (door backs)", round(door_area, 1), math.ceil(door_area * WASTE / SHEET)])
    if by_mat.get(GL):
        mats.append([GL, round(by_mat[GL], 1), "-"])
    if by_mat.get("5 mm mirror"):
        mats.append(["5 mm mirror", round(by_mat["5 mm mirror"], 1), "-"])
    mats.append(["Edge band 2 mm (doors, drawer fronts)", f"{math.ceil(sum(r[3] * 2 * (r[4] + r[5]) for r in cut if r[8].startswith('2 mm')) / 1000 * 1.1)} m", ""])
    mats.append(["Edge tape 0.5 mm (carcass fronts)", f"{math.ceil(sum(r[3] * r[4] for r in cut if r[8].startswith('0.5')) / 1000 * 1.1)} m", ""])
    hg = lambda h: 4 if h > 1800 else 3 if h > 1200 else 2
    hinges = len(c["loft_doors"]) * hg(L - GAP) + sum(hg(main_h - drawer_zone.get(m, 0) - GAP) for m, *_ in c["main_doors"]) + 2 * len(bottom_doors)
    channel = next(x for x in (550, 500, 450, 400, 350, 300, 250) if x <= db_l)
    hardware = [["Soft-close hinges", hinges]]
    if nbox:
        hardware.append([f"Soft-close telescopic channels {channel} mm (pairs)", nbox])
    hardware += [["Bar handles gold, long vertical (main doors)", len(c["main_doors"])],
                 ["Bar handles gold, short vertical (loft & bottom doors)", len(c["loft_doors"]) + len(bottom_doors)]]
    n_ext = sum(x[3] for x in drawers)
    if n_ext:
        hardware.append(["Bar handles gold, horizontal (outside drawers)", n_ext])
    if nbox - n_ext > 0:
        hardware.append(["Finger-pull / profile handle (inside drawers)", nbox - n_ext])
    if rods_3d:
        hardware.append([f"Wardrobe rod + 2 end supports", len(rods_3d)])
    if glass_3d:
        hardware.append(["Glass shelf supports (studs)", 4 * len(glass_3d)])
    if leds_3d:
        hardware.append([f"LED profile light over dressing mirror ({max(l[1] - l[0] for l in leds_3d) / 1000:.1f} m) + driver + door sensor switch", len(leds_3d)])
    if mirrors_3d:
        hardware.append(["Mirror fixing clips / adhesive", "1 set"])
    hardware.append(["Shelf pins / minifix", "as required"])

    wb = Workbook()
    ws = wb.active
    ws.title = "Cut list"
    gold = PatternFill("solid", fgColor="EFE6DA")
    ws.append([f"{NAME} - Mr. Manoker - cut list (mm) | {W:.0f} x {H:.0f} x {DT:.0f} | base {P:.0f} | "
               + ", ".join(f"{k} {v}" for k, v in COLS.items()) + " | Astra Interiors"])
    ws.append(["No", "Group", "Part", "Material", "Qty", "Finished L", "Finished W", "Cut L", "Cut W", "Edge band", "Sq.ft"])
    for cc in ws[2]:
        cc.font, cc.fill = Font(bold=True), gold
    for i, r in enumerate(cut, 1):
        ws.append([i] + r + [round(sqft(r), 1)])
    ws.append([])
    ws.append(["", "", "Total pieces", "", sum(r[3] for r in cut)])
    ws["A1"].font = Font(bold=True, size=12)
    for col, wdt in zip("ABCDEFGHIJK", (5, 26, 38, 38, 6, 11, 11, 10, 10, 15, 8)):
        ws.column_dimensions[col].width = wdt
    for row in ws.iter_rows(min_row=3, min_col=8, max_col=9):
        for cc in row:
            cc.font = Font(bold=True)
    ws.freeze_panes = "A3"
    for title, rows, hdr in (("Materials", mats, ["Material", "Area sq.ft / length", "8x4 sheets (15% waste)"]),
                             ("Hardware", hardware, ["Item", "Qty"])):
        s = wb.create_sheet(title)
        s.append(hdr)
        for r in rows:
            s.append(r)
        for cc in s[1]:
            cc.font, cc.fill = Font(bold=True), gold
        s.column_dimensions["A"].width, s.column_dimensions["B"].width, s.column_dimensions["C"].width = 50, 20, 22
    wb.save(os.path.join(OUT, f"{NAME} - Cut List.xlsx"))
    data = {"name": NAME, "title": c["title"], "colours": COLS, "shades": c.get("shades", {}), "cut": cut, "sqft": [round(sqft(r), 1) for r in cut],
            "mats": mats, "hardware": hardware,
            "geom": {"W": W, "H": H, "DT": DT, "D": D, "L": L, "P": P, "T": T, "SH": SH, "GAP": GAP, "SW": SW,
                     "modules": NM, "part_x": part_x, "loft_doors": c["loft_doors"], "main_doors": c["main_doors"],
                     "drawers": drawers, "bottom_doors": bottom_doors, "loft_colour": c.get("loft_colour", "A"), "shelves": shelves_3d,
                     "rods": rods_3d, "glass": glass_3d, "vparts": vparts_3d, "drawer_boxes": drawer_boxes, "int_drawers": int_drawers, "mirrors": mirrors_3d, "leds": leds_3d}}
    json.dump(data, open(os.path.join(OUT, f"{NAME} - data.json"), "w"), indent=1)
    print(NAME, "| pieces", sum(r[3] for r in cut), "| door width", round(SW - GAP, 1), "| sections", [round(b) for b in bay_w])
    for m in mats:
        print("  ", m)
    for h in hardware:
        print("  ", h)
    return data
