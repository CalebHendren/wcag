# Rebuilding, per target format

Read the section for the format you are producing. `../SKILL.md` holds the contract these
recipes serve: same words, same order, real structure, approximate design, nothing
invented.

Check what you have before choosing a tool. A library that is not installed is not an
option, and the standard library always is.

```bash
python3 -c "import docx, pptx, openpyxl" 2>&1 | tail -1
command -v soffice libreoffice pandoc
```

## Word

**With `python-docx`**, which is the best case. Create from the organization's template
where one exists, so the rebuild inherits the right styles:

```python
from docx import Document

source = Document("original.docx")           # read the content out
rebuilt = Document("house-template.dotx")    # or Document() for a blank start

rebuilt.core_properties.title = "Quarterly accessibility report"
rebuilt.core_properties.language = "en-GB"

rebuilt.add_heading("Quarterly accessibility report", level=1)
rebuilt.add_paragraph("This report covers the period to March.")
rebuilt.add_paragraph("First finding", style="List Bullet")

table = rebuilt.add_table(rows=1, cols=2, style="Table Grid")
for cell, text in zip(table.rows[0].cells, ("Region", "Total")):
    cell.text = text
table.rows[0].header = True        # repeats the row, and exports as TH
rebuilt.save("report-accessible.docx")
```

Three things `python-docx` will not do for you. It cannot mark an image decorative, so
either give every image real alternative text or leave the decorative flag for someone
working in Word. It writes alternative text through the underlying XML rather than through
a documented property, so set it and then confirm it with
`python3 scripts/office_audit.py`. And a style you name has to exist in the template you
started from, so check the template before assuming `List Bullet` or `Quote` is there.

**With the standard library only**, build the document as flat XML and write the package
with `zipfile`. This is more work and entirely doable, and it is what
`tests/fixtures/build_office_fixtures.py` in this repository does if you want a worked
example of the minimum package Word will open.

**Through Markdown and a converter.** Writing the content as Markdown and converting with
`pandoc -o out.docx --reference-doc=house-template.docx` produces real heading styles,
lists, and tables in one step, and is the fastest route when the content is mostly prose.
Check the result: table header rows and image alternative text are the parts that most
often need setting afterwards.

## PowerPoint

`python-pptx` is the practical tool, and the discipline that matters is building on layouts
rather than on blank slides.

```python
from pptx import Presentation

deck = Presentation("house-template.potx")   # or Presentation()
layout = deck.slide_layouts[1]               # Title and Content

slide = deck.slides.add_slide(layout)
slide.shapes.title.text = "Programme update"
slide.placeholders[1].text_frame.text = "Uptake rose in every region."

picture = slide.shapes.add_picture("chart.png", left, top, width=width)
picture._element._nvXxPr.cNvPr.set("descr", "Bar chart. Uptake by quarter, 40 to 62 "
                                            "percent.")
deck.save("deck-accessible.pptx")
```

Every slide gets a title, including the ones whose design has no visible title: a title
placeholder moved off the slide area still gives a screen reader user the name. Content
goes in layout placeholders, because that is what carries the reading order. Anything you
do add outside a placeholder has to be checked in the reading order pane afterwards, and
that check is a person's job.

Speaker notes come across through `slide.notes_slide.notes_text_frame.text`. Bring them,
and remember they are not an accessible alternative to what is on the slide.

## Excel

`openpyxl` writes a new workbook cleanly, which is the case it is good at. What it is not
good at is saving a workbook it opened, because it drops charts, images, and some
conditional formatting on the way through. In a rebuild that is fine, since you are writing
a new file, but it means the charts have to be rebuilt rather than carried over.

```python
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo

book = Workbook()
sheet = book.active
sheet.title = "Regional totals"           # never leave it as Sheet1
sheet.append(["Region", "Total"])
sheet.append(["North", 12])

table = Table(displayName="RegionalTotals", ref="A1:B2")
table.tableStyleInfo = TableStyleInfo(name="TableStyleLight1", showRowStripes=True)
sheet.add_table(table)                     # this is what associates the header row
book.save("workbook-accessible.xlsx")
```

One table per sheet where you can manage it, the range defined as a table so the header
association is real, no merged cells in the data, no blank rows for spacing, and a text
column wherever the original used cell color to mean something.

## PDF

A PDF is rebuilt by building the source and exporting, not by writing PDF operators.
Produce the Word or Markdown version first, get it right, then export.

LibreOffice exports tagged PDF from a command line, which is the reliable route on a
machine with no Microsoft Office. The filter options are passed as JSON, which recent
versions accept:

```bash
soffice --headless --convert-to \
  'pdf:writer_pdf_Export:{"UseTaggedPDF":{"type":"boolean","value":"true"},
   "ExportBookmarks":{"type":"boolean","value":"true"}}' \
  report-accessible.docx
python3 scripts/pdf_audit.py report-accessible.pdf
```

Check the version in front of you accepts that form before relying on it, and check the
output every time regardless. An export that silently dropped tagging looks identical in a
viewer, and `pdf_audit.py` is how you find out. From the applications, use Word's own PDF
export with document structure tags turned on, not print to PDF, which rasterizes the
structure away.

## HTML and EPUB

Rebuilding into HTML is the easiest target, because the structure is the markup:
`h1` to `h6` in order, `ul` and `ol` for lists, `table` with `th` and `scope`, `figure` and
`figcaption`, one `main`, and a `lang` on `html`. `../../wcag-web/SKILL.md` covers the rest.

EPUB is a ZIP of XHTML, so the same applies inside it, plus a navigation document with a
full table of contents, a spine in reading order, the language set in the package document,
and an accessibility metadata section that declares what the book actually has.

## Google Workspace

Without a connector or API access there is nothing to rebuild into, so establish that
first. With the Docs, Slides, or Sheets API, build the same structure the desktop formats
need: named heading styles rather than font sizes, alt text on every image through the
image properties, tables with a header row, and a document title that is not "Untitled
document".

Where you have no API, the honest answer is to produce the desktop format, hand it over,
and say it has to be uploaded. An accessible file the person cannot get into their system
is not a delivery.
