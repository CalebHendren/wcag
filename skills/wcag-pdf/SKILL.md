---
name: wcag-pdf
description: "Audit or fix accessibility in PDF files against WCAG 2.2 and PDF/UA (ISO 14289). Use for any PDF: reports, forms, statements, scanned documents, brochures, invoices, policy documents, or a folder of them. Covers tagging, reading order, alternative text, headings, tables, form field labels, bookmarks, document language, and OCR of scans. Load this whenever someone mentions a PDF and accessibility, asks whether a document is screen-reader friendly, mentions tagged PDF, PDF/UA, Section 508 documents, remediation, Acrobat's accessibility checker, veraPDF, or the Matterhorn Protocol."
license: MIT
allowed-tools: Read, Grep, Glob, Bash, WebFetch, Write, Edit
---

# PDF accessibility: audit and remediation

Read `../wcag/SKILL.md` first if you have not. It sets the mode, the finding record, and
the report shape.

Audit is the default here as everywhere. If the user asked a question rather than for
fixes, report and change nothing. This skill carries edit permissions because it also
describes remediation, not because auditing may edit.

PDF is the format where the gap between "looks fine" and "readable" is widest. A PDF that
prints perfectly can be completely unreadable to a screen reader, and nothing on screen
tells you which one you have. Everything below is about finding out.

A document is not a web page, so WCAG's conformance model does not apply to it directly.
`../../references/non-web.md` covers WCAG2ICT, which is what makes a WCAG statement about a
document coherent, and the language to use for it.

## The one thing that decides everything

A PDF is accessible only if it is **tagged**: it carries a structure tree describing which
text is a heading, which is a paragraph, which is a table cell, and in what order it should
be read. Without tags, a screen reader guesses the reading order from the position of text
on the page, and on anything with columns, sidebars, or a header it guesses wrong.

Check this first, because it decides whether you are writing an audit or recommending a
rebuild:

The commands below use paths relative to the plugin root. The core skill's "Find the bundled scripts" section explains how to locate it when the working directory is elsewhere.

```bash
python3 scripts/pdf_audit.py document.pdf
python3 scripts/pdf_audit.py document.pdf --dump-tags     # see the structure
python3 scripts/pdf_audit.py document.pdf --json > findings.json
```

Three outcomes, and the advice differs sharply between them:

**Untagged.** Report it as a single critical finding rather than enumerating everything
downstream of it. There is no point listing missing alt text on a document that has no
structure at all. The fix is to go back to the source file, fix it there, and re-export.

**Tagged but wrong.** This is the common case and where audit effort pays off. The tags
exist, so go through them: reading order, heading levels, figure alt, table headers, form
field names, artifacts.

**Scanned images.** No extractable text at all. The document is entirely unavailable to
blind readers and to search. It needs OCR and then tagging, and OCR output always needs
correction, so scope the work honestly.

## Fix the source, not the PDF

State this early in any remediation conversation, because it changes the whole plan.

Remediating a PDF by hand in Acrobat is slow, it has to be redone every time the document
is reissued, and the result is usually worse than a clean export. When the source file
exists in Word, InDesign, PowerPoint, LaTeX, or a reporting tool, fix the source and
re-export. `../wcag-documents/SKILL.md` covers how to prepare each source format.

Hand remediation is the right call only when the source is genuinely gone, the document is
a one-off legal or archival artifact, or the change is small and the document is frozen.

Say which situation applies and why. A recommendation to retag 300 pages by hand when the
InDesign file is sitting on a server is a bad recommendation regardless of how thorough the
finding list is.

## What the script checks and what it cannot

The script reads the file structure: tagging, document language, title and
DisplayDocTitle, figure alt text, heading levels, table header cells, form field tooltips,
bookmarks, tab order, and whether pages carry extractable text.

It cannot judge the things that decide whether the document actually works. Those are
yours:

**Reading order.** The single most important check, and the one no tool can settle. The tag
tree can look correct while reading a two-column page straight across, mixing the two
columns into nonsense. Read the document in order, either with a screen reader or by
following the tag tree against the visual layout. Pay particular attention to pages with
columns, pull quotes, sidebars, captions, and figures placed between paragraphs (1.3.2).

**Alternative text quality.** The script finds figures with no alt. It cannot tell you
whether "Chart 1" is a useful alternative for a chart. Charts and data graphics usually
need a description of the trend plus the underlying data, either as a long description or
as an adjacent table (1.1.1).

**Artifacts.** Page numbers, running headers, decorative rules, and background images
should be marked as artifacts so they are not read as content. Tagged decoration is a
common reason a document reads as noise.

**Color and contrast.** PDF structure carries no color information the script can compare.
Extract the colors and run `scripts/contrast.py` on the text and background pairs
(1.4.3, 1.4.11). Also check for information carried by color alone, such as red for
negative figures (1.4.1).

**Table complexity.** Scope works for simple tables. Tables with merged cells or two levels
of headers need `headers` and `id` associations, and the script cannot verify those are
correct (1.3.1).

**Lists.** A bulleted list tagged as a series of paragraphs reads as prose. Check the tag
tree for L, LI, and LBody (1.3.1).

**Language of parts.** Passages in another language need their own language tag (3.1.2).

**Link text.** Does each link say where it goes when read alone (2.4.4).

## Forms

A PDF form is where inaccessibility becomes exclusion, since the user cannot complete it at
all. Check each field for:

- A tooltip (`/TU`), which is the field's accessible name. Without it the field announces
  only its type.
- A tab order that follows the visual order, which means `/Tabs /S` on every page and a tag
  order that matches the layout (2.4.3).
- Required fields marked programmatically, not only with an asterisk or red text (3.3.2).
- Instructions and format hints available to a screen reader, not only printed beside the
  field.
- Radio and checkbox groups sharing a group name so they are announced as a set.
- Validation messages that reach the user as text (3.3.1, 3.3.3).

## Standards beyond WCAG

WCAG applies to PDF through the W3C PDF techniques (PDF1 through PDF23), which describe how
to satisfy each criterion in this format. `references/pdf-techniques.md` maps the criteria
to those techniques.

PDF/UA-1 (ISO 14289-1) is the format-specific accessibility standard. The Matterhorn
Protocol expresses it as 31 checkpoints and 136 failure conditions, of which 87 can be
checked by software and 47 need human judgement. `references/matterhorn.md` covers the
checkpoints that matter most in practice and which of them a person has to decide.

The two standards overlap but neither contains the other. A PDF/UA-conforming file can
still fail WCAG on contrast, and a file that satisfies WCAG can miss PDF/UA structural
requirements. If a procurement asks for both, say which you tested.

Where a fuller check is available, recommend it and say what it adds:

- **veraPDF** is the open-source PDF/UA validator, and it covers the machine-checkable
  Matterhorn conditions properly.
- **Acrobat's accessibility checker** is what most document owners have, and its report is
  the vocabulary they will use.
- **PAC** checks PDF/UA and shows a screen-reader preview of the reading order, which is
  the fastest way for a person to see an order problem.

Recommending these is not an admission that the audit was thin. It is how a real
accessibility team works, and the skill's value is in the judgement calls those tools do
not make.


Read `../wcag/SKILL.md` first if you have not. It sets the mode, the finding record, and
the report shape.

Audit is the default here as everywhere. If the user asked a question rather than for
fixes, report and change nothing. This skill carries edit permissions because it also
describes remediation, not because auditing may edit.

PDF is the format where the gap between "looks fine" and "readable" is widest. A PDF that
prints perfectly can be completely unreadable to a screen reader, and nothing on screen
tells you which one you have. Everything below is about finding out.

## When remediating

Read `../wcag-remediate/SKILL.md` first. PDF-specific notes:

- Establish where the source file is before proposing anything.
- If the PDF must be edited directly, note that the tooling for this is Acrobat Pro, and
  scripted approaches with `pikepdf` or `pypdf` can set document-level properties such as
  language, title, and DisplayDocTitle safely, but rebuilding a structure tree by script is
  fragile and usually produces a worse result than a re-export.
- The safe scripted fixes are: set `/Lang`, set the document title and `DisplayDocTitle`,
  set `/Tabs /S` on pages, and add `/Alt` to existing Figure elements where the correct
  text is known.
- The unsafe ones, which need the authoring tool: creating the structure tree, changing
  reading order, adding heading structure, and building table header associations.
- After any change, re-run `pdf_audit.py` and re-read the document in order. A PDF edit
  that silently corrupts the tag tree looks fine in a viewer.
- Never invent alternative text for an image whose content you cannot see. Report the gap
  and name what the author has to supply.
