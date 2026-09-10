# Working as a desktop agent

Most accessibility tooling assumes a developer editing source code. A growing share of this
work now happens somewhere else: an agent with access to a person's files and applications,
asked to fix the deck before it goes out. Claude Cowork, ChatGPT's work and agent modes,
Copilot inside Office, Gemini inside Workspace, and any assistant that can open a folder
and drive an application all sit in that position.

The content is the same and the constraints are not. A coding agent changes text files
under version control and a test suite says whether it worked. A desktop agent changes a
binary container that one application owns, usually with no version control, often with the
author waiting. This file covers what that changes.

## Establish the envelope before promising anything

What you can fix depends on which of these you actually have. Check, do not assume, and say
what you found:

**File access.** You can read and write the bytes of the document. Office files and EPUBs
are ZIP archives of XML, so this alone is enough for a large share of fixes.

**A Python environment.** `python-docx`, `python-pptx`, and `openpyxl` are easier and safer
than raw XML where they are installed. Check rather than assume, and fall back to the
`zipfile` standard library module, which is always there.

**A converter.** LibreOffice in headless mode converts between formats, opens the legacy
binary `.doc`, `.ppt`, and `.xls`, and exports tagged PDF. It is the most useful single
tool on a machine with no Microsoft Office.

**The application itself.** If you can drive Word, PowerPoint, Excel, or Acrobat, you can
reach features that have no file-level equivalent, and you can run the built-in
accessibility checker. `builtin-checkers.md` covers those and what they are worth.

**A connector or an API.** Google Workspace and SharePoint files are not on disk. The Docs,
Slides, and Sheets APIs set alt text, heading styles, and table headers, and without a
connector you cannot touch the file at all.

A one-line probe answers most of this:

```bash
python3 -c "import docx, pptx, openpyxl" 2>&1 | tail -1   # which libraries exist
command -v soffice libreoffice                             # a converter
```

State the envelope in the report. "Fixed in the file with python-docx, could not run
PowerPoint's reading order pane in this environment" is a useful sentence. It tells the
reader which findings a person still has to open the application for.

## How fixable is part of the finding

Every finding carries `agent_fix`, saying who or what can actually close it. An audit that
lists 40 problems without saying which ones the agent can fix is a list of homework. Five
values, and the first is the only one you close on your own:

**`direct`.** You can apply it with the tools you have, and the correct value is derivable
from the document. Setting the document language, associating a visible label with its
field, marking the first row of a table as a header row, setting a document title from the
heading that is already on page one.

**`app`.** The fix needs the authoring application, because the file format has no place to
put it or because getting it right needs the tool's own view. Acrobat's tag tree editor,
PowerPoint's reading order pane where you cannot reorder shapes safely, a Word template
that lives in a corporate library. If you can drive the application, these become `direct`
and you should say so.

**`recreate`.** The file cannot carry the fix at all in its current state. An untagged PDF
with no source, a Word file whose headings are all direct formatting on top of Normal with
a hundred manual list paragraphs, a deck built entirely of free-floating text boxes.
Repairing these in place produces something worse than rebuilding, and
`../skills/wcag-recreate/SKILL.md` covers the rebuild.

**`owner`.** The content is information you do not have. Alt text for a photograph you
cannot see, captions, what an error message should say. Guessing here is the worst
available option, because it looks fixed to everyone who checks later.

**`design`.** Someone has to choose. Contrast, target size, and anything that changes the
visual design. Propose specific values with measured ratios and let the designer pick.

Anything that is not `direct` belongs in its own section of the audit, under a heading that
says plainly that an agent cannot close it. That section is what the person reading the
report has to act on.

## Round trips are where documents get damaged

Opening a file and saving it again is not free. Every library and every converter rewrites
what it does not understand, and the parts they drop are usually the parts nobody notices
until later.

**Raw ZIP and XML editing preserves everything you do not touch.** Rewrite one XML part,
copy the rest of the archive across byte for byte, and nothing else can change. This is the
safest option and the reason `scripts/office_remediate.py` works this way.

**`python-docx` and `python-pptx` round trip well**, because both keep the underlying XML
and edit it in place rather than regenerating it.

**`openpyxl` does not round trip a rich workbook.** Charts, images, pivot tables, and some
conditional formatting are dropped on save, because it rebuilds the parts it models. Use it
to read a workbook and to write a new one. Do not use it to save a workbook that has
anything in it you cannot afford to lose, and check what a file contains before deciding.

**LibreOffice reflows the layout.** Converting a Word file through LibreOffice and back
produces a document that is close, not identical, and page breaks move. That is acceptable
for a conversion you were asked for and unacceptable as a side effect of a fix.

Three rules follow. Work on a copy, always, and keep the original untouched until the
person has seen the result. Before saving, know what the file holds that your tool does not
model. After saving, compare the two files on what should not have changed: text, image
count, table count, slide count, sheet count, page count where you can get it.

## What is usually out of reach

Say so early rather than discovering it half way through. A document that is encrypted or
password protected cannot be opened, and asking for the password is the whole of the fix.
A digitally signed document loses its signature the moment you write to it, so ask before
touching one. A file marked final or under editing restrictions needs those lifted first. A
file open in the application on the person's machine may be locked, and on a shared drive
your write may collide with theirs.

Two more that look like failures and are not. Legacy binary formats, `.doc`, `.ppt`, and
`.xls`, have no ZIP container to edit, so convert to the modern format first and say that
you did. Files stored in Google Workspace or SharePoint are not files on disk until
something exports them, and an export loses the link back to the original.

## Fixing the template beats fixing the document

An organization with one bad Word template produces a bad document every week, and the
accessible version of last quarter's report does not help with this quarter's. When you can
see that the failure came from the template, the theme, or the slide master, say so and
offer to fix that too. It is the highest-leverage change available in document work, and
almost nobody asks for it.
