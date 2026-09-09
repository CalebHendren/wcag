# Reading the WCAG criteria for a mobile app

Based on the W3C note *Guidance on Applying WCAG 2.2 to Mobile Applications*, which is
informative and does not change WCAG. This file covers the Level A and AA criteria whose
mobile reading differs from the web reading, plus the ones that rarely apply. Criteria not
listed here read the same way on mobile as on the web.

## Criteria that read differently

**1.1.1 Non-text Content.** The text alternative is the platform accessibility label, not
an `alt` attribute. Icons, images, and custom-drawn views all need one, and decorative
elements must be actively hidden from the accessibility tree rather than left unlabelled,
since an unlabelled element is often announced by its filename or class.

**1.3.1 Info and Relationships.** Headings come from platform heading traits, not markup.
Grouping comes from grouping APIs. A form field's label is an association the platform
provides, not proximity on screen. A card whose children are announced separately has lost
its relationships even though it looks grouped.

**1.3.2 Meaningful Sequence.** The screen reader swipe order, which the platform derives
from the view hierarchy and which is frequently wrong for absolutely positioned or
custom-drawn layouts.

**1.3.4 Orientation.** Applies with full force. Locking to portrait is common in apps and
is a failure unless the orientation is essential.

**1.3.5 Identify Input Purpose.** Platform content types and autofill hints: `textContentType`
on iOS, `autofillHints` on Android.

**1.4.4 Resize Text.** The platform text size setting rather than browser zoom. Dynamic
Type on iOS, `sp` scaling on Android. Text that does not scale, or a layout that clips when
it does, fails.

**1.4.10 Reflow.** Applies to the app's own layout at large text sizes and in split-screen
or multi-window modes. Content requiring scrolling in two directions fails.

**1.4.12 Text Spacing.** Less directly applicable, since users cannot inject a stylesheet,
but the underlying concern reappears at large text scales.

**2.1.1 Keyboard.** Reads as external keyboard and switch access support. Many apps have
never been tested this way, and it is worth an explicit pass on any app that claims AA.

**2.4.1 Bypass Blocks.** Long repeated headers and navigation blocks in a screen, addressed
by grouping and by heading traits that allow rotor navigation.

**2.4.2 Page Titled.** Screen titles announced on navigation, through the navigation bar
title or a screen-changed announcement.

**2.4.3 Focus Order.** The swipe order and the external keyboard tab order, which can
differ from each other. Check both if a keyboard is available.

**2.4.7 Focus Visible.** Applies to keyboard and switch focus. Many apps show no visible
focus for an external keyboard at all.

**2.5.1 Pointer Gestures.** The most commonly failed mobile criterion. Swipe to delete,
swipe to reveal actions, pinch to zoom, and drag sliders all need single-pointer,
non-path-based alternatives. Custom accessibility actions satisfy this.

**2.5.4 Motion Actuation.** Shake to undo, tilt to steer, raise to answer. Each needs an
interface alternative and a way to disable the motion trigger.

**2.5.7 Dragging Movements.** Reorderable lists, drag-to-dismiss, and sliders. Custom
actions or explicit controls satisfy this.

**2.5.8 Target Size (Minimum).** 24 by 24 CSS pixels is the criterion. Both platforms
recommend more, 44 points on iOS and 48 density-independent pixels on Android. Report the
criterion, recommend the platform figure.

**3.2.3 Consistent Navigation and 3.2.4 Consistent Identification.** Read across the app's
screens rather than across a set of web pages. A tab bar that reorders between sections, or
an icon that means different things on different screens, fails.

**3.2.6 Consistent Help.** Help and support entry points in the same relative place across
screens.

**3.3.7 Redundant Entry.** Multi-step flows that ask again for what was already entered,
which is worse on mobile where typing is harder.

**3.3.8 Accessible Authentication.** Password manager and autofill support, paste allowed
in credential and one-time-code fields, and a usable fallback when biometrics fail. Apps
that block paste in a PIN or code field fail this.

**4.1.2 Name, Role, Value.** The platform accessibility API rather than ARIA. Custom
controls drawn rather than built from platform widgets carry no role or state until the app
supplies it.

**4.1.3 Status Messages.** Platform announcements and live regions. Snackbars, toasts, and
inline validation that appear without focus moving need to be announced explicitly.

## Criteria that rarely apply

**4.1.1 Parsing.** Removed in WCAG 2.2, and it never applied meaningfully to native apps.

**2.4.5 Multiple Ways.** Reads as more than one way to reach a screen, such as search
alongside navigation, and is often satisfied by the app's structure.

**3.1.1 and 3.1.2 Language.** Set at the app or view level. Less often a source of findings
than on the web, but still worth checking in multilingual apps.

## Conformance language for a mobile report

WCAG's conformance model is defined for web pages, so a native app cannot "conform to WCAG
2.2 Level AA" in the specification's own terms. Write the position accurately:

> Assessed against the WCAG 2.2 Level AA success criteria, applied to a native application
> through the W3C WCAG2Mobile guidance. 14 criteria were not satisfied. WCAG's formal
> conformance model is defined for web pages, so this report states criterion-level results
> rather than a conformance claim.

When the obligation is EN 301 549, say which of its software clauses were and were not in
scope. When it is ADA Title II, note that the rule names mobile applications directly and
sets WCAG 2.1 Level AA as the standard.
