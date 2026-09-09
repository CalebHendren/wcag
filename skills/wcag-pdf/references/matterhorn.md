# Matterhorn Protocol: the checkpoints that matter

The Matterhorn Protocol expresses PDF/UA-1 (ISO 14289-1) as 31 checkpoints containing 136
failure conditions. 87 of those can be determined by software; 47 need human judgement.
veraPDF implements the machine-checkable subset.

This file covers the checkpoints that produce most real-world failures, and marks which
ones a person has to decide. Use it to structure a PDF audit and to explain findings to
someone whose remediation tool reports in Matterhorn terms.

`M` means a machine can decide it. `H` means a human must.

## 01 Real content and artifacts

- 01-005 (M): the document is not tagged. This is the checkpoint everything else depends on.
- 01-003 (H): content that conveys meaning is marked as an artifact, so it is never read.
- 01-006 (H): decoration, page numbers, and running heads are tagged as content, so they
  are read on every page.
- 01-007 (H): a text-bearing image is tagged as a Figure with no alternative text or
  replacement text.

Human judgement decides the boundary between content and decoration. A tool cannot tell
whether a horizontal rule separates sections meaningfully.

## 06 Metadata

- 06-002 (M): the document has no title in its XMP metadata.
- 06-003 (M): the PDF/UA identifier is missing from the metadata.

## 07 Document title

- 07-001 (M): ViewerPreferences DisplayDocTitle is not set to true, so readers show the
  filename instead of the title.

## 09 Structure element types

- 09-001 (H): a structure type is used for something it does not describe, for example a
  paragraph tagged as a heading to make it navigable, or the reverse.
- 09-004 (H): headings are not nested correctly. Levels skip, or a level is used for
  visual size.
- 09-005 (H): the structure does not reflect the logical reading order.
- 09-006 (M): a non-standard structure type has no role mapping to a standard type.
- 09-007 (H): a table is used for layout without being marked as an artifact or given
  presentation semantics.
- 09-008 (H): a list is not tagged as L, LI, LBody.

Checkpoint 09 carries most of the human-judgement conditions and most of the real
failures. Reading order and heading structure both live here.

## 11 Natural language

- 11-001 (M): the document has no default language.
- 11-002 to 11-005 (M and H): text in a language other than the default has no language
  tag on that part. A tool can find missing tags on tagged parts; it cannot detect that a
  paragraph is in another language.

## 13 Graphics

- 13-004 (M): a Figure has neither /Alt nor /ActualText.
- 13-001 (H): the alternative text does not describe what the graphic conveys.
- 13-008 (H): a caption is not associated with its figure.

13-004 is machine checkable and 13-001 is the one that matters. Presence is trivially
satisfied and quality is where the value is.

## 14 Headings

- 14-002 (H): heading levels skip, or the outline does not reflect the document structure.
- 14-003 (M): a numbered heading level is used in a document that also uses unnumbered H
  tags, mixing the two heading models.

## 15 Tables

- 15-003 (H): header cells are not marked as TH, or the scope is wrong.
- 15-005 (M and H): the table structure is irregular, with cells that do not resolve to a
  grid.
- 15-004 (H): a complex table lacks the headers and id associations it needs.

## 17 Optional content

- 17-002 (M): optional content groups have no name, so users cannot tell what a layer
  toggle does.

## 19 XObjects

- 19-003 (H): a form XObject's content is not reflected in the structure tree.

## 21 Fonts

- 21-001 (M): a font is not embedded, so the text may render or extract incorrectly.
- 21-003 (M): a font has no ToUnicode map, so text extraction produces the wrong
  characters. This is a common cause of a document that looks fine but copies as gibberish,
  and screen readers read the same gibberish.

## 25 Reader requirements

- 25-001 (H): the document requires a feature the reader cannot provide accessibly.

## 26 Permissions

- 26-001 (M): the document's encryption blocks content extraction for accessibility, which
  stops a screen reader from reading it at all.

## 28 Annotations and 30 Forms

- 28-002 (M): an annotation has no /Contents or alternative description.
- 28-004 (H): a link annotation's text does not describe its destination.
- 30-001 (M): a form field has no /TU tooltip, so it has no accessible name.
- 30-002 (H): the tab order does not follow the reading order.

## Using this in an audit

Report against WCAG criteria, and cite the Matterhorn checkpoint in the finding as
supporting detail. The audience for a WCAG audit is usually a compliance obligation written
in WCAG terms, and the audience for a Matterhorn checkpoint is the person operating the
remediation tool. Giving both serves each.

When a client asks for "PDF/UA conformance", note that veraPDF settles the machine-checkable
half, and the other half is the human review this skill describes.
