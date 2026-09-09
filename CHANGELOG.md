# Changelog

## Unreleased

`pdf_audit.py` now checks table header association rather than header presence. The
previous check asked only whether any `TH` existed, which passes exactly the tables that
fail their readers: a real faculty timetable with all 37 header cells correctly typed, and
not one of them carrying `/Scope`, came back clean.

Three checks were added. Headers with no `/Scope` and no `/Headers` association anywhere.
Two-axis tables with data cells carrying no `/Headers`. And rows holding fewer cells than
the table has columns while no cell declares `/RowSpan` or `/ColSpan`, which is the one
that produces wrong answers rather than missing ones, because an undeclared merge makes the
reader fill columns left to right and shift every later cell into the wrong column.

The underlying bug was that PDF table properties live in the element's `/A` attribute
dictionary, not as direct keys, so a lookup for `node["/Scope"]` returns nothing on a
correct file and a broken one alike. Added `merged_attributes()` to read `/A` properly,
including the array form.

## 0.1.0

First release.

Seven skills: `wcag` as the router, plus `wcag-web`, `wcag-pdf`, `wcag-documents`,
`wcag-mobile`, `wcag-remediate`, and `wcag-report`.

Audit mode is the default and makes no changes. Remediation runs only on an explicit
request and carries its own rules for what can be fixed safely.

Six scripts: contrast ratios, static HTML checks, an axe-core scan through Playwright, PDF
structure analysis, report generation including a VPAT draft, and a repository self-check.

Reference material covering all 87 WCAG 2.2 success criteria, the five conformance
requirements, severity ranking, the laws that point at each standard, media, the Matterhorn
Protocol checkpoints, the W3C WCAG2Mobile interpretation, the mobile platform accessibility
APIs, ARIA widget keyboard contracts, and framework-specific failures.

Manifests for Claude Code, Cursor, and Codex, plus a Cursor rules file.

Validated against four eval cases run with and without the skills. The runs fed five
changes back into the code and the references:

- `report.py` gained `--not-applicable`, because defaulting every unchecked criterion to
  "not tested" overstated the uncertainty on targets where criteria genuinely do not apply.
- `report.py` gained `--keep-ids`, because renumbering on merge silently broke
  cross-references between hand-authored findings.
- `html_audit.py` no longer reports 2.2.2 against an autoplaying video that has `controls`,
  since the native player supplies the pause mechanism the criterion asks for.
- `axe_scan.py` says how to install axe-core locally before it tries a CDN that managed
  environments commonly block.
- `references/non-web.md` was added, and the mobile, PDF, and document skills now anchor
  conformance language to WCAG2ICT, the completed W3C Group Note that regulations
  reference for non-web software, with WCAG2Mobile as the mobile-specific reading.
