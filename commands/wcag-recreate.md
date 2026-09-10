---
description: Rebuild a document as an accessible equivalent when it cannot be repaired in place
argument-hint: <file path> [--output <path>] [--from-findings findings.json]
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, WebFetch
---

Rebuild this document as an accessible equivalent: $ARGUMENTS

This creates a new file. Read the `wcag-recreate` skill before starting, and the format
skill for the target. The original is never modified and never overwritten.

Work in this order:

1. Say in one line what you are rebuilding, where the new file will go, and that the
   original stays as it is.
2. Confirm recreating is the right call. If the document can be repaired in place, say so
   and offer remediation instead, because a repair keeps things a rebuild loses. If the
   original is a record, such as a signed contract, a filed return, or an archived edition,
   the accessible version is a companion to it rather than a replacement, and the user has
   to know that before you build it.
3. Inventory what the file holds that a rebuild will lose: macros, digital signatures,
   tracked changes, comments, embedded objects, exact layout. Say it as a short list and
   get agreement before spending the effort.
4. Extract everything in document order: text with the role it plays, tables with their
   header rows, images with any existing alternative text, links with their targets, slide
   titles and notes, sheet names and ranges. Record what you could not extract.
5. Build the new file with real structure from the start, using the organization's template
   where one exists. `references/rebuild-recipes.md` in the skill covers each format.
6. Run the parity check: same words, same order, same numbers, same counts of tables,
   images, links, slides, and sheets. Read the new document top to bottom against the
   original, because reading order is what a rebuild decides and no tool checks.
7. Re-audit the new file and compare it against the original's findings.
8. Write the recreation record: what was rebuilt and why, what the new file has that the old
   one did not, the parity check, what was lost, what is still open, and what a person still
   has to check.

Preserve the words exactly. Recreating is not editing, not summarizing, and not improving
the copy. If you think something should change, say so separately and leave it alone.

Never invent content to fill a gap. Where alternative text, a caption, or a figure is
missing, put in a clearly marked placeholder and name it in the record. A rebuild is the
easiest place to manufacture content quietly and the hardest place for anyone to notice.

Do not describe the result as accessible while a placeholder is still in it, or while the
reading order has not been read by a person.
