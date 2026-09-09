# wcag

Accessibility auditing and remediation for AI coding agents. Seven skills that check web
pages, PDFs, office documents, and mobile apps against WCAG 2.2, and fix what they find
when you ask them to.

Audit mode is the default and it changes nothing. Remediation is a separate request.

## Why this exists

Running an automated scanner is easy and it finds a minority of accessibility failures. The
rest need someone to read the alt text and ask whether it says anything, to tab through the
page and see where focus goes, to read a PDF in order and notice that the two columns are
being read across instead of down.

That work is what these skills do. They run the scanners first, because deterministic
checks belong in scripts, and then spend their effort on the criteria no scanner can judge.
They also refuse to make the report look better than the evidence supports: an audit says
what was not tested, before it says what was found.

## What is in it

Seven skills:

| Skill | Covers |
|---|---|
| `wcag` | The router. Sets audit or remediation mode, the finding record, and the report shape. Start here. |
| `wcag-web` | HTML, CSS, JavaScript, React, Vue, Svelte, Angular, design systems, HTML email. |
| `wcag-pdf` | Tagging, reading order, alt text, tables, forms, bookmarks, scanned documents. |
| `wcag-documents` | Word, PowerPoint, Excel, Google Workspace, OpenDocument, EPUB, Markdown. |
| `wcag-mobile` | iOS, Android, React Native, Flutter, hybrid apps, applied through W3C WCAG2Mobile guidance. |
| `wcag-remediate` | What order to fix in, what needs the content owner, and the fixes that pass a checker while making things worse. |
| `wcag-report` | VPAT and ACR drafts, accessibility statements, issue tickets, executive summaries. |

Six scripts the skills call:

| Script | Does |
|---|---|
| `contrast.py` | Contrast ratios for 1.4.3, 1.4.6, and 1.4.11. Handles hex, rgb, hsl, named colors, and alpha compositing. |
| `html_audit.py` | Static checks on HTML source. No browser, no network, no dependencies. |
| `axe_scan.py` | axe-core against a live page through Playwright, including axe's undecided results. |
| `pdf_audit.py` | Tag tree, reading order, figure alt text, table headers, form field names, text layer. |
| `report.py` | Merges findings into an audit report, a VPAT draft, or a CSV for a tracker. |
| `selfcheck.py` | Validates this repository before you commit to it. |

Reference material covering all 87 WCAG 2.2 success criteria, the five conformance
requirements, the Matterhorn Protocol checkpoints for PDF/UA, the mobile platform
accessibility APIs, the ARIA widget keyboard contracts, and the laws that point at each
standard.

## Install

### Claude Code

```text
/plugin marketplace add CalebHendren/wcag
/plugin install wcag@wcag
```

### Cursor and Codex

The repository carries `.cursor-plugin/plugin.json` and `.codex-plugin/plugin.json`
alongside the Claude manifest, so the same skills load in either. Point your tool's plugin
installer at this repository.

### Any agent that reads skill folders

Clone the repository and copy the folders you want from `skills/` into your agent's skills
directory. Each skill is a self-contained folder holding a `SKILL.md`. Copy `references/`
and `scripts/` next to them, because the skills call both.

```bash
git clone https://github.com/CalebHendren/wcag
cp -r wcag/skills/* ~/.claude/skills/
cp -r wcag/references wcag/scripts ~/.claude/
```

## Use it

Ask in your own words. The skills trigger on the shape of the request, not on a keyword.

```text
Check this PDF for accessibility problems: quarterly-report.pdf

Is the checkout flow on staging.example.com usable with a screen reader?

Our procurement team wants a VPAT for the mobile app. What do we have and what is missing?

Fix the accessibility findings in src/components/. Do not touch the copy.
```

Or use the commands:

```text
/wcag-audit https://example.com --level AA
/wcag-fix src/components/AddressForm.tsx
```

An audit produces a report with the scope, what was not tested, the findings ranked by
severity, a table of every criterion at the target level with its status, and a conformance
position stated in the terms WCAG allows.

Remediation produces changed files plus a record of what was fixed, what needs the content
owner, what needs a design decision, and what could not be verified.

## The two modes

The distinction matters enough to be the first thing the router skill decides.

**Audit reads.** It creates one file, the report, and only if you want it on disk. Asking
whether something is accessible does not authorize editing it.

**Remediation edits.** It runs only when you ask for fixes, and it follows rules about what
can be changed safely. It will not invent alt text for an image it cannot see, will not add
an accessible name that contradicts the visible label, and will not add an ARIA role
without the keyboard behavior that role promises. Each of those satisfies an automated
checker while leaving the user worse off.

## What it will not claim

WCAG conformance is defined precisely, and accessibility reports get attached to
procurement decisions and legal filings. These skills will not tell you a page conforms
when nobody verified it, will not report a percentage of conformance, and will not describe
a site as compliant on the strength of one page passing a scan.

When testing is limited by the environment, the report says so and marks the affected
criteria not tested. That is less satisfying than a clean score and it is the only version
that is any use.

## Standards covered

WCAG 2.2, all 87 success criteria across Levels A, AA, and AAA, with the nine criteria new
in 2.2 marked and 4.1.1 Parsing handled as removed. Titles, numbering, and levels were
generated from the W3C guidelines source rather than transcribed.

PDF/UA-1 through the Matterhorn Protocol checkpoints, for PDF work. The W3C WCAG2Mobile
guidance, for native apps. The reference on laws maps ADA Title II, Section 508, Section
504, the European Accessibility Act, the Web Accessibility Directive, EN 301 549, and
several national statutes to the version and level each requires.

## Contributing

Run the self-check before opening a pull request:

```bash
python3 scripts/selfcheck.py
```

It validates the manifests, checks skill frontmatter, resolves internal links, verifies the
criteria table against the specification's own counts, and enforces the prose rules the
documentation follows.

See `CONTRIBUTING.md` for what a good addition looks like.

## Documentation style

The prose in this repository follows the anti-slop rules from
[anti-slop](https://github.com/miqdadbadjuber/anti-slop): no em dashes, no buzzword
vocabulary, no invented numbers or claims, an actor named in each sentence, and no
inline-header bullet lists outside the documented conventions. `selfcheck.py` enforces the
part of that which a script can check.

## License

MIT. See `LICENSE`.
