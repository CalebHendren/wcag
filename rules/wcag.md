# WCAG accessibility rules

This project has the `wcag` skills installed. They cover auditing, remediating, and
rebuilding against WCAG 2.2 for web pages, PDFs, office documents, and mobile apps, in
source code or directly in the file.

Load `skills/wcag/SKILL.md` whenever a task involves accessibility, a11y, WCAG, Section
508, the ADA, the European Accessibility Act, EN 301 549, a VPAT, screen readers, alt text,
color contrast, or keyboard navigation. It routes to the right format skill.

Three rules apply to every accessibility task in this project:

**Audit is the default and it changes nothing.** Someone who asks whether content is
accessible wants an answer, not an edited file. Edit only when asked to fix, remediate, or
correct, and say which mode you are in before you start.

**Never invent accessibility content.** Alt text, captions, transcripts, and error messages
must come from the material or from the author. An invented description satisfies a checker
while telling the user nothing, and it looks fixed to everyone who checks later.

**Work on a copy of any document, and stop when a fix will not apply.** Never write over
the original. If a fix cannot be applied, say what failed and offer to rebuild the document
rather than trying another angle, because a half-patched file looks repaired and is not.
