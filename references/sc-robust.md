# WCAG 2.2 success criteria: Robust

Content must be robust enough to be interpreted reliably by a wide variety of user agents,
including assistive technologies. Three criteria, one of which was removed in WCAG 2.2.

## 4.1.1 Parsing (removed in WCAG 2.2)

This criterion was obsoleted and removed in WCAG 2.2, and it is deprecated in WCAG 2.1. The
problems it addressed, such as duplicate `id` values and unclosed tags, are now handled by
browsers or are caught by other criteria, mostly 4.1.2 and 1.3.1.

Do not report a finding against 4.1.1 in a WCAG 2.2 audit. If a duplicate `id` actually
breaks a label association or an `aria-labelledby` reference, report it under 1.3.1 or
4.1.2 and name the real consequence.

Note that an audit against WCAG 2.0 or 2.1 for a legal regime that cites those versions may
still need to address it. Say which version you are testing against.

## 4.1.2 Name, Role, Value (A, 2.0)

Intent: for every user interface component, the name and role are programmatically
determinable; states, properties, and values that can be set by the user can be set
programmatically; and changes to these are available to assistive technology.

Test: inspect the accessibility tree for each interactive element. Confirm three things:
the role matches what the control does, the name matches the visible label, and the state
updates as the user operates it.

Fails when:
- A `div` or `span` acts as a button with no `role`, no name, and no keyboard support.
- A custom checkbox or toggle never updates `aria-checked` or `aria-pressed`.
- An accordion or disclosure control does not update `aria-expanded`.
- A tab set has no `role="tablist"`, `role="tab"`, `role="tabpanel"` relationship, or has
  the roles but no `aria-selected` maintenance.
- `aria-labelledby` or `aria-describedby` points at an `id` that does not exist.
- An ARIA role is applied without its required properties, for example `role="slider"` with
  no `aria-valuenow`.
- A native element is given a conflicting role, such as `<button role="link">` without
  matching behavior.
- A control is hidden from assistive technology with `aria-hidden="true"` while remaining
  focusable, which produces a phantom stop in the tab order.

The reliable rule: use the native element when one exists. A `<button>` carries role, name
computation, keyboard behavior, and focus for free. Every ARIA attribute you add is a
promise you then have to keep in JavaScript.

## 4.1.3 Status Messages (AA, 2.1)

Intent: status messages can be programmatically determined through role or properties, so
assistive technology can announce them without the message receiving focus.

Test: trigger every non-focus status change (search result counts, form save confirmations,
validation summaries, cart updates, loading states) with a screen reader running and
confirm it is announced.

Fails when: a "Saved" toast appears with no live region; search results update the count
silently; an inline validation error appears without `role="alert"` or an `aria-live`
region; a live region is added to the DOM at the same moment as its content, so nothing is
announced.

Practical notes:
- `role="status"` and `aria-live="polite"` wait for a pause. `role="alert"` and
  `aria-live="assertive"` interrupt. Reserve assertive for genuine urgency, because
  interruptions are hostile when overused.
- The live region container must exist in the DOM before the text changes.
- A message that moves focus to itself does not need a live region, but moving focus for a
  routine confirmation is its own problem.
