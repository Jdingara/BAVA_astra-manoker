"""Cut list - 5-door design (boards.json from make_5door_boards.py; outer box from the owner's AutoCAD drawing).
Total depth 500 = 494 carcass + 6 mm back (outer to outer, screwed). LED strip-light groove per main section."""
import json
import math
import os
import time

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

HERE = os.path.dirname(os.path.abspath(__file__))
T, BACK = 18.0, 6.0
DEPTH = 457.0                      # 18 inch carcass depth (default)
DEPTHS = {"GF": 500.0, "1F Master": 500.0, "1F Bedroom 2": 500.0, "2F": 500.0}   # owner: all wardrobes 500 deep
PART_D = DEPTH - BACK              # partitions stop at the back panel
SHELF_D = DEPTH - BACK - 20        # shelves set back 20 mm
GROOVE = "LED profile groove 12 W x 8 D, 100 mm from front edge"
GROOVE_REF = "LED profile groove - see LED groove sheet"
GAP_END, GAP_JOINT, GAP_EDGE = 3.0, 2.0, 1.0   # end door <-> side cover/strip | door <-> door | bottom / top
C18, B6 = "18 mm ply", "6 mm back ply"

boards = json.load(open(os.path.join(HERE, "boards.json")))    # 5-door layout (make_5door_boards.py); 6-door in "boards (6-door).json"
META = {k: v["meta"] for k, v in boards.items()}
# 2 bottom drawers per bedroom (opening 173 + 182, box 150): clear width of the drawer section from the 5-door layout
DRAWERS = {k: [(m["sections"][i]["x"][0], m["sections"][i]["x"][1], 2, 173.0,
                "Bottom drawers (centre, under dressing)" if i == 1 else "Bottom drawers (right section)")
               for i in range(3) if m["sections"][i]["drawers"]] for k, m in META.items()}
DRAWER_BOX_H = 150.0
# 5 doors (2 + 1 + 2), left -> right. Accent: doors 2 + 4 (GF, 1F Bed 2, 2F) / 2 + 5 (1F Master) + drawer fronts.
# 1F Bed 2 / 2F: drawers under doors 4-5, door 4 above the drawers = accent (L-shape). Centre door 3 = main colour.
_GF = ("DC687 Foliage Blue (Advance)", "21125 MR+ Sunburn (Merino)")
_MM = ("27292 LV Mink (grey)", "27262 LV Peacock (teal)")
_B2 = ("21433 SF Neo Banana Leaf (green)", "21457 SF Aspen Gold (yellow)")
_2F = ("21462 SF Lavendura (lavender)", "21452 SF Prism Violet (violet)")
_pat = lambda c, acc: [c[1] if i in acc else c[0] for i in range(1, 6)]
DOOR_COLOURS = {"GF": _pat(_GF, (2, 4)), "1F Master": _pat(_MM, (2, 5)), "1F Bedroom 2": _pat(_B2, (2, 4)), "2F": _pat(_2F, (2, 4))}
LOFT_COLOURS = {"GF": _pat(_GF, (2, 4)), "1F Master": [_MM[0]] * 5, "1F Bedroom 2": [_B2[0]] * 5, "2F": [_2F[0]] * 5}
DRAWER_COLOUR = {"GF": _GF[1], "1F Master": _MM[1], "1F Bedroom 2": _B2[1], "2F": _2F[1]}
SKIRT_COLOUR = {"GF": _GF[0], "1F Master": _MM[0], "1F Bedroom 2": _B2[0], "2F": _2F[0]}
COVER_SIDE = {"GF": "left", "1F Master": "left", "1F Bedroom 2": "right", "2F": "left"}   # one side cover only
LOFT_DOORS = {"GF": True, "1F Master": True, "1F Bedroom 2": True, "2F": True}
DOORS_PER_SECTION = [2, 1, 2]
GLASS_ROOMS, GLASS_BORDER = {"GF"}, 90.0      # owner: glass panel in the centre door only in GF (90 laminate border)
MIRROR_H = 700.0                              # dressing mirror height (width = dressing clear - 110)
# Every wardrobe: cupboard box up to 2000 mm, separate loft box on top (an 8 ft sheet is only 2400 long).
# GF is wider than 2400 -> two boxes side by side (cupboard and loft), joint at these two back-to-back sides.
SPLIT_X = {k: tuple(m["split"]) for k, m in META.items() if m["split"]}   # (left board x, right board x + 18)   # GF: 2 boxes, joint behind door 3 | door 4
MAX_SHEET = 2400.0
FRAME_W = 90.0                     # loft = 90 mm frame only
TITLES = {"GF": "GF Bedroom", "1F Master": "1st Floor M.Bedroom", "1F Bedroom 2": "1st Floor Bedroom 2", "2F": "2nd Floor Bedroom"}



def edge_cut(L, W, edge):
    """cut size = finished - edge band, rounded DOWN to whole mm (owner: no .5 numbers)"""
    if edge == "2 mm, 4 sides":
        return math.floor(L - 4 + 1e-6), math.floor(W - 4 + 1e-6)
    if edge == "2 mm, 1 long":          # side cover / strip: front edge only
        return math.floor(L + 1e-6), math.floor(W - 2 + 1e-6)
    eb = 0.5 if edge == "0.5 mm, 1 long" else 0.0
    return math.floor(L + 1e-6), math.floor(W - eb + 1e-6)


def analyse(name, d):
    DEPTH = DEPTHS.get(name, 457.0)
    PART_D = DEPTH - BACK
    CARC_D = DEPTH - BACK              # owner: total 500 = carcass 494 + 6 mm back screwed on the back edges (no groove)
    SHELF_D = DEPTH - BACK - 20
    hb = [tuple(b) for b in d["h"]]
    vb = [tuple(b) for b in d["v"]]
    xs = [b[0] for b in vb] + [b[0] + T for b in vb]
    x_min, x_max = min(b[0] for b in vb), max(b[0] + T for b in vb)
    width = x_max - x_min
    tall = max(b[2] - b[1] for b in vb)
    rows = []

    def add(group, part, mat, qty, L, W, edge, note=""):
        cl, cw = edge_cut(L, W, edge)
        rows.append([group, part, mat, qty, round(L, 1), round(W, 1), cl, cw, edge, note])

    # ---- levels: bottom | cupboard (box) top + loft bottom | loft top
    y_floor = min(b[1] for b in vb)
    ys = [b[0] for b in hb]
    y_bot, y_top = min(ys), max(ys)
    big = [b for b in hb if b[2] - b[1] >= 0.3 * width]
    main_top_y = META[name]["main_top"]               # cupboard top panel level (from make_5door_boards.py)
    top_lo = min(b[0] for b in hb if b[0] >= y_top - 40)
    mid_hi = max(b[0] for b in big if main_top_y - 1 <= b[0] <= main_top_y + 40)
    box_h = round(main_top_y + T - y_floor)          # cupboard box height (2000 in the drawings)

    # GF: boards that cross the box joint become two pieces (one per box)
    sx = SPLIT_X.get(name)
    if sx:
        new_hb = []
        for y, a, b in hb:
            if a < sx[0] - 1 and b > sx[1] + 1:
                new_hb += [(y, a, sx[0]), (y, sx[1], b)]
            else:
                new_hb.append((y, a, b))
        hb = new_hb

    # ---- vertical boards: full-height sides become cupboard side (box_h) + loft side
    for x, a, b in sorted(vb):
        L = b - a
        if L >= tall - 30:
            add("Cupboard box", f"Side panel (cupboard, {box_h} high)", C18, 1, box_h, CARC_D, "0.5 mm, 1 long", "6 mm back screwed on back edge")
            add("Loft box", "Side panel (loft)", C18, 1, L - box_h, DEPTH, "0.5 mm, 1 long")
        elif a >= main_top_y - 1:
            add("Loft box", "Loft partition / box side (back to back)", C18, 1, L, PART_D, "0.5 mm, 1 long")
        else:
            if L >= 1800:   # full-height partition: doors hinge on it -> same depth as side panel; back panel joint on its back edge
                add("Cupboard box", "Partition (full height, doors fixed)", C18, 1, L, CARC_D, "0.5 mm, 1 long", "back panel joint on its back edge (centre)")
            else:           # inside partition (dressing / bangle column) stops in front of the back panel
                add("Cupboard box", "Partition (inside)", C18, 1, L, PART_D, "0.5 mm, 1 long", "")
    # ---- horizontal boards
    tops_seen = 0
    for y, a, b in sorted(hb):
        L = b - a
        if y <= y_bot + 1:
            add("Cupboard box", "Bottom panel", C18, 1, L, CARC_D, "0.5 mm, 1 long")
        elif abs(y - main_top_y) < 1 and L >= 0.3 * width / (2 if sx else 1):
            add("Cupboard box", "Top panel", C18, 1, L, CARC_D, "0.5 mm, 1 long")
        elif main_top_y < y <= mid_hi + 1 and L >= 0.3 * width / (2 if sx else 1):
            add("Loft box", "Bottom panel", C18, 1, L, DEPTH, "0.5 mm, 1 long")
        elif y >= top_lo - 1:
            add("Loft box", "Top panel" if abs(y - top_lo) < 1 else "Top cover panel (2nd top, as drawn)", C18, 1, L, DEPTH, "0.5 mm, 1 long")
        elif abs(y - (META[name]["dress_y"] or -1)) < 0.5:
            add("Inside", "Dressing top (centre section)", C18, 1, L, PART_D, "0.5 mm, 1 long",
                f"flush with front (behind door 3); top {y - y_floor:.0f} from floor; mirror + LED above")
        else:
            add("Inside", "Shelf", C18, 1, L, SHELF_D, "0.5 mm, 1 long")

    # ---- 6 mm back panels: one per opening in the main zone and in the loft zone
    zones = {"Main": (y_bot + T, main_top_y), "Loft": (mid_hi + T, top_lo)}
    grooves = 0
    led = []
    for zname, (z1, z2) in zones.items():
        cols = sorted({x for x, a, b in vb if a <= z1 + 5 and b >= z2 - 5})
        edges = []
        for x in cols:
            edges.append((x, x + T))
        for (l1, r1), (l2, r2) in zip(edges, edges[1:]):
            w = l2 - r1
            if w < 60:
                continue                          # back-to-back boards
            if zname == "Main":
                grooves += 1
                # LED profile groove on the LEFT board of this section (its right face), vertical
                lx = l1
                full = any(abs(x - lx) < 0.5 and (b - a) >= tall - 30 for x, a, b in vb)
                pname = "Side panel" if full else "Partition"
                g_from = 0.0
                for x1, x2, n, dh, lab in DRAWERS[name]:
                    if abs(x1 - r1) < 15 and x2 <= l2 + 15:           # drawers fixed on this face -> stop groove above them
                        top_div = max(y for y, a, b in hb if abs(a - x1) < 1 and y < z1 + 450)
                        g_from = top_div + T - z1
                dy = META[name]["dress_y"]
                if dy and r1 - 1 < META[name]["sections"][1]["x"][0] < l2:   # dressing section: groove starts on the dressing top
                    g_from = dy + T - z1
                sec_h = z2 - z1
                led.append({"section": len(led) + 1, "opening": round(w), "panel": pname, "x": lx, "face": "right face (inside section)",
                            "from_front": 100, "start": round(g_from), "length": round(sec_h - g_from), "strip": round(sec_h - g_from - 20)})

    # ---- 6 mm back: outer to outer per box, full box height, screwed on the back edges; joints on partition centres (sheet 1220)
    boxes = [(x_min, sx[0] + T), (sx[1] - T, x_max)] if sx else [(x_min, x_max)]
    mids = sorted(x + T / 2 for x, a, b in vb if 1800 <= b - a < tall - 30)
    for bx0, bx1 in boxes:
        cuts = [bx0] + [c for c in mids if bx0 + 5 < c < bx1 - 5] + [bx1]
        for c0, c1 in zip(cuts, cuts[1:]):
            add("Back panels 6 mm", "Main back panel (outer to outer)", B6, 1, box_h, round(c1 - c0, 1), "-",
                "screw on back edges of sides / top / bottom / partitions; joint on partition centre")

    # ---- drawers
    n_drawers = 0
    for x1, x2, n, dh, label in DRAWERS[name]:
        w = x2 - x1
        box_w, dbox_h = w - 26, DRAWER_BOX_H
        box_l = next(c for c in (550, 500, 450, 400, 350) if c <= DEPTH - BACK - 40)
        gnote = "groove 8 mm wide x 10 deep: leave 12 mm from bottom edge, groove 12-20 mm (6 mm drawer bottom slides in)"
        add("Drawers", f"{label}: drawer side", C18, 2 * n, box_l, dbox_h, "0.5 mm, 1 long", gnote)
        add("Drawers", f"{label}: drawer front/back inner", C18, 2 * n, box_w - 2 * T, dbox_h, "0.5 mm, 1 long", gnote)
        add("Drawers", f"{label}: drawer bottom 6 mm (in groove)", B6, n, box_l - 2 * T + 18, box_w - 2 * T + 18, "-",
            "inside size + 9 mm each side (10 mm groove, 1 mm play)")
        n_drawers += n

    # ---- LOFT = 90 mm FRAME ONLY: replace loft box parts + loft back panels with a front frame of 90 mm strips
    rows = [r for r in rows if r[0] != "Loft box" and r[1] != "Loft back panel"]
    loft_h = tall - box_h
    up_x = sorted({x for x, a, b in vb if (b - a) >= tall - 30 or a >= main_top_y - 1})
    merged_x = []
    for x in up_x:
        if not merged_x or x - merged_x[-1] > 40:     # back-to-back boards -> one frame upright
            merged_x.append(x)
    add("Loft frame 90 mm", "Frame upright (end / partition)", C18, len(merged_x), loft_h, FRAME_W, "0.5 mm, 1 long", "loft frame only - no box, no back panel")
    rail_pieces = [(sx[0] - (x_min + T)), (x_max - T - sx[1])] if sx else [width - 2 * T]
    for L in rail_pieces:
        add("Loft frame 90 mm", "Top rail", C18, 1, L, FRAME_W, "0.5 mm, 1 long", "fix to ceiling")
        add("Loft frame 90 mm", "Bottom rail (front, on cupboard top)", C18, 1, L, FRAME_W, "0.5 mm, 1 long")

    # ---- SHUTTERS: 6 doors (2 per section), full overlay, 3 mm gaps; drawer section: doors only above the drawers,
    #      drawers get outside fronts (shutter material)
    SH = "18 mm ply + Merino laminate (shutter)"
    z1m, z2m = y_bot + T, main_top_y
    cols = sorted({x for x, a, b in vb if a <= z1m + 5 and b >= z2m - 5})
    groups = []
    for x in cols:
        if groups and x - groups[-1][-1] < 40:
            groups[-1].append(x)
        else:
            groups.append([x])
    edges = []
    for i, g in enumerate(groups):
        lo, hi = min(g), max(g) + T
        edges.append(lo if i == 0 else (hi if i == len(groups) - 1 else (lo + hi) / 2))
    edges[-1] = max(groups[-1]) + T
    f_bot, f_top = y_bot, main_top_y + T                      # door covers bottom panel .. top of top panel
    hinges = 0
    door_rows = []
    per = DOORS_PER_SECTION if len(edges) == 4 else [2] * (len(edges) - 1)
    nd = sum(per)
    front_w = edges[-1] - edges[0]
    dw = math.floor((front_w - 2 * GAP_END - (nd - 1) * GAP_JOINT) / nd)      # all doors equal, whole mm
    glass = []
    for (xa, xb), q in zip(zip(edges, edges[1:]), per):
        drw = [dd for dd in DRAWERS[name] if xa - 5 <= dd[0] and dd[1] <= xb + 5]
        if drw:
            x1, x2, n, dh, lab = drw[0]
            divs = sorted(y for y, a, b in hb if a <= x1 + 5 and b >= x2 - 5 and y_bot + 1 < y < y_bot + 30 + n * (dh + T) + 40)[:n]
            cuts = [f_bot] + [y + T / 2 for y in divs]
            for k_, (lo_, hi_) in enumerate(zip(cuts, cuts[1:])):
                hgt = (hi_ - lo_) - (GAP_EDGE if k_ == 0 else GAP_JOINT / 2) - GAP_JOINT / 2
                add("Shutters", "Drawer outside front (laminate)", SH, 1, q * dw + (q - 1) * GAP_JOINT, round(hgt, 1), "2 mm, 4 sides", "fix on drawer box; handle")
            dh_ = f_top - cuts[-1] - GAP_JOINT / 2 - GAP_JOINT / 2
            door_rows.append((q, dh_, dw, "Door above drawers"))
        else:
            door_rows.append((q, f_top - f_bot - GAP_EDGE - GAP_JOINT / 2, dw, "Door (full height)"))
    col = DOOR_COLOURS.get(name)
    k = 0
    for q, h_, w_, lab in door_rows:
        for j in range(q):
            k += 1
            c = f" - {col[k - 1]}" if col else ""
            note = "concealed hinges; gaps: 2 mm between doors, 3 mm at end, 1 mm bottom, 2 mm to loft door"
            lab_ = lab
            if k == 3 and name in GLASS_ROOMS:          # centre door: laminate frame with glass panel
                gw, gh = w_ - 2 * GLASS_BORDER, h_ - 2 * GLASS_BORDER
                glass.append((math.floor(gw + 20), math.floor(gh + 20)))
                lab_ += " GLASS"
                note = (f"CENTRE GLASS DOOR: CNC cut-out {gw:.0f} x {gh:.0f} after laminate + edge band ({GLASS_BORDER:.0f} border all round); "
                        f"glass {glass[-1][0]} x {glass[-1][1]} fixed behind with beading; " + note)
            add("Shutters", lab_ + c, SH, 1, round(h_, 1), round(w_, 1), "2 mm, 4 sides", note)
        hinges += q * (5 if h_ > 1700 else 4)
    if col:   # drawer fronts colour
        rows[:] = [r if r[1] != "Drawer outside front (laminate)" else r[:1] + [f"Drawer outside front - {DRAWER_COLOUR[name]}"] + r[2:] for r in rows]
    if LOFT_DOORS.get(name):   # loft doors: same widths as the doors below, on the 90 mm loft frame
        loft_dh = tall - (f_top - y_floor) - GAP_JOINT / 2 - GAP_EDGE
        lc = LOFT_COLOURS.get(name)
        for i in range(nd):
            c = f" - {lc[i]}" if lc else ""
            add("Shutters", "Loft door" + c, SH, 1, round(loft_dh, 1), dw, "2 mm, 4 sides", "on loft frame; same width as doors below; 2 mm to cupboard door, 1 mm at top")
            hinges += 2 if loft_dh < 900 else 3
        # front skirting (base 80) - one piece per box (no piece over 2400)
        pieces = [(edges[0], (sx[0] + sx[1]) / 2), ((sx[0] + sx[1]) / 2, edges[-1])] if sx else [(edges[0], edges[-1])]
        for xa, xb in pieces:
            add("Shutters", "Skirting (front, base 80)" + (f" - {SKIRT_COLOUR[name]}" if name in SKIRT_COLOUR else ""), SH, 1, round(xb - xa, 1), round(y_bot - y_floor, 1), "0.5 mm, 1 long", "full base height 80 (doors start 1.5 above); 0.5 mm tape on top edge only")
        # side cover (end) panels, colour laminate outside, both ends, depth = box + door, full height (floor to loft top)
        # in 2 pieces (sheet max 2400): joint at the cupboard / loft door line
        cov_d = DEPTH + T
        low_h = f_top - y_floor
        for lab_, h_ in (("Side cover panel - lower (floor to 2000)", low_h), ("Side cover panel - upper (loft)", tall - low_h)):
            add("Shutters", lab_ + f" - {SKIRT_COLOUR[name]}", SH, 1, round(h_, 1), round(cov_d, 1), "2 mm, 1 long",
                f"{COVER_SIDE[name].upper()} end only, outside of side panel; {cov_d:.0f} deep = box {DEPTH:.0f} + door {T:.0f}; joint in line with door gap")
        # opposite (wall) side: 100 mm wide strip, same colour, full height, flush with door front
        other = "right" if COVER_SIDE[name] == "left" else "left"
        for lab_, h_ in (("Wall-side strip 100 - lower (floor to 2000)", low_h), ("Wall-side strip 100 - upper (loft)", tall - low_h)):
            add("Shutters", lab_ + f" - {SKIRT_COLOUR[name]}", SH, 1, round(h_, 1), 100.0, "2 mm, 1 long",
                f"{other.upper()} end, outside of side panel at the front (flush with door front); joint in line with door gap")

    # mark the panels that carry the LED groove
    for g in led:
        add("LED groove", f"Section {g['section']} ({g['opening']} wide): {g['panel']} - {g['face']}", C18, 0, g["length"], 12, "-",
            f"groove 12 W x 8 D, {g['from_front']} mm from front edge, from {g['start']} mm above bottom panel to underside of top panel")
    rows = [r for r in rows if r[0] != "LED groove"]
    # merge identical rows
    merged = {}
    for r in rows:
        k = (r[0], r[1], r[2], r[4], r[5], r[8], r[9])
        if k in merged:
            merged[k][3] += r[3]
        else:
            merged[k] = list(r)
    rows = list(merged.values())
    order = {"Cupboard box": 0, "Loft frame 90 mm": 1, "Loft box": 1, "Inside": 2, "Back panels 6 mm": 3, "Drawers": 4, "Shutters": 5}
    rows.sort(key=lambda r: (order[r[0]], -r[4], -r[5]))

    led_m = round(sum(g["strip"] for g in led) / 1000, 2)
    sqft = lambda r: r[3] * r[4] * r[5] / 92903.04
    by = {}
    for r in rows:
        by[r[2]] = by.get(r[2], 0) + sqft(r)
    mats = [[m, round(by.get(m, 0), 1), math.ceil(by.get(m, 0) * 1.15 / 32)] for m in (C18, B6, SH)]
    mats.append(["Edge tape 0.5 mm (front edges)", f"{math.ceil(sum(r[3] * r[4] for r in rows if r[8].startswith('0.5')) / 1000 * 1.1)} m", ""])
    mats.append(["Edge tape 2 mm (shutters, 4 sides)", f"{math.ceil(sum(r[3] * (2 * (r[4] + r[5]) if r[8] == '2 mm, 4 sides' else r[4]) for r in rows if r[8].startswith('2 mm')) / 1000 * 1.1)} m", ""])
    hardware = [["LED strip light + aluminium profile (in grooves)", f"{grooves} pcs, {led_m} m total"],
                ["LED driver + door sensor switch", 1],
                [f"Soft-close telescopic channels {box_l} mm (pairs)", n_drawers],
                ["Drawer handles / profile", n_drawers],
                ["Concealed soft-close hinges (doors)", hinges],
                ["Door handles", nd]]
    m = META[name]
    if m["dress_y"]:
        hardware.append([f"Dressing mirror 5 mm (on back panel), {m['sections'][1]['clear'] - 110} x {MIRROR_H:.0f}", 1])
    for s_ in m["sections"]:
        if s_.get("hanging"):
            hardware.append([f"Coat stand: oval SS hanging rod {s_['clear'] - 2} long + 2 end brackets (rod {s_['rod_y'] - y_floor:.0f} from floor, 1200 hanging)", 1])
    for gw, gh in glass:
        hardware.append([f"Glass panel for centre door {gw} x {gh} (type to confirm) + beading", 1])
    longest = max(r[4] for r in rows)
    depth_used = DEPTH
    info = {"depth": depth_used, "channel": box_l if DRAWERS[name] else None, "longest_piece": longest, "box_h": box_h, "width": round(width), "height": round(tall), "main_clear": round(zones["Main"][1] - zones["Main"][0]),
            "loft_clear": round(zones["Loft"][1] - zones["Loft"][0]), "grooves": grooves, "led_m": led_m, "led": led}
    return rows, mats, hardware, info


def save(wb, path):
    root, ext = os.path.splitext(path)
    for cand in (path, root + " (updated)" + ext, root + time.strftime(" (%H%M%S)") + ext):
        try:
            wb.save(cand)
            return cand
        except PermissionError:
            continue


if __name__ == "__main__":
    wb = Workbook()
    gold = PatternFill("solid", fgColor="EFE6DA")
    summary = wb.active
    summary.title = "Summary"
    summary.append(["Wardrobe", "Width", "Height", "Main clear H", "Loft clear H", "Pieces", "18 mm sheets", "6 mm sheets", "LED grooves", "LED m"])
    for c in summary[1]:
        c.font, c.fill = Font(bold=True), gold
    allres = {}
    for name in ["GF", "1F Master", "1F Bedroom 2", "2F"]:
        rows, mats, hw, info = analyse(name, boards[name])
        allres[name] = (rows, mats, hw, info)
        ws = wb.create_sheet(name)
        ws.append([f"{TITLES[name]} wardrobe - from owner's AutoCAD drawing | {info['width']} W x {info['height']} H x {info['depth']:.0f} D | Astra Interiors"])
        ws["A1"].font = Font(bold=True, size=12)
        ws.append(["No", "Group", "Part", "Material", "Qty", "Finished L", "Finished W", "Cut L", "Cut W", "Edge band", "Machining / note"])
        for c in ws[2]:
            c.font, c.fill = Font(bold=True), gold
        for i, r in enumerate(rows, 1):
            ws.append([i] + r)
        ws.append([])
        ws.append(["", "", "Total pieces", "", sum(r[3] for r in rows)])
        ws.append([])
        ws.append(["", "Materials", "", "Area sq.ft / length", "8x4 sheets (15% waste)"])
        for m in mats:
            ws.append(["", m[0], "", m[1], m[2]])
        ws.append([])
        ws.append(["", "Hardware", "", "Qty"])
        for h in hw:
            ws.append(["", h[0], "", h[1]])
        for col, wdt in zip("ABCDEFGHIJK", (5, 16, 46, 14, 6, 11, 11, 10, 10, 15, 52)):
            ws.column_dimensions[col].width = wdt
        for row in ws.iter_rows(min_row=3, max_row=2 + len(rows), min_col=8, max_col=9):
            for c in row:
                c.font = Font(bold=True)
        for row in ws.iter_rows(min_row=3, max_row=2 + len(rows), min_col=11, max_col=11):
            for c in row:
                c.alignment = Alignment(wrap_text=True)
        ws.freeze_panes = "A3"
        summary.append([TITLES[name], info["width"], info["height"], info["main_clear"], info["loft_clear"],
                        sum(r[3] for r in rows), mats[0][2], mats[1][2], info["grooves"], info["led_m"]])
    ls = wb.create_sheet("LED groove cutting")
    ls.append(["LED STRIP LIGHT - aluminium profile groove cutting (all wardrobes) | Astra Interiors"])
    ls["A1"].font = Font(bold=True, size=12)
    ls.append(["Groove: 12 mm wide x 8 mm deep, 100 mm from the FRONT edge, vertical, on the panel face inside the section (router / grooving cutter)."])
    ls.append(["Start = height above the top of the bottom panel. Groove runs up to the underside of the top panel. Drill 10 mm wire hole through the top panel at the groove top (to driver in loft)."])
    ls.append(["Where drawers are fixed on that face the groove starts above the drawers (channel would cover it). Keep shelf screws clear of the groove."])
    ls.append([])
    ls.append(["Wardrobe", "Section", "Opening W", "Panel", "Face", "From front", "Groove start", "Groove length", "Profile + strip length"])
    for c in ls[6]:
        c.font, c.fill = Font(bold=True), gold
    for nm in ["GF", "1F Master", "1F Bedroom 2", "2F"]:
        for g in allres[nm][3]["led"]:
            ls.append([TITLES[nm], g["section"], g["opening"], g["panel"], g["face"], g["from_front"], g["start"], g["length"], g["strip"]])
        ls.append([TITLES[nm], "Total", "", "", "", "", "", "", f"{allres[nm][3]['led_m']} m"])
    for col, wdt in zip("ABCDEFGHI", (22, 9, 11, 13, 26, 11, 13, 14, 20)):
        ls.column_dimensions[col].width = wdt
    summary.append([])
    summary.append(["Depth 500 total = carcass 494 (sides/top/bottom/full partitions) + 6 mm back screwed on, outer to outer, joints on partition centres. Shelves 474. No back groove."])
    summary.append([f"{GROOVE}: one vertical groove per main section - see sheet LED groove cutting."])
    summary.append(["All wardrobes: cupboard box 2000 mm high; LOFT above = 90 mm FRAME ONLY (uprights + top/bottom rails, no box, no back panel)."])
    summary.append(["GF Bedroom: wider than 2400, so 2 cupboard boxes side by side; loft rails in 2 pieces; no board over 2400."])
    summary.append(["Shutters: 5 doors per bedroom (2 + 1 + 2), full overlay, 2 mm between doors. Drawer section: doors only above the drawers; drawers have outside fronts."])
    summary.append(["Centre section (door 3) = dressing: top 750 from floor (GF) / 800 (others), mirror + LED above. GF centre door has a glass panel (90 laminate border); other rooms plain door."])
    for col, wdt in zip("ABCDEFGHIJ", (24, 9, 9, 13, 13, 9, 13, 12, 12, 9)):
        summary.column_dimensions[col].width = wdt
    out = save(wb, os.path.join(HERE, "Owner Drawings - Wardrobe Cut List (500 depth).xlsx"))
    json.dump({k: {"rows": v[0], "mats": v[1], "hardware": v[2], "info": v[3]} for k, v in allres.items()},
              open(os.path.join(HERE, "owner_cutlist.json"), "w"), indent=1)
    print("saved", out)
    for k, v in allres.items():
        print(k, v[3], "pieces", sum(r[3] for r in v[0]))
        for r in v[0]:
            print("   ", r[:9])
