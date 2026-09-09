---
description: Apply accessibility fixes to a web page, PDF, document, or mobile app after an audit
argument-hint: <url, file path, or directory> [--findings findings.json]
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, WebFetch
---

Remediate the accessibility findings on this target: $ARGUMENTS

This edits files. Read the `wcag-remediate` skill before changing anything, and the format
skill for the target.

Work in this order:

1. If no audit exists, run one first. Fixing without findings means fixing what is easy to
   see rather than what matters.
2. Check the working tree is clean and version controlled. If it is not, say plainly that
   the changes will not be reversible, and work on a copy for any binary document.
3. Tell the user which findings you will fix, which need the content owner, and which need
   a design decision, before you start.
4. Fix in the order the remediation skill sets: blockers, then shared components, then
   structural fixes, then the rest by severity.
5. Verify each fix or each related batch. Re-run the scanner, and test by hand whatever the
   scanner cannot see.
6. Write the remediation record, including what was not fixed and what remains unverified.

Never invent alt text, captions, or error message content you cannot derive from the
material in front of you. Report the gap and name what the author has to supply. An
invented description looks fixed and is not, which is worse than an open finding.

Never add an accessible name that differs from the visible label, and never add an ARIA
role without the keyboard behavior it promises.
