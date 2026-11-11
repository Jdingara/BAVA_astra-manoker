import json, glob, os
from openpyxl import load_workbook
import owner_cutlist as oc
B = json.load(open("boards.json")); D = json.load(open("owner_cutlist.json"))
oc_dress = {"GF": 750, "1F Master": 800, "1F Bedroom 2": 800, "2F": 800}   # owner: GF 50 lower
T = 18.0
ok = []; bad = []
def chk(cond, msg): (ok if cond else bad).append(msg)
for room, v in D.items():
    rows = v["rows"]; inf = v["info"]
    hb = [tuple(b) for b in B[room]["h"]]; vb = [tuple(b) for b in B[room]["v"]]
    y_floor = min(b[1] for b in vb); tall_top = max(b[2] for b in vb)
    x_min = min(b[0] for b in vb); x_max = max(b[0] + T for b in vb); W = x_max - x_min
    y_bot = min(b[0] for b in hb)
    main_top = B[room]["meta"]["main_top"]
    f_top = main_top + T
    R = lambda key: [r for r in rows if key in r[1]]
    # 1 cut sizes whole, sheet limits
    chk(all(r[6] == int(r[6]) and r[7] == int(r[7]) for r in rows), f"{room}: all cut sizes whole numbers")
    chk(all(max(r[6], r[7]) <= 2400 and min(r[6], r[7]) <= 1220 for r in rows), f"{room}: every piece fits 8x4 sheet (<=2400 x 1220)")
    # 2 heights: box 2000, door 1918, loft door, skirting, cover
    chk(round(f_top - y_floor) == 2000, f"{room}: cupboard box height 2000 (floor to top of top panel)")
    chk(all(r[4] == 1918 for r in R("Door (full height)")), f"{room}: full door 1918 = 1920 - 1 bottom - 1 (half of 2 mm to loft door)")
    chk(round(f_top - y_bot) == 1920, f"{room}: door opening 1920 (bottom panel to top)")
    sk = R("Skirting")[0]; chk(sk[5] == 80 and round(y_bot - y_floor) == 80, f"{room}: skirting 80 = base 80")
    ld = R("Loft door")[0]; chk(abs(ld[4] - (tall_top - f_top - 2)) < 0.01, f"{room}: loft door {ld[4]} = loft {tall_top - f_top:.0f} - 1 - 1")
    cv = R("Side cover panel"); st = R("Wall-side strip 100")
    chk(abs(sum(r[4] for r in cv) - (tall_top - y_floor)) < 0.6 and all(r[5] == 518 and r[7] == 516 for r in cv), f"{room}: side cover lower+upper = full height {tall_top - y_floor:.0f}, depth 518")
    chk(abs(sum(r[4] for r in st) - (tall_top - y_floor)) < 0.6 and all(r[5] == 100 for r in st), f"{room}: 100 strip = full height")
    # 3 widths: doors + gaps = front width
    n_doors = sum(r[3] for r in R("Door (full height)") + R("Door above drawers"))
    chk(n_doors == 5, f"{room}: 5 cupboard doors (2 + 1 + 2)")
    chk(sum(r[3] for r in R("Loft door")) == 5, f"{room}: 5 loft doors")
    dw = R("Door (full height)")[0][5]
    chk(0 <= W - (5 * dw + 2 * 3 + 4 * 2) < 5, f"{room}: 5 doors x {dw} + 2 x 3 end + 4 x 2 joints = {5 * dw + 14:.0f} <= front {W:.0f} (extra {W - 5 * dw - 14:.0f} mm goes to the end gaps)")
    m = B[room]["meta"]
    eg = m["end_gap"]
    for k_, jx in enumerate(m["joints"], 1):                     # a full partition must be behind each door joint
        chk(any(x - 0.5 <= jx <= x + T + 0.5 or (m["split"] and m["split"][0] - 0.5 <= jx <= m["split"][1] + 0.5)
                for x, a, b in vb if b - a >= 1800), f"{room}: partition behind door joint {k_} (x {jx})")
    # 5-door: dressing in centre, glass only GF
    dt = R("Dressing top")
    chk(len(dt) == 1 and dt[0][3] == 1 and abs(dt[0][4] - m["sections"][1]["clear"]) < 1 and dt[0][5] == inf["depth"] - 6,
        f"{room}: 1 dressing top in centre section ({m['sections'][1]['clear']} x {inf['depth'] - 6:.0f})")
    chk(round(m["dress_y"] - y_floor) == oc_dress[room], f"{room}: dressing top {m['dress_y'] - y_floor:.0f} from floor")
    gl = [r for r in rows if "GLASS" in r[1]]
    chk((len(gl) == 1) == (room in oc.GLASS_ROOMS), f"{room}: glass centre door {'yes' if room in oc.GLASS_ROOMS else 'no'}")
    hs = m["sections"][0]
    chk(hs.get("hanging") and round(hs["shelves"][1] - hs["shelves"][0] - T) == 1200 and round(hs["rod_y"] - y_floor) == 1609,
        f"{room}: coat stand left section, 1200 hanging, rod 1609 from floor")
    # 4 shelves & backs
    bk = [r for r in R("Main back panel") for _ in range(r[3])]
    chk(abs(sum(r[5] for r in bk) - W) < 0.6, f"{room}: back panels outer to outer, widths {[r[5] for r in bk]} add up to {W:.0f}")
    chk(all(r[4] == 2000 and r[5] <= 1220 for r in bk), f"{room}: back panels 2000 high, each <= 1220 wide")
    shelves = R("Shelf"); chk(all(r[5] == inf["depth"] - 26 for r in shelves), f"{room}: shelves {inf['depth'] - 26:.0f} deep (500 - 6 back - 20 set back)")
    sh_ok = all(any(abs(r[4] - (b - a)) < 1 for y, a, b in hb) for r in shelves)
    chk(sh_ok, f"{room}: every shelf length matches the drawing")
    chk(all(r[5] == 494 for r in R("Side panel (cupboard") + R("Partition (full") + R("Bottom panel") + R("Top panel")), f"{room}: sides/top/bottom/full partitions 494 (+ 6 back = 500)")
    # 5 drawers
    x1, x2, n, dh, lab = oc.DRAWERS[room][0]; op = x2 - x1
    side = R("drawer side")[0]; inner = R("front/back inner")[0]; bot = R("drawer bottom")[0]
    chk(side[4] == 450 and side[5] == 150, f"{room}: drawer side 450 x 150 (450 channel)")
    chk(abs(inner[4] - (op - 26 - 36)) < 0.6, f"{room}: drawer inner {inner[4]} = opening {op:.0f} - 26 channel - 36 sides")
    chk(abs(bot[5] - (inner[4] + 18)) < 0.6 and bot[4] == 450 - 36 + 18, f"{room}: drawer bottom {bot[4]} x {bot[5]} = inside + 9 each side")
    df = R("Drawer outside front")[0]; chk(df[3] == 2 and df[5] == 198, f"{room}: 2 drawer fronts, 198 high")
    # 6 LED
    chk(all(g["length"] + g["start"] == 1884 for g in inf["led"]), f"{room}: LED grooves end at top panel (start + length = 1884)")
    # 7 laminate codes
    codes = {r[1].rsplit(" - ", 1)[1].split()[0] for r in rows if r[0] == "Shutters"}
    chk(len(codes) == 2, f"{room}: shutters use exactly 2 laminate codes {sorted(codes)}")
    # 8 loft frame
    up = R("Frame upright")[0]; chk(up[3] == 4 and abs(up[4] - (tall_top - f_top)) < 0.6, f"{room}: 4 loft uprights x {up[4]:.0f}")
# factory excel vs cut list
f = sorted(glob.glob("Mr. Manoker - FACTORY Cut List*.xlsx"), key=os.path.getmtime)[-1]
wb = load_workbook(f, data_only=True)
tot = 0
for ws in wb.worksheets[1:]:
    if ws.title == "LED groove": continue
    tot += sum(r[5] for r in ws.iter_rows(min_row=3, values_only=True) if isinstance(r[0], int))
cl = sum(r[3] for v in D.values() for r in v["rows"])
chk(tot == cl, f"factory Excel ({os.path.basename(f)}) pieces {tot} = cut list pieces {cl}")
print("PASSED", len(ok)); [print("  ok ", m) for m in ok]
print("FAILED", len(bad)); [print("  XX ", m) for m in bad]
