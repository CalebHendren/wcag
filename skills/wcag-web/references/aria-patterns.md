# ARIA widget patterns: the keyboard contract

Roles alone do not make a widget accessible. Announcing `role="tablist"` promises the
arrow-key behavior that screen reader users have learned to expect, and a tab set that
announces the role without implementing the keys is more confusing than a set of plain
links. This file lists the interaction contract for the widgets that come up most often, so
an audit can check the whole promise rather than just the role attribute.

Each entry gives the required structure, the keys that must work, and the state that must
stay in sync. Anything missing is a 4.1.2 finding, and missing keyboard operation is also
2.1.1.

## Dialog (modal)

Structure: `role="dialog"` with `aria-modal="true"`, and an accessible name from
`aria-labelledby` pointing at the dialog's heading, or `aria-label`.

Keys: Escape closes. Tab and Shift+Tab cycle within the dialog only.

Focus: moves into the dialog on open, to the first interactive element or the dialog
container. Returns to the element that opened it on close. Content behind the dialog is
inert, not merely visually covered, so that a screen reader's virtual cursor cannot reach
it either.

Common failures: focus left on the trigger; focus returning to the top of the page; the
background reachable by Tab; `aria-hidden` on the background while focus is still inside
it; `<dialog>` used with `show()` rather than `showModal()`, which skips the inertness.

The native `<dialog>` element with `showModal()` handles most of this. Prefer it.

## Disclosure (show and hide)

Structure: a `<button>` with `aria-expanded="true"` or `"false"`, and `aria-controls`
pointing at the content region.

Keys: Enter and Space toggle. Nothing else is required.

State: `aria-expanded` updates on every toggle, including toggles triggered by code.

Common failures: `aria-expanded` set once and never updated; the attribute placed on a
wrapper rather than the button; a `div` with a click handler instead of a button.

## Accordion

A set of disclosures. Each header contains a button, and the button sits inside a heading
element at the right level for the page outline. Optionally arrow keys move between
headers, but that is not required.

Common failure: the heading wrapping the whole panel rather than only the trigger, which
puts the panel content into the heading's accessible name.

## Tabs

Structure: `role="tablist"` containing `role="tab"` elements, each with
`aria-selected` and `aria-controls`. Each panel has `role="tabpanel"` and
`aria-labelledby` pointing back at its tab.

Keys: Left and Right arrows move between tabs in a horizontal tablist, Up and Down in a
vertical one with `aria-orientation="vertical"`. Home and End go to the first and last tab.
Only the selected tab is in the tab order; the others carry `tabindex="-1"`. Tab moves from
the tablist into the panel.

State: `aria-selected="true"` on exactly one tab at a time.

Common failures: every tab in the tab order, so Tab walks all of them; arrow keys not
implemented; `aria-selected` never updated; the panel not associated back to its tab.

## Combobox and autocomplete

Structure: an `<input>` with `role="combobox"`, `aria-expanded`, `aria-controls` pointing
at the listbox, and `aria-activedescendant` naming the currently highlighted option. The
list is `role="listbox"` containing `role="option"` elements with `aria-selected`.

Keys: Down opens the list and moves to the first option. Up and Down move through options.
Enter selects. Escape closes and returns focus to the input. Typing filters.

State: `aria-expanded` tracks the list. `aria-activedescendant` changes with the highlight,
and DOM focus stays on the input throughout.

Common failures: focus moved into the list, so typing stops working; no
`aria-activedescendant`, so screen readers announce nothing as the user arrows; the option
count never announced, which needs a live region.

This is the widget most often built wrong. Use a tested library or the native
`<input list>` and `<datalist>` where the design allows.

## Menu and menu button

Use `role="menu"` only for application menus that act like a desktop menu bar. A site
navigation dropdown is a list of links, and marking it as a menu makes screen readers
announce it in a way that does not match how it behaves.

For a real menu: a button with `aria-haspopup="menu"` and `aria-expanded`, opening
`role="menu"` with `role="menuitem"` children. Arrow keys move between items, Escape closes
and returns focus to the button, Enter activates.

## Tooltip

Structure: `role="tooltip"` on the bubble, referenced by `aria-describedby` from the
trigger. The trigger must be focusable.

Behavior for 1.4.13: the tooltip appears on both hover and focus, stays while the pointer
moves onto it, dismisses with Escape without moving the pointer, and stays visible until
dismissed or no longer valid.

Common failures: tooltip on a non-focusable element, so keyboard users never see it;
tooltip that disappears when the pointer travels toward it, which makes it unreadable under
magnification; a `title` attribute standing in for a tooltip, which is not shown on touch
and is announced inconsistently.

## Data grid and sortable table

Use a plain `<table>` with `<th scope>` unless the grid needs cell-level keyboard
navigation. A real grid needs `role="grid"`, arrow-key movement between cells, and
`aria-sort` on the sorted column header.

For a sortable table: the header contains a button, `aria-sort` on the `<th>` is
`ascending`, `descending`, or `none`, and the change is announced through a live region or
by the `aria-sort` update alone depending on screen reader support. State the support
caveat in the finding rather than claiming either way.

## Switch and toggle

`role="switch"` with `aria-checked`, or a native checkbox styled as a switch. Space toggles.
The accessible name says what the switch controls, not its state, because the state is
already announced.

Common failure: the name changing between "Turn on notifications" and "Turn off
notifications" as the state changes, which makes the control unfindable by voice.

## Live regions

`role="status"` or `aria-live="polite"` for routine updates. `role="alert"` or
`aria-live="assertive"` for urgent ones, used sparingly because they interrupt.

The container must be in the DOM before the text changes. Adding the region and its content
in the same update announces nothing in most screen readers.

Common failures: a toast component that mounts the whole region on demand; `aria-live` on a
container whose entire subtree is replaced, which announces unpredictably; assertive used
for every notification, which makes the page hostile.
