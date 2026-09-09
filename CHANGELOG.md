# Changelog

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
