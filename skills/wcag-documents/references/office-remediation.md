# Applying document fixes, in the application and in the file

Each fix below is given twice: how a person does it in the application, which is what to
say when the fix is theirs and what to do yourself if you can drive the application, and
how to apply it to the file directly, which is what to do when you cannot.

Read `../../../references/desktop-agents.md` first for the round-trip rules. The short
version: work on a copy, never save over the original, and know what your tool drops before
you use it.

Start by finding out what you have, because the answer decides the whole approach:

```bash
python3 -c "import docx, pptx, openpyxl" 2>&1 | tail -1
command -v soffice libreoffice
python3 scripts/office_audit.py report.docx          # findings, each with agent_fix
```

## The fixes a script can make

`scripts/office_remediate.py` applies these four to the file and writes a new copy. It
refuses anything whose correct value it was not given, and it exits 1 when a fix fails,
which is the signal to stop rather than to try another approach.

```bash
python3 scripts/office_remediate.py report.docx \
    --title auto --language en-GB --table-headers --alt-text alt.json
python3 scripts/office_audit.py report-remediated.docx    # always re-audit
```

**Document title** (2.4.2). In the application: File, Info, Title. `--title auto` takes it
from the document's first heading, the first slide title, or the first named sheet, which
is what the author already wrote. Pass the text yourself when none of those is right.

**Document language** (3.1.1). In Word: Review, Language, Set Proofing Language, then apply
it to the whole document and to the default style. In the file, the value sits on the
default run properties in `word/styles.xml`. PowerPoint keeps language on each run instead,
so it is set per text run. A workbook has nowhere to record a document language at all, and
saying so is the right answer rather than inventing a place for it.

**Table header rows** (1.3.1). In Word: select the first row, then Table Layout, Repeat
Header Rows, and turn on Header Row in Table Design, Table Style Options. Both matter: the
style option is what Word's own checker looks at, and the repeat setting is what carries
into the PDF export as `TH`. Check the first row really is the header before setting it.

**Alternative text** (1.1.1) where you have the text. In the application: right-click the
image, View Alt Text, or Picture Format, Alt Text. The script takes a JSON map of shape
name to text, keyed by the names `office_audit.py` reports.

Where the alternative text does not exist yet, there are two honest paths and one dishonest
one. If you can view the image, draft the alternative from what you can see, mark the
finding `needs-review` rather than closed, and put the drafts in front of the author. If
you cannot view it, ask. What you must not do is write something that sounds plausible:
`alt="chart showing growth"` on a chart you never saw satisfies every checker and tells the
reader nothing, and nobody will look at it again.

## The fixes that need the application

These have no file-level equivalent worth trusting. If you can drive the application, do
them there. If you cannot, they are `agent_fix: app` findings and they belong in the
section of the report that says an agent cannot close them.

**Marking an image decorative.** Word and PowerPoint record this with an extension that
their own Alt Text pane writes, and there is no reliable way to set it from outside. An
empty alt attribute is not the same thing: the object is still announced. Use the "Mark as
decorative" checkbox in the Alt Text pane.

**Adding a slide title where the layout has no title placeholder.** Changing the layout is
a PowerPoint operation. In the application: Home, Layout, choose one with a title, or
View, Outline View and type the title there. Where the design has no visible title, add the
placeholder and move it off the slide area rather than leaving the slide unnamed.

**Reading order on a slide.** PowerPoint's Reading Order pane is the tool, and the order it
shows has to be read against the visual layout by a person. Reordering shapes in the file
is possible and deciding the right order is not, so this stays a judgement call even when
the mechanism is available.

**Anything in a corporate template library.** Fixing the document does not fix next
quarter's. Templates usually live somewhere only a person can reach.

## The fixes that need the author or a designer

Report these, do not close them. `../../wcag-remediate/SKILL.md` covers the boundary.

Alternative text for images you cannot see. Captions and transcripts for embedded media.
Restructuring a table whose merged cells carry grouping, since where the data should go is a
content decision. Rewriting link text that says "click here", because the right wording
depends on the destination. Renaming things where the name has meaning. Contrast, target
size, and anything else that changes the visual design, where the job is to propose specific
values with measured ratios and let someone choose.

## Reading the file without the application

Office files are ZIP archives of XML, so an audit needs no Office installation:

```bash
unzip -o report.docx -d /tmp/docx && ls /tmp/docx/word/

# heading styles actually used
grep -o 'w:pStyle w:val="[^"]*"' /tmp/docx/word/document.xml | sort | uniq -c | sort -rn

# images and their alternative text
grep -o '<wp:docPr[^>]*>' /tmp/docx/word/document.xml
```

`ppt/slides/slideN.xml` holds each slide, with alt text in `p:cNvPr @descr`.
`xl/worksheets/sheetN.xml` holds cells, `xl/workbook.xml` the sheet names, and
`xl/tables/tableN.xml` the defined tables that make a header row real.
`scripts/office_audit.py` does all of this and maps it to criteria, so reach for the grep
only when you need something the script does not report.

## Legacy and locked files

**`.doc`, `.ppt`, `.xls`** carry no XML package. Convert first, work on the converted copy,
and say in the report that a conversion happened, because the conversion itself can move
content:

```bash
soffice --headless --convert-to docx old-report.doc
```

**Encrypted or password protected.** Nothing can be read. Ask for the password or an
unprotected copy, and say the audit could not start.

**Digitally signed.** Any write invalidates the signature. Ask before touching it, and
expect the answer to be that the accessible version has to be a new document with a new
signature.

**Restricted editing, or marked final.** The restriction has to be lifted in the
application first.

**Open on someone's machine, or on a shared drive.** Your write may be locked out or may
collide with theirs. Work on a copy and hand it back rather than editing in place.

## Export, which is where the work survives or does not

The export step destroys more accessibility than the authoring does. Use the application's
own PDF export rather than print to PDF, which rasterizes structure away. Turn on document
structure tags, which some exporters default to off. Include bookmarks from the headings for
anything longer than a few pages, and include document properties so the title carries
through.

From a command line, LibreOffice exports tagged PDF:

```bash
soffice --headless --convert-to \
  'pdf:writer_pdf_Export:{"UseTaggedPDF":{"type":"boolean","value":"true"}}' report.docx
python3 scripts/pdf_audit.py report.pdf
```

Check the output every time. An export that silently dropped tagging looks identical in a
viewer, and the audit script is the only thing that will tell you.
