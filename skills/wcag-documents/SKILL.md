---
name: wcag-documents
description: "Audit or fix accessibility in Word, PowerPoint, Excel, Google Workspace, OpenDocument, EPUB, and Markdown files against WCAG 2.2, including the export settings that decide whether the resulting PDF is accessible. Load whenever someone asks about an accessible Word document, slide deck, spreadsheet or ebook, mentions heading styles, alt text or table headers in a document, or wants a document prepared so its PDF export works."
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

## What to check

Read the section for your format in `references/per-format.md`, which covers Word and
OpenDocument, PowerPoint and Slides, Excel and Sheets, Markdown, and EPUB. Read only the
one you need.

Four checks decide most outcomes whatever the format, so start there:

1. **Headings are real styles**, not text made large and bold. This is what produces the
   PDF tag tree and the navigable outline, and it is the most common single failure
   (1.3.1).
2. **Tables are real tables** with a marked header row, no merged cells where they can be
   avoided, and no blank rows for spacing. Merged cells are what survive an export worst,
   and a table whose merges are dropped reads with its data in the wrong columns (1.3.1).
3. **Every image has alt text or is marked decorative.** The authoring tool's decorative
   flag is the right mechanism, because it exports as an artifact (1.1.1).
4. **Document language and title are set**, since both carry into the export (3.1.1,
   2.4.2).

Then contrast, link text, list structure, and reading order, which
`references/per-format.md` covers per format.

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
