"""Read the owner's AutoCAD wardrobe drawings (DXF exported from 'manoker  bedroom 2d model.dwg') and list every
18 mm board: each board is drawn as two parallel lines 18 mm apart. Prints boards per wardrobe region."""
import json
import sys

import ezdxf

T = 18.0
TOL = 1.2


def lines_in(msp, x0, x1):
    H, V = [], []
    for e in msp.query("LINE"):
        s, t = e.dxf.start, e.dxf.end
        if not (x0 <= min(s.x, t.x) <= x1):
            continue
        if abs(s.y - t.y) < 0.5:
            H.append([round(s.y, 1), round(min(s.x, t.x), 1), round(max(s.x, t.x), 1)])
        elif abs(s.x - t.x) < 0.5:
            V.append([round(s.x, 1), round(min(s.y, t.y), 1), round(max(s.y, t.y), 1)])
    return H, V


def merge(segs, gap=19.0):
    """Join collinear segments on the same line that touch or nearly touch (a crossing board splits a line)."""
    out = []
    for pos, a, b in sorted(segs):
        if out and abs(out[-1][0] - pos) < 0.2 and a <= out[-1][2] + gap:
            out[-1][2] = max(out[-1][2], b)
        else:
            out.append([pos, a, b])
    return out


def pair(segs):
    """Greedy: each line pairs with the nearest line 18 mm above/right that overlaps it -> a board."""
    segs = sorted(segs)
    used = [False] * len(segs)
    boards = []
    for i, (p, a, b) in enumerate(segs):
        if used[i]:
            continue
        for j in range(i + 1, len(segs)):
            q, c, d = segs[j]
            if used[j] or abs(q - p - T) > TOL:
                continue
            lo, hi = max(a, c), min(b, d)
            if hi - lo > 40:
                boards.append((p, lo, hi))
                used[i] = used[j] = True
                break
    # second pass: two boards touching share one drawn line (e.g. back-to-back sides, loft bottom on main top)
    for i, (p, a, b) in enumerate(segs):
        if used[i]:
            continue
        for j, (q, c, d) in enumerate(segs):
            if j == i or abs(abs(q - p) - T) > TOL:
                continue
            lo, hi = max(a, c), min(b, d)
            if hi - lo > 40:
                boards.append((min(p, q), lo, hi))
                used[i] = True
                break
    return boards


if __name__ == "__main__":
    doc = ezdxf.readfile(sys.argv[1])
    msp = doc.modelspace()
    regions = json.loads(sys.argv[2])
    out = {}
    for name, (x0, x1) in regions.items():
        H, V = lines_in(msp, x0, x1)
        hb = pair(merge(H))
        vb = pair(merge(V))
        out[name] = {"h": hb, "v": vb}
        print(f"== {name}: {len(hb)} horizontal, {len(vb)} vertical boards")
        for y, a, b in sorted(hb):
            print(f"   H y={y:7.1f}  x {a:7.1f}..{b:7.1f}  L={b - a:6.1f}")
        for x, a, b in sorted(vb):
            print(f"   V x={x:7.1f}  y {a:7.1f}..{b:7.1f}  L={b - a:6.1f}")
    json.dump(out, open(sys.argv[3], "w"), indent=1)
