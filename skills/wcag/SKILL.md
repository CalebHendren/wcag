---
name: wcag
description: "Audit or fix accessibility against WCAG 2.2 for web pages, PDFs, Office documents, and mobile apps. Start here for any accessibility work: it sets audit mode (read-only, the default) or remediation mode (edits only when asked), routes to the right format skill, and defines the finding record every wcag-* skill shares. Load whenever the user mentions accessibility, a11y, WCAG, Section 508, the ADA, the European Accessibility Act, EN 301 549, a VPAT, screen readers, alt text, color contrast, or keyboard navigation, or asks whether something works for people with disabilities, even without saying WCAG."
license: MIT
allowed-tools: Read, Grep, Glob, Bash, WebFetch, Write
---

# WCAG audit and remediation

You are checking real content against WCAG 2.2 for real people. Two things make an
accessibility review worth reading: it says what is broken and where, and it is honest
about what nobody checked. Everything below serves those two goals.

## Set the mode before anything else

The most damaging mistake here is editing someone's files when they asked a question.
Decide the mode from what was actually asked, and say which one you are in before starting.

**Audit is the default.** Read, test, report. Create exactly one new file, the report, and
only if the user wants it on disk. Change nothing else. Audit words: check, review, audit,
assess, is this compliant, will this pass, what's wrong with, how accessible is.

**Remediation needs an explicit request.** Remediation words: fix, remediate, make it
compliant, correct these, apply the fixes, add the alt text. Read
`../wcag-remediate/SKILL.md` before touching anything, because it carries the ordering,
safety and verification rules that stop you breaking what you are repairing.

Ambiguous ("sort out the accessibility on this page")? Audit first, then offer the fixes.
An audit costs the user nothing and lets them decide. Never read permission to edit out of
silence.

Say the mode in one line, so a misread is cheap to correct:

> Running an audit of `report.pdf` against WCAG 2.2 Level AA. No changes to the file.

## Scope the target

Conformance is a property of a page or document, not of a website or a brand. Pin down four
things, asking only what you cannot infer:

1. **What is in scope.** Which URLs, files, screens, components. If the user names a site,
   propose the home page, one of each distinct template, and every page in at least one
   complete process such as checkout.
2. **Which level.** Default AA, because every major law points there. AAA is not achievable
   across a whole site. `../../references/legal.md` maps laws to version and level.
3. **Which version.** Default WCAG 2.2. Some regimes still cite 2.1; 2.2 is backward
   compatible, so a 2.2 AA pass covers a 2.1 AA obligation.
4. **What you can actually run.** A live URL with a browser supports far more than a pasted
   fragment. Establish this early, because it decides what you can honestly claim later.

For anything that is not a web page, read `../../references/non-web.md` before writing a
conformance position. WCAG's conformance model is defined for web pages, and WCAG2ICT is
what makes a WCAG statement about an app or a document coherent.

## Route to the format skill

Read the one that matches the target. Read more than one when the target spans formats,
for example a web page that serves PDFs.

| Target | Skill |
|---|---|
| Web pages, web apps, HTML email, components, design systems | `../wcag-web/SKILL.md` |
| PDF files, scanned documents, forms | `../wcag-pdf/SKILL.md` |
| Word, PowerPoint, Excel, Google Docs, Markdown, EPUB | `../wcag-documents/SKILL.md` |
| iOS, Android, React Native, Flutter, hybrid apps | `../wcag-mobile/SKILL.md` |
| Any target, once findings exist and the user wants fixes | `../wcag-remediate/SKILL.md` |
| VPAT, ACR, conformance statement, issue tickets, exec summary | `../wcag-report/SKILL.md` |

Shared reference material lives in `../../references/`:

- `sc-perceivable.md`, `sc-operable.md`, `sc-understandable.md`, `sc-robust.md` hold all 87
  success criteria with intent, test method, and the failures that actually occur. Read the
  files for the principles in play rather than all four by reflex.
- `conformance.md` covers the five conformance requirements and what a claim may say.
- `legal.md` maps laws and policies to the standard they require.
- `media.md` covers captions, audio description, and transcripts across every format.
- `severity.md` explains how to rank findings so the report is triageable.

## Find the bundled scripts

Deterministic checks belong in scripts. Contrast arithmetic in particular is something
models get wrong, and a wrong ratio in a report is worse than no ratio.

In Claude Code they sit at `${CLAUDE_PLUGIN_ROOT}/scripts/`. Otherwise they sit in a
`scripts/` directory beside the `skills/` directory this file lives in. Resolve it once:

```bash
ls "${CLAUDE_PLUGIN_ROOT}/scripts" 2>/dev/null || \
  find . -type d -name scripts -path '*wcag*' 2>/dev/null | head -3
```

`contrast.py` for ratios (1.4.3, 1.4.6, 1.4.11). `html_audit.py` for static HTML with no
browser. `axe_scan.py` for a live URL through Playwright. `pdf_audit.py` for PDF structure.
`report.py` to turn findings JSON into the report or a VPAT draft, with `--passed` and
`--not-applicable` so the criteria table reflects what you established.

Each prints usage with `--help` and writes findings in the schema below. Run them first,
then spend your own effort on what they cannot see.

## What the tools cannot see

Automated rules catch a minority of WCAG failures, and the criteria needing human judgement
are the ones that decide whether the content is usable at all. Budget your effort
accordingly:

- Is the alt text *right*, not merely present. `alt="image"` passes a null check and tells
  a blind reader nothing.
- Do the reading and focus order match the visual order and the meaning.
- Do headings describe the sections they introduce, in a structure that makes sense.
- Does a link's text say where it goes when read on its own.
- Do error messages say what went wrong and how to fix it.
- Can every task be completed by keyboard alone, without traps or invisible focus.
- Do captions carry the speaker and the meaningful sound, not approximate words.
- Does the visible label match the accessible name, which decides whether voice control
  users can operate the control at all.

A report that only repeats a tool's output is not worth commissioning. State plainly which
findings came from a tool and which from your own inspection.

## The finding record

Every finding carries the same fields. A finding without a location and a fix is a
complaint, and the developer who receives it cannot act on it.

```json
{
  "id": "F-012", "sc": "1.3.1", "sc_title": "Info and Relationships",
  "level": "A", "severity": "high",
  "location": "src/checkout/AddressForm.tsx:88",
  "selector": "form#address input[name='postcode']",
  "issue": "The postcode input has no programmatic label. Its visible text sits in a sibling div with no association.",
  "impact": "Screen reader users hear 'edit text, blank' and cannot tell which field they are in. Voice control users have no name to speak.",
  "evidence": "<div class=\"lbl\">Postcode</div><input name=\"postcode\">",
  "fix": "Replace the div with <label for=\"postcode\">Postcode</label> and add id=\"postcode\" to the input.",
  "verification": "Focus the field with a screen reader and confirm it announces 'Postcode, edit text'.",
  "source": "manual", "confidence": "confirmed"
}
```

Field rules that matter:

- `sc` is the criterion the failure violates, not the nearest topic. If nothing is
  violated but the pattern is poor, record it as an advisory and say so.
- `location` must let someone open the exact place: a file and line, a page number, a
  selector, a screen name.
- `impact` names who is affected and what they cannot do. It is what gets findings
  prioritised, and the field most often left vague.
- `source` is `tool` or `manual`. `confidence` is `confirmed` when you observed the failure
  or `needs-review` when it depends on context you could not check.
- Do not invent a count of affected users or a conformance percentage. Neither is derivable
  from an audit, and both destroy the report's credibility.

## Severity

Severity is not the conformance level. A Level A failure on a decorative footer link
matters less than a Level AA failure that blocks payment, so rank by consequence: does it
stop a task (critical), force guesswork (high), add friction (medium), or merely annoy
(low). An advisory is not a WCAG failure but will hurt users or fail the next audit, and it
is counted separately so it never inflates the failure count.

Raise a band when the finding sits in a global component or in a required process. Never
lower one because the fix is hard. `../../references/severity.md` has the full rubric with
worked examples.

## Report structure

Use this shape unless the user asks for something else. `../wcag-report/SKILL.md` covers
VPATs, ACRs, and ticket exports.

```markdown
# Accessibility audit: [target]

## Scope and method
What was tested, against which version and level, with which tools, on which dates.

## What was not tested
The pages, states, flows, and criteria nobody checked, and why.

## Summary
Counts by severity and by level. The three problems to fix first, named.

## Findings
One entry per finding, ordered by severity, in the record format above.

## Criteria assessed
A table of every criterion at the target level with pass, fail, not applicable, or
not tested, so a reader can see the shape of the coverage.

## Conformance position
What can and cannot be claimed, in the terms `references/conformance.md` allows.
```

Lead with what was not tested, before the findings rather than after. A reader who skims
only the top of the report should still come away with an accurate idea of its limits.

## Honesty rules

These exist because accessibility reports get attached to legal filings and procurement
decisions, and an overstated one causes real harm.

- Never claim conformance you did not verify. "No automated errors found" is not "conforms
  to Level AA".
- One page passing does not make a site conform. Say which pages you tested.
- If you could not run a screen reader, open a browser, or see more than source, say so in
  the method section and mark the affected criteria not tested.
- Where a criterion depends on something you cannot see, such as whether a video's
  transcript is accurate, mark it `needs-review` and name what a human must check.
- Do not soften a failure into an advisory to make the summary look better, and do not
  inflate an advisory into a failure to look thorough.
