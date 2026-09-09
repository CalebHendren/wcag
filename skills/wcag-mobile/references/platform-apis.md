# Mobile platform accessibility APIs

What to look for per stack, what correct looks like, and what to grep for. Read the section
for the codebase in front of you.

## Contents

- [iOS: UIKit](#ios-uikit)
- [iOS: SwiftUI](#ios-swiftui)
- [Android: Views](#android-views)
- [Android: Jetpack Compose](#android-jetpack-compose)
- [React Native](#react-native)
- [Flutter](#flutter)

## iOS: UIKit

The properties that matter, on `UIView` and anything inheriting from it:

- `isAccessibilityElement` decides whether the element is exposed at all. Custom views
  drawn with Core Graphics default to `false` and are invisible to VoiceOver until set.
- `accessibilityLabel` is the name. Short, no control type in it, since the trait supplies
  that. "Delete" not "Delete button".
- `accessibilityHint` describes the result of acting, and is optional. "Deletes the message
  permanently." Do not put the label's job here.
- `accessibilityValue` is the current value, for sliders, steppers, and progress.
- `accessibilityTraits` is the role. `.button`, `.header`, `.link`, `.selected`,
  `.adjustable`, `.notEnabled`, `.updatesFrequently`.
- `accessibilityElements` sets the order explicitly when the default order is wrong.
- `accessibilityViewIsModal` contains VoiceOver inside a modal.
- `shouldGroupAccessibilityChildren` groups children into one swipe stop.
- `accessibilityCustomActions` adds actions to the rotor, which is the fix for swipe-only
  interactions.

Announcements: `UIAccessibility.post(notification: .announcement, argument: "Saved")` for a
message, `.screenChanged` when a new screen appears, `.layoutChanged` when part of the
screen changes and focus should move.

Text scaling: `UIFont.preferredFont(forTextStyle:)` plus
`adjustsFontForContentSizeCategory = true`. A hardcoded `UIFont.systemFont(ofSize: 14)` does
not scale.

Grep for: `isAccessibilityElement`, `accessibilityLabel`, `accessibilityTraits`,
`UIFont.systemFont(ofSize`, `UIAccessibility.post`, `accessibilityElementsHidden`.

Anti-patterns worth flagging:
- A `UIButton` with only an image and no `accessibilityLabel`.
- `accessibilityLabel` set to a value that differs from the visible title (2.5.3).
- `accessibilityElementsHidden = true` on something the user needs.
- `UIFont.systemFont(ofSize:)` on body text, which blocks Dynamic Type.
- A `UITapGestureRecognizer` on a `UIView` with no trait and no label, which is a control
  VoiceOver cannot find.
- `accessibilityTraits = .none` on an interactive element.

## iOS: SwiftUI

- `.accessibilityLabel("Delete")`, `.accessibilityValue`, `.accessibilityHint`.
- `.accessibilityAddTraits(.isButton)` and `.isHeader`, `.isSelected`.
- `.accessibilityHidden(true)` for decoration.
- `.accessibilityElement(children: .combine)` to merge a card into one element, or
  `.ignore` with an explicit label.
- `.accessibilityAction(named:)` for custom actions, and `.accessibilityActions` for a set.
- `.accessibilitySortPriority` to correct the order.
- `@ScaledMetric` for sizes that should grow with the text size.
- `.dynamicTypeSize(...)` clamps, and clamping too tightly is itself a finding.

`Image(decorative:)` and `Image(systemName:)` inside a `Button` with a text label are
common sources of duplicate announcements.

Grep for: `.accessibilityLabel`, `.accessibilityHidden`, `.accessibilityElement`,
`.font(.system(size:`, `@ScaledMetric`, `.dynamicTypeSize`.

## Android: Views

- `android:contentDescription` is the name. `null` marks decoration, and the literal string
  "null" is a bug worth flagging.
- `android:importantForAccessibility="no"` or `noHideDescendants` hides an element.
- `android:labelFor` associates a `TextView` label with an `EditText`, which is how a field
  gets its name.
- `android:hint` is not a label. It disappears on typing and is announced inconsistently.
- `ViewCompat.setAccessibilityHeading(view, true)` marks a heading.
- `android:screenReaderFocusable="true"` plus child descriptions groups a card.
- `AccessibilityNodeInfoCompat.AccessibilityActionCompat` adds custom actions.
- `view.announceForAccessibility("Saved")` announces, and `android:accessibilityLiveRegion`
  makes a region announce on change.
- `android:minWidth` and `android:minHeight` of `48dp` for touch targets.
- Text sizes in `sp`, never `dp`. `dp` text does not scale with the user's setting.

Grep for: `contentDescription`, `importantForAccessibility`, `labelFor`, `android:hint`,
`textSize="[0-9]+dp"`, `announceForAccessibility`, `setAccessibilityHeading`.

Anti-patterns:
- `ImageButton` or `ImageView` with a click listener and no `contentDescription`.
- `contentDescription` on a `TextView` that already has visible text, causing a duplicate.
- `android:hint` as the only label on an `EditText`.
- Text sizes in `dp`.
- Touch targets below `48dp` with no padding.
- A `View` with `setOnClickListener` and no role, announced as plain text.

## Android: Jetpack Compose

- `Modifier.semantics { contentDescription = "Delete" }`, or the `contentDescription`
  parameter on `Image` and `Icon`. `null` marks decoration.
- `Modifier.semantics { heading() }` marks a heading.
- `Modifier.clearAndSetSemantics { }` replaces a subtree's semantics, which is how a card
  becomes one element. Used carelessly it also erases things users need.
- `Modifier.semantics(mergeDescendants = true)` merges children.
- `Modifier.semantics { role = Role.Button }`, `stateDescription`, `selected`, `toggleable`.
- `Modifier.semantics { customActions = listOf(...) }` for gesture alternatives.
- `Modifier.clickable` supplies the button role and the minimum touch target; a bare
  `pointerInput` detector does neither.
- Text sizes in `.sp`.
- `LocalDensity` and `fontScale` for anything that must track the text size.

Grep for: `contentDescription`, `clearAndSetSemantics`, `mergeDescendants`, `Role.`,
`pointerInput`, `\.dp\)` near `fontSize`, `heading()`.

## React Native

- `accessible={true}` groups a view's children into one element, which is the main tool for
  reducing swipe count.
- `accessibilityLabel` is the name, `accessibilityHint` the result of acting.
- `accessibilityRole` is the role: `button`, `link`, `header`, `image`, `search`,
  `adjustable`, `alert`.
- `accessibilityState={{ disabled, selected, checked, expanded, busy }}`.
- `accessibilityValue={{ min, max, now, text }}` for sliders and progress.
- `accessibilityActions` with `onAccessibilityAction` for custom actions.
- `AccessibilityInfo.announceForAccessibility('Saved')` for announcements.
- `accessibilityLiveRegion` on Android, `accessibilityViewIsModal` on iOS.
- `importantForAccessibility="no-hide-descendants"` to hide a subtree.
- `allowFontScaling` defaults to true on `Text`; setting it to `false` blocks text scaling
  and is a finding.

Grep for: `accessibilityLabel`, `accessibilityRole`, `accessible=`, `allowFontScaling`,
`TouchableOpacity`, `onPress`, `announceForAccessibility`.

Anti-patterns:
- `TouchableOpacity` with an icon child, no label and no role.
- `allowFontScaling={false}`.
- Fixed `height` on a container holding scalable text.
- `Pressable` with `hitSlop` used to meet target size, which helps touch but the visible
  target is what 2.5.8 measures. Report both.

## Flutter

- `Semantics(label: 'Delete', button: true, child: ...)`.
- `ExcludeSemantics` for decoration, `MergeSemantics` to group.
- `Semantics(header: true)` for headings.
- `SemanticsService.announce('Saved', TextDirection.ltr)` for announcements.
- `Semantics(customSemanticsActions: ...)` for gesture alternatives.
- `MediaQuery.textScalerOf(context)` for text scaling. A `Text` with a hardcoded
  `fontSize` inside a fixed-height `Container` clips at large scales.
- `IconButton` supplies a `tooltip` which becomes the semantic label; a bare `GestureDetector`
  wrapping an `Icon` supplies nothing.

Grep for: `Semantics(`, `ExcludeSemantics`, `MergeSemantics`, `GestureDetector`,
`textScaleFactor`, `SemanticsService`.

Anti-patterns:
- `GestureDetector` around an `Icon` with no `Semantics` wrapper.
- `Container` with a fixed `height` holding `Text`.
- Custom painted widgets with no `Semantics`, invisible to the screen reader.

## Hybrid and webview apps

The web content inside the webview follows `../../wcag-web/SKILL.md`. Two things break at
the boundary:

- Focus moving between native chrome and webview content, which is often lost entirely.
  Test the transition in both directions.
- Native controls overlaying webview content, where the native layer covers the focused web
  element (2.4.11).

Audit both layers and say which findings belong to which, because they go to different
teams.
