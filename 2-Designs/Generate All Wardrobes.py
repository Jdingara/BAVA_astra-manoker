"""Astra Interiors - Mr. Manoker wardrobes. Edit sizes / colours / layout here and run:
    python "Generate All Wardrobes.py"
Each wardrobe gets its own folder with: AutoCAD 2D.dxf, Cut List.xlsx, data.json, Drawing.png, Drawing & Cut List.pdf
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from wardrobe_gen import build  # noqa: E402
from wardrobe_sheets import make_sheets  # noqa: E402

PAIR_LOFT_6 = [(0, 1, "L"), (1, 2, "R"), (2, 3, "L"), (3, 4, "R"), (4, 5, "L"), (5, 6, "R")]

WARDROBES = [
    dict(
        name="GF Bedroom Wardrobe", title="GF Bedroom", out=os.path.join(HERE, "GF Bedroom"),
        W=2564, H=2879, DT=450,
        colours={"A": "Sage green high-gloss acrylic", "B": "Fluted walnut wood"}, shades={"A": "#8fb2a6", "B": "#7f4626"},
        modules=6, bays=[(0, 2), (2, 4), (4, 6)],
        loft_doors=[(0, 1, "L", "A"), (1, 2, "R", "B"), (2, 3, "L", "A"), (3, 4, "R", "A"), (4, 5, "L", "B"), (5, 6, "R", "A")],
        main_doors=[(0, "A", "L", "R"), (1, "B", "R", "L"), (2, "A", "L", "R"), (3, "A", "R", "L"),
                    (4, "B", "L", "R"), (5, "A", "R", "L")],
        drawers=[(2, 4, "B", 2, 400)],
        inside=[dict(type="col_dressing"), dict(type="col_hang", drawers=(2, 4, 2, 400)), dict(type="col_shelves")],
    ),
    dict(
        name="1F Master Bedroom Wardrobe", title="1F Master Bedroom", out=os.path.join(HERE, "1F Master Bedroom"),
        W=2410, H=2900, DT=450,
        colours={"A": "27292 LV Mink", "B": "27262 LV Peacock"}, shades={"A": "#d9cdd2", "B": "#075f7f"},
        modules=6, bays=[(0, 2), (2, 4), (4, 6)],
        loft_doors=PAIR_LOFT_6,
        main_doors=[(0, "A", "L", "R"), (1, "B", "R", "L"), (2, "A", "L", "R"), (3, "A", "R", "L"),
                    (4, "B", "L", "R"), (5, "A", "R", "L")],
        drawers=[(2, 4, "B", 2, 400)],
        inside=[dict(type="col_dressing"), dict(type="col_hang", drawers=(2, 4, 2, 400)), dict(type="col_shelves")],
    ),
    dict(
        name="1F 2nd Bedroom Wardrobe", title="1F 2nd Bedroom", out=os.path.join(HERE, "1F 2nd Bedroom"),
        W=2335, H=2900, DT=450,
        colours={"A": "21433 SF Neo Banana Leaf", "B": "21457 SF Aspen Gold"}, shades={"A": "#035f33", "B": "#f7cd0b"},
        modules=6, bays=[(0, 2), (2, 4), (4, 6)],
        loft_doors=PAIR_LOFT_6,
        main_doors=[(0, "B", "L", "R"), (1, "B", "R", "L"), (2, "A", "L", "R"), (3, "A", "R", "L"),
                    (4, "B", "L", "R"), (5, "B", "R", "L")],
        drawers=[(0, 2, "B", 2, 400), (4, 6, "B", 2, 400)],
        inside=[dict(type="col_dressing", drawers=(0, 2, 2, 400)), dict(type="col_shelves"),
                dict(type="col_hang", drawers=(4, 6, 2, 400))],
    ),
    dict(
        name="2F Bedroom Wardrobe", title="2F Bedroom", out=os.path.join(HERE, "2F Bedroom"),
        W=2400, H=2828, DT=450,
        colours={"A": "21462 SF Lavendura", "B": "21452 SF Prism Violet"}, shades={"A": "#a994c7", "B": "#5c2568"},
        modules=6, bays=[(0, 2), (2, 4), (4, 6)],
        loft_doors=PAIR_LOFT_6,
        main_doors=[(0, "B", "L", "R"), (1, "B", "R", "L"), (2, "A", "L", "R"), (3, "A", "R", "L"),
                    (4, "B", "L", "R"), (5, "B", "R", "L")],
        drawers=[(0, 2, "B", 2, 400), (4, 6, "B", 2, 400)],
        inside=[dict(type="col_dressing", drawers=(0, 2, 2, 400)), dict(type="col_shelves"),
                dict(type="col_hang", drawers=(4, 6, 2, 400))],
    ),
]

if __name__ == "__main__":
    only = sys.argv[1:]
    for cfg in WARDROBES:
        if only and not any(o.lower() in cfg["name"].lower() for o in only):
            continue
        data = build(cfg)
        make_sheets(cfg["out"], data)
