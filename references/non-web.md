# Applying WCAG outside a web page

WCAG is written for web content, and its conformance requirements are defined for web
pages. A native mobile app, a Word file, a desktop application, and a kiosk are none of
those. Reports go wrong at this seam, either by claiming a conformance WCAG does not
define, or by treating the criteria as inapplicable when regulators plainly apply them.

## WCAG2ICT is the bridge

*Guidance on Applying WCAG 2 to Non-Web Information and Communications Technologies*
(WCAG2ICT) was published by the W3C Accessibility Guidelines Working Group as a completed
Group Note in October 2024, covering WCAG 2.0, 2.1, and 2.2. It says how each success
criterion and glossary term reads when the subject is a non-web document or a piece of
software rather than a web page.

It is informative. It defines no new requirements and no conformance model of its own. What
it gives you is the substitution rules that make a criterion meaningful off the web, and it
is the document that regulators lean on when they apply WCAG to software. That makes it the
right thing to cite when someone asks whether their app meets WCAG.

The substitutions that matter most:

- "Web page" becomes "non-web document" or "software".
- "Set of web pages" becomes "set of documents" or "set of software programs".
- "Programmatically determined" is satisfied through the platform accessibility API rather
  than through markup.
- "User agent" includes the platform software and the assistive technology on it.
- Conformance Requirement 3, complete processes, does not carry over cleanly, because a
  process in software is not a set of pages.

WCAG2ICT also adds terms that have no web equivalent: closed functionality, meaning a
product that prevents the user from attaching their own assistive technology such as a
ticket machine or a card terminal; platform software; menu-driven interface; and virtual
keyboard. Closed functionality is where WCAG alone runs out, and where EN 301 549 and the
Revised 508 Standards carry requirements WCAG does not.

## Where WCAG2Mobile fits

*Guidance on Applying WCAG 2.2 to Mobile Applications* (WCAG2Mobile) is a more recent and
narrower W3C draft note, first published in May 2025. It reads the Level A and AA criteria
specifically for mobile apps and gives more concrete mobile advice than WCAG2ICT does.

Use both, in this order: WCAG2ICT establishes that and how WCAG applies to non-web
software, and WCAG2Mobile supplies the mobile-specific reading of individual criteria. When
a claim has to be anchored to something, anchor it to WCAG2ICT, because it is a completed
Group Note that regulations already reference, and cite WCAG2Mobile as supporting
interpretation. Check the current status of both before relying on either in a formal
document.

## Non-web documents

The same logic covers PDFs, Word files, slide decks, and ebooks. A PDF is a non-web
document, so WCAG2ICT is what makes "this PDF meets WCAG 2.2 AA" a coherent statement, and
the criteria that describe navigation across a set of pages are read against a set of
documents rather than a website.

For PDFs specifically, PDF/UA-1 is the format's own accessibility standard and covers
structural requirements WCAG does not express. See `../skills/wcag-pdf/references/matterhorn.md`.

## Writing the conformance position

Do not write that a native app or a document "conforms to WCAG 2.2 Level AA" without
qualification. Write what is true:

> Assessed against the WCAG 2.2 Level A and AA success criteria as applied to non-web
> software through WCAG2ICT, with WCAG2Mobile used for the mobile-specific reading of
> individual criteria. 14 criteria were not satisfied. WCAG's own conformance model is
> defined for web pages, so this report states criterion-level results rather than a WCAG
> conformance claim.

For a VPAT or an ACR this is less awkward, because the template already reports per
criterion rather than as a single conformance statement. Say in the evaluation methods
section which interpretation you applied.

## What the obligation usually is

A native app or a document is rarely regulated through WCAG directly. It is regulated
through a standard that imports WCAG:

- **Revised Section 508** applies WCAG Level A and AA to software and electronic documents,
  with exceptions for non-web software set out in E207.2. Four criteria and Conformance
  Requirement 3 are excepted there: 2.4.1 Bypass Blocks, 2.4.5 Multiple Ways, 3.2.3
  Consistent Navigation, and 3.2.4 Consistent Identification. Confirm the current text
  before relying on the list.
- **EN 301 549** covers non-web documents in Clause 10 and software including native mobile
  apps in Clause 11, and adds requirements beyond WCAG for closed functionality, hardware,
  documentation, and support services.
- **ADA Title II** names mobile applications directly in the Department of Justice rule.

`legal.md` has the fuller mapping. The practical consequence is that an audit scoped to
"WCAG criteria only" leaves out clauses the buyer is actually obliged to meet, so say which
clauses were outside your scope rather than implying full coverage.
