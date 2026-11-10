# Mr. Manoker – Interiors (Astra Interiors, Chennai)

Design, cut lists, factory files and 3D for **Mr. Manoker's villa**:
**4 bedroom wardrobes · kitchen · pooja unit · quotation.**

| Need | Open |
|---|---|
| Send to the customer | `2-Designs/Owner Drawings/Mr. Manoker - 4 Bedrooms + Kitchen FINAL.pdf`, `2-Designs/Pooja/Mr. Manoker - Pooja unit 3D + 2D.pdf` |
| Send to the factory (panel saw) | `2-Designs/Owner Drawings/Mr. Manoker - FACTORY Cut List (latest timestamp).xlsx` (first sheet "ALL - one page") |
| Give to the carpenter | `2-Designs/Owner Drawings/Mr. Manoker - CARPENTER A4 Printout.pdf`, `Mr. Manoker - Wardrobes Carpenter Pack (final).pdf` |
| Plywood / laminate to buy | `2-Designs/Owner Drawings/Mr. Manoker - Laminate List from Cut List (latest).xlsx`, `Owner Drawings - Plywood and Laminate List.xlsx` |
| Quotation | `Quotation - Mr. Manoker (updated).xlsx` |

> The wardrobe cut list and factory files are the **6-door** version. The **5-door + glass-panel** design exists as pictures only, until the owner confirms it.

## Folders
- `2-Designs/Owner Drawings/`: **current wardrobe work** (from the owner's AutoCAD drawing)
- `2-Designs/Kitchen/`: kitchen build, plan, renders, colour options
- `2-Designs/Pooja/`: pooja unit 2D / 3D
- `2-Designs/Unit 2060/`: earlier kitchen gas-unit study
- `2-Designs/GF Bedroom` … `2F Bedroom`, root `*.pdf`: **old first concepts** (superseded)

## For AI agents / developers
- **`AGENTS.md`** holds all rules, the pipeline, how to regenerate, and pending decisions. Read this first.
- **`PROJECT_HISTORY.md`** is the full story of what happened and why.
- Tool pointers: `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, `.cursor/rules/project.mdc`, `.windsurfrules`, `CONVENTIONS.md`.

**Quick regenerate (wardrobes):**
```bash
cd "2-Designs/Owner Drawings"
python owner_cutlist.py && python check_all.py        # must report FAILED 0
python make_material_list.py && python make_final_excel.py && python make_factory_excel.py
python make_laminate_cutlist.py && python make_carpenter_excel.py && python make_carpenter_a4.py
```
Requirements: Python 3.12 with ezdxf, openpyxl, python-docx, matplotlib, numpy, pillow, pymupdf. Blender 5.2 is needed for the 3D.

---
Astra Interiors · No 2, KVK Nagar, IAF Road, Selaiyur, Chennai 600073 · +91 97911 82789
