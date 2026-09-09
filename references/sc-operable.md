# WCAG 2.2 success criteria: Operable

User interface components and navigation must be operable. 35 criteria across five
guidelines. Three of them are new in WCAG 2.2 and two more were added in 2.1, so this
principle is where recent obligations concentrate.

## Contents

- [Guideline 2.1 Keyboard Accessible](#guideline-21-keyboard-accessible)
- [Guideline 2.2 Enough Time](#guideline-22-enough-time)
- [Guideline 2.3 Seizures and Physical Reactions](#guideline-23-seizures-and-physical-reactions)
- [Guideline 2.4 Navigable](#guideline-24-navigable)
- [Guideline 2.5 Input Modalities](#guideline-25-input-modalities)

## Guideline 2.1 Keyboard Accessible

### 2.1.1 Keyboard (A, 2.0)

Intent: all functionality is operable through a keyboard interface, without requiring
specific timings for individual keystrokes.

Test: unplug the mouse. Complete every task using Tab, Shift+Tab, Enter, Space, the arrow
keys, and Escape. This single test finds more real failures than any automated scan.

Fails when: click handlers sit on `div` or `span` with no `tabindex` and no key handler;
custom dropdowns, sliders, carousels, and drag-and-drop have no keyboard path; hover-only
menus never open on focus; a canvas or map widget captures the pointer only.

### 2.1.2 No Keyboard Trap (A, 2.0)

Intent: if keyboard focus can move to a component, it can move away using the keyboard
alone, and the user is told how if a non-standard key is required.

This criterion applies to the whole page under the non-interference conformance
requirement.

Fails when: a modal keeps focus inside after it should close; an embedded plugin or iframe
swallows Tab; a rich text editor captures Tab with no documented escape.

### 2.1.3 Keyboard (No Exception) (AAA, 2.0)

Intent: 2.1.1 with no exception for functions that require path-dependent input.

### 2.1.4 Character Key Shortcuts (A, 2.1)

Intent: single-character shortcuts can be turned off, remapped, or are active only on
focus.

Fails when: a web app binds `s`, `j`, `k`, or `/` globally, so speech input users trigger
actions while dictating.

## Guideline 2.2 Enough Time

### 2.2.1 Timing Adjustable (A, 2.0)

Intent: users can turn off, adjust, or extend any time limit, with the exceptions of
real-time events, essential limits, and limits longer than 20 hours.

Fails when: a session expires silently; a checkout holds inventory for 10 minutes with no
extension; a carousel advances before someone can read a slide (see also 2.2.2).

### 2.2.2 Pause, Stop, Hide (A, 2.0)

Intent: moving, blinking, or scrolling content lasting more than five seconds can be
paused, stopped, or hidden. Auto-updating content can be paused or its frequency
controlled.

This criterion applies to the whole page under the non-interference conformance
requirement.

Fails when: hero carousels autoplay with no pause control; background video loops with no
control; a live ticker updates continuously with no stop.

### 2.2.3 No Timing (AAA, 2.0)

Intent: timing is not essential to any event or activity except non-interactive
synchronized media and real-time events.

### 2.2.4 Interruptions (AAA, 2.0)

Intent: interruptions can be postponed or suppressed except in an emergency.

### 2.2.5 Re-authenticating (AAA, 2.0)

Intent: when a session expires, the user can continue without losing data after
re-authenticating.

### 2.2.6 Timeouts (AAA, 2.1)

Intent: users are warned about any inactivity timeout that could cause data loss, unless
the data is preserved for more than 20 hours.

## Guideline 2.3 Seizures and Physical Reactions

### 2.3.1 Three Flashes or Below Threshold (A, 2.0)

Intent: nothing flashes more than three times per second, or the flash stays below the
general flash and red flash thresholds.

This criterion applies to the whole page under the non-interference conformance
requirement. Photosensitive seizures are the one accessibility failure that can cause
immediate physical harm, so treat any candidate as critical severity.

Fails when: rapid strobing in video or animated GIFs; a loading spinner that flickers at
high frequency across a large area.

### 2.3.2 Three Flashes (AAA, 2.0)

Intent: no content flashes more than three times per second, with no threshold exception.

### 2.3.3 Animation from Interactions (AAA, 2.1)

Intent: motion animation triggered by interaction can be disabled unless the animation is
essential. Respect `prefers-reduced-motion`.

## Guideline 2.4 Navigable

### 2.4.1 Bypass Blocks (A, 2.0)

Intent: a mechanism exists to skip blocks of content repeated across pages.

Test: press Tab from the address bar on a fresh page load. A skip link should appear and
should move focus, not just scroll.

Fails when: no skip link and no landmark structure; a skip link is present but hidden from
keyboard focus; the skip target has no `tabindex="-1"` so focus never lands on it.

### 2.4.2 Page Titled (A, 2.0)

Intent: pages have titles that describe topic or purpose.

Fails when: every page in a single-page app keeps the same `<title>` after routing;
templates ship with "Untitled" or the site name alone.

### 2.4.3 Focus Order (A, 2.0)

Intent: when the order of focus affects meaning or operability, focus moves in an order
that preserves meaning and operability.

Fails when: a modal opens without moving focus into it; closing a modal drops focus to the
top of the page instead of returning to the trigger; positive `tabindex` values create an
order unrelated to the layout; newly revealed content appears before the current focus
point with no focus management.

### 2.4.4 Link Purpose (In Context) (A, 2.0)

Intent: the purpose of each link is determinable from the link text alone or from its
programmatically determinable context.

Fails when: repeated "Read more" and "Click here" links whose only distinguishing context
is visual proximity; links whose accessible name is the raw URL; icon links with no name.

### 2.4.5 Multiple Ways (AA, 2.0)

Intent: more than one way to locate a page within a set, unless the page is a step in a
process.

Fails when: a site offers navigation only, with no search, sitemap, or index.

### 2.4.6 Headings and Labels (AA, 2.0)

Intent: headings and labels describe topic or purpose. This is about quality, not presence.

Fails when: headings read "Section 1", "More information", or repeat the same text down the
page; form labels say "Input" or "Field".

### 2.4.7 Focus Visible (AA, 2.0)

Intent: any keyboard-operable interface has a visible focus indicator.

Fails when: a stylesheet sets `outline: none` with no replacement; a custom focus style is
applied on `:hover` but not `:focus-visible`; the indicator is invisible against a dark
section of a gradient.

### 2.4.8 Location (AAA, 2.0)

Intent: information about the user's location within a set of pages is available, such as a
breadcrumb trail.

### 2.4.9 Link Purpose (Link Only) (AAA, 2.0)

Intent: link purpose is determinable from the link text alone, with no reliance on context.

### 2.4.10 Section Headings (AAA, 2.0)

Intent: section headings organize content.

### 2.4.11 Focus Not Obscured (Minimum) (AA, 2.2) [new in 2.2]

Intent: when a component receives keyboard focus, it is not entirely hidden by
author-created content.

Test: tab through the whole page with a sticky header, sticky footer, and any cookie banner
present. Watch for focused elements sliding under them.

Fails when: a sticky header covers the focused link as the page scrolls it into view; a
cookie consent bar hides the focused control at the bottom of the viewport; a chat widget
overlays focused content.

### 2.4.12 Focus Not Obscured (Enhanced) (AAA, 2.2) [new in 2.2]

Intent: no part of the focused component is hidden by author-created content.

### 2.4.13 Focus Appearance (AAA, 2.2) [new in 2.2]

Intent: the focus indicator is at least as large as a 2 CSS pixel perimeter of the
component and has at least 3:1 contrast between focused and unfocused states.

## Guideline 2.5 Input Modalities

### 2.5.1 Pointer Gestures (A, 2.1)

Intent: functionality using multipoint or path-based gestures can also be operated with a
single pointer without a path-based gesture, unless the gesture is essential.

Fails when: a carousel advances only by swipe; a map zooms only by pinch; a signature field
is the only way to proceed and no alternative exists. Note that a signature is essential,
but a swipe carousel is not.

### 2.5.2 Pointer Cancellation (A, 2.1)

Intent: for single-pointer functions, the action does not complete on the down event, or it
can be aborted or undone.

Fails when: a button fires on `mousedown` or `touchstart`, so a user who presses the wrong
control cannot slide off to cancel.

### 2.5.3 Label in Name (A, 2.1)

Intent: for components with a visible text label, the accessible name contains the visible
text.

Test: compare the visible label with the accessible name in the accessibility tree. This
decides whether speech input users can operate the control by saying what they see.

Fails when: a button reads "Submit" but carries `aria-label="Send form"`; an icon plus text
control has an `aria-label` describing only the icon; the accessible name reorders or
paraphrases the visible words.

### 2.5.4 Motion Actuation (A, 2.1)

Intent: functionality operated by device motion or user motion can also be operated by
interface components, and motion actuation can be disabled.

Fails when: shake to undo is the only undo; a form submits by tilting the device.

### 2.5.5 Target Size (Enhanced) (AAA, 2.1)

Intent: pointer targets are at least 44 by 44 CSS pixels.

### 2.5.6 Concurrent Input Mechanisms (AAA, 2.1)

Intent: content does not restrict use of input modalities available on a platform.

### 2.5.7 Dragging Movements (AA, 2.2) [new in 2.2]

Intent: any function that uses a dragging movement can be achieved with a single pointer
without dragging, unless dragging is essential.

Fails when: a kanban board moves cards only by drag; a range slider has no click-to-set or
keyboard alternative; a file upload accepts only drag and drop; a reorderable list offers
no up and down controls.

### 2.5.8 Target Size (Minimum) (AA, 2.2) [new in 2.2]

Intent: pointer targets are at least 24 by 24 CSS pixels, unless spacing, an equivalent
control elsewhere, inline position, user agent control, or an essential presentation
applies.

Test: measure the target's bounding box. If it is smaller than 24 by 24, check the spacing
exception: a 24 pixel diameter circle centered on the target must not intersect another
target or another undersized target's circle.

Fails when: icon buttons sized to a 16 pixel glyph with no padding; close buttons in
toasts; dense table row actions packed side by side; pagination links smaller than 24
pixels with no spacing.

Note the exception for links inside a sentence, whose size is constrained by line height.
