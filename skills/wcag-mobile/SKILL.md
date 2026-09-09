---
name: wcag-mobile
description: "Audit or fix accessibility in mobile apps and mobile content against WCAG 2.2 and the W3C WCAG2Mobile guidance. Use for native iOS (UIKit or SwiftUI), native Android (Views or Compose), React Native, Flutter, hybrid and webview apps, responsive mobile web, and app store or in-app content. Covers VoiceOver and TalkBack, accessibility labels and traits, focus and swipe order, Dynamic Type and text scaling, touch target size, gestures and drag alternatives, orientation, motion actuation, and live announcements. Load this whenever someone mentions a mobile app, iOS, Android, VoiceOver, TalkBack, Swift, Kotlin, React Native, Flutter, accessibilityLabel, contentDescription, or asks whether an app works for blind or motor-impaired users."
license: MIT
allowed-tools: Read, Grep, Glob, Bash, WebFetch, Write, Edit
---

# Mobile accessibility: audit and remediation

Read `../wcag/SKILL.md` first if you have not. It sets the mode, the finding record, and
the report shape.

Audit is the default here as everywhere. If the user asked a question rather than for
fixes, report and change nothing. This skill carries edit permissions because it also
describes remediation, not because auditing may edit.

## What WCAG means on a mobile app

WCAG was written for web content, and its normative conformance model is defined for web
pages, so a native app cannot conform to WCAG in the specification's own terms. Two W3C
notes bridge the gap, and they do different jobs:

**WCAG2ICT** (*Guidance on Applying WCAG 2 to Non-Web Information and Communications
Technologies*) is a completed W3C Group Note from October 2024 covering WCAG 2.0, 2.1, and
2.2. It supplies the substitution rules that make each criterion meaningful for non-web
software, and it is the document regulations already reference. Anchor a claim to this one.

**WCAG2Mobile** (*Guidance on Applying WCAG 2.2 to Mobile Applications*) is a narrower and
more recent draft note, first published in May 2025. It gives the mobile-specific reading of
the Level A and AA criteria, which is more concrete than WCAG2ICT for an app. Cite it as
supporting interpretation.

`../../references/non-web.md` covers both, including the substitutions and the language for
a conformance position. Read it before writing one.

Two practical consequences for a report:

First, use WCAG criteria as the vocabulary, because that is what the obligation is written
in, and say in the method section which interpretation you applied. Do not claim
conformance in the WCAG sense for a native app without naming that caveat.

Second, where a legal obligation covers native apps, it usually reaches them through a
different route. ADA Title II names mobile applications directly. EN 301 549 covers native
apps under its software clauses, chiefly Clause 11, which imports the WCAG criteria and
adds requirements WCAG does not carry. `../../references/legal.md` has the mapping.

## Establish what you can test

The strongest position is a build on a real device with the screen reader running. Nothing
substitutes for it, because the platform accessibility API is where the truth lives.

If you have source only, you can find a great deal: missing labels, decorative elements not
hidden, hardcoded sizes, missing traits and roles, gesture-only interactions, and hardcoded
strings that will not scale. Say clearly that no runtime testing was done, and mark focus
order, announcement quality, and contrast as not tested unless you can derive them.

Grep is effective here. `references/platform-apis.md` lists the attributes and the search
patterns for each platform, and the anti-patterns worth grepping for.

## Test in this order

### 1. Screen reader sweep

VoiceOver on iOS, TalkBack on Android. Swipe right through the whole screen from the top,
then use the rotor or the reading controls to move by heading.

What to check on every element:

- Does it announce a **label** that says what it is, matching the visible text (1.1.1,
  4.1.2, and 2.5.3 for anything with a visible label).
- Does it announce its **role**, so a button is announced as a button rather than as plain
  text (4.1.2). On iOS this is the trait; on Android it comes from the widget class or the
  semantics role.
- Does it announce its **state**, selected, expanded, checked, disabled, and update when the
  state changes (4.1.2).
- Is the **swipe order** the same as the visual order, top to bottom, and does it skip
  decoration (1.3.2, 2.4.3).
- Are decorative images and duplicated text **hidden** from the screen reader rather than
  read out twice (1.1.1).

The recurring failure is an icon button with no label, announced as its image asset name or
as nothing at all. Second is a card where every child element is announced separately, so
one item takes twelve swipes, when the card should be grouped into a single element with
one label.

### 2. Text scaling

Set the system font size to its largest setting, and turn on any bold-text or larger-accessibility-sizes
option the platform offers.

Text must scale, and the layout must survive it (1.4.4). Look for text truncated with an
ellipsis, text clipped by a fixed-height container, buttons whose labels no longer fit,
and content pushed off screen with no way to scroll to it. Also check for horizontal
scrolling appearing where there was none (1.4.10).

iOS scales text automatically only when the app uses Dynamic Type. Android scales `sp`
units and not `dp`, so hardcoded `dp` text sizes are a reliable failure.

### 3. Touch targets and gestures

Measure the small controls. WCAG 2.5.8 sets 24 by 24 CSS pixels as the minimum with a
spacing exception, while both platforms recommend more: 44 by 44 points on iOS and 48 by 48
density-independent pixels on Android. Report against the criterion, and mention the
platform guidance as the better target.

Then find every interaction that needs a gesture, and check for a single-pointer
alternative:

- Path-based gestures such as swipe to delete, pinch to zoom, or a slider dragged along a
  track need an alternative that is not path-based (2.5.1).
- Anything that requires dragging, such as reordering a list or moving a card, needs a
  non-dragging way to do the same thing (2.5.7). Custom accessibility actions are the usual
  answer on both platforms.
- Actions that fire on touch-down rather than touch-up cannot be aborted by sliding away
  (2.5.2).

Swipe-to-delete with no alternative is the most common 2.5.1 failure in production apps,
and it is usually a small fix with a custom action.

### 4. Orientation and motion

The app supports both portrait and landscape unless a specific orientation is essential
(1.3.4). Locking to portrait excludes users whose device is mounted to a wheelchair.

Anything triggered by shaking, tilting, or moving the device needs an interface control
that does the same thing, and the motion trigger should be able to be turned off (2.5.4).
Respect the platform's reduce-motion setting for animation and parallax (2.3.3).

### 5. Announcements and dynamic content

Toasts, snackbars, validation errors, loading completions, and content that arrives without
focus moving all need to reach a screen reader user (4.1.3). On iOS this is a
`UIAccessibility` announcement notification or a layout-changed notification; on Android it
is a live region or `announceForAccessibility`.

A toast that disappears after three seconds and is never announced is invisible to a screen
reader user, and it is usually the confirmation that their action worked.

### 6. Forms and authentication

Every field has a label that persists, not a placeholder that vanishes (3.3.2). Errors are
announced and say how to fix them (3.3.1, 3.3.3). Fields carry the right content type or
autofill hint so password managers work.

Authentication is worth a specific pass (3.3.8). Check that the password field accepts
paste and works with the platform password manager, that a one-time code can be autofilled
rather than transcribed, and that biometric authentication has a usable fallback. Blocking
paste in a password field is a failure and a common one.

### 7. Contrast and color

Measure text and interface element contrast with `scripts/contrast.py`, in both light and
dark themes, since dark themes are frequently unchecked (1.4.3, 1.4.11). Then look for
anything conveyed by color alone, such as a status dot or a chart series (1.4.1).

## Platform tooling

Recommend these and say what each covers:

- **iOS**: Accessibility Inspector in Xcode for the accessibility tree and audits, VoiceOver
  on a device, and the Accessibility Audit API in XCUITest for regression coverage.
- **Android**: Accessibility Scanner for on-device checks, TalkBack on a device, and the
  Espresso accessibility checks for automated coverage in the test suite.
- **React Native and Flutter**: the platform tools above still apply, since both render to
  native accessibility APIs. Flutter also has `SemanticsDebugger`.

None of these judge label quality, announcement order, or whether an alternative to a
gesture exists. That is the audit.

## Platform detail

`references/platform-apis.md` covers the attributes, the correct patterns, the
anti-patterns, and grep-able search terms for UIKit, SwiftUI, Android Views, Jetpack
Compose, React Native, and Flutter. Read the section for the stack in front of you rather
than the whole file.

`references/wcag2mobile.md` covers how the Level A and AA criteria read for a mobile app,
including the ones that need reinterpretation and the ones that rarely apply.


Read `../wcag/SKILL.md` first if you have not. It sets the mode, the finding record, and
the report shape.

Audit is the default here as everywhere. If the user asked a question rather than for
fixes, report and change nothing. This skill carries edit permissions because it also
describes remediation, not because auditing may edit.

## When remediating

Read `../wcag-remediate/SKILL.md` first. Mobile-specific notes:

- Fix the shared component. A label missing from one button is usually missing from the
  design-system button.
- Grouping is usually a bigger win than labelling. Merging a card's children into one
  accessible element with a composed label turns twelve swipes into one and makes the
  screen usable.
- Never add a label that differs from the visible text. Voice Control on iOS and Voice
  Access on Android both operate controls by their visible name (2.5.3).
- Do not hide something from the screen reader to silence a scanner warning. Hiding a
  control that users need is a worse failure than the one being reported.
- Adding a custom accessibility action is often the correct fix for a gesture-only
  interaction, and it is smaller than redesigning the gesture.
- Re-test with the screen reader after every change. Accessibility changes on mobile
  interact with focus in ways that source review does not reveal.
