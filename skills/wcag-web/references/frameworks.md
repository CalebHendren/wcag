# Framework and platform notes

Where accessible output comes from a build step, the fix belongs in the source. This file
lists what breaks per stack and where to look for it.

## Single-page applications, any framework

**Route changes.** The browser does the work on a full page load: it moves focus to the
document, announces the new title, and resets the reading position. Client-side routing
does none of that unless the app does it.

After each navigation, set `document.title`, and move focus to a heading or a container
with `tabindex="-1"`. A live region announcing the new page name is an acceptable
alternative and is easier to get right in some routers. Without one of these, a screen
reader user hears nothing and stays where they were (2.4.2, 2.4.3).

**Focus after async content.** Focus moved before the element renders does nothing and
fails silently. Move focus in the effect that runs after the render, and guard on the ref
being present.

**Virtualized lists.** Removing the focused row from the DOM drops focus to `<body>`,
losing the user's place. Keep a stable focus target, or move focus deliberately before
recycling.

## React

- `useEffect` focus calls that run before the node exists. Check the ref before calling
  `focus()`, and confirm the effect's dependency array actually re-runs it.
- Portals put the modal outside the DOM order, so focus containment and `inert` on the
  background have to be written explicitly.
- Custom `Button` components that render `div` or `a` based on props. Read the component,
  not its usage.
- `dangerouslySetInnerHTML` bringing in unlabelled markup from a CMS.
- Fragment-heavy trees that lose the landmark structure, so nothing is wrapped in `<main>`.
- Icon libraries rendering bare `<svg>` with no `aria-hidden="true"`.

## Vue, Svelte, Angular

- Vue: `v-show` hides visually but leaves the element in the accessibility tree and the tab
  order. `v-if` removes it. Reach for `v-if` when the content should be gone.
- Svelte: transitions can leave an element focusable during its outro. Check that closing
  a menu removes it from the tab order immediately.
- Angular: `[hidden]` is overridden by any `display` rule, which leaves supposedly hidden
  content reachable. CDK's `A11yModule` (`cdkTrapFocus`, `LiveAnnouncer`) handles focus and
  announcements, and is worth recommending when the codebase already uses the CDK.

## Design systems and component libraries

Audit the primitives, then spot-check usage. In order of yield: form field wrapper, button,
link, modal, dropdown or select, tabs, table, toast or notification, icon.

For each primitive, check that it renders the native element, forwards `aria-*` props,
exposes a way to set an accessible name, keeps its own focus styles rather than resetting
them, and maintains state attributes.

One finding on a primitive replaces dozens on pages. Say that in the report, because it
changes how the work is estimated.

## Tailwind and utility CSS

- `outline-none` applied without a replacement `focus-visible:` style. Grep for it.
- `sr-only` used correctly is fine; `hidden` on something that should still be announced is
  not.
- Arbitrary color values bypass the palette, so contrast has to be checked per instance.
- `text-xs` on body copy tends to fail contrast at the greys most palettes pair it with.

## HTML email

A constrained environment with its own rules:

- Set `lang` on the wrapping element, and give the message a `<title>`.
- Layout tables need `role="presentation"`, or screen readers announce table navigation
  over the layout.
- Every image needs `alt`, and spacer images need `alt=""`.
- Do not rely on background images for content, since many clients strip them.
- Keep link text meaningful, because "click here" is even worse in an email read linearly.
- Do not rely on CSS that clients strip. Contrast must hold in the plain rendering too.
- Provide a plain-text alternative part.

## Content management systems

The template is the author's responsibility and the content is the editor's. Separate the
two in the report, because they go to different people with different tools.

Template findings: landmarks, heading levels around the content region, skip links, focus
styles, contrast in the theme.

Content findings: alt text, heading structure inside articles, link text, table headers,
embedded media captions. These recur, so recommend an editor checklist and, where the CMS
supports it, a publish-time check rather than one-off fixes.
