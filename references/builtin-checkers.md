# The accessibility checkers built into the tools

Word, PowerPoint, Excel, Acrobat, and LibreOffice all ship an accessibility checker. Run
the one that belongs to the file in front of you whenever you can reach it. It is fast, the
document owner already knows its vocabulary, and it inspects the document the way the
application sees it, which catches things a file-level check cannot.

Then treat its output the way you treat any scanner: as the start of the audit. These
checkers report what a rule can decide. Whether the alt text says anything, whether the
reading order matches the meaning, and whether the headings describe their sections are all
outside what any of them attempt.

## Microsoft Office

**Where it is.** Review tab, then Check Accessibility, in Word, Excel, PowerPoint, Outlook,
OneNote, and Visio, on Windows, on Mac, and on the web. Current Microsoft 365 builds also
put an Accessibility tab on the ribbon and open the results in the Accessibility Assistant
pane. Turning on "Keep accessibility checker running while I work" adds a status bar
indicator reading "Accessibility: Good to go" or "Accessibility: Investigate", which is the
fastest way to see the state of a document you have just changed.

**What it gives you.** Results in three bands. Errors are content the checker judges hard
or impossible to use. Warnings are content that is difficult for many people. Tips are
content that could be better organised. Each result names the objects it applies to,
explains why it matters, and often offers a one-click recommended action.

**What it reliably catches.** Missing alt text on pictures, shapes, charts, and SmartArt.
Tables with no header row, and merged or split cells. Blank rows and columns inside a
table. Slides with no title, and duplicate slide titles. Link text that is a bare URL
rather than a description. Runs of blank characters used to fake layout. Objects floating
rather than in line with the text. Default sheet names, and blank sheet names, in Excel.
Missing captions on inserted audio and video. Recent versions also check text contrast.

**What it does not catch**, which is most of what decides whether the document works. It
does not judge whether alt text is accurate or useful, so `alt="image"` passes. It does not
tell you that text styled large and bold is standing in for a heading, and it is not a
reliable check on heading levels that skip. It does not check the reading order of a Word
document. It does not check the document language, or a passage in a second language. It
does not check information carried by color alone beyond its contrast rule. It does not
look at the PDF you export afterwards, which is where the accessibility either survives or
does not.

**The rules move between versions.** Microsoft publishes the current set as "Rules for the
Accessibility Checker". Read that page for the version in front of you rather than assuming
a rule exists, and never report a criterion as passing because the checker was quiet about
it.

**There is no command line.** Microsoft does not publish a scripted interface to the
checker, so an agent that cannot drive the application UI cannot run it. That is a limit to
state in the report, not a gap to paper over: say the built-in checker was not run, say
what you ran instead, and note that a person opening the file will see results you could
not.

**The repair tools sit beside it.** Alt Text pane, Table Style Options with Header Row,
Styles for real headings, the Navigation pane for the heading outline in Word, the Reading
Order pane in PowerPoint, and Check Accessibility again afterwards. An agent driving the
application should use these rather than editing the file underneath the application, and
should never do both at once on the same open document.

## Adobe Acrobat Pro

**Where it is.** The accessibility tool set, reached through All tools and the prepare for
accessibility entry in current builds, and through the Accessibility tool in older ones.
Full Check, sometimes labelled Check for accessibility, produces an accessibility report
grouped into document, page content, forms, alternate text, tables, lists, and headings.

**What makes it useful.** It marks results as passed, failed, or needs manual check, and it
puts logical reading order and color contrast in that third bucket honestly, because they
are not decidable by rule. Its Reading Order tool and Tags panel are also the practical way
to repair a tag tree by hand.

**Autotag is a starting point, not a fix.** Acrobat's autotag produces a plausible tag tree
that is frequently wrong on columns, tables, and figures. Run it only as the first step of
a manual pass, and never report a document as remediated because it was autotagged.

**veraPDF** validates PDF/UA-1 against the machine-checkable Matterhorn conditions and is
open source, which makes it the right tool when a procurement asks for PDF/UA specifically.
**PAC** renders a screen reader preview of the reading order, which is the fastest way for
a person to see an order failure. `../skills/wcag-pdf/references/matterhorn.md` covers what
each standard asks for.

## LibreOffice

Tools, then Accessibility Check, on a machine with no Microsoft Office. It covers a similar
mechanical set: missing alt text, missing document language, tables with structural
problems, text styled to look like a heading, hyperlink text that is a bare URL, and
contrast. Its PDF export dialog also carries a PDF/UA option that runs the check before
exporting, which is the most reliable way to produce a tagged PDF from a command line
machine.

## Google Workspace and Apple iWork

Neither ships an equivalent checker. Google Docs, Sheets, and Slides have accessibility
settings that turn on screen reader support for the person editing, which is a different
thing, and the checking add-ons for Workspace are third party. Pages, Keynote, and Numbers
have no checker at all.

For these, the audit is your own inspection plus whatever the API exposes. Say that in the
method section, because a reader who is used to Office will assume a checker was run.

## Putting the results in a report

Three rules keep a built-in checker's output honest once it reaches the report.

**Translate the vocabulary.** Errors, warnings, and tips are the tool's categories, not
WCAG's. Map each result to the criterion it violates and to the severity the consequence
deserves, using `severity.md`. A warning about a merged cell in the table that carries the
document's only data is not a warning.

**Say which findings came from the checker.** Set `source` to `tool` on those and `manual`
on your own, so the reader can see how much of the audit was mechanical.

**Never let a clean result become a claim.** "Accessibility: Good to go" means no rule in
that version fired. It does not mean the document is accessible, and it does not support a
statement about WCAG conformance. `conformance.md` has the language that is defensible.
