# WCAG 2.2 success criteria: Perceivable

Information and interface components must be presentable to users in ways they can
perceive. 29 criteria across four guidelines.

Each entry gives the criterion number, title, conformance level, and the WCAG version that
introduced it. `Intent` says what the criterion is protecting. `Test` is the fastest
reliable way to check it. `Fails when` lists what actually goes wrong in real content.

## Contents

- [Guideline 1.1 Text Alternatives](#guideline-11-text-alternatives)
- [Guideline 1.2 Time-based Media](#guideline-12-time-based-media)
- [Guideline 1.3 Adaptable](#guideline-13-adaptable)
- [Guideline 1.4 Distinguishable](#guideline-14-distinguishable)

## Guideline 1.1 Text Alternatives

### 1.1.1 Non-text Content (A, 2.0)

Intent: every image, icon, chart, control, and media element that is not text carries a
text alternative serving the same purpose, so it can be spoken, brailled, or enlarged.

Test: list every non-text element. For each, ask what a person misses if the image does not
load. The alternative must supply that, not describe the pixels.

Fails when:
- Informative images have empty or missing `alt`.
- Decorative images have descriptive `alt` instead of `alt=""`, adding noise.
- Alt text is a filename, `"image"`, `"graphic"`, or the word "image of".
- Icon-only buttons have no accessible name, so the control is announced as "button".
- Charts and infographics get a one-line alt where the data needs a long description or an
  adjacent data table.
- CAPTCHA offers only one sensory mode. Two modes covering different senses are required.
- Text is rendered as an image with no equivalent text (see also 1.4.5).
- CSS background images carry meaning with nothing in the accessibility tree.

## Guideline 1.2 Time-based Media

Full guidance on captions, audio description, and transcripts, including how to judge
quality rather than presence, is in `media.md`. The criteria are summarized here.

### 1.2.1 Audio-only and Video-only (Prerecorded) (A, 2.0)

Intent: a transcript for audio-only, and either a transcript or an audio track for
video-only.

Fails when: a podcast ships with no transcript, or a silent explainer video has no text
description of what it shows.

### 1.2.2 Captions (Prerecorded) (A, 2.0)

Intent: synchronized captions for all prerecorded audio in video.

Fails when: only auto-generated captions are provided and they misname speakers, drop
punctuation, or garble terms. Auto-captions are a starting draft, not conformance.

### 1.2.3 Audio Description or Media Alternative (Prerecorded) (A, 2.0)

Intent: visual information not carried by the soundtrack is available, either through audio
description or a full text alternative for the video.

Fails when: an on-screen demonstration is narrated as "click here, then here".

### 1.2.4 Captions (Live) (AA, 2.0)

Intent: real-time captions for live audio in synchronized media.

Fails when: a livestream or webinar relies on the platform's automatic captions with no
human captioner and no correction pass.

### 1.2.5 Audio Description (Prerecorded) (AA, 2.0)

Intent: audio description for prerecorded video. At AA the text alternative that satisfies
1.2.3 is no longer sufficient on its own.

Fails when: the video shows a chart, a form, or a facial reaction that the narration never
mentions.

### 1.2.6 Sign Language (Prerecorded) (AAA, 2.0)

Intent: sign language interpretation for prerecorded audio, because sign language is a
first language for many Deaf people and captions are read in a second language.

### 1.2.7 Extended Audio Description (Prerecorded) (AAA, 2.0)

Intent: where pauses in the audio are too short for description, the video pauses to allow
extended description.

### 1.2.8 Media Alternative (Prerecorded) (AAA, 2.0)

Intent: a full text alternative for all prerecorded synchronized media.

### 1.2.9 Audio-only (Live) (AAA, 2.0)

Intent: a text alternative for live audio-only content.

## Guideline 1.3 Adaptable

### 1.3.1 Info and Relationships (A, 2.0)

Intent: structure and relationships conveyed visually are also conveyed in markup, so
assistive technology can present them. This is the most frequently failed criterion in
practice and the one that most rewards careful reading.

Test: turn off styles, or read the accessibility tree. Every visual grouping, heading,
list, table relationship, and label association must survive.

Fails when:
- Headings are styled `div`s or bold paragraphs, so no heading structure exists.
- Heading levels skip or are chosen for size rather than hierarchy.
- Lists are built from paragraphs with bullet characters or `<br>`.
- Data tables lack `<th>`, `scope`, or a caption, or layout tables carry header markup.
- Form fields are labeled by proximity only, with no `<label for>`, `aria-label`, or
  `aria-labelledby`.
- Required fields are marked only with a red asterisk and no programmatic `required`.
- Related radio buttons or checkboxes are not wrapped in a `fieldset` with a `legend`.
- Emphasis is conveyed by color or size alone with no `<strong>`, `<em>`, or equivalent.
- Regions are not identifiable: no `<main>`, `<nav>`, `<header>`, `<footer>` or equivalent
  landmark roles.

### 1.3.2 Meaningful Sequence (A, 2.0)

Intent: when the order of content affects its meaning, a correct reading order is
programmatically determinable.

Test: read the DOM order, or tab through, and compare with the visual order.

Fails when: CSS `order`, `grid-area`, `float`, or absolute positioning reorders content
visually so that the DOM order no longer makes sense; a multi-column layout is built from
positioned blocks that read across rather than down; a PDF's tag order does not match the
visual layout.

### 1.3.3 Sensory Characteristics (A, 2.0)

Intent: instructions do not depend solely on shape, size, position, orientation, or sound.

Fails when: "click the round button on the right", "see the box below", "fields marked in
red". Add a name, a label, or a text cue alongside the sensory reference.

### 1.3.4 Orientation (AA, 2.1)

Intent: content does not lock to portrait or landscape unless a specific orientation is
essential.

Fails when: a mobile web app refuses to render in landscape, which locks out users whose
device is fixed to a wheelchair mount. Essential exceptions include a piano keyboard app or
a bank check capture screen.

### 1.3.5 Identify Input Purpose (AA, 2.1)

Intent: inputs collecting information about the user carry a programmatic purpose, so
browsers and assistive technology can autofill or add familiar icons.

Test: check every field that collects a name, email, phone, address, or payment detail for
a correct `autocomplete` token from the WCAG input purposes list.

Fails when: `autocomplete` is missing, set to `off` on personal data fields, or set to a
token that does not match the field.

### 1.3.6 Identify Purpose (AAA, 2.1)

Intent: the purpose of icons, regions, and controls is programmatically determinable, so
users can substitute familiar symbols or hide non-essential content.

## Guideline 1.4 Distinguishable

### 1.4.1 Use of Color (A, 2.0)

Intent: color is never the only visual means of conveying information, indicating an
action, prompting a response, or distinguishing an element.

Test: view in grayscale. Every distinction must survive.

Fails when: required fields shown only in red; link text distinguished from body text by
color alone with no underline and under 3:1 contrast against the surrounding text; chart
series identified only by legend color; status shown by a colored dot with no text or shape.

### 1.4.2 Audio Control (A, 2.0)

Intent: audio that plays automatically for more than three seconds can be paused, stopped,
or its volume controlled independently of the system volume.

This criterion applies to the whole page under the non-interference conformance
requirement, even to content that is not otherwise relied upon.

### 1.4.3 Contrast (Minimum) (AA, 2.0)

Intent: text has a contrast ratio of at least 4.5:1 against its background, or 3:1 for
large text (18pt, or 14pt bold, which is 24px and 18.66px at default sizing).

Test: run `scripts/contrast.py` on the computed foreground and background. Do not estimate
ratios by eye or by arithmetic in your head.

Fails when: placeholder text and helper text sit at low contrast; text sits over a
photograph or gradient where some regions fail; disabled-looking but active controls fall
below the threshold; light gray on white for secondary text.

Exempt: genuinely inactive controls, pure decoration, text in a logotype, and text that is
part of a picture containing significant other content.

### 1.4.4 Resize Text (AA, 2.0)

Intent: text can be resized to 200 percent without assistive technology, with no loss of
content or function.

Test: set browser zoom to 200 percent, and separately increase only the text size where the
browser supports it.

Fails when: fixed-height containers clip text; absolute `px` sizing inside fixed-size boxes
causes overlap; a viewport meta tag sets `user-scalable=no` or `maximum-scale=1`.

### 1.4.5 Images of Text (AA, 2.0)

Intent: use real text rather than pictures of text, unless the presentation is essential or
the image is customizable.

Fails when: headings, quotes, or infographics with substantive text are shipped as images;
marketing banners carry the offer only in a JPEG.

### 1.4.6 Contrast (Enhanced) (AAA, 2.0)

Intent: 7:1 for body text, 4.5:1 for large text.

### 1.4.7 Low or No Background Audio (AAA, 2.0)

Intent: background sound in speech audio is at least 20 dB below the speech, or can be
turned off.

### 1.4.8 Visual Presentation (AAA, 2.0)

Intent: users can select foreground and background colors, line length stays at or below 80
characters, text is not justified, line spacing is at least 1.5 within paragraphs, and text
resizes to 200 percent without horizontal scrolling.

### 1.4.9 Images of Text (No Exception) (AAA, 2.0)

Intent: images of text are used only for pure decoration or where the presentation is
essential.

### 1.4.10 Reflow (AA, 2.1)

Intent: content reflows into a single column without two-dimensional scrolling at 320 CSS
pixels wide, which corresponds to 400 percent zoom on a 1280 pixel viewport.

Test: set the browser to 1280 pixels wide and zoom to 400 percent, or set the viewport to
320 by 256 CSS pixels. Scroll in one direction only.

Fails when: fixed-width containers, wide tables without a scroll container, sticky headers
that consume the viewport, or absolute positioning force horizontal scrolling.

Exempt: content requiring two-dimensional layout for use or meaning, such as data tables,
maps, diagrams, and code blocks.

### 1.4.11 Non-text Contrast (AA, 2.1)

Intent: 3:1 contrast for the parts of user interface components needed to identify them,
and for graphical objects needed to understand the content.

Test: check control boundaries, focus indicators, toggle states, form field borders, icon
glyphs that carry meaning, and chart elements. Run `scripts/contrast.py` on each pair.

Fails when: input borders are a pale gray on white; a focus ring is a light outline on a
light background; a toggle's on and off states differ only by a low-contrast fill; chart
series colors are indistinguishable against the plot background.

### 1.4.12 Text Spacing (AA, 2.1)

Intent: no loss of content or function when the user overrides line height to 1.5 times the
font size, paragraph spacing to 2 times, letter spacing to 0.12 times, and word spacing to
0.16 times.

Test: apply that override with a bookmarklet or dev tools and look for clipping and
overlap.

Fails when: fixed-height buttons and cards clip their labels; `overflow: hidden` on a
text container truncates the text.

### 1.4.13 Content on Hover or Focus (AA, 2.1)

Intent: additional content triggered by hover or focus is dismissable without moving the
pointer, hoverable so the pointer can travel into it, and persistent until dismissed or no
longer valid.

Fails when: a tooltip disappears when the pointer moves toward it, so it cannot be read by
someone using magnification; a custom tooltip cannot be dismissed with Escape; a hover menu
vanishes before a user with a tremor can reach it.
