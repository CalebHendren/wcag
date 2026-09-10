---
name: wcag-recreate
description: "Rebuild a document as an accessible equivalent when it cannot be repaired in place: untagged PDFs with no source, Word files with no real structure, decks built entirely of floating text boxes, legacy or damaged files. Load when the user asks to recreate, rebuild, redo, or remake a document accessibly, when a remediation pass has failed and patching further would make things worse, or when an audit found the file structurally unfixable. Covers what must be preserved exactly, what is always lost, the parity check before handing it over, and when recreating is the wrong answer because the original is a record."
license: MIT
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, WebFetch
---

# Recreate: rebuilding a document that cannot be repaired

Read `../wcag/SKILL.md` first if you have not, and `../wcag-remediate/SKILL.md`, because
recreate mode is what remediation escalates to rather than an alternative to it.

Some documents cannot be fixed where they are. A PDF with no tags and no source file, a
report whose headings are all bold text on top of Normal, a deck with every slide built
from free-floating boxes, a file the format itself cannot carry the fix into. Patching
those produces something that passes more checks and reads no better, and the effort is
spent again next quarter.

Recreating means building a new file that says exactly what the original said, in the same
order, with the structure the original never had. It is the honest answer often enough to
deserve its own mode, and dangerous enough to need rules, because a rebuild is the one
operation in this skill set that can silently lose a person's content.

## The three ways in

**The user asked.** "Rebuild this accessibly", "make me a clean version", "start it again
properly". Straightforward: confirm the scope and go.

**A remediation pass failed.** `../wcag-remediate/SKILL.md` sets the stop rule. When a fix
cannot be applied, remediation halts and offers recreation rather than trying another
angle. The user either approves, or has already approved by asking for remediation with
auto-recreate on.

**An audit found the file unrepairable.** Findings marked `agent_fix: recreate` say so.
Recommend it, say what it would cost and what it would lose, and wait. An audit never
starts a rebuild on its own.

Whichever door you came through, say so in one line before you touch anything:

> Recreating `report.docx` as `report-accessible.docx`. The original is not modified. The
> new file will carry the same text in the same order, with real heading styles, a header
> row on each table, and alternative text where you supply it.

## What recreate mode guarantees, and what it does not

This is the contract. Everything below serves it, and a rebuild that breaks it is worse
than the inaccessible original.

**The words are preserved exactly.** Every sentence, number, caption, footnote, and cell
value comes across as it was written. Recreating is not editing, not summarizing, and not
tidying. If you think a sentence should change, say so separately and leave it alone.

**The order is preserved.** The new document says things in the order the old one did.
Where the original's reading order was ambiguous, which is often why it is being rebuilt,
choose the order the visual layout implies and record the choice.

**The structure is added.** This is the whole point. Real headings, real lists, real
tables with header rows, real slide titles, a document language, a title.

**The design is approximated, not reproduced.** Fonts, spacing, page breaks, and exact
positions will differ. Say this before you start, because a person expecting a
pixel-identical copy will be unhappy with a correct one.

**Nothing is invented.** No alt text you cannot support, no caption you did not have, no
heading text you made up to fill a level, no data you inferred from a chart image. A
rebuild is the easiest place in this whole skill set to quietly manufacture content, and
the hardest place for anyone to notice.

## Before you start

**Never write over the original.** Write beside it, with a name that says what it is, and
leave the original where it was. The person may need it, the comparison is the only proof
the rebuild is faithful, and an overwritten source cannot be recovered.

**Inventory what the file holds**, so you can say what a rebuild costs before it is spent:

```bash
python3 scripts/office_audit.py original.docx --json | python3 -c "
import json,sys; print(json.load(sys.stdin)['container'])"
```

The `at_risk_in_a_rebuild` list is what to raise. Macros, digital signatures, tracked
changes, comments, embedded objects, SmartArt, and custom XML do not survive a rebuild.
Neither do form field bindings, mail merge fields, cross-reference fields, or a link back to
a SharePoint or Workspace original.

**Say what will be lost and get agreement.** One short list, before the work, not in the
record afterwards. A signature or a set of tracked changes may matter more to the person
than the accessibility problem does.

**Check whether the original is a record.** Some documents are evidence of themselves: a
signed contract, a filed return, a published notice, a court exhibit, an archived edition.
Recreating one does not produce an accessible version of the record. It produces a
different document. For those, build the accessible version as a companion, keep the
original intact and referenced, and say plainly in the record which is which. When you
cannot tell, ask.

## Extract before you build

Read everything out of the original first, into a form you can check against later. Build
from that inventory rather than from the original file directly, because working from an
inventory is what makes the parity check at the end mean something.

Capture, in document order: every block of text with the role it plays (heading and its
level, paragraph, list item, caption, quote, footnote); every table as rows and columns
with which row is the header; every image with its file, its existing alternative text, and
where it sits relative to the text; every link with its text and its target; every slide
with its title, its body content, and its notes; every sheet with its name and its used
range.

Where the original is a PDF, `../wcag-pdf/SKILL.md` covers getting text out in reading
order rather than in page order, and reading order is the thing most likely to be wrong.
Where it is a scan, the text has to be recognised first and OCR output always needs
correction, so scope that honestly and never present recognised text as verified.

Record what you could not extract. A chart image whose data you cannot read, a text box
whose position makes its order ambiguous, a formula that renders as an image. These are the
gaps the record has to name.

## Build it

`references/rebuild-recipes.md` covers each target format: what to build with, the
structure to put in, and the parts that need care. Read the section for the format you are
producing.

Three rules hold across all of them. Build the structure as you go rather than adding it
afterwards, because structure applied at the end is structure that gets missed. Put a
placeholder in for anything you could not extract, marked clearly enough that nobody ships
it by accident, rather than dropping it silently. And build from the template the
organization already uses where one exists, since a rebuild is the cheapest opportunity
anyone will get to fix the template too.

## The parity check

A rebuild is not finished when it opens. It is finished when you have shown it says the
same things. Run this before handing anything over, and put the numbers in the record.

**Content parity.** Extract the plain text of both files and compare. Word counts within a
small margin, every heading present, every table with the same number of rows and columns,
the same number of images, the same number of links with the same targets, the same number
of slides or sheets. Read the differences rather than counting them: a paragraph missing
from the middle is what this catches.

**Order parity.** Read the new document top to bottom against the original. The rebuild is
the moment reading order gets decided, so this is the check that matters most and the one
no tool performs.

**Number parity.** Every figure in a table or a caption, checked against the original
rather than retyped from memory. A rebuilt table with a transposed digit is a worse
document than the one you started with.

**Accessibility parity, in the direction of better.** Re-audit the new file. It should have
the structure the original lacked, and it should not have introduced anything new.

```bash
python3 scripts/office_audit.py original.docx --json > before.json
python3 scripts/office_audit.py rebuilt.docx  --json > after.json
python3 -c "
import json
b, a = (json.load(open(f))['findings'] for f in ('before.json', 'after.json'))
print('before', len(b), 'after', len(a))
print('new in the rebuild:', sorted({f[\"sc\"] for f in a} - {f[\"sc\"] for f in b}))"
```

If the parity check fails, fix the rebuild. Do not hand over a document whose parity you
could not establish, and do not describe a rebuild as complete while a placeholder is still
in it.

## The recreation record

Six sections, and the last three are what make it trustworthy:

**What was rebuilt and why**, naming which of the three doors you came through, and where
the original still is.

**What the new file has that the old one did not.** The structural additions, criterion by
criterion.

**The parity check**, with the counts and the fact that you read it in order.

**What was lost.** From the inventory. Macros, signatures, tracked changes, comments,
embedded objects, exact layout. Say it plainly rather than in a footnote.

**What is still open.** Alternative text nobody has supplied, captions, anything a
placeholder is standing in for, anything you could not extract. A rebuild does not close
`owner` findings, and presenting one as complete when the alt text is still missing is the
most common way this work goes wrong.

**What a person still has to check.** Reading order, above all. Say it every time.

Then state the position accurately. "Rebuilt with real structure, 11 findings closed, 4
awaiting alternative text from the author, reading order needs a human read" is credible.
"Now accessible" is not.
