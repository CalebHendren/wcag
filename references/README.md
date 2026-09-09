# Shared references

Material used by more than one skill. Format-specific references live inside the skill that
owns them, for example `skills/wcag-pdf/references/`.

| File | Read it when |
|---|---|
| `sc-perceivable.md` | Testing text alternatives, media, structure, contrast, or reflow. |
| `sc-operable.md` | Testing keyboard access, timing, navigation, focus, or pointer input. |
| `sc-understandable.md` | Testing language, predictability, forms, errors, help, or authentication. |
| `sc-robust.md` | Testing names, roles, values, and status messages. |
| `conformance.md` | Writing the conformance section, or deciding what a claim may say. |
| `severity.md` | Ranking findings, or ordering the report. |
| `legal.md` | Choosing the target version and level, or answering a compliance question. |
| `media.md` | Any audio or video, in any format. |
| `non-web.md` | Any target that is not a web page: native apps, PDFs, office documents, kiosks. Read it before writing a conformance position for one. |

The four criteria files together cover all 87 WCAG 2.2 success criteria: 31 at Level A, 24
at Level AA, and 31 at Level AAA, plus 4.1.1 Parsing, which was removed in 2.2. Titles,
levels, and numbering were generated from the W3C guidelines source, so they match the
specification exactly.
