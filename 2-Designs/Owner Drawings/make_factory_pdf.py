"""Factory cut list PDF (A4 landscape) from the 'ALL - one page' sheet of the newest FACTORY Excel (no Excel/Word needed)."""
import glob
import html
import os
import time

import pymupdf
from openpyxl import load_workbook

HERE = os.path.dirname(os.path.abspath(__file__))
src = max(glob.glob(os.path.join(HERE, "Mr. Manoker - FACTORY Cut List*.xlsx")), key=os.path.getmtime)
ws = load_workbook(src, data_only=True)["ALL - one page"]

out = ['<body style="font-family: sans-serif; font-size: 7.5pt;">']
table = False
for row in ws.iter_rows(values_only=True):
    cells = ["" if c is None else str(c) for c in row]
    while cells and cells[-1] == "":
        cells.pop()
    if not any(cells):
        if table:
            out.append("</table>"); table = False
        out.append("<p></p>")
        continue
    filled = [c for c in cells if c]
    if len(filled) == 1:                                   # title / note / board heading
        if table:
            out.append("</table>"); table = False
        t = html.escape(filled[0])
        out.append(f'<p style="font-weight: bold; color: #7a5a30; font-size: 9pt;">{t}</p>' if t.startswith(("BOARD", "Mr.")) else f"<p>{t}</p>")
        continue
    if not table:
        out.append('<table border="1" cellpadding="2" style="border-collapse: collapse; width: 100%;">'); table = True
    head = cells[0] in ("No", "") and any(h in cells for h in ("Part", "Board type"))
    tag = "th" if head else "td"
    style = ' style="background-color: #efe6da;"' if head else ""
    out.append(f"<tr{style}>" + "".join(f"<{tag}>{html.escape(c)}</{tag}>" for c in cells) + "</tr>")
if table:
    out.append("</table>")
out.append("</body>")

story = pymupdf.Story("".join(out))
rect = pymupdf.paper_rect("a4-l")
where = rect + (28, 28, -28, -28)
name = os.path.join(HERE, "Mr. Manoker - FACTORY Cut List.pdf")
for cand in (name, name.replace(".pdf", " (updated).pdf"), name.replace(".pdf", time.strftime(" (%H%M%S).pdf"))):
    try:
        w = pymupdf.DocumentWriter(cand)
        more = True
        while more:
            dev = w.begin_page(rect)
            more, _ = story.place(where)
            story.draw(dev)
            w.end_page()
        w.close()
        print("saved", os.path.basename(cand), "from", os.path.basename(src))
        break
    except (PermissionError, RuntimeError):
        continue
