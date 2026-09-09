# WCAG 2.2 success criteria: Understandable

Information and the operation of the interface must be understandable. 20 criteria across
three guidelines. Four are new in WCAG 2.2, all of them in areas where users are routinely
locked out: help, re-entry of data, and authentication.

## Contents

- [Guideline 3.1 Readable](#guideline-31-readable)
- [Guideline 3.2 Predictable](#guideline-32-predictable)
- [Guideline 3.3 Input Assistance](#guideline-33-input-assistance)

## Guideline 3.1 Readable

### 3.1.1 Language of Page (A, 2.0)

Intent: the default human language of each page is programmatically determinable, so screen
readers load the right pronunciation rules.

Test: check `<html lang="...">` for a valid BCP 47 tag that matches the actual content.

Fails when: `lang` is missing; `lang="en"` on a page written in French; `lang=""`; a
region-only value that is not a valid tag.

### 3.1.2 Language of Parts (AA, 2.0)

Intent: passages in another language carry their own `lang`.

Fails when: quoted foreign-language text, product names in another language, or a language
switcher listing language names in their own script, all without `lang` on the part. Proper
names and technical terms are exempt.

### 3.1.3 Unusual Words (AAA, 2.0)

Intent: a mechanism identifies definitions of jargon, idioms, and words used in an unusual
way.

### 3.1.4 Abbreviations (AAA, 2.0)

Intent: a mechanism identifies the expanded form of abbreviations.

### 3.1.5 Reading Level (AAA, 2.0)

Intent: where text requires reading ability beyond lower secondary education, a
supplementary simpler version or explanation is available.

### 3.1.6 Pronunciation (AAA, 2.0)

Intent: a mechanism identifies pronunciation where meaning is ambiguous without it.

## Guideline 3.2 Predictable

### 3.2.1 On Focus (A, 2.0)

Intent: receiving focus does not initiate a change of context.

Fails when: focusing a select element navigates immediately; focusing a field opens a modal
or moves focus elsewhere.

A change of context means a change of user agent, viewport, focus, or content that changes
the meaning of the page. A change of content alone is not a change of context.

### 3.2.2 On Input (A, 2.0)

Intent: changing a form control's setting does not automatically change context unless the
user was told beforehand.

Fails when: choosing an option in a select submits the form or navigates; typing the last
character of a postcode auto-advances focus in a way the user cannot predict; a checkbox
reloads the page.

### 3.2.3 Consistent Navigation (AA, 2.0)

Intent: navigation repeated across pages appears in the same relative order each time.

Fails when: the main navigation reorders per section; the search box moves between header
and sidebar across templates.

### 3.2.4 Consistent Identification (AA, 2.0)

Intent: components with the same functionality are identified consistently across the set
of pages.

Fails when: the same action is labeled "Search", "Find", and a magnifier icon with no name
across three templates; a download icon means print on one page.

### 3.2.5 Change on Request (AAA, 2.0)

Intent: changes of context happen only on user request, or a mechanism exists to turn them
off.

### 3.2.6 Consistent Help (A, 2.2) [new in 2.2]

Intent: where a set of pages offers help, whether human contact details, a human contact
mechanism, a self-help option, or an automated contact mechanism, it appears in the same
relative order on each page unless the user changes it.

Test: locate every help affordance across the tested pages and compare its position in the
page order.

Fails when: a chat widget appears bottom right on most pages and top left on the checkout;
a support link sits in the header on marketing pages and only in the footer inside the
application. This criterion does not require you to offer help, only to keep it where users
found it last time.

## Guideline 3.3 Input Assistance

### 3.3.1 Error Identification (A, 2.0)

Intent: input errors that are automatically detected are identified in text, and the item
in error is described.

Fails when: fields turn red with no text; the error message says "Invalid input" without
naming the field; errors are announced only visually, with no live region and no focus
move, so a screen reader user submits and hears nothing.

### 3.3.2 Labels or Instructions (A, 2.0)

Intent: labels or instructions are provided when content requires user input.

Fails when: placeholder text is the only label, so it vanishes on typing; format
requirements such as date order or password rules appear only after a failed attempt;
required fields are unmarked.

### 3.3.3 Error Suggestion (AA, 2.0)

Intent: when an input error is detected and a correction is known, the suggestion is
offered to the user, unless it would jeopardize security or purpose.

Fails when: "Invalid date" with no expected format shown; a password rejection that does
not list which rule failed.

### 3.3.4 Error Prevention (Legal, Financial, Data) (AA, 2.0)

Intent: for pages causing legal commitments or financial transactions, or modifying or
deleting user-controllable data, submissions are reversible, checked, or confirmed.

Fails when: a delete action with no confirmation and no undo; a purchase with no review
step.

### 3.3.5 Help (AAA, 2.0)

Intent: context-sensitive help is available.

### 3.3.6 Error Prevention (All) (AAA, 2.0)

Intent: 3.3.4 extended to all submissions.

### 3.3.7 Redundant Entry (A, 2.2) [new in 2.2]

Intent: information the user previously entered in the same process is either auto-populated
or available to select, unless re-entry is essential, the information is needed for
security, or the earlier information is no longer valid.

Test: walk a multi-step flow and note every field asking for something already supplied.

Fails when: a checkout asks for the billing address again with no "same as shipping"
option; a multi-step form loses entries on the back button; a wizard asks for the email
twice across steps. Password confirmation is an essential exception.

### 3.3.8 Accessible Authentication (Minimum) (AA, 2.2) [new in 2.2]

Intent: no cognitive function test, such as remembering a password or solving a puzzle, is
required for any authentication step, unless an alternative exists, a mechanism assists, or
the test is object recognition or identifying non-text content the user provided.

Test: check whether password managers can paste and autofill, and whether any step demands
memory or transcription.

Fails when: paste is blocked in a password or one-time-code field; `autocomplete` is
disabled on credential fields; the login requires transcribing a code from an image; a
puzzle CAPTCHA gates sign-in with no alternative. Object recognition CAPTCHA (identifying
pictures of a common object) remains permitted, and so does recognizing content the user
supplied.

### 3.3.9 Accessible Authentication (Enhanced) (AAA, 2.2) [new in 2.2]

Intent: 3.3.8 without the object recognition and personal content exceptions.
