---
name: wcag-remediate
description: "Apply accessibility fixes safely after an audit, in source code or directly in a Word, PowerPoint, Excel, or PDF file. Covers what order to fix in, which fixes are derivable and which need the content owner, the authoring application, or a rebuild, the anti-patterns that satisfy a checker while making things worse, what to do when a fix cannot be applied, and how to verify and record each change. Load before editing anything for accessibility reasons: whenever the user asks to fix, remediate, correct, or resolve accessibility issues, make something WCAG or Section 508 compliant, add alt text, or apply an audit's findings."
license: MIT
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, WebFetch
---

# Remediation: fixing without breaking

Read `../wcag/SKILL.md` first if you have not, and the format skill for the target. This
file governs the act of changing things, whether the thing is a source file under version
control or a document on someone's desk.

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
are not reversible if it is not. A document on a desktop usually has no version control at
all, which makes the next rule the one that protects the user.

**Work on a copy and never write over the original.** Write beside it, hand back the new
file, and leave the original where it was until the person has seen the result. This holds
for every binary document, and it is the only thing standing between a failed pass and a
lost afternoon.

**Know what your tools drop.** `../../references/desktop-agents.md` covers the round trips
that damage documents, the libraries that do not preserve what they do not model, and the
files that cannot be opened at all. Establish this before you promise a fix.

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
- Marking a decorative image as decorative, where the format expresses it, such as
  an empty `alt` in HTML or an artifact in a PDF. Word and PowerPoint do not, and are
  covered below.
- Adding an `autocomplete` token that matches the field.
- Setting document language, title, and tab order in a PDF.
- Setting the document title and language, marking a table's first row as its header row,
  and writing alternative text you were given, in a Word, PowerPoint, or Excel file.
  `scripts/office_remediate.py` applies these four to a copy and rewrites only the XML
  parts it changes:

```bash
python3 scripts/office_remediate.py report.docx \
    --title auto --language en-GB --table-headers --alt-text alt.json
```

**Needs the content owner**, because the right answer is information you do not have:

- Alt text for an image whose content you cannot determine. Guessing produces something
  that looks fixed and is not, which is worse than an open finding because nobody will look
  again.
- Captions or transcripts for media.
- Rewriting heading text or link text where you do not know what the section or destination
  contains.
- Error messages that must say what the business rule was.
- Any change to what the content says.

**Needs the authoring application**, because the file format has no place to put the fix or
because getting it right needs the tool's own view:

- Marking an image decorative, which Word and PowerPoint record in a way their own alt text
  pane writes and nothing outside reliably can. An empty alt is not the same thing.
- Adding a slide title where the layout carries no title placeholder.
- Reading order on a slide, where the mechanism is reachable and the judgement is not.
- Anything in a template that lives in a corporate library.

If you can drive the application, these become fixes you can make, and you should say so.
`../wcag-documents/references/office-remediation.md` gives each one both ways: the path
through the application's menus, and the change in the file.

**Needs a design decision**:

- Contrast fixes, which change the visual design. Propose specific values that pass, with
  the measured ratios, and let the designer choose.
- Target size increases that change the layout.
- Adding visible labels where the design used placeholders only.
- Alternatives to gesture-only interactions.

Say which bucket each finding falls into, and use the same words the audit used, so a
reader can match them up: `direct`, `app`, `recreate`, `owner`, `design`. A remediation
report that closes 30 findings and names 6 that need the author is more useful than one
that closes 36 with invented content.

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

## When a fix will not apply

A pass fails when a fix cannot be applied, when it applies and the re-audit shows it did
not take, or when applying it damaged the file. `scripts/office_remediate.py` exits 1 in
the first case and names what failed. A file that cannot be opened at all is the same
answer arriving earlier.

A finding you were never going to close is not a failure. Anything marked `owner`, `design`,
or `app` that you cannot reach was reported, not attempted, and it belongs in the record
rather than in this rule.

**Stop the pass on that document.** Do not try a third approach on the same fix, and do not
carry on to the next fix as though nothing happened. A half-patched document is the worst
thing to hand back, because it looks repaired and is not, and whoever checks it next will
check the parts you changed rather than the part that failed.

Then, in this order:

1. Say what failed and why, in a sentence or two. Name the fix, the criterion, and the
   reason the file would not take it.
2. Say where the partial copy is, and that it is not the deliverable. The original is
   untouched, which is why this is recoverable.
3. Say what is still fixed and what is not, so the user can see what the pass bought.
4. **Recommend recreating the document**, with what that would cost and what it would lose.
   `../wcag-recreate/SKILL.md` covers the rebuild and the inventory of what does not
   survive one.
5. Wait for the answer.

**Auto-recreate.** A user who does not want to be asked can say so in advance, with
`--auto-recreate` on `/wcag-fix` or in their own words: "if patching fails just rebuild
it". Then you go straight into recreate mode on a failed pass without stopping to ask.

It changes who decides, not what happens. You still say the pass failed, still say why,
still name what the rebuild loses before it is lost, and still produce both records. An
auto-recreate that arrives as a finished file with no account of why the original could not
be repaired has taken a decision away from the user rather than saving them a question.

Without that instruction, ask. A rebuild is not a heavier version of a fix. It is a
different document, and the person who has to live with it decides.

## Verify each fix

A remediation that is not verified is a claim, not a change.

For each fix, or each batch of related fixes:

1. Re-run the tool that found it. `scripts/html_audit.py`, `scripts/axe_scan.py`,
   `scripts/pdf_audit.py`, or `scripts/office_audit.py` on the changed target.
2. Test what the tool cannot see. If you touched focus, tab through it. If you touched a
   name, check the accessibility tree. If you touched a PDF's structure, read it in order.
3. Check you did not break something else. Contrast changes affect other states, hover and
   focus among them. Focus changes affect modals and menus. Heading changes affect the
   outline.
4. Run the project's own tests and linters if the target is code. For a document, run the
   application's own accessibility checker where you can reach it, since it is the
   vocabulary the document owner will use, and open the file to confirm it still looks
   right. `../../references/builtin-checkers.md` covers what those checkers do and do not
   see.
5. For a document, confirm you changed only what you meant to. Compare the new file against
   the original on the parts that should not have moved: the text, the image count, the
   table count, the slide or sheet count.

Do not batch 40 changes and verify once at the end. When something regresses, you will not
know which change did it.

## Record what changed

Produce a remediation record alongside the changes. It goes to whoever signs off, and it is
what the next audit reads first. Five sections:

**Fixed**, as a table of finding, criterion, what changed, which files, and how you
verified it. **Needs the content owner**, naming what is needed and from whom. **Needs a
design decision**, with specific options and their measured values. **Not fixed, with
reasons**, including anything that needs the authoring application and anything that failed
to apply. **Still unverified**, saying what could not be confirmed in this environment and
what a person must check.

For a document, say where the new file is and that the original is unchanged. Someone has
to know which of the two to circulate.

The last two are what make the record trustworthy. A remediation report with no unfixed
items and no unverified items usually means nobody looked hard.

## After remediation

Re-audit rather than assuming the findings are closed. The re-audit is shorter, because
scope and method are already established, and it is the artifact that supports any claim
about the current state.

State the position accurately. "23 of 29 findings resolved, 6 awaiting content" is
credible. "Now WCAG compliant" is not, unless every criterion at the level was verified
across every page in scope and every step of the processes in scope.
