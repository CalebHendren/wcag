---
name: wcag-report
description: "Turn audit findings into the deliverable someone asked for: a VPAT or Accessibility Conformance Report, an accessibility statement, issue tickets, an executive summary, or a remediation roadmap. Load when someone asks for a VPAT or ACR, a Section 508 or EN 301 549 conformance report, an accessibility statement, a procurement response about accessibility, or wants findings turned into Jira or GitHub issues."
license: MIT
allowed-tools: Read, Grep, Glob, Bash, WebFetch, Write
---

# Reporting: turning findings into the deliverable someone asked for

Read `../wcag/SKILL.md` and `../../references/conformance.md` first. Conformance language is
where these documents go wrong, and the rules are precise.

The same findings serve different audiences. A developer needs a location and a fix. A
procurement officer needs a row per criterion. An executive needs the three things that
matter and what they cost. Pick the deliverable, then shape the findings for it.

```bash
python3 scripts/report.py findings.json --title "Checkout" --level AA --out audit.md
python3 scripts/report.py findings.json --format vpat --title "Product" --out acr.md
python3 scripts/report.py findings.json --format csv --out tickets.csv
```

The script generates the criteria table from the full WCAG 2.2 catalogue, so every
criterion at the target level appears with a status, and untested criteria are marked
untested rather than passed. Edit the output afterwards; the script produces a correct
skeleton, not a finished document.

Two flags stop the default from overstating the uncertainty. `--passed` names the criteria
you verified as passing, and `--not-applicable` names the ones with no relevant content in
this target, such as the media criteria on a document containing no audio or video. Assert
both deliberately, because a criterion left at "not tested" says nobody looked, and a page
of those when you did look reads as a thinner audit than you performed. A finding always
wins over either flag, so you cannot mark away a failure.

## The audit report

Covered in `../wcag/SKILL.md`. Two things decide whether it is any good:

**The "what was not tested" section comes before the findings.** A reader who stops after
the summary should already know the report's limits. Putting coverage gaps in an appendix
is how an audit gets misread as a clean bill of health.

**Every finding is actionable.** A location someone can open, an explanation of who is
affected, a specific fix, and a way to check it worked.

## VPAT and ACR

A VPAT is Information Technology Industry Council's template. The completed document is an
Accessibility Conformance Report. Procurement teams, especially in United States government
and higher education, ask for one by name.

Four editions exist. Ask which one is wanted rather than guessing:

- **WCAG edition**: WCAG only.
- **Section 508 edition**: WCAG plus the Revised 508 chapters.
- **EU edition**: WCAG plus EN 301 549.
- **INT edition**: all of the above, and the safe default when the buyer has not said.

The conformance vocabulary is fixed, and each term means something specific:

- **Supports**: the functionality meets the criterion without known defects.
- **Partially Supports**: some functionality does not meet the criterion.
- **Does Not Support**: the majority of the functionality does not meet the criterion.
- **Not Applicable**: the criterion is not relevant to this product.
- **Not Evaluated**: permitted only for Level AAA criteria in the template. If you did not
  evaluate a Level A or AA criterion, the honest answer is to say so in the remarks and
  mark the report a draft rather than to quietly write Supports.

Remarks carry the weight. "Partially Supports" with no explanation is not usable by a
buyer. Say what fails, where, and what the workaround or the plan is.

Two rules for a report you generate:

Never issue a VPAT as a finished document from an audit alone. A VPAT is a vendor's
statement about a product, signed by someone accountable for it. What you can produce is a
complete, accurate draft with every row supported by evidence and every gap marked. Say
that in the document.

Never write Supports for a criterion nobody tested. This is the single most common defect
in real VPATs, and it is the one that damages the vendor when a buyer finds out.

## Accessibility statement

A public page saying where the product stands. Required by the EU Web Accessibility
Directive for public sector bodies, and expected practice elsewhere.

Include: the standard and level being aimed at, the current status in plain language,
which parts are not yet accessible and why, known problems with dates for fixing them,
content excluded from scope and the reason, how someone reports a problem and how long a
reply takes, an escalation route where the law requires one, when the statement was
prepared and how, and when it was last reviewed.

Write it in plain language. This page is read by the people the failures affect, and a page
about accessibility that is written in procurement prose reads badly.

Do not write "fully accessible" or "fully compliant". Write what is true, including the
parts that are not done. A statement that admits three known problems and gives dates is
more credible, and more legally defensible, than one that claims perfection.

## Issue tickets

One finding to one ticket, unless the same fix closes several, in which case group them and
list the instances in the body.

A good ticket title names the criterion and the place: "1.3.1: address form fields have no
programmatic labels (checkout step 2)".

The body needs the location, the evidence, who is affected and what they cannot do, the
fix, and how to verify it. Add the severity as a label and the criterion as a label, so the
backlog can be filtered by both.

Bundle by component rather than by page where a component is the cause. Forty tickets for
one button component is noise; one ticket listing forty instances gets fixed.

`--format csv` produces a file most trackers can import.

## Executive summary

One page. The audience decides budget, not implementation.

Say what was tested and against what. State the position in one sentence. Name the three
things that matter most and what each blocks. Give a realistic shape for the work,
distinguishing what is a component fix from what is a content or design programme. Name the
obligation and its date if one applies. Say what happens if nothing is done, factually,
without inflating it.

Do not include a compliance percentage. It is not derivable from an audit, it invites
management by metric, and every reader who knows the standard will discount the document
for containing one.

## Remediation roadmap

Order by user impact and dependency, not by how easy things are.

Group into phases with a theme: blockers first, then the shared components, then the
content programme, then the design changes. For each item give the findings it closes, who
does it, and what has to happen first.

Name the recurring causes as their own work item. A roadmap that fixes 60 alt text findings
without addressing the CMS that lets images be published without alt text will produce the
same 60 findings next year.
