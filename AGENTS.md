# WCAG plugin

This repository is an agent plugin, not an application. It ships seven skills for auditing
and remediating accessibility against WCAG 2.2, plus five scripts they call.

## Layout

- `skills/` holds the skills. `wcag/SKILL.md` is the router and the shared contract; the
  rest cover web, PDF, documents, mobile, remediation, and reporting.
- `references/` holds material used by more than one skill: the full WCAG 2.2 criteria
  catalogue, conformance rules, severity, legal mapping, and media guidance.
- `scripts/` holds the executable checks. They are Python 3, standard library only except
  where noted in each file's docstring.
- `commands/` holds the two slash commands.
- `.claude-plugin/`, `.cursor-plugin/`, `.codex-plugin/` and `.agents/` hold the manifests
  for each host.

## Working on this repository

Run `scripts/selfcheck.py` before committing. It validates the manifests, checks every
skill has the frontmatter its host requires, verifies that internal links resolve, and
confirms the criteria table in `scripts/report.py` matches the W3C numbering.

The success criteria numbering, titles, and levels were generated from the W3C WCAG 2.2
guidelines source. If you change them, regenerate rather than editing by hand, and keep the
counts at 31 Level A, 24 Level AA, and 31 Level AAA, with 4.1.1 removed.

Documentation in this repository follows the anti-slop rules at
https://github.com/miqdadbadjuber/anti-slop. In practice: no em dashes, no buzzword
vocabulary, name the actor in each sentence, no invented numbers or claims, and no
inline-header bullet lists outside the documented conventions.
