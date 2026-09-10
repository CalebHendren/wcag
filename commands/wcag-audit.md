---
description: Audit a web page, PDF, document, or mobile app against WCAG 2.2 without changing anything
argument-hint: <url, file path, or directory> [--level A|AA|AAA]
allowed-tools: Read, Grep, Glob, Bash, WebFetch, Write
---

Audit this target against WCAG 2.2: $ARGUMENTS

This is an audit. Read and report. Do not edit the target, and do not edit any file other
than the report itself, and only if the user wants it written to disk.

Follow the `wcag` skill for the mode contract, the finding record, and the report shape.
Route to the format skill that matches the target: `wcag-web`, `wcag-pdf`,
`wcag-documents`, or `wcag-mobile`.

Work in this order:

1. Say in one line what you are auditing, at which level (default AA), and that nothing
   will be changed.
2. Establish what you can actually test in this environment. A live URL with a browser
   supports far more than source alone, and a document you can open in its application
   supports more than one you can only read as a file. The difference belongs in the
   report.
3. Run the bundled scripts that apply. Locate them at `${CLAUDE_PLUGIN_ROOT}/scripts/`, or
   in the `scripts/` directory beside the plugin's `skills/` directory. For an Office file
   run `office_audit.py`, and run the application's own accessibility checker as well where
   you can reach it.
4. Test what the tools cannot see, which is where most real failures are: reading and focus
   order, alt text quality, heading meaning, link purpose, error messages, keyboard
   operation, and the criteria new in WCAG 2.2.
5. Mark every finding with who can close it: `direct` when an agent can apply it, `app`
   when it needs the authoring application, `recreate` when the file cannot carry the fix
   at all, `owner` when the content is information nobody has supplied, `design` when
   someone has to choose.
6. Write the report with what was not tested stated before the findings, and a section
   naming the findings an agent cannot close on its own. Keep that section even when it is
   empty, and say it is empty.

If the user has not said which level, use AA and say so. If the target spans formats, for
example a page that serves PDFs, audit both and separate the findings.

Offer the remediation as a next step at the end. Do not start it. Where findings are
marked `recreate`, offer the rebuild instead and say what it would cost, without starting
that either.
