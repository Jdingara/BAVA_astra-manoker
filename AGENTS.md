# AGENTS.md: Mr. Manoker interiors project (Astra Interiors)

This file is the **single source of truth** for any AI coding agent working in this repo: Claude Code, OpenAI Codex CLI, Gemini CLI, GitHub Copilot, Cursor, Windsurf, Aider and others.
Tool-specific files (`CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cursor/rules/`, `.windsurfrules`, `CONVENTIONS.md`) only point here.
For the full story of how the project evolved, see **`PROJECT_HISTORY.md`**.

---

## 1. What this project is

- **Business:** Astra Interiors, an interior designer and carpenter contractor.
  - Address: No 2, KVK Nagar, IAF Road, Selaiyur, Chennai 600073 · +91 97911 82789.
- **Customer:** Mr. Manoker (a villa). The work covers:
  1. **4 bedroom wardrobes**: GF Bedroom, 1st Floor Master Bedroom, 1st Floor Bedroom 2, 2nd Floor Bedroom.
  2. **Kitchen**: masonry U/G-shaped counter with 18 mm ply boxes inside the openings, plus top units.
  3. **Pooja unit**: a CNC-jali-door pooja cabinet.
  4. **Quotation** in Excel.
- **The owner (the user)** is the carpenter/contractor. He writes in **Tanglish** (Tamil in Latin script mixed with English), often in CAPS. Reply in **simple English with short Tamil-friendly sentences**. Explain sizes in tables. He sends photos and screenshots, and he works from his own AutoCAD drawing.
- **Outputs he needs:**
  - **factory** cut lists (panel-saw shop, grouped by board type)
  - **carpenter** lists and A4 printouts (grouped by bedroom, with 2D/3D)
  - **customer** PDFs (pictures only, colours shown)
  - laminate and plywood counts

## 2. Environment

- Windows 11 with Git Bash + PowerShell. Python 3.12 has: `ezdxf`, `openpyxl`, `python-docx`, `matplotlib`, `numpy`, `PIL`, `pymupdf` (`import pymupdf`).
- **Blender 5.2:** `C:/Program Files/Blender Foundation/Blender 5.2/blender.exe`, run headless with `-b -P script.py -- args`.
  - Renders on an RTX 3050 with **CUDA**. OptiX fails on driver 560.94; the "HIP" warning is harmless.
- **AutoCAD 2024** is installed. Read the open drawing through COM (`[Runtime.InteropServices.Marshal]::GetActiveObject("AutoCAD.Application")`) and **never modify the owner's drawing**: read only, or export a *copy*.
- **SketchUp 2025** is installed. Scripts are `.rb` builders the user loads by hand in the Ruby Console. The `-RubyStartup` switch is blocked by the welcome screen.
- **Excel / Word 2016** are available through COM, for PDF export and recalculation.
- **Files are often open in Excel/Word/PDF viewers on the user's PC.** Every generator therefore saves with a **lock fallback**:
  - first the normal name,
  - then `"(updated)"`,
  - then `"(HHMMSS)"`.
  - Always tell the user which file is the newest.
- Common bugs to avoid:
  - When patching Python through a shell heredoc, `"\n"` inside strings can turn into real newlines and break string literals. Prefer editing with a file-edit tool, or write the patch script to a file.
  - In openpyxl, `ws.append([])` does not move `max_row`. Use `ws._current_row` for row positions and page breaks.

## 3. Repository layout

```
Manoker/
├─ make_quotation.py                     -> Quotation - Mr. Manoker.xlsx (yellow cells editable, GST 18%)
├─ 2-Designs/
│  ├─ Owner Drawings/        ★ CURRENT wardrobe pipeline (from the owner's AutoCAD drawing)
│  ├─ Kitchen/               ★ CURRENT kitchen build + renders
│  ├─ Pooja/                 ★ CURRENT pooja unit
│  ├─ Unit 2060/             kitchen gas unit 2060x710x540 (earlier study, 600 / 21" basket variants)
│  ├─ GF Bedroom/, 1F Master Bedroom/, 1F 2nd Bedroom/, 2F Bedroom/   OLD generator outputs (superseded)
│  ├─ wardrobe_gen.py, wardrobe_sheets.py, blender_wardrobe.py, customer_pdf.py, combine_all.py,
│  │  Generate All Wardrobes.py          OLD parametric wardrobe generator (superseded by Owner Drawings)
└─ *.pdf / *.jpg at the root             OLD customer design PDFs (first concept; superseded)
```
Merino catalogue PDFs (`MerinoLam-Play-E-Catalogue-Latest.pdf`, `Merino Calplus 2025.pdf`) are kept locally but are **git-ignored**.

## 4. Wardrobes: `2-Designs/Owner Drawings/` (the main work)

### 4.1 Pipeline (run in this order after any change)
| Script | Reads → writes |
|---|---|
| `read_owner_dwg.py` | DXF copy of the owner's DWG → board pairs (two lines 18 mm apart = one board). Its `merge()`/`pair()` are reused. |
| `make_5door_boards.py` | `boards (6-door).json` (owner's drawing, hand-edited) → **`boards.json` = 5-door layout** (`h` = [y, x0, x1], `v` = [x, y0, y1] in AutoCAD mm, plus `meta`: door width, joints, sections, dressing, GF split). Run first after any inside change. |
| `render_5door_2d.py` | → `2D 5 doors - <room>.png`, `Mr. Manoker - 5 doors 2D drawing.pdf`, and `drawing_<room>.png` / `shutters_<room>.png` used by the carpenter files |
| `owner_cutlist.py` | `boards.json` → `Owner Drawings - Wardrobe Cut List (500 depth).xlsx` + **`owner_cutlist.json`** (rows, mats, hardware, info). **All rules live here.** |
| `check_all.py` | 97 automatic checks (widths, heights, gaps, shelves, backs, drawers, LED, laminates, factory = cut-list pieces). Run after every change. |
| `make_material_list.py` | → `Owner Drawings - Plywood and Laminate List.xlsx` |
| `make_final_excel.py` | → `Mr. Manoker - Wardrobe Cut List FINAL.xlsx` (Summary + room sheets + LED + ply/laminate) |
| `make_factory_excel.py` | → `Mr. Manoker - FACTORY Cut List*.xlsx` ("ALL - one page" sheet first, then one sheet per board type + LED groove) |
| `make_laminate_cutlist.py` | → `Mr. Manoker - Laminate List from Cut List*.xlsx` (face 1 / face 2 laminate per piece, MaxRects packing on 2440x1220) |
| `make_carpenter_excel.py` | → `Mr. Manoker - CARPENTER List*.xlsx` (by bedroom, "where / fitting" notes, 2D+3D pictures, page breaks) |
| `make_carpenter_a4.py` | → `Mr. Manoker - CARPENTER A4 Printout.docx/.pdf` (A4 portrait, readable) |
| `make_word_cutlist.py` | → `Mr. Manoker - Wardrobes Carpenter Pack (print).docx` (+ PDF via Word COM) |
| `render_gf.py`, `render_rooms.py` | 2D elevations `drawing_<room>.png` |
| `render_shutters.py` | `shutters_<room>.png` + `All Bedrooms - Laminate Shutters.png` (door colours + codes) |
| `render_pieces.py` | `Pieces - <room>.png` (every piece to scale, numbered as in Excel) |
| `make_sketchup.py` | `Owner Wardrobes - SketchUp Builder.rb` + `model_parts.json` |
| `blender_owner_model.py` | `3D - <room> - assembled (no doors).png`, `... - exploded pieces.png` |
| `blender_customer.py` | `Customer 3D - <room> - front / 3-4 view.png` (doors closed, colours) |
| `make_customer_pdf.py` | `Mr. Manoker - Wardrobes 3D (for customer).pdf` (6-door version) |
| `render_5door.py`, `render_5door_inside.py` | 5-door customer pictures (front + inside overview) |
| `make_party_pdf.py`, `make_picture_pdf.py` | customer PDFs of the 5-door design (+ kitchen page). Latest sent: `Mr. Manoker - 4 Bedrooms + Kitchen FINAL.pdf` |

### 4.2 Construction rules (agreed with the owner; do not change silently)
- **Board:** 18 mm ply; 6 mm ply for backs and drawer bottoms. **A piece can't be longer than 2400** (8x4 sheet = 2440 x 1220).
- **Cupboard box** is **2000 high** from the floor, with a **base of 80** (skirting zone). The **loft** above is a **90 mm frame only**: uprights + top/bottom rails, with no loft box and no loft back.
- **GF Bedroom** is wider than 2400, so it's built as **2 boxes side by side** (split at x 3156.3/3192.3), and the loft rails come in 2 pieces.
- **Depth:**
  - **500 for all 4 wardrobes**: sides, top, bottom and **full-height partitions** (doors hinge on them).
  - **Inside partitions** (dressing / bangle column): 494.
  - **Shelves:** 474 (set back 20).
- **Back panel:** 6 mm in a 6 mm groove all round; size = opening + 12. Each section has its own back, so full partitions get a groove on both faces.
- **Drawers:** only the **2 bottom drawers** per bedroom. Opening 173, **box 150 high**, **450 soft-close channel** (13 mm each side).
  - Drawer-bottom groove: **leave 12 mm from the bottom, 8 wide x 10 deep**.
  - Bottom = inside size + 9 per side (1 mm play).
  - No small drawer under the dressing top.
- **GF dressing top** was moved **50 lower**, and the inside partition there is 1444.
- **LED profile groove:** 12 W x 8 D, **100 mm from the front edge**, vertical, on the panel face inside each section.
  - It stops above the drawers: GF starts at 373; the other bedrooms start at 509 on the dressing section.
  - Drill a 10 mm wire hole through the top panel.
- **Edge band:** carcass gets 0.5 mm on the front edge (cut width −0.5); shutters get 2 mm on 4 sides (cut −4).
  - Side cover and 100 strip: **2 mm on the front edge only**.
  - Skirting: **0.5 mm on the top edge**.
- **Cut sizes are always whole mm, rounded DOWN** (`math.floor`), never ".5".
- **5 DOORS (current, confirmed 2026-11-11):** 2 + 1 + 2. Full partitions sit behind the 2 door joints. **Centre section = dressing** in all 4 rooms: top 750 from floor (GF) / 800 (others), 494 deep flush front, 850 clear above with mirror 700 high + LED, shelf above. Side sections: shelves 305 clear. Drawers: GF + 1F Master under the dressing (centre); 1F Bed 2 + 2F in the right section (L-shape). **Glass panel (90 border) in the centre door ONLY in GF**; other rooms plain centre door in the main colour. GF box joint (2 boards) behind the door 3|4 joint: box 1 1513, box 2 1013. Old 6-door layout kept in `boards (6-door).json`.
- **Shutters (old 6-door version, superseded):**
  - 2 doors per section, full overlay.
  - **Gaps:** 2 mm between doors · 3 mm+ next to the side cover / strip · 2 mm between the cupboard door and the loft door · 1 mm at the bottom and top.
  - All 6 doors are equal whole-mm widths, and the leftover goes into the end gaps.
  - Full door 1918 (cut 1914); door above the drawers 1518; loft door = loft − 2.
  - 2 drawer outside fronts, 198 high.
- **Side cover panel:** 518 deep (500 + door), full height, in 2 pieces joined at the 2000 door line. It goes on **ONE side only**: GF / 1F Master / 2F **left**, 1F Bed 2 **right**. The other end gets a **100 mm strip**, full height, in the same colour.
- **Skirting:** 80 high (cut 79), one piece per box.
- **Hinges:** a door over 1700 gets 5; a 1518 door gets 4; a loft door under 900 gets 2, otherwise 3.

### 4.3 Colours / laminates (latest)
| Room | Main | Accent (doors 2 & 6 + drawer fronts; L-shape in 1F Bed 2 / 2F uses door 5) |
|---|---|---|
| GF | **DC687 Foliage Blue (Advance)**, replaces 27173 LV Seaglass | **21125 MR+ Sunburn (Merino)** |
| 1F Master | 27292 LV Mink | 27262 LV Peacock |
| 1F Bedroom 2 | 21433 SF Neo Banana Leaf | 21457 SF Aspen Gold |
| 2F | 21462 SF Lavendura | 21452 SF Prism Violet |

- **Inside:** **no liner.** The shutter back and both faces of the carcass get **one WHITE laminate**. The code is **still to confirm**: 27121 LV Tulip / 27131 Coconut / 27181 Chalky / 21091 Frosty.
  - The older docs say "27111 LV Ivory White" and "backer", but the owner changed this.
- **Shades:** Advance DC687, 626 and 676 and Merino 10225 SF could **not be verified** online or in the local catalogue, so the renders use **approximate** shades and are labelled that way.
- **Latest laminate count** (from the cut list, MaxRects packing):
  - **colour 17 sheets** (main colours 3 each, Sunburn 2, accents 1)
  - **white ≈ 57**
- **Plywood:** 18 mm carcass 20–21, 18 mm shutters 16–17, 6 mm 8–9 (about 45–46 sheets).

### 4.4 Pending wardrobe decisions
- 5-door cut list, factory, laminate and carpenter files are done (check_all: 121 checks). The A4 / Word packs are .docx only on the Mac (no Word for PDF).
- GF side shelves are 977–982 wide: may need a centre support.
- White laminate code.
- Handle type: the pictures are handleless (G-profile, push-to-open or handles?).
- Glass type (clear / frosted / tinted / mirror).

## 5. Kitchen: `2-Designs/Kitchen/`
- `kitchen_build.py` defines **every unit and piece** and writes `kitchen_cutlist.json` + `kitchen_parts.json` (3D boxes).
- `blender_kitchen.py -- <samples> ["code:#hex" "suffix"] [--corner]` renders 3 views, an optional top-colour override, and a corner close-up.
- `kitchen_plan.py` draws the plan; `kitchen_elevations.py` draws the wall elevations (older, approximate).
- Colour studies:
  - `kitchen_bottom_options.py` recolours the TOP units of the reference renders.
  - `kitchen_advance_colours.py` applies Advance 626 / 676 to the reference renders.
- **Site:**
  - Masonry openings **710 high**, concrete slab 110, granite → **counter 847**. **Pillars 110.**
  - Boxes are **540 deep** inside the openings (opening depth about 550); **21" baskets** (533 + 24 channel → 557 column).
  - The right corner is a **single L-pillar** (110 + 110); under the sink there are 2 pillars, one each side. The granite corner is one continuous joint.
- **Layout (room schematic 3420 x 3350):**
  - **Window wall:** gas unit 2080 = 3 pull-outs (4/6/8") + 2 pull-outs (8"+8") + gas cylinder 2 doors (890). **No top unit.**
  - **Right wall:** sink 668 (**frame + 2 doors, no box**). **Top 1420** runs from the wall over the sink.
  - **Left wall:** 1050 = 3 pull-outs + door/shelf 435. **Top 3000** (2 boxes of 1500), then the **appliance garage 600 with a rolling shutter** in the corner (counter to 2857).
  - **Entrance wall:** **1490 opening from the corner** = **Ebco Magic Corner, RIGHT-hand, 900 box / 450 door** (blind 465 in the corner) + 3 wicker baskets 536. **Top box 1120** after the garage.
  - **Top units:** 350 deep, 1410 high, **1447–2857** from the floor (600 above the counter).
- **Handles:**
  - **Bottom:** aluminium G/J **profile handle** on the top edge of every front (front 20 shorter, `PROF=20`).
  - **Top:** handleless, with the door hanging **25 below** the box (`DROP=25`).
- **Colours:**
  - Bottom first 27183 LV Camouflage, top option chosen 27111 LV Ivory White (Mink / Hazel shown too).
  - **Latest customer pictures use Advance 626 Dream Green (bottom) + 676 Aqua Green (top).**
- **Pending:** confirm the final codes; the empty left-wall corner leg (about 960x560x710, open or frame + 2 doors); profile height; the kitchen cut list Excel / carpenter files ("cut list later").

## 6. Pooja unit: `2-Designs/Pooja/`
- `pooja_2d.py` → `Pooja unit - 2D drawing.png/.pdf`; `pooja_textures.py` → door textures; `blender_pooja.py` → `Pooja 3D - front/angle.png`.
- Final PDF: `Mr. Manoker - Pooja unit 3D + 2D.pdf`.
- **Size:** 1040 W x 2720 H x 405 D, laminate **10225 SF Merino**. **Side colour panel on the RIGHT.**
- **From the floor:**
  - skirting 80
  - 2 plain doors 80–760 (storage)
  - **2 CNC jali doors 760–1905** (bells+chains, Ganesha trunk, lotus) with an **LED behind** them. They hide a **90 pull-out shelf (760–850)** and the **pooja niche 1055**
  - **5 kalasam band 1905–2133** (kalasam 100 deep at the front)
  - **top unit 2 doors 2133–2720, 305 deep**, set behind the kalasams
- **Pending:** the pooja cut list.

## 7. How to work here (rules for agents)
1. **Never edit the owner's AutoCAD drawing.** Read through COM, or open a copy.
2. **After any wardrobe rule change:**
   - run `owner_cutlist.py` → `check_all.py` (it must say FAILED 0)
   - then regenerate the Excel and PDF outputs he asked for
   - report which file is newest
3. Keep cut sizes **whole mm (floor)**, keep pieces **≤ 2400**, and keep the edge-band rules above.
4. **Laminate codes:** never invent a code or shade. Look codes up in the Merino catalogue (page 17 = LV series). If a code isn't found, say so and use a clearly labelled approximate colour.
5. **Ask when the request is ambiguous** (Tanglish can be read two ways), and confirm with a drawing or picture before you rebuild cut lists.
6. **Don't install pirated software.** GetIntoPC / cracked V-Ray / Enscape requests were refused; offer Blender, D5 Render free, SketchUp, or Blender done by the agent.
7. **Customer data:** the repo must stay **private**. Don't push the catalogues.
8. **Commits:** author "Astra Interiors". Push to `origin main` (https://github.com/Jdingara/BAVA_astra-manoker).
