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
   supports far more than source alone, and the difference belongs in the report.
3. Run the bundled scripts that apply. Locate them at `${CLAUDE_PLUGIN_ROOT}/scripts/`, or
   in the `scripts/` directory beside the plugin's `skills/` directory.
4. Test what the tools cannot see, which is where most real failures are: reading and focus
   order, alt text quality, heading meaning, link purpose, error messages, keyboard
   operation, and the criteria new in WCAG 2.2.
5. Write the report with what was not tested stated before the findings.

If the user has not said which level, use AA and say so. If the target spans formats, for
example a page that serves PDFs, audit both and separate the findings.

Offer the remediation as a next step at the end. Do not start it.
