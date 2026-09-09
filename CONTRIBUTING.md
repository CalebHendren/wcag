# Contributing

## Before you open a pull request

```bash
python3 scripts/selfcheck.py
```

It has to pass. The check covers the manifests, the skill frontmatter, internal links, the
criteria table against the specification's counts, and the prose rules.

## What makes a good addition

**A criterion entry that says how it fails in practice.** The catalogue in `references/` is
useful because each entry says what actually goes wrong, not because it restates the
normative text. If you add or improve an entry, add the failures you have seen.

**A check that a script can make deterministically.** Anything a model has to compute in its
head is a candidate for a script, and contrast arithmetic is the clearest example. If you
find yourself writing "carefully calculate" in a skill, write the script instead.

**Format coverage that is genuinely different.** A new skill is warranted when the testing
method changes, not when the subject changes. Video accessibility lives in
`references/media.md` because the method is the same across formats. Mobile is its own
skill because the platform APIs, the tools, and the conformance framing all differ.

## What to avoid

**Restating the specification.** The W3C text is a link away and better written for its
purpose. These files exist to say what to do about it.

**Checks that produce false positives.** A scanner that flags correct code trains people to
ignore it. `html_audit.py` is tested against a clean fixture and reports nothing on it;
keep it that way.

**Claims that cannot be verified.** No conformance percentages, no counts of affected
users, no statistics without a named source. This applies to the skills as much as to the
documentation, because the skills are what a model repeats.

## Skill conventions

Each skill is a directory under `skills/` holding a `SKILL.md` with YAML frontmatter. The
frontmatter `name` must match the directory name, or the skill is invoked under the wrong
name once installed.

The `description` field is the only thing a host reads when deciding whether to load the
skill. Say what it does and when to use it, including the phrasings a user would actually
type. Keep it specific enough that a near-miss request does not trigger it.

Keep `SKILL.md` under 500 lines. Longer material goes in a `references/` directory inside
the skill, with a pointer from the body saying when to read it.

Write in the imperative, and say why an instruction matters. A model that understands the
reason handles the case you did not anticipate; a model following a rule it does not
understand does not.

## Updating the criteria data

The numbering, titles, and levels come from the W3C guidelines source. Regenerate rather
than editing by hand:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/w3c/wcag
cd wcag && git sparse-checkout set guidelines
```

`guidelines/index.html` holds the document order, and `guidelines/sc/<version>/<slug>.html`
holds each criterion's title and level. The counts to expect for WCAG 2.2 are 31 Level A,
24 Level AA, and 31 Level AAA, with 4.1.1 Parsing removed. `selfcheck.py` verifies this.

## Prose rules

Documentation follows the anti-slop rules from
[anti-slop](https://github.com/miqdadbadjuber/anti-slop). The ones that come up most:

No em dashes. Use a period, a comma, a colon, or parentheses.

No buzzword vocabulary. Words like unlock, elevate, seamless, robust, and leverage signal
an intent to impress rather than to inform.

Name the actor. Write "we rewrote the export" rather than "the export was rewritten", and
avoid giving an abstraction a human verb.

No invented specifics. A number, a date, a name, or a citation appears only if a source
supports it. A plausible-looking fabrication is worse than a vague sentence, because it
reads as honest.
