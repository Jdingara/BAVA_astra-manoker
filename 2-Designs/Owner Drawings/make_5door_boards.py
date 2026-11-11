"""5-door design: build new board geometry from the outer box of the 6-door drawing ("boards (6-door).json") -> boards.json.
Doors 2 + 1 + 2; full-height partitions sit behind the door joints (doors hinge on them).
Centre (1 door) = dressing: top at 750 (GF, 50 lower) / 800 from floor, 850 clear above, mirror + LED, shelf above.
Side sections = shelves 305 clear. 2 bottom drawers (173 / 182 openings): GF + 1F Master in the centre section,
1F Bedroom 2 + 2F in the right section (L-shape).
GF is wider than 2400 -> 2 boxes; the box joint (2 boards back to back) goes behind the door 3 | door 4 joint.
Loft = 90 frame: uprights behind the same 2 door joints."""
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
T = 18.0
GAP_END, GAP_JOINT = 3.0, 2.0
SP, TOP_SPACE = 305.0, 150.0         # shelf clear spacing, keep at least 150 under the top panel
DRESS_TOP = {"GF": 750.0, "1F Master": 800.0, "1F Bedroom 2": 800.0, "2F": 800.0}   # from floor
DRESS_OPEN = 850.0                   # clear space above the dressing top
DRAWER_SEC = {"GF": 1, "1F Master": 1, "1F Bedroom 2": 2, "2F": 2}                  # 0 left, 1 centre, 2 right
DRAWER_DIV = (191.0, 391.0)          # drawer divider boards above y_bot (openings 173 + 182, as before)
SPLIT = {"GF"}                       # 2 boxes side by side


def r1(v):
    return round(v, 1)


def build(name, d):
    hb = [tuple(b) for b in d["h"]]
    vb = [tuple(b) for b in d["v"]]
    x_min, x_max = min(b[0] for b in vb), max(b[0] + T for b in vb)
    W = x_max - x_min
    tall = max(b[2] - b[1] for b in vb)
    y_floor = min(b[1] for b in vb)
    y_top = max(b[2] for b in vb)
    y_bot = min(b[0] for b in hb)
    main_top = min(b[0] for b in hb if b[0] > y_bot + 1500 and b[2] - b[1] >= 0.6 * W)

    # door widths (all equal, whole mm) and the 2 joints the partitions sit behind
    dw = math.floor((W - 2 * GAP_END - 4 * GAP_JOINT) / 5)
    end = GAP_END + (W - 5 * dw - 2 * GAP_END - 4 * GAP_JOINT) / 2
    j1 = x_min + end + 2 * dw + GAP_JOINT / 2
    j2 = j1 + dw + GAP_JOINT

    # vertical boards: keep the 2 end sides; new partitions
    sides = [b for b in vb if b[2] - b[1] >= tall - 30 and (abs(b[0] - x_min) < 1 or abs(b[0] + T - x_max) < 1)]
    v = [list(b) for b in sides]
    loft_a = main_top + T                                   # loft uprights start on the cupboard top
    if name in SPLIT:                                       # box 1 right side + box 2 left side, full height
        s0, s1 = r1(j2 - T), r1(j2 + T)
        v += [[s0, y_floor, y_top], [r1(j2), y_floor, y_top]]
        v += [[r1(j1 - T / 2), y_bot + T, main_top], [r1(j1 - T / 2), loft_a, y_top]]
        parts = [r1(j1 - T / 2), s0]                        # left board of each joint
    else:
        s0 = s1 = None
        for j in (j1, j2):
            v += [[r1(j - T / 2), y_bot + T, main_top], [r1(j - T / 2), loft_a, y_top]]
        parts = [r1(j1 - T / 2), r1(j2 - T / 2)]

    # horizontal boards outside the cupboard inside (bottom, top, loft): same levels, re-split for GF boxes
    h = []
    levels = sorted({b[0] for b in hb if b[0] <= y_bot + 1 or b[0] >= main_top - 1})
    for y in levels:
        segs = [b for b in hb if b[0] == y]
        a, b = min(s[1] for s in segs), max(s[2] for s in segs)
        if s0 is not None and a < s0 and b > s1 and y < y_top - T - 1:     # GF: one board per box
            h += [[y, a, s0], [y, s1, b]]
        elif s0 is not None and a < s0 and b > s1:
            h += [[y, a, b]]
        else:
            h += [[y, a, b]]

    # sections (clear openings)
    pw = T * (2 if name in SPLIT else 1)
    sec_x = [(x_min + T, parts[0]), (parts[0] + T, parts[1]), (parts[1] + pw, x_max - T)]
    z0, z1 = y_bot + T, main_top                           # clear inside height
    secs = []
    dress = None
    for i, (xa, xb) in enumerate(sec_x):
        sh = []
        drawers = DRAWER_SEC[name] == i
        z = z0
        if drawers:
            sh += [y_bot + DRAWER_DIV[0], y_bot + DRAWER_DIV[1]]
            z = y_bot + DRAWER_DIV[1] + T
        if i == 1:                                          # dressing
            if not drawers:
                sh.append(y_floor + round((z0 - y_floor + DRESS_TOP[name] - T) / 2))
            dress = y_floor + DRESS_TOP[name]
            sh.append(dress)
            z = dress + T + DRESS_OPEN
            sh.append(z)
            z += T
        while z + SP + T <= z1 - TOP_SPACE:
            z += SP
            sh.append(z)
            z += T
        for y in sh:
            h.append([r1(y), r1(xa), r1(xb)])
        secs.append({"x": [r1(xa), r1(xb)], "clear": round(xb - xa), "shelves": [r1(y) for y in sh],
                     "drawers": drawers, "dressing": i == 1, "doors": 1 if i == 1 else 2})
    h.sort()
    v.sort()
    meta = {"door_w": dw, "end_gap": round(end, 1), "joints": [r1(j1), r1(j2)], "split": [s0, s1] if s0 else None,
            "dress_y": dress, "dress_open": DRESS_OPEN, "sections": secs, "y_floor": y_floor, "y_bot": y_bot,
            "main_top": main_top, "y_top": y_top, "x": [x_min, x_max]}
    return {"h": h, "v": v, "meta": meta}


if __name__ == "__main__":
    src = json.load(open(os.path.join(HERE, "boards (6-door).json")))
    out = {k: build(k, d) for k, d in src.items()}
    json.dump(out, open(os.path.join(HERE, "boards.json"), "w"), indent=1)
    for k, o in out.items():
        m = o["meta"]
        print(k, "door", m["door_w"], "end gap", m["end_gap"], "sections", [(s["clear"], len(s["shelves"])) for s in m["sections"]])
