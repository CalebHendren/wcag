# Conformance: what can and cannot be claimed

WCAG defines conformance precisely, and reports lose credibility when they use the word
loosely. This file exists so that the conformance section of an audit says only what the
evidence supports.

## The five conformance requirements

A web page conforms to WCAG 2.2 only when all five hold. All five, not the first one.

**1. Conformance Level.** One level is met in full. Level A means every Level A criterion
is satisfied or a conforming alternate version is provided. Level AA means every Level A
and AA criterion. Level AAA means all three levels. There is no partial level, no "AA
except two criteria", and no percentage. W3C advises against requiring Level AAA as a
general policy for whole sites, because some content cannot satisfy every AAA criterion.

**2. Full pages.** Conformance is for full pages only and cannot be achieved if any part of
the page is excluded. A responsive page conforms only if every variation it presents at
different screen sizes conforms.

**3. Complete processes.** When a page is one step in a process, every page in that process
must conform at the level claimed. If the payment step fails, no page in the checkout
conforms, including the ones that pass on their own.

**4. Only accessibility-supported ways of using technologies.** Only technology features
that actually work with users' assistive technology may be relied upon. Anything relied
upon that is not accessibility supported must also be available in a way that is.

**5. Non-interference.** Technologies used in a non-conforming way must not block access to
the rest of the page, and the page must keep conforming whether or not those technologies
are turned on or supported. Four criteria apply to all content on the page for this reason,
even content not otherwise relied upon:

- 1.4.2 Audio Control
- 2.1.2 No Keyboard Trap
- 2.2.2 Pause, Stop, Hide
- 2.3.1 Three Flashes or Below Threshold

A page that cannot conform, such as a deliberate failure example, cannot be included in the
scope of a claim.

## Conforming alternate version

An alternate version satisfies a criterion only when it conforms at the level claimed,
provides all the same information and functionality, is as up to date, and can be reached
from the non-conforming page by an accessibility-supported mechanism, or the
non-conforming page can be reached only from the conforming one.

A separate "accessible version" of a site that lags behind the main one, or that drops
features, is not a conforming alternate version. Report it as a failure of the criteria the
main page fails.

## Statements of partial conformance

Two situations allow a narrower statement rather than a claim:

**Third-party content.** A page with content outside the author's control, such as
user-generated posts or an embedded widget, can state that it would conform if the
non-conforming content were removed. The author must monitor and correct such content
within two business days.

**Language.** A page can state partial conformance when it uses a language for which no
accessibility-supported user agent support exists.

## What a conformance claim must contain

Claims are optional. When one is made it must include the date, the guidelines title,
version and URI, the conformance level, a concise description of the pages covered, and a
list of the web content technologies relied upon. A claim may not exclude any part of a
page it covers.

## Language for the report

Use these forms and avoid inventing others:

- "Conforms to WCAG 2.2 Level AA" only when every A and AA criterion is satisfied across
  every page in scope and every step of the processes in scope.
- "Does not conform to Level AA. N criteria failed" when any criterion fails.
- "Partially supports" and "Does not support" belong to VPAT and ACR terminology, not to
  WCAG conformance. Use them in a VPAT, where they are defined, and see
  `../skills/wcag-report/SKILL.md`.
- "Tested against Level AA. 12 criteria could not be evaluated" when coverage was limited.
  Name them.

Phrases to avoid because they mean nothing precise: "WCAG compliant", "95 percent
accessible", "AA ready", "fully accessible". If a stakeholder asks for one of these, give
the accurate statement and explain the difference in one sentence.

## Accessibility supported

A way of using a technology is accessibility supported when it works with users' assistive
technology and with the accessibility features of browsers and operating systems. W3C does
not publish a list, so this is a judgement about the audience and their tools.

Practical consequence for an audit: a technically correct ARIA pattern that no common
screen reader announces usefully is not accessibility supported. When you rely on support
that is patchy, say which combinations you verified and which you did not.
