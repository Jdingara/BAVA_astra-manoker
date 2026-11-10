"""Mr. Manoker kitchen - full build: every unit and piece (cut list) + 3D positions for Blender.
Bottom: 18 mm ply boxes (540 deep) inside the masonry openings (710 high), fronts 27183 LV Camouflage.
Top: 350 deep, 1410 high, bottom at 1447 (600 above the 847 counter), doors 27111 LV Ivory White.
Writes kitchen_cutlist.json and kitchen_parts.json."""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
T, BK = 18.0, 6.0
OPEN_H, SLAB, GRAN = 710.0, 110.0, 27.0
CTR = OPEN_H + SLAB + GRAN                 # 847
MD, GD = 560.0, 600.0                      # masonry depth (wall to pillar face), granite depth
BD = 540.0                                 # bottom box depth
TOP_Z, TOP_H, TD = CTR + 600, 1410.0, 350.0
P = 110.0
PROF = 20.0       # bottom: aluminium G/J profile handle on the top edge of every front (front is 20 shorter)
DROP = 25.0       # top: door hangs 25 below the box bottom = finger-grip (handleless)
RX, RY = MD + P + 2080 + P + MD, 3350.0    # room inside: window wall length x left wall (3000 top + 350 garage corner)
BOT_LAM, TOP_LAM, IN_LAM = "27183 LV Camouflage", "27111 LV Ivory White", "27111 LV Ivory White"
C18, B6 = "18 mm ply", "6 mm ply"

rows, parts, hardware = [], [], {}


def cut(L, W, edge):
    if edge == "2 mm, 4 sides":
        return math.floor(L - 4 + 1e-6), math.floor(W - 4 + 1e-6)
    if edge == "0.5 mm, 1 long":
        return math.floor(L + 1e-6), math.floor(W - 0.5 + 1e-6)
    return math.floor(L + 1e-6), math.floor(W + 1e-6)


def add(unit, group, part, mat, lam, q, L, W, edge, note=""):
    cL, cW = cut(L, W, edge)
    rows.append([unit, group, part, mat, lam, q, round(L, 1), round(W, 1), cL, cW, edge, note])


def hw(name, q):
    hardware[name] = hardware.get(name, 0) + q


# ---------- placement: a "run" along a wall. local lx along the run, ly from the wall (0) outwards, z up
class Run:
    def __init__(self, wall, start):
        self.wall, self.start = wall, start

    def world(self, lx, ly, z, w, d, h):
        s = self.start
        if self.wall == "N":   # window wall, y = RY, run +x
            return (s + lx, RY - ly - d, z, w, d, h)
        if self.wall == "S":   # entrance wall, y = 0, run +x from left wall
            return (s + lx, ly, z, w, d, h)
        if self.wall == "W":   # left wall, x = 0, run -y from window corner
            return (ly, s - lx - w, z, d, w, h)
        if self.wall == "E":   # right wall, x = RX, run -y from window corner
            return (RX - ly - d, s - lx - w, z, d, w, h)


def put(run, kind, name, lx, ly, z, w, d, h, colour=None):
    parts.append({"kind": kind, "name": name, "box": run.world(lx, ly, z, w, d, h), "colour": colour})


# ---------- fronts helper: split [a, b] (lx) x [z0, z1] into fronts with 1 mm edges / 2 mm joints
def fronts_row(edges, z0, z1):
    out = []
    for i, (a, b) in enumerate(zip(edges, edges[1:])):
        out.append((a + 1, b - 1))
    return out, (z0 + 1, z1 - 1)


def base_box(unit, run, ox, opening, cols, lam=BOT_LAM):
    """cols: list of (internal width, kind, data) left->right along the run. kinds: baskets(list of inch), doors(n), magic, wicker"""
    W, H = opening - 4, OPEN_H - 4
    x0, z0 = ox + 2, 2.0
    iw = sum(c[0] for c in cols) + T * (len(cols) - 1)
    assert abs(iw - (W - 2 * T)) < 1.5, (unit, iw, W - 2 * T)
    note_o = f"box {W:.0f} x {H:.0f} x {BD:.0f} in opening {opening:.0f}"
    add(unit, "Carcass", "Side panel", C18, IN_LAM, 2, H, BD, "0.5 mm, 1 long", note_o)
    add(unit, "Carcass", "Bottom panel", C18, IN_LAM, 1, W - 2 * T, BD, "0.5 mm, 1 long")
    add(unit, "Carcass", "Top rail (front + back)", C18, IN_LAM, 2, W - 2 * T, 100, "0.5 mm, 1 long", "granite on masonry above")
    add(unit, "Back 6 mm", "Back panel", B6, IN_LAM + " 1S", 1, H - 2 * T + 12, W - 2 * T + 12, "-", "in 6 mm groove")
    put(run, "carcass", "side", x0, 0, z0, T, BD, H); put(run, "carcass", "side", x0 + W - T, 0, z0, T, BD, H)
    put(run, "carcass", "bottom", x0 + T, 0, z0, W - 2 * T, BD, T)
    put(run, "back", "back", x0 + T, 0, z0 + T, W - 2 * T, BK, H - 2 * T)
    x, edges = x0 + T, [x0]
    for i, (cw, kind, data) in enumerate(cols):
        if i:
            add(unit, "Carcass", "Partition", C18, IN_LAM, 1, H - 2 * T, BD - BK, "0.5 mm, 1 long")
            put(run, "carcass", "partition", x, BK, z0 + T, T, BD - BK, H - 2 * T)
            edges.append(x + T / 2); x += T
        if kind == "doors":
            add(unit, "Carcass", "Shelf", C18, IN_LAM, 1, cw, BD - 26, "0.5 mm, 1 long", "middle of the section")
            put(run, "shelf", "shelf", x, BK + 20, z0 + H / 2, cw, BD - 26, T)
        x += cw
    edges.append(x0 + W)
    # fronts
    for i, (cw, kind, data) in enumerate(cols):
        a, b = edges[i] + 1, edges[i + 1] - 1
        if kind == "baskets":
            hs = {4: 176, 6: 227, 8: 279, 9: 344}
            tot = sum(hs[s] for s in data); z = z0
            for s in data[::-1]:                             # bottom first
                seg = H * hs[s] / tot
                fh = seg - 2 - PROF
                add(unit, "Shutters", f'Basket front ({s if s != 9 else 8}" basket)', C18, lam, 1, fh, b - a, "2 mm, 4 sides", "screw to basket front frame; profile handle on top edge")
                put(run, "front", "basket front", a, BD, z + 1, b - a, T, fh, lam)
                put(run, "profile", "profile", a, BD, z + 1 + fh, b - a, T + 4, PROF)
                hw("Aluminium profile handle (G/J) - running mm", round(b - a))
                hw(f'21" basket {s if s != 9 else 8}" high (533 wide, 540 deep) + soft-close channels', 1)
                z += seg
        elif kind == "doors":
            n = data; dw = ((b - a) - 2 * (n - 1)) / n
            for k in range(n):
                add(unit, "Shutters", "Door", C18, lam, 1, H - 2 - PROF, dw, "2 mm, 4 sides", "3 hinges; profile handle on top edge")
                put(run, "front", "door", a + k * (dw + 2), BD, z0 + 1, dw, T, H - 2 - PROF, lam)
                put(run, "profile", "profile", a + k * (dw + 2), BD, z0 + 1 + H - 2 - PROF, dw, T + 4, PROF)
                hw("Aluminium profile handle (G/J) - running mm", round(dw))
                hw("Concealed soft-close hinge (base doors)", 3)
        elif kind == "magic":                                # [blind][door] with blind at the corner (lx=0 side)
            blind = (b - a) - 450 - 2
            add(unit, "Shutters", "Blind panel (fixed, magic corner)", C18, lam, 1, H - 2, blind, "2 mm, 4 sides", "fixed to box, covers corner")
            add(unit, "Shutters", "Magic corner door 450", C18, lam, 1, H - 2 - PROF, 450, "2 mm, 4 sides", "fixed to Ebco magic corner front frame; profile on top")
            hw("Aluminium profile handle (G/J) - running mm", 450)
            put(run, "front", "blind", a, BD, z0 + 1, blind, T, H - 2, lam); put(run, "front", "magic door", a + blind + 2, BD, z0 + 1, 450, T, H - 2, lam)
            hw("Ebco Magic Corner, RIGHT-hand, 900 cabinet / 450 door", 1); hw("Concealed hinge (magic corner door)", 2)
        elif kind == "wicker":
            seg = H / 3
            for k in range(3):
                add(unit, "Shutters", "Wicker basket front", C18, lam, 1, seg - 2 - PROF, b - a, "2 mm, 4 sides", "on wicker basket channel; profile on top")
                hw("Aluminium profile handle (G/J) - running mm", round(b - a))
                put(run, "front", "wicker front", a, BD, z0 + k * seg + 1, b - a, T, seg - 2, lam)
            hw('Wicker basket 21" (533) with channels', 3)


def masonry(run, length, items, g_start=0.0):
    """items along the run: ('P', w) pillar, ('O', w) opening, ('C', w) solid corner."""
    lx = 0
    for k, w in items:
        if k in ("P", "C"):
            put(run, "masonry", "pillar", lx, 0, 0, w, MD, OPEN_H)
        lx += w
    put(run, "masonry", "slab", 0, 0, OPEN_H, length, MD, SLAB)
    put(run, "granite", "granite", g_start, 0, OPEN_H + SLAB, length - g_start, GD, GRAN)


def top_box(unit, run, lx, W, n_doors, height=TOP_H, z=TOP_Z, shelves=2):
    secs = n_doors if n_doors <= 3 else n_doors
    n_part = (n_doors - 1) if n_doors in (2, 3) else 0
    iw = (W - 2 * T - n_part * T) / max(1, n_part + 1)
    add(unit, "Carcass", "Side panel", C18, IN_LAM, 2, height, TD, "0.5 mm, 1 long", f"box {W:.0f} x {height:.0f} x {TD:.0f}")
    add(unit, "Carcass", "Top / bottom panel", C18, IN_LAM, 2, W - 2 * T, TD, "0.5 mm, 1 long")
    add(unit, "Back 6 mm", "Back panel", B6, IN_LAM + " 1S", 1, height - 2 * T + 12, W - 2 * T + 12, "-", "in 6 mm groove")
    if n_part:
        add(unit, "Carcass", "Partition", C18, IN_LAM, n_part, height - 2 * T, TD - BK, "0.5 mm, 1 long")
    add(unit, "Carcass", "Shelf", C18, IN_LAM, shelves * (n_part + 1), iw, TD - 26, "0.5 mm, 1 long", f"{shelves} per section")
    put(run, "carcass", "side", lx, 0, z, T, TD, height); put(run, "carcass", "side", lx + W - T, 0, z, T, TD, height)
    put(run, "carcass", "tb", lx + T, 0, z, W - 2 * T, TD, T); put(run, "carcass", "tb", lx + T, 0, z + height - T, W - 2 * T, TD, T)
    put(run, "back", "back", lx + T, 0, z + T, W - 2 * T, BK, height - 2 * T)
    dw = (W - 2 - 2 * (n_doors - 1)) / n_doors
    for k in range(n_doors):
        add(unit, "Shutters", "Door", C18, TOP_LAM, 1, height - 2 + DROP, dw, "2 mm, 4 sides", f"4 hinges; HANDLELESS - door hangs {DROP:.0f} below box bottom = finger grip")
        put(run, "front", "top door", lx + 1 + k * (dw + 2), TD, z + 1 - DROP, dw, T, height - 2 + DROP, TOP_LAM)
        hw("Concealed soft-close hinge (top doors)", 4)


# ================= BOTTOM =================
N = Run("N", 0); E = Run("E", RY); Wl = Run("W", RY); S = Run("S", 0)
# window wall: corner | P | 2080 | P | corner
masonry(N, RX, [("C", MD), ("P", P), ("O", 2080), ("P", P), ("C", MD)])
base_box("B1 Gas unit 2080 (window wall)", N, MD + P, 2080, [(557, "baskets", [4, 6, 8]), (557, "baskets", [9, 9]), (890, "doors", 2)])
# right wall (sink): from window corner: (corner of N run already there) P | sink 668 | P
E2 = Run("E", RY - MD)
masonry(E2, P + 668 + P, [("P", P), ("O", 668), ("P", P)], g_start=GD - MD)
u = "B2 Sink 668 (right wall) - frame + 2 doors, no box"
add(u, "Frame", "Frame stile", C18, BOT_LAM, 2, OPEN_H, 50, "0.5 mm, 1 long", "fixed to pillars, doors hinge on it")
add(u, "Frame", "Frame rail (top + bottom)", C18, BOT_LAM, 2, 668 - 100, 50, "0.5 mm, 1 long")
dw = (668 - 2 - 2) / 2
for k in range(2):
    add(u, "Shutters", "Sink door", C18, BOT_LAM, 1, OPEN_H - 2 - PROF, dw, "2 mm, 4 sides", "3 hinges on frame; profile on top")
    put(E2, "front", "sink door", P + 1 + k * (dw + 2), MD - T, 1, dw, T, OPEN_H - 2 - PROF, BOT_LAM)
    put(E2, "profile", "profile", P + 1 + k * (dw + 2), MD - T, OPEN_H - 1 - PROF, dw, T + 4, PROF)
    hw("Aluminium profile handle (G/J) - running mm", round(dw))
hw("Concealed soft-close hinge (base doors)", 6)
# left wall: from window corner: P | 1050 | P
W2 = Run("W", RY - MD)
masonry(W2, P + 1050 + P, [("P", P), ("O", 1050), ("P", P)], g_start=GD - MD)
base_box("B3 Left 1050", W2, P, 1050, [(557, "baskets", [4, 6, 8]), (435, "doors", 1)])
# left wall corner leg of the L opening (1500) down to the entrance wall: slab + granite over it
W3 = Run("W", RY - MD - P - 1050 - P)
masonry(W3, RY - MD - P - 1050 - P - GD, [("O", RY - MD - P - 1050 - P - GD)])   # stops at the entrance-wall granite
# entrance wall: 1490 opening from the left wall corner | P
masonry(S, 1490 + P, [("O", 1490), ("P", P)])
base_box("B4 Corner 1490 (entrance wall)", S, 0, 1490, [(896, "magic", None), (536, "wicker", None)])

# ================= TOP =================
top_box("T1 Right top 1420 (over sink)", Run("E", RY), 0, 1420, 3)
top_box("T2 Left top 3000 - box A 1500", Run("W", RY), 0, 1500, 3)
top_box("T3 Left top 3000 - box B 1500", Run("W", RY), 1500, 1500, 3)
top_box("T4 Entrance-wall top box 1120", S, 600, 1120, 2)
# appliance garage: counter to top, 600 wide, 350 deep, rolling shutter in front
u = "T5 Appliance garage 600 (rolling shutter)"
GH = TOP_Z + TOP_H - CTR
add(u, "Carcass", "Side panel", C18, IN_LAM, 2, GH, TD, "0.5 mm, 1 long", f"stands on granite, {GH:.0f} high")
add(u, "Carcass", "Top / bottom panel", C18, IN_LAM, 2, 600 - 2 * T, TD, "0.5 mm, 1 long")
add(u, "Carcass", "Shelf", C18, IN_LAM, 2, 600 - 2 * T, TD - 26 - 40, "0.5 mm, 1 long", "set back for the rolling shutter")
add(u, "Back 6 mm", "Back panel", B6, IN_LAM + " 1S", 1, GH - 2 * T + 12, 600 - 2 * T + 12, "-", "in 6 mm groove")
hw("Rolling shutter (aluminium / PVC) 600 W x 2010 H with side tracks", 1)
Sg = S
put(Sg, "carcass", "side", 0, 0, CTR, T, TD, GH); put(Sg, "carcass", "side", 600 - T, 0, CTR, T, TD, GH)
put(Sg, "carcass", "tb", T, 0, CTR + GH - T, 600 - 2 * T, TD, T)
put(Sg, "back", "back", T, 0, CTR, 600 - 2 * T, BK, GH)
put(Sg, "rolling", "rolling shutter", 2, TD, CTR + 2, 596, 20, GH - 4)
# extras for the 3D: hob, sink bowl, window
parts.append({"kind": "hob", "name": "hob", "box": (MD + P + 1300, RY - 520, CTR, 700, 400, 8), "colour": None})
parts.append({"kind": "sink", "name": "sink", "box": (RX - 520, RY - MD - P - 600, CTR - 1, 420, 540, 3), "colour": None})
parts.append({"kind": "window", "name": "window", "box": (MD + 350, RY - 5, CTR + 120, 1700, 10, 900), "colour": None})

hw("Under-cabinet LED profile (top units)", 1)

json.dump({"rows": rows, "hardware": hardware, "room": [RX, RY], "ctr": CTR}, open(os.path.join(HERE, "kitchen_cutlist.json"), "w"), indent=1)
json.dump({"parts": parts, "room": [RX, RY, 3000.0]}, open(os.path.join(HERE, "kitchen_parts.json"), "w"), indent=1)
print("rows", len(rows), "pieces", sum(r[5] for r in rows), "parts", len(parts))
for r in rows:
    print(" ", r[0][:28].ljust(28), "|", r[1][:9].ljust(9), "|", r[2][:34].ljust(34), "|", r[4][:22].ljust(22), "|", r[5], "|", r[8], "x", r[9])
print(hardware)
