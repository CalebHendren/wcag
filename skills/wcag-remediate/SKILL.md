---
name: wcag-remediate
description: "Apply accessibility fixes safely after an audit, for any format. Covers what order to fix in, which fixes are derivable and which need the content owner, the anti-patterns that satisfy a checker while making things worse, and how to verify and record each change. Load before editing anything for accessibility reasons: whenever the user asks to fix, remediate, correct, or resolve accessibility issues, make something WCAG or Section 508 compliant, add alt text, or apply an audit's findings."
license: MIT
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, WebFetch
---

# Remediation: fixing without breaking

Read `../wcag/SKILL.md` first if you have not, and the format skill for the target. This
file governs the act of changing things.

Remediation is where accessibility work goes wrong. The failure is rarely a fix that does
not work. It is a fix that satisfies a checker while leaving the user worse off: alt text
that says nothing, an ARIA label that contradicts the button, a role added without the
keyboard behavior it promises. A page can go from 40 automated errors to zero and become
harder to use.

Everything below exists to prevent that.

## Before changing anything

**Confirm you were asked.** Remediation edits files. If the user asked a question, answer
it and offer the fixes. Editing on an ambiguous request is the one mistake here that is
expensive to undo.

**Have an audit.** Fixing without one means fixing what is easy to see rather than what
matters. If no audit exists, run one first, then bring the findings here.

**Check the working tree is clean and version controlled**, or say plainly that the changes
are not reversible if it is not. For a binary document, work on a copy.

**Agree the scope.** Say which findings you will fix, which you will leave, and why. A
finding needing content the author must supply is not yours to close.

## What to fix first

Work in this order. It front-loads the changes that unblock users and back-loads the ones
that are cosmetic.

1. **Blockers.** Anything that stops a task being completed: keyboard traps, unnamed submit
   controls, authentication that cannot be completed, flashing content. Every hour these
   stay is an hour someone cannot use the product.
2. **Shared components.** One fix in a design-system button, form field, modal, or table
   removes the same finding everywhere. Fixing pages one at a time when a component is the
   cause wastes the budget and leaves the next page broken.
3. **Structural fixes** that other fixes depend on: document tagging, reading order,
   heading structure, landmarks. Alt text applied before reading order is fixed gets moved
   around by the reordering.
4. **The rest by severity**, using `../../references/severity.md`.
5. **Advisories last**, and only with the user's agreement, since they are not failures.

## Fixes you can make, and fixes you cannot

**Safe to apply directly**, because the correct value is derivable from the code or the
content in front of you:

- Associating an existing visible label with its field.
- Adding `lang` to a document whose language is evident.
- Replacing a `div` click handler with a `button`.
- Adding `scope` to header cells in a simple table.
- Adding a `title` to an iframe whose content you can identify.
- Correcting an ARIA reference that points at a renamed id.
- Removing `outline: none` and adding a visible focus style.
- Fixing a heading level to remove a skip.
- Marking a decorative image as decorative.
- Adding an `autocomplete` token that matches the field.
- Setting document language, title, and tab order in a PDF.

**Needs the content owner**, because the right answer is information you do not have:

- Alt text for an image whose content you cannot determine. Guessing produces something
  that looks fixed and is not, which is worse than an open finding because nobody will look
  again.
- Captions or transcripts for media.
- Rewriting heading text or link text where you do not know what the section or destination
  contains.
- Error messages that must say what the business rule was.
- Any change to what the content says.

**Needs a design decision**:

- Contrast fixes, which change the visual design. Propose specific values that pass, with
  the measured ratios, and let the designer choose.
- Target size increases that change the layout.
- Adding visible labels where the design used placeholders only.
- Alternatives to gesture-only interactions.

Say which bucket each finding falls into. A remediation report that closes 30 findings and
names 6 that need the author is more useful than one that closes 36 with invented content.

## Anti-patterns to avoid

These all satisfy an automated checker and make the experience worse. Do not produce them,
and report them as findings when you see them.

**Alt text that says nothing.** `alt="image"`, `alt="chart"`, `alt=""` on an informative
image. The checker sees an attribute; the user gets nothing. If you cannot describe it,
say so.

**An accessible name that contradicts the visible label.** A button reading "Send" with
`aria-label="Submit form"` fails 2.5.3 and breaks voice control, because the user says what
they see and nothing happens. The accessible name must contain the visible text.

**A role without its behavior.** `role="button"` on a `div` with no `tabindex` and no key
handler is worse than the plain `div`, because it now announces as a button that cannot be
pressed. If you add a role, implement the whole pattern.

**`tabindex` sprayed on to make things focusable.** Positive values wreck the order.
Focusable non-interactive elements create empty stops. Make the interactive things
interactive instead.

**`aria-hidden` to silence a warning.** Hiding a control that users need is a worse failure
than the one being reported.

**Accessibility overlays and widget scripts.** They do not fix the underlying content, they
frequently interfere with the user's own assistive technology, and their presence has
featured in litigation rather than preventing it. If a client asks about one, say plainly
that the fixes belong in the content.

**Skip links that go nowhere.** A skip link needs a target with `tabindex="-1"` so focus
actually lands, otherwise it only scrolls and keyboard focus stays where it was.

**Empty live regions added at the moment of the announcement.** The container must exist
first, or nothing is announced.

**Bulk find-and-replace on alt text or labels.** Every image is different. A script that
sets the same alt on 200 images has created 200 new findings.

## Verify each fix

A remediation that is not verified is a claim, not a change.

For each fix, or each batch of related fixes:

1. Re-run the tool that found it. `scripts/html_audit.py`, `scripts/axe_scan.py`, or
   `scripts/pdf_audit.py` on the changed target.
2. Test what the tool cannot see. If you touched focus, tab through it. If you touched a
   name, check the accessibility tree. If you touched a PDF's structure, read it in order.
3. Check you did not break something else. Contrast changes affect other states, hover and
   focus among them. Focus changes affect modals and menus. Heading changes affect the
   outline.
4. Run the project's own tests and linters if the target is code.

Do not batch 40 changes and verify once at the end. When something regresses, you will not
know which change did it.

## Record what changed

Produce a remediation record alongside the changes. It goes to whoever signs off, and it is
what the next audit reads first. Five sections:

**Fixed**, as a table of finding, criterion, what changed, which files, and how you
verified it. **Needs the content owner**, naming what is needed and from whom. **Needs a
design decision**, with specific options and their measured values. **Not fixed, with
reasons.** **Still unverified**, saying what could not be confirmed in this environment and
what a person must check.

The last two are what make the record trustworthy. A remediation report with no unfixed
items and no unverified items usually means nobody looked hard.

## After remediation

Re-audit rather than assuming the findings are closed. The re-audit is shorter, because
scope and method are already established, and it is the artifact that supports any claim
about the current state.

State the position accurately. "23 of 29 findings resolved, 6 awaiting content" is
credible. "Now WCAG compliant" is not, unless every criterion at the level was verified
across every page in scope and every step of the processes in scope.
