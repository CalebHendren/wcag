---
name: wcag-documents
description: "Audit or fix accessibility in office documents and publications against WCAG 2.2. Use for Word (.docx), PowerPoint (.pptx), Excel (.xlsx), Google Docs, Slides and Sheets, OpenDocument files, EPUB and ebooks, Markdown, and any document that will be exported to PDF or published to the web. Covers heading styles, alt text, reading order, table headers, list structure, link text, color and contrast, slide layouts, spreadsheet structure, and export settings that preserve accessibility. Load this whenever someone asks about an accessible Word document, slide deck, spreadsheet, ebook, or how to prepare a document so the exported PDF is accessible."
license: MIT
allowed-tools: Read, Grep, Glob, Bash, WebFetch, Write, Edit
---

# Document accessibility: audit and remediation

Read `../wcag/SKILL.md` first if you have not. It sets the mode, the finding record, and
the report shape.

Audit is the default here as everywhere. If the user asked a question rather than for
fixes, report and change nothing. This skill carries edit permissions because it also
describes remediation, not because auditing may edit.

A document is not a web page, so WCAG's conformance model does not apply to it directly.
`../../references/non-web.md` covers WCAG2ICT, which is what makes a WCAG statement about a
document coherent, and the language to use for it.

## Why the source document is the highest-leverage place to work

Most inaccessible PDFs began as an inaccessible Word file or slide deck. Every hour spent
remediating the PDF is spent again the next time the document is reissued, and the fix
never reaches the author who will make the same document next quarter.

Fixing the source is cheaper, it survives reissue, and the accessible PDF falls out of a
correct export. When someone asks for PDF remediation, ask where the source is before
anything else. `../wcag-pdf/SKILL.md` covers the case where the source is genuinely gone.

## Reading the files

Office formats are ZIP archives of XML, so they can be inspected without the authoring
application:

```bash
unzip -o report.docx -d /tmp/docx && ls /tmp/docx/word/
# document.xml holds the content, styles.xml the styles,
# and the drawing elements carry alt text in wp:docPr @descr

# Headings actually used, as style references
grep -o 'w:pStyle w:val="[^"]*"' /tmp/docx/word/document.xml | sort | uniq -c | sort -rn

# Images and their alt text
grep -o '<wp:docPr[^>]*>' /tmp/docx/word/document.xml

# Hyperlinks and their visible text
grep -o '<w:hyperlink[^>]*>' /tmp/docx/word/document.xml | head
```

For `.pptx`, `ppt/slides/slideN.xml` holds each slide and `p:cNvPr @descr` holds alt text.
For `.xlsx`, `xl/worksheets/sheetN.xml` holds cells and `xl/workbook.xml` the defined names.

Where the `python-docx`, `python-pptx`, or `openpyxl` libraries are available, they are
easier to work with than raw XML. Where they are not, the grep approach above answers most
audit questions without installing anything.

EPUB is also a ZIP: `META-INF/container.xml` points at the package document, the content is
XHTML, and `../wcag-web/SKILL.md` applies to those files directly.

## What to check, per format

### Word and OpenDocument text

**Headings must be real styles.** Text made large and bold is not a heading. Check that
Heading 1 through Heading 6 styles are applied, that levels descend without skipping, and
that the document has exactly one top-level heading (1.3.1).

**Alt text on every image, chart, and shape**, and decorative items marked as decorative
(1.1.1). Word's own "mark as decorative" flag is the right mechanism, since it produces an
artifact on export.

**Tables**: a real table, not text aligned with tabs or spaces. A header row marked as a
header row and set to repeat. No merged cells where they can be avoided, since merged cells
export badly. No blank rows used for spacing (1.3.1).

**Lists** built with the list feature, not with typed hyphens or manual numbering (1.3.1).

**Link text** that names the destination, not a pasted URL and not "click here" (2.4.4).

**Document language** set, and any passage in another language marked with its own language
(3.1.1, 3.1.2).

**Document title** set in the file properties, since that becomes the PDF title (2.4.2).

**Contrast**, measured rather than eyeballed, especially in themed templates and in text
placed over images (1.4.3).

**Color alone** not carrying meaning, which shows up in tracked changes, highlighted rows,
and red negative figures (1.4.1).

**Columns and text boxes** used sparingly, since floating text boxes are a frequent cause
of reading-order failures on export (1.3.2).

**Headers, footers, and footnotes** carrying no content that exists nowhere else, since
content in headers and footers is often skipped by assistive technology.

### PowerPoint and Slides

**Every slide has a title**, even when hidden from view, because screen readers use slide
titles to navigate (2.4.2). Check the outline view: slides with no title show as blank.

**Reading order** on each slide, checked in the selection or reading order pane. Content
added outside a layout placeholder goes to the end of the order, so a slide that looks
correct can read the caption before the heading (1.3.2).

**Use the layouts.** Placeholders from a slide layout carry structure and order.
Free-floating text boxes carry neither.

**Alt text on images, charts, SmartArt, and grouped shapes** (1.1.1). Charts usually need
the data available another way as well.

**Tables** with a header row, and no tables used purely for layout.

**Contrast** against the actual slide background, including gradient and image backgrounds
where different regions of the same text block differ (1.4.3).

**Text size** large enough to be read, which is a usability point rather than a criterion,
but worth an advisory.

**Animations and transitions** that do not flash, and that do not carry meaning that is
lost when animation is disabled (2.3.1).

**Speaker notes** are not an accessible alternative to on-slide content, since many
exports drop them.

### Excel and Sheets

**Sheet tabs named meaningfully**, not Sheet1.

**One table per sheet where possible**, with a header row, no blank rows or columns inside
the data, and the range defined as a table so the header association is real (1.3.1).

**Alt text on charts and images** (1.1.1).

**No information carried by cell color alone**. A red fill marking overdue rows needs a
text column too (1.4.1).

**No merged cells** in data ranges, since they break screen reader navigation.

**Meaningful cell content**, not blank cells used for spacing.

**Complex formulas and pivot outputs** summarized in text where the meaning is not
otherwise available.

### Markdown and plain text

Headings by level with no skipping, alt text in image syntax, meaningful link text rather
than bare URLs or "here", tables with a header row, and lists using list syntax. Where
Markdown is rendered to HTML, `../wcag-web/SKILL.md` applies to the output.

### EPUB and ebooks

The content is XHTML, so the web criteria apply directly. Additionally: a navigation
document with a full table of contents, correct document language, a logical reading order
in the spine, page-list navigation where the ebook maps to a print edition, and an
accessibility metadata section declaring the features present. Semantic markup through
`epub:type` helps navigation but does not substitute for correct HTML.

## Exporting so the accessibility survives

The export step destroys accessibility more often than the authoring does. Check these:

- Export using the application's own PDF export, not "print to PDF". Printing rasterizes
  structure away and produces an untagged file.
- Turn on the document structure tags option, which most exporters have and some default
  to off.
- Include bookmarks generated from the heading structure for anything longer than a few
  pages.
- Include document properties so the title carries through.
- After export, run `python3 scripts/pdf_audit.py output.pdf` and confirm the file is
  tagged, has a language, has a title, and has the headings you expect. An export that
  silently dropped tagging is common enough to be worth checking every time.


Read `../wcag/SKILL.md` first if you have not. It sets the mode, the finding record, and
the report shape.

Audit is the default here as everywhere. If the user asked a question rather than for
fixes, report and change nothing. This skill carries edit permissions because it also
describes remediation, not because auditing may edit.

## When remediating

Read `../wcag-remediate/SKILL.md` first. Document-specific notes:

- Fix the template, not just this document. An organization with one bad Word template
  produces a bad document every week.
- Applying a heading style changes the visual formatting. Check with the document owner
  before restyling a document that is already circulated, or adjust the style definition so
  the appearance is preserved.
- Never write alt text for an image whose content you cannot determine. Report the gap and
  name what the author must supply.
- Where you can edit the file programmatically, `python-docx` and `python-pptx` set alt
  text and read structure reliably. Both preserve the rest of the file, but work on a copy
  and diff the result.
- Re-export and re-check after the fixes, since the export is where the work either
  survives or does not.
