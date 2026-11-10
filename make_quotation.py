"""Editable Excel quotation for Mr. Manoker (Astra Interiors). Yellow cells = type your values; totals calculate automatically."""
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.worksheet.datavalidation import DataValidation

OUT = r"C:\Users\Home\Manoker\Quotation - Mr. Manoker.xlsx"
INK, GOLD, CREAM, INPUT = "1F1A17", "C9A46A", "F7F2EB", "FFF4C2"
thin = Side(style="thin", color="D9CFC2")
box = Border(left=thin, right=thin, top=thin, bottom=thin)
inp = PatternFill("solid", fgColor=INPUT)
head = PatternFill("solid", fgColor=INK)
sect = PatternFill("solid", fgColor=CREAM)

wb = Workbook()
ws = wb.active
ws.title = "Quotation"
widths = {"A": 5, "B": 30, "C": 44, "D": 10, "E": 10, "F": 10, "G": 9, "H": 12, "I": 15}
for k, v in widths.items():
    ws.column_dimensions[k].width = v

# ---------------- letterhead
ws.merge_cells("A1:F1")
ws["A1"] = "ASTRA INTERIORS"
ws["A1"].font = Font(size=22, bold=True, color=GOLD)
ws.merge_cells("A2:F2")
ws["A2"] = "Modular Kitchens · Wardrobes · Pooja · TV Units · False Ceiling · Mosquito Nets · Aluminium & UPVC"
ws["A2"].font = Font(size=9, color="6F655C")
for r, t in enumerate(["No 2, KVK Nagar, IAF Road, Selaiyur, Chennai 600073",
                       "Mob: +91 97911 82789  |  chennaistyle1@gmail.com", "Contact: Vengatachalam"], start=1):
    ws.merge_cells(f"G{r}:I{r}")
    c = ws[f"G{r}"]
    c.value = t
    c.alignment = Alignment(horizontal="right")
    c.font = Font(size=9, color="3A322C")
for col in "ABCDEFGHI":
    ws[f"{col}4"].border = Border(bottom=Side(style="medium", color=GOLD))

ws.merge_cells("A5:I5")
ws["A5"] = "QUOTATION"
ws["A5"].font = Font(size=18, bold=True, color=INK)
ws["A5"].alignment = Alignment(horizontal="center")

# ---------------- customer / quote details (yellow = editable)
details = [
    ("B7", "Customer", "C7", "Mr. Manoker"), ("B8", "Mobile", "C8", ""), ("B9", "Site address", "C9", ""),
    ("G7", "Quote No.", "H7", "AI/2026/001"), ("G8", "Date", "H8", "=TODAY()"), ("G9", "Valid for", "H9", "15 days"),
]
for lc, lab, vc, val in details:
    ws[lc] = lab
    ws[lc].font = Font(bold=True, color="6F655C")
    ws[vc] = val
    ws[vc].fill = inp
    ws[vc].border = box
ws.merge_cells("H7:I7")
ws.merge_cells("H8:I8")
ws.merge_cells("H9:I9")
ws["H8"].number_format = "DD-MM-YYYY"
ws["H8"].alignment = Alignment(horizontal="left")

# ---------------- item table
HR = 11
hdr = ["#", "Item", "Description / specification", "Width (mm)", "Height (mm)", "Qty", "Unit", "Rate (₹)", "Amount (₹)"]
for i, h in enumerate(hdr):
    c = ws.cell(row=HR, column=i + 1, value=h)
    c.font = Font(bold=True, color="FFFFFF")
    c.fill = head
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    c.border = box
ws.row_dimensions[HR].height = 30

SPEC = "18 mm ply (16 mm + 1 mm laminate + 0.8 mm backer), 2 mm edge band on doors, soft-close hinges & channels, gold bar handles"
rows = [
    ("SECTION", "GF Bedroom wardrobe"),
    ("AREA", "Wardrobe with loft (6 doors)", f"Sage green high-gloss acrylic + fluted walnut. {SPEC}", 2564, 2879),
    ("SECTION", "1F Master Bedroom wardrobe"),
    ("AREA", "Wardrobe with loft (6 doors)", f"Merino 27292 LV Mink + 27262 LV Peacock. {SPEC}", 2410, 2900),
    ("SECTION", "1F 2nd Bedroom wardrobe"),
    ("AREA", "Wardrobe with loft (6 doors)", f"Merino 21433 SF Neo Banana Leaf + 21457 SF Aspen Gold. {SPEC}", 2335, 2900),
    ("SECTION", "2F Bedroom wardrobe"),
    ("AREA", "Wardrobe with loft (6 doors)", f"Merino 21462 SF Lavendura + 21452 SF Prism Violet. {SPEC}", 2400, 2828),
    ("SECTION", "Wardrobe inside fittings (all 4 wardrobes)"),
    ("QTY", "Inside dressing unit", "Table top, slim drawer, 5 mm mirror with LED light + door sensor, glass shelves", 4, "nos"),
    ("QTY", "Bangle & perfume shelf column", "300 mm column with shelves beside dressing table", 4, "nos"),
    ("QTY", "Drawers (soft-close)", "Telescopic soft-close channels, 350 mm", 20, "nos"),
    ("QTY", "Coat hanging rod", "Rod with end supports", 4, "nos"),
    ("SECTION", "Kitchen (bottom units under granite) – Merino 27183 LV Camouflage"),
    ("RFT", "Kitchen bottom units", "Shutters & drawers inside 806 H × 714 D opening between pillars (left 2228 + window 2207 + right 675 + entrance 1411)", 6521, None),
    ("QTY", "Sink unit with bin pull-out", "Under sink, right side", 1, "nos"),
    ("QTY", "Cutlery / plate / cup baskets", "Stainless steel pull-out baskets", 3, "set"),
    ("QTY", "Corner carousel / magic corner", "Open corner of the U", 1, "nos"),
    ("QTY", "Hob / gas unit", "Drawers or cylinder space under the stove", 1, "nos"),
    ("SECTION", "Kitchen top boxes – Merino 27173 LV Seaglass (no boxes on window wall)"),
    ("AREA", "Top box – left wall", "1442 H × 350 D", 3359, 1442),
    ("AREA", "Top box – right wall", "1442 H × 350 D", 1531, 1442),
    ("AREA", "Top box – back wall", "1442 H × 350 D", 1728, 1442),
    ("SECTION", "TV unit"),
    ("AREA", "TV unit", "Back panel + base unit with drawers, display shelves, profile LED (type size)", None, None),
    ("SECTION", "Pooja unit"),
    ("AREA", "Pooja box / unit", "Pooja unit with shutters, bell hangers, drawer for pooja items (type size)", None, None),
    ("SECTION", "Other"),
    ("QTY", "Transport & installation", "", 1, "lump sum"),
    ("QTY", "", "", None, ""),
    ("QTY", "", "", None, ""),
]
r = HR + 1
n = 0
first_item = r
for row in rows:
    kind = row[0]
    if kind == "SECTION":
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
        c = ws.cell(row=r, column=1, value=row[1])
        c.font = Font(bold=True, color="A9834A")
        c.fill = sect
        for col in range(1, 10):
            ws.cell(row=r, column=col).border = box
        r += 1
        continue
    n += 1
    ws.cell(row=r, column=1, value=n)
    ws.cell(row=r, column=2, value=row[1])
    ws.cell(row=r, column=3, value=row[2])
    if kind == "AREA":
        ws.cell(row=r, column=4, value=row[3])
        ws.cell(row=r, column=5, value=row[4])
        ws.cell(row=r, column=6, value=f'=IF(OR(D{r}="",E{r}=""),"",ROUND(D{r}*E{r}/92903.04,2))')   # sq.ft from mm
        ws.cell(row=r, column=7, value="sq.ft")
        for col in (4, 5):
            ws.cell(row=r, column=col).fill = inp
    elif kind == "RFT":
        ws.cell(row=r, column=4, value=row[3])
        ws.cell(row=r, column=6, value=f"=ROUND(D{r}/304.8,2)")            # running feet from mm
        ws.cell(row=r, column=7, value="r.ft")
        ws.cell(row=r, column=4).fill = inp
    else:
        ws.cell(row=r, column=6, value=row[3])
        ws.cell(row=r, column=7, value=row[4])
        ws.cell(row=r, column=6).fill = inp
        ws.cell(row=r, column=7).fill = inp
        ws.cell(row=r, column=6).number_format = "General"
    ws.cell(row=r, column=8).fill = inp
    ws.cell(row=r, column=9, value=f'=IF(OR(F{r}="",H{r}=""),"",ROUND(F{r}*H{r},0))')
    for col in range(1, 10):
        c = ws.cell(row=r, column=col)
        c.border = box
        c.alignment = Alignment(vertical="top", wrap_text=col in (2, 3))
    for col in (8, 9):
        ws.cell(row=r, column=col).number_format = "#,##,##0"
    if kind != "QTY":
        ws.cell(row=r, column=6).number_format = "0.00"
    r += 1
last_item = r - 1

# ---------------- totals
r += 1
tot = {}
for label, formula, editable in [
    ("Sub total", f"=SUM(I{first_item}:I{last_item})", False),
    ("Discount (₹)", 0, True),
    ("Taxable amount", None, False),
    ("GST %", 18, True),
    ("GST amount", None, False),
    ("GRAND TOTAL", None, False),
]:
    ws.merge_cells(start_row=r, start_column=7, end_row=r, end_column=8)
    lc = ws.cell(row=r, column=7, value=label)
    lc.font = Font(bold=True)
    lc.alignment = Alignment(horizontal="right")
    vc = ws.cell(row=r, column=9)
    tot[label] = r
    if label == "Taxable amount":
        formula = f"=I{tot['Sub total']}-I{tot['Discount (₹)']}"
    if label == "GST amount":
        formula = f"=ROUND(I{tot['Taxable amount']}*I{tot['GST %']}/100,0)"
    if label == "GRAND TOTAL":
        formula = f"=I{tot['Taxable amount']}+I{tot['GST amount']}"
        for col in (7, 8, 9):
            ws.cell(row=r, column=col).fill = head
            ws.cell(row=r, column=col).font = Font(bold=True, color="FFFFFF", size=12)
    vc.value = formula
    vc.number_format = "0" if label == "GST %" else "₹ #,##,##0"
    vc.border = box
    if editable:
        vc.fill = inp
    r += 1

r += 1
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
ws.cell(row=r, column=1, value="Amount in words: Rupees ______________________________________________ only").font = Font(italic=True, color="6F655C")
r += 2
ws.cell(row=r, column=1, value="Terms & conditions").font = Font(bold=True, color="A9834A")
terms = [
    "1. Payment: 50% advance with order, 40% before installation, 10% after completion.",
    "2. Delivery: within 30 working days from advance and final design approval.",
    "3. Electrical, plumbing, civil and painting work not included unless listed above.",
    "4. Final amount as per actual site measurement. Colours as per the selected Merino shade card.",
    "5. Warranty as per manufacturer for boards and hardware.",
    "6. Granite, sink, tap and hob are not included unless listed above.",
    "7. This quotation covers ONLY the items listed above. Any additional accessories or items requested later "
    "will be charged extra and paid by the customer.",
    "    இந்த மதிப்பீட்டில் மேலே குறிப்பிட்ட பொருட்கள் மட்டுமே அடங்கும். கூடுதலாக சேர்க்கும் accessories-க்கு வாடிக்கையாளர் தனியாக பணம் செலுத்த வேண்டும்.",
]
for t in terms:
    r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
    c = ws.cell(row=r, column=1, value=t)
    c.fill = inp
    if t.startswith(("7.", "    ")):
        c.font = Font(bold=True, color="B00000")
        ws.row_dimensions[r].height = 30
    c.alignment = Alignment(wrap_text=True)
r += 2
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
ws.cell(row=r, column=1, value="Bank details / UPI:").font = Font(bold=True, color="A9834A")
ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
ws.cell(row=r, column=3, value="A/c name / A/c no. / IFSC / UPI – type here").fill = inp
r += 3
ws.cell(row=r, column=2, value="Customer signature").font = Font(bold=True)
ws.merge_cells(start_row=r, start_column=7, end_row=r, end_column=9)
ws.cell(row=r, column=7, value="For ASTRA INTERIORS – Authorised signatory").font = Font(bold=True)
ws.cell(row=r, column=7).alignment = Alignment(horizontal="center")
r += 2
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
c = ws.cell(row=r, column=1, value="Yellow cells can be edited. Width/height in mm turn into sq.ft or running ft automatically. Leave a row's Rate empty to keep it out of the total.")
c.font = Font(size=8, italic=True, color="8A8077")

# ---------------- print setup (A4, fit to 1 page wide)
ws.print_area = f"A1:I{r}"
ws.page_setup.paperSize = ws.PAPERSIZE_A4
ws.page_setup.orientation = "portrait"
ws.page_setup.fitToWidth = 1
ws.page_setup.fitToHeight = 0
ws.sheet_properties.pageSetUpPr.fitToPage = True
ws.page_margins.left = ws.page_margins.right = 0.4
ws.page_margins.top = ws.page_margins.bottom = 0.5
ws.print_title_rows = f"{HR}:{HR}"
ws.freeze_panes = f"A{HR + 1}"
dv = DataValidation(type="list", formula1='"sq.ft,r.ft,nos,set,lump sum"', allow_blank=True)
ws.add_data_validation(dv)
dv.add(f"G{first_item}:G{last_item}")
import time
for cand in (OUT, OUT.replace(".xlsx", " (updated).xlsx"), OUT.replace(".xlsx", time.strftime(" (%H%M%S).xlsx"))):
    try:
        wb.save(cand)
        OUT = cand
        break
    except PermissionError:  # open in Excel
        continue
print("saved", OUT, "items", n, "rows", r)
