# PROJECT_HISTORY.md: what happened, in order

This is a chronological record of the Mr. Manoker project as it was worked out with an AI assistant (Claude Code) for Astra Interiors.
Read it to understand **why** things are the way they are. For the current rules and how to run things, read **`AGENTS.md`**.

---

## Phase 0: background (other Astra work, outside this repo)
- The Astra Interiors website (`C:\Users\Home\Chennai Style`) and a Flutter Android app (`E:\dev\astra_interiors_app`) were built earlier.
- They aren't part of this repo.

## Phase 1: first wardrobe concepts (OLD, superseded)
- Built 4 wardrobes, one per bedroom, each with its own design taken from a reference picture.
- The tools were a parametric generator (`2-Designs/wardrobe_gen.py`, `Generate All Wardrobes.py`), DXF, a carpenter PDF, Blender renders and customer PDFs (`*Design for Mr. Manoker.pdf`, `All Wardrobes - Mr. Manoker.pdf`).
- **The common inside model was:**
  - a dressing unit (table at 800, slim drawer, mirror + LED, bangle column)
  - a coat-stand unit
  - a full-shelves unit
- **The first colour codes were:**
  - GF: sage + fluted walnut
  - 1F Master: 27292 LV Mink + 27262 LV Peacock
  - 1F Bed 2: 21433 SF Banana Leaf + 21457 SF Aspen Gold
  - 2F: 21462 SF Lavendura + 21452 SF Prism Violet
- The quotation Excel was built with `make_quotation.py`. Term 7 says extra accessories are charged.

## Phase 2: kitchen gas unit study (`2-Designs/Unit 2060`)
- The gas unit is 2060 x 710 x 540, with basket sections of 600 + 24 channel and a **21" variant** (533 + 24). The rest of the width is gas doors.
- The output was a 2D plan plus a cut list in 18 mm ply with a 6 mm back.

## Phase 3: switch to the OWNER'S OWN AutoCAD drawing (`2-Designs/Owner Drawings`)
1. The owner sent his own AutoCAD drawing of all 4 wardrobes and asked for a cut list with 6 mm backs (in a groove) and an LED strip groove.
2. A DXF copy was read and boards were detected as pairs of lines 18 mm apart (`read_owner_dwg.py`). This produced `boards.json`.
3. **Rules he gave, one after another:**
   - depth 18" (457)
   - **GF is wider than 2400, so it's 2 boxes**, cupboard up to **2000**, loft above
   - **loft = 90 mm frame only**
   - Word printouts with the 2D drawing
4. A SketchUp builder (`.rb`) was made. SketchUp can't be auto-started (welcome screen), so the owner loads it in the Ruby Console.
5. A request to install pirated software (GetIntoPC / KD Max) was **refused**. Legal options were given instead.
6. **GF depth became 500**, and later **all 4 wardrobes went to 500**.
7. The owner updated GF in AutoCAD, and the GF boards were re-read live through **COM** from the open drawing. His file isn't modified.
8. **Small-drawer / dressing changes:**
   - First, a "50 mm less" request was read as the GF dressing top going 50 lower.
   - The small drawer was kept at 144 inside by also lowering the shelf below it. The inside partition went 1394 → 1444.
   - Many back-and-forth messages followed about the other 3 rooms.
   - **Final:** only the **2 bottom drawers** in every room, opening 173, **box 150**. Drawer-bottom groove: leave 12, then 8 wide x **10 deep**.
9. **Full-height partitions are 500** (doors hinge on them); inside partitions are 494.
10. **LED profile groove** schedule added. It moved from 30 mm to **100 mm from the front**.
11. **Shutters added:**
    - 6 doors per room, full overlay.
    - In the drawer section, doors sit only above the drawers, and the drawers get outside fronts.
    - **6 loft doors + skirting**.
    - Door colours were taken from the owner's 4 reference pictures.
12. **1F Bedroom 2 and 2F:** the owner's pictures put the drawers on the **right section**, forming an "L-shape". The inside (drawers + dressing + bangle column) was **swapped to the right section** in `boards.json`. Later the L was made a proper "L" by moving the accent from door 6 to door 5.
13. The owner gave the **final Merino codes** (see AGENTS.md). Inside: **off-white**, then later **"no liner, all white"**.
14. **Side cover panel:**
    - 518 deep (box + door), full height, in 2 pieces at the door line, on **one side only**.
    - The other side gets a **100 mm strip** in the same colour.
15. **Finishing rules added:**
    - cut sizes **rounded down to whole mm**
    - skirting **80** with **0.5 tape on top**
    - door height = **1920 − 1 − 1 = 1918**
    - then gaps: **2 between doors, 3 next to the side cover, 2 between the cupboard and loft doors, 1 at the bottom and top**
    - side cover / strip get **2 mm tape on the front edge only**
16. **Verification:** `check_all.py` runs 97 checks. All passed.
17. **Deliverables made:**
    - factory Excel: one sheet per board, plus "ALL – one page"
    - carpenter Excel with pictures, and the carpenter A4 printout
    - Word pack, pieces sheets, 3D (assembled / exploded / customer)
    - plywood and laminate lists
18. **Laminate counts:** the first packing gave 4 sheets per main colour. The owner challenged it, so a **MaxRects** packer was added, and the result is **3 sheets** per main colour (total colour 17).
19. **Latest design study (pictures only):**
    - **5 doors** per wardrobe, with the centre door carrying a **glass panel inside a 90 mm laminate border**.
    - Inside: shelves 305 apart, no dressing table.
    - **GF colours changed to Advance DC687 Foliage Blue + Merino 21125 MR+ Sunburn.**
    - Customer PDFs were sent: `Mr. Manoker - 4 Bedrooms + Kitchen FINAL.pdf`. **The cut list hasn't been redone for 5 doors yet.**

## Phase 4: kitchen (`2-Designs/Kitchen`)
1. **Site photos:** a masonry counter with openings. Measurements came in step by step:
   - opening 710 high, slab 110, counter 847, pillars 110
   - sink 668 (frame + 2 doors), opposite 2080 (pull-outs + gas), left 1050, corner 1490
2. **Units:**
   - 21" baskets, box depth 540
   - 3 pull-outs (4/6/8") + 2 pull-outs in the 2080
   - 3 pull-outs + door/shelf in the 1050
   - **Ebco Magic Corner, right-hand, 900 box / 450 door, sitting in the corner** + 3 wicker in the 1490
3. **Top units:** 350 deep, 1410 high, 600 above the counter (1447–2857).
   - Right top 1420 runs from the wall over the sink.
   - Left top 3000, then an **appliance garage 600 with a rolling shutter** in the corner.
   - Entrance-wall box 1120. No top unit on the window wall.
4. **Colours:**
   - The bottom started as 27183 LV Camouflage. A contrast was wanted for the **top unit**: options Ivory White / Stone / Antique Walnut / Hazel → Ivory White chosen → the customer then asked for 27292 Mink / 27184 Hazel.
   - Later, **Advance 626 Dream Green (bottom) + 676 Aqua Green (top)** were applied to the reference renders for the customer.
5. **Handles:** bottom gets a profile handle on top of each front; top units are handleless with the door hanging 25 below the box.
6. The right corner was corrected to a single L-pillar, with one granite joint.
7. **Pending:** the final kitchen cut list / factory / carpenter files.

## Phase 5: pooja unit (`2-Designs/Pooja`)
- 1040 x 2720 x 405, Merino 10225 SF.
- 2 plain doors at the bottom; **CNC jali doors (covering the pull-out + niche) with LED behind**.
- **5 kalasams** (100 deep) in front of a dummy box; **top unit 305 deep**; side panel on the right.
- Outputs: a 2D drawing (front closed, front open, side section), a 3D render, and a combined PDF.

## Phase 6: repository
- Pushed to **https://github.com/Jdingara/BAVA_astra-manoker** (keep it private).
- Merino catalogues and older duplicate files are git-ignored.
- These markdown docs were added so that any AI CLI can continue the work.
