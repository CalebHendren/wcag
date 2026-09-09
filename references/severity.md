# Severity: ranking findings so they get fixed

Conformance level answers "which rule does this break". Severity answers "how much does
this hurt, and what should the team do on Monday". A report that sorts only by level tells
a team to fix a decorative footer link before a checkout button nobody can press.

## The rubric

Rate each finding on three axes, then take the highest applicable band.

**Blocking effect**
- Blocks a task entirely for a group of users: critical.
- Task completable with significant difficulty, guessing, or outside help: high.
- Task completable with friction: medium.
- Noticeable defect, no practical obstruction: low.

**Reach**
- Appears in a global component (header, navigation, footer, design system primitive) or on
  every page: raise one band.
- Appears in one page in a required process (sign-up, checkout, payment, account recovery):
  raise one band.
- Appears once, in optional content: leave as is.

**Population affected**
- Affects several disability groups at once, for example a control with no name and no
  keyboard access: raise one band.
- Affects a group with no workaround available: raise one band.

Never lower a band because a fix is hard. Effort belongs in the fix estimate, not the
severity.

## Bands with examples

**Critical**
- Keyboard trap in a modal that cannot be escaped.
- Submit button with no accessible name.
- CAPTCHA with no non-visual alternative on a login.
- Content flashing more than three times per second.
- A form whose validation errors are shown only visually, so a screen reader user cannot
  discover why submission failed.

**High**
- Focus indicator removed site-wide.
- Data table with no header association, where the data is the point of the page.
- Video with no captions on a page whose purpose is that video.
- Reading order in a PDF that scrambles a multi-column article.
- Drag-only reordering with no alternative in a core workflow.

**Medium**
- Body text at 4.1:1 contrast against white.
- Heading levels skipping from h2 to h4 in an article.
- Placeholder used as the only label on an optional field.
- Icon buttons at 20 by 20 pixels with adequate spacing around them.

**Low**
- Missing skip link on a page with three links above the content.
- `lang` missing on a short quoted phrase in another language.
- Redundant alt text that repeats an adjacent caption.

**Advisory**
- A pattern that passes today but will fail as soon as content grows, such as a fixed-height
  card that will clip at longer translations.
- A tooltip that meets 1.4.13 but is unreadable at 400 percent zoom.
- A heading structure that is technically valid but does not describe the sections.

Advisories are worth including because they prevent the next audit's findings. Keep them in
a separate section so they never inflate the failure count.

## Ordering the report

Sort by severity, then by reach, then by level. Within the summary, name the three findings
to fix first and say why those three. A team that fixes three things this sprint should fix
the three that matter most, and the report should make that choice for them.
