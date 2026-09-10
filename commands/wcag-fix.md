---
description: Apply accessibility fixes to a web page, PDF, document, or mobile app after an audit
argument-hint: <url, file path, or directory> [--findings findings.json] [--auto-recreate]
allowed-tools: Read, Grep, Glob, Bash, Edit, Write, WebFetch
---

Remediate the accessibility findings on this target: $ARGUMENTS

This edits files. Read the `wcag-remediate` skill before changing anything, and the format
skill for the target.

Work in this order:

1. If no audit exists, run one first. Fixing without findings means fixing what is easy to
   see rather than what matters.
2. Establish what this environment can reach: the file itself, the Python document
   libraries, a converter, the authoring application. It decides which findings you can
   close. The `wcag` skill's section on establishing what you can operate covers it.
3. Check the working tree is clean and version controlled. If it is not, say plainly that
   the changes will not be reversible. For any binary document, work on a copy and never
   write over the original.
4. Tell the user which findings you will fix, which need the authoring application, which
   need the content owner, and which need a design decision, before you start.
5. Fix in the order the remediation skill sets: blockers, then shared components, then
   structural fixes, then the rest by severity.
6. Verify each fix or each related batch. Re-run the scanner, run the application's own
   accessibility checker where you can reach it, and test by hand whatever neither can see.
7. Write the remediation record, including what was not fixed and what remains unverified,
   and say where the new file is and that the original is unchanged.

If a fix cannot be applied, stop the pass on that document rather than trying another
approach or moving on. Say what failed and why, say what is still fixed, and recommend
recreating the document, naming what a rebuild would lose. Then wait.

`--auto-recreate` means the user does not want to be asked: on a failed pass, go straight
into recreate mode following the `wcag-recreate` skill. Say the pass failed and why, and
say what the rebuild loses, before it is lost. It changes who decides, not what is
disclosed.

Never invent alt text, captions, or error message content you cannot derive from the
material in front of you. If you can view an image, draft the alternative and mark it for
the author to confirm rather than closing the finding. If you cannot, report the gap and
name what the author has to supply. An invented description looks fixed and is not, which
is worse than an open finding.

Never add an accessible name that differs from the visible label, and never add an ARIA
role without the keyboard behavior it promises.
