# wcag

Accessibility auditing and remediation for AI agents. Eight skills that check web pages,
PDFs, office documents, and mobile apps against WCAG 2.2, and fix what they find when you
ask them to.

It works for a coding agent editing source files and for a desktop agent working on a
person's documents, in Claude Cowork, ChatGPT's work and agent modes, Copilot inside
Office, or anything else that can open a folder and drive an application. Those agents can
apply the fixes to the Word, PowerPoint, and Excel files directly, and rebuild a document
that will not take a fix.

Audit mode is the default and it changes nothing. Remediation is a separate request.
Recreating is a third.

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

Eight skills:

| Skill | Covers |
|---|---|
| `wcag` | The router. Sets audit, remediation, or recreate mode, the finding record, and the report shape. Start here. |
| `wcag-web` | HTML, CSS, JavaScript, React, Vue, Svelte, Angular, design systems, HTML email. |
| `wcag-pdf` | Tagging, reading order, alt text, tables, forms, bookmarks, scanned documents. |
| `wcag-documents` | Word, PowerPoint, Excel, Google Workspace, OpenDocument, EPUB, Markdown. |
| `wcag-mobile` | iOS, Android, React Native, Flutter, hybrid apps, applied through W3C WCAG2Mobile guidance. |
| `wcag-remediate` | What order to fix in, what needs the content owner or the authoring application, what to do when a fix will not apply, and the fixes that pass a checker while making things worse. |
| `wcag-recreate` | Rebuilding a document that cannot be repaired in place: what must survive exactly, what a rebuild always loses, and the parity check before handing it over. |
| `wcag-report` | VPAT and ACR drafts, accessibility statements, issue tickets, executive summaries. |

Nine scripts the skills call:

| Script | Does |
|---|---|
| `contrast.py` | Contrast ratios for 1.4.3, 1.4.6, and 1.4.11. Handles hex, rgb, hsl, named colors, and alpha compositing. |
| `html_audit.py` | Static checks on HTML source. No browser, no network, no dependencies. |
| `axe_scan.py` | axe-core against a live page through Playwright, including axe's undecided results. |
| `pdf_audit.py` | Tag tree, reading order, figure alt text, table headers, form field names, text layer. |
| `office_audit.py` | Word, PowerPoint, and Excel structure, with no Office installation needed. Marks each finding with who can close it. |
| `office_remediate.py` | Applies the derivable document fixes to a copy, rewriting only the XML parts that carry them. |
| `report.py` | Merges findings into an audit report, a VPAT draft, or a CSV for a tracker. |
| `build_sc_index.py` | Regenerates the criteria index from the criteria table. |
| `selfcheck.py` | Validates this repository before you commit to it. |

Reference material covering all 86 WCAG 2.2 success criteria and the 13 guidelines they sit
under, the five conformance requirements, the Matterhorn Protocol checkpoints for PDF/UA,
the mobile platform accessibility APIs, the ARIA widget keyboard contracts, the
accessibility checkers built into Office and Acrobat, the capability envelope of a desktop
agent, and the laws that point at each standard.

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

### Claude Cowork, ChatGPT, and other desktop agents

Any agent that reads a skills folder loads these. Copy `skills/`, `references/`, and
`scripts/` into wherever your assistant looks for skills, keeping the three beside each
other, because the skills call the scripts and read the references by relative path. The
scripts need Python 3 and nothing else, so they run wherever the agent does.

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

Make this deck accessible before I send it out: Q3-board-update.pptx

This Word file is a mess of bold text pretending to be headings. Can you rebuild it?
```

Or use the commands:

```text
/wcag-audit https://example.com --level AA
/wcag-fix src/components/AddressForm.tsx
/wcag-fix quarterly-report.docx --auto-recreate
/wcag-recreate legacy-handbook.docx
```

An audit produces a report with the scope, what was not tested, the findings ranked by
severity, a table of every criterion at the target level with its status, and a conformance
position stated in the terms WCAG allows.

Every finding also says who can close it: an agent directly, the authoring application, the
content owner, a design decision, or nobody without rebuilding the file. The report keeps
that as its own section, so a reader can see what still needs a person before they book
one.

Remediation produces changed files plus a record of what was fixed, what needs the content
owner, what needs a design decision, and what could not be verified.

## The three modes

The distinction matters enough to be the first thing the router skill decides.

**Audit reads.** It creates one file, the report, and only if you want it on disk. Asking
whether something is accessible does not authorize editing it.

**Remediation edits.** It runs only when you ask for fixes, and it follows rules about what
can be changed safely. It will not invent alt text for an image it cannot see, will not add
an accessible name that contradicts the visible label, and will not add an ARIA role
without the keyboard behavior that role promises. Each of those satisfies an automated
checker while leaving the user worse off.

For a document it works on a copy and never writes over the original, and it applies only
the fixes whose correct value is derivable: the document title, the language, a table's
header row, alternative text you supplied.

**Recreation rebuilds.** Some documents cannot be repaired. A PDF with no tags and no
source, a report whose headings are all bold text, a deck of floating boxes. Recreating
builds a new file that says exactly what the original said, in the same order, with the
structure it never had, and leaves the original untouched.

If a remediation pass fails, it stops there rather than trying another angle, says what
failed, and offers the rebuild. A half-patched document is the worst thing to hand back,
because it looks repaired. If you would rather not be asked, `--auto-recreate` goes
straight to the rebuild, and still tells you the pass failed and what the rebuild cost.

## What it will not claim

WCAG conformance is defined precisely, and accessibility reports get attached to
procurement decisions and legal filings. These skills will not tell you a page conforms
when nobody verified it, will not report a percentage of conformance, and will not describe
a site as compliant on the strength of one page passing a scan.

When testing is limited by the environment, the report says so and marks the affected
criteria not tested. That is less satisfying than a clean score and it is the only version
that is any use.

## Standards covered

WCAG 2.2, all 86 success criteria across Levels A, AA, and AAA and the 13 guidelines they
sit under, with the nine criteria new in 2.2 marked and 4.1.1 Parsing handled as removed.
Titles, numbering, and levels were generated from the W3C guidelines source rather than
transcribed. `references/sc-index.md` has the whole list in one table.

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
