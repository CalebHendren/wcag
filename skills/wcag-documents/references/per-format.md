# What to check, per document format

Read the section for the format in front of you. The criterion each check serves is in
brackets, and `../../../references/` holds the full catalogue.

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
Markdown is rendered to HTML, `../../wcag-web/SKILL.md` applies to the output.

### EPUB and ebooks

The content is XHTML, so the web criteria apply directly. Additionally: a navigation
document with a full table of contents, correct document language, a logical reading order
in the spine, page-list navigation where the ebook maps to a print edition, and an
accessibility metadata section declaring the features present. Semantic markup through
`epub:type` helps navigation but does not substitute for correct HTML.

