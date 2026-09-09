# WCAG criteria in PDF: what satisfying each one looks like

WCAG is technology-neutral, and the W3C PDF techniques (PDF1 through PDF23) describe how to
satisfy each criterion in this format. This file maps the criteria that come up in PDF
audits to what the document actually has to contain.

## Perceivable

**1.1.1 Non-text Content.** Figure tags carry /Alt describing what the image conveys.
Decorative images are artifacts, not tagged figures. Charts get a long description or an
adjacent data table, because a sentence rarely substitutes for a chart.

**1.2.x Media.** Video and audio embedded in a PDF carry the same obligations as anywhere
else. In practice, link out to a properly captioned player rather than embedding.

**1.3.1 Info and Relationships.** Headings tagged H1 through H6. Lists tagged L, LI, LBody.
Tables tagged Table, TR, TH, TD with scope, and headers and id associations where the table
is complex. Form fields with tooltips. This one criterion covers most PDF structure work.

**1.3.2 Meaningful Sequence.** The tag tree order matches the intended reading order. This
is the criterion that multi-column layouts fail, and the one that needs a person to check.

**1.3.3 Sensory Characteristics.** Instructions do not depend on position, shape, or color,
so "see the box on the right" needs a name or a reference.

**1.4.1 Use of Color.** Negative figures in red, required fields in red, chart series by
color alone. Add a symbol, a label, or a pattern.

**1.4.3 and 1.4.11 Contrast.** Measure text against its background and check interface
elements in forms. PDF structure does not carry this, so extract the colors and measure.

**1.4.4 Resize Text.** The document reflows or the reader can zoom without loss. A tagged
document reflows in readers that support it; an untagged one does not.

**1.4.5 Images of Text.** Text as an image with no text equivalent, common in scanned
letterheads and marketing pages inside otherwise text-based documents.

## Operable

**2.1.1 Keyboard.** Every interactive element in the document, meaning form fields, links,
and buttons, is reachable by keyboard.

**2.4.1 Bypass Blocks.** Bookmarks in a long document serve this purpose.

**2.4.2 Page Titled.** A document title in the metadata, with DisplayDocTitle set so
readers show it instead of the filename.

**2.4.3 Focus Order.** /Tabs /S on every page, so tab order follows the structure rather
than the order the fields were drawn.

**2.4.4 Link Purpose.** Link text and link annotation /Contents describe the destination. A
bare URL is a poor link name because it is read character by character.

**2.4.5 Multiple Ways.** Bookmarks and a table of contents with working links.

**2.4.6 Headings and Labels.** Headings describe their sections. Form field tooltips match
the visible label.

## Understandable

**3.1.1 Language of Page.** /Lang on the document catalog.

**3.1.2 Language of Parts.** /Lang on the structure element containing the passage.

**3.2.x Predictable.** Form fields that do not trigger a change of context on focus or on
selection, which in PDF usually means avoiding JavaScript actions on focus.

**3.3.1, 3.3.2, 3.3.3 Input assistance.** Field tooltips as labels, format hints available
to a screen reader rather than only printed, and validation messages delivered as text.

## Robust

**4.1.2 Name, Role, Value.** Form fields have a tooltip as the name, the right field type
as the role, and their state exposed. Annotations have /Contents.

## The order to work in

When remediating a document from scratch, this order avoids rework:

1. Set the document language, title, and DisplayDocTitle.
2. Establish the tag tree and the reading order.
3. Tag headings at the right levels.
4. Tag lists and tables, adding header cells and scope.
5. Add figure alternative text, and mark decoration as artifacts.
6. Name form fields, and set the tab order to follow the structure.
7. Add bookmarks.
8. Check contrast and color usage, which are design changes rather than tagging.

Doing alt text before reading order wastes effort, because reordering the tree moves the
figures.
