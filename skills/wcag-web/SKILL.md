---
name: wcag-web
description: "Audit or fix accessibility on web pages, web apps, and UI components against WCAG 2.2, from a live URL or from source in any framework. Covers keyboard operation, focus management, ARIA, forms and errors, contrast, reflow, and target size. Load whenever someone asks whether a page or component is accessible, mentions axe, Lighthouse, screen readers, alt text, ARIA, focus traps, or color contrast, or asks to make a page WCAG or Section 508 compliant."
license: MIT
allowed-tools: Read, Grep, Glob, Bash, WebFetch, Write, Edit
---

# Web accessibility: audit and remediation

Read `../wcag/SKILL.md` first if you have not. It sets the mode, the finding record, and
the report shape.

Audit is the default here as everywhere. If the user asked a question rather than for
fixes, report and change nothing. This skill carries edit permissions because it also
describes remediation, not because auditing may edit.

This file covers what is specific to the web.

## Work out what you can actually test

Your leverage depends on what you can reach, and it decides which criteria you can honestly
assess.

**A live URL with a browser** is the strongest position. Run `scripts/axe_scan.py URL
--json`, then test by hand what it cannot see. If Playwright is missing, try installing it
once (`pip install playwright && playwright install chromium`); if that fails, drop to the
source path and say so in the report.

**Source only** means no computed styles, no rendered accessibility tree, no runtime
behaviour. Run `scripts/html_audit.py` over the templates, read the components, and mark
contrast, reflow, focus visibility and target size not tested unless the stylesheets settle
them.

**A pasted snippet** supports structural findings only. Say so in one line rather than
implying the page was reviewed.

For a framework codebase the output is generated, so read the components that produce it:
the button primitive, the modal, the form field wrapper, the data table, the menu. One fix
in a design-system primitive removes the same finding from every page, which is why
component-level auditing beats page-level auditing on anything with a component library.

## Run the tools first

The commands below use paths relative to the plugin root. The core skill's "Find the bundled scripts" section explains how to locate it when the working directory is elsewhere.

```bash
# Live page, default WCAG 2.2 A and AA rule sets
python3 scripts/axe_scan.py https://example.com --json > axe.json

# Same page at a narrow viewport, which surfaces reflow and target-size problems
python3 scripts/axe_scan.py https://example.com --viewport 320x800 --json > axe-320.json

# Source templates, no browser needed
python3 scripts/html_audit.py "src/**/*.html" --json > static.json

# Any color pair you are unsure about
python3 scripts/contrast.py "#6b7280" "#f9fafb" --size 14px
```

The two scanners overlap only partially. `axe_scan.py` sees the rendered result, computed
contrast, and runtime-built DOM. `html_audit.py` sees source patterns that survive into
every rendered page and points at the file and line where the fix goes. Running both on a
codebase with a live environment is worth the extra minute.

Then merge and report:

```bash
python3 scripts/report.py axe.json static.json --title "Checkout" --level AA --out audit.md
```

## Then test what the tools cannot

Budget most of your time here. Work through these in order, because the early ones find
the failures that make everything else moot.

### Keyboard, start to finish

Put the mouse down and complete every task on the page. Tab, Shift+Tab, Enter, Space,
arrows, Escape, Home and End in composite widgets.

Watch for: elements that never receive focus; focus that disappears entirely; focus that
jumps somewhere unrelated; a modal that leaves focus behind it on the page; a dialog that
does not return focus to its trigger on close; anything that can only be reached by
hovering; a component that traps focus with no documented escape (2.1.1, 2.1.2, 2.4.3,
2.4.7).

New in 2.2, and easy to miss: tab through the page with the sticky header, sticky footer,
cookie banner, and chat widget all present, and watch whether the focused element slides
underneath any of them (2.4.11).

### Screen reader pass

If a screen reader is available, use it. If not, read the accessibility tree and say in the
report that no screen reader was run.

Check the landmark structure, then the heading outline, then tab through the interactive
elements listening to what each announces. Every control should announce a role, a name
that matches its visible label, and its current state. A control that announces "button" and
nothing else is a critical finding regardless of what the code looks like (4.1.2, 2.5.3).

### Forms and errors

Submit the form empty. Submit it wrong. Then ask what a person using a screen reader
learns from the failure.

Errors must be identified in text, name the field, and say how to fix it, and they must
reach a screen reader user without the user hunting for them, through a live region or a
focus move (3.3.1, 3.3.3, 4.1.3). Check that every field has a persistent visible label
rather than a placeholder (3.3.2), that personal-data fields carry the right `autocomplete`
token (1.3.5), and that a multi-step flow does not ask twice for what it already has
(3.3.7).

On authentication specifically: try pasting into the password field and the one-time-code
field. Blocking paste, or disabling autocomplete on credentials, fails 3.3.8, and it is one
of the most common failures on otherwise careful sites.

### Zoom, reflow, and spacing

Set the browser to 1280 pixels wide and zoom to 400 percent. Content should reflow to a
single column with no horizontal scrolling (1.4.10). Separately, zoom text to 200 percent
and look for clipping (1.4.4). Then apply the text-spacing override and look again (1.4.12).

Fixed-height containers and `overflow: hidden` cause most failures here, and they show up
only at those settings.

### Pointer and target size

Measure the small controls: icon buttons, close buttons on toasts, table row actions,
pagination. Below 24 by 24 CSS pixels they need the spacing exception to pass 2.5.8.

Then look for anything that only works by dragging (2.5.7), only by a path gesture such as
swipe or pinch (2.5.1), or that fires on the down event with no way to abort (2.5.2).

### Motion, media, and time

Anything that autoplays with sound, or moves for more than five seconds without a pause
control, breaks conformance for the whole page under the non-interference requirement
(1.4.2, 2.2.2). Check `prefers-reduced-motion` is respected. See `../../references/media.md`
for captions and audio description.

## Framework-specific traps

Read `references/frameworks.md` for the details. The recurring ones:

- Client-side routing that never updates `document.title` or moves focus after navigation,
  so a screen reader user does not know the page changed (2.4.2, 2.4.3).
- Component libraries whose `Button` renders a `div` when given an `href` or an `as` prop.
- `useEffect` focus management that runs before the element exists, silently doing nothing.
- Portals and modals rendered outside the DOM order, so focus containment has to be
  written by hand.
- CSS-in-JS `outline: none` resets inherited from a normalize layer (2.4.7).
- Virtualized lists that remove focused rows from the DOM while focus is on them.
- Icon component libraries that render `<svg>` with no `aria-hidden` and no name, which
  fills the tab order and the accessibility tree with noise.

## ARIA, used sparingly

The first rule of ARIA is not to use it. A native `<button>`, `<a href>`, `<input>`,
`<select>`, `<details>` or `<dialog>` arrives with role, name computation, keyboard
behaviour, focus and state already correct. Every ARIA attribute is a promise you then have
to keep in JavaScript, and a half-kept promise is worse than none: a `role="checkbox"` that
never updates `aria-checked` reports the wrong state rather than no state.

When a custom widget is unavoidable, implement the full keyboard interaction pattern, not
just the roles. `references/aria-patterns.md` has the interaction contracts for dialog,
disclosure, tabs, combobox, menu, tooltip and data grid.

Report as findings: ARIA references pointing at ids that do not exist, `aria-hidden="true"`
on something still focusable, roles applied without their required properties, an
`aria-label` that contradicts the visible text (2.5.3), and `role="presentation"` on
something interactive.

## When remediating

Read `../wcag-remediate/SKILL.md` for the ordering and safety rules. Web-specific notes:

- Fix the component, not the page. A finding that appears 40 times is usually one component.
- Prefer deleting ARIA and using the native element over adding more ARIA.
- Never add an accessible name that differs from the visible label. That trades one failure
  for a 2.5.3 failure and breaks voice control.
- Never add `alt` text you cannot justify from the surrounding content. If you cannot tell
  what an image conveys, say so and leave it for the content owner. An invented description
  is worse than a reported gap, because it looks fixed.
- Re-run the scanners after the change, and re-do the keyboard pass on anything where you
  touched focus.
