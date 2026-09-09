# Audio, video, and synchronized media

Media criteria are failed more often by quality than by absence. Captions exist; they name
no speakers. A transcript exists; it omits what the screen showed. This file covers how to
judge the artifact, not just find it.

Applies to criteria 1.2.1 through 1.2.9, plus 1.4.2 Audio Control and 2.2.2 Pause, Stop,
Hide for autoplaying media, and 2.1.1 Keyboard for the player controls.

## Decide what the media is first

The requirements follow from the type, so classify before testing:

- Audio-only, prerecorded: a podcast, a recorded call. Needs a transcript (1.2.1).
- Video-only, prerecorded: a silent animation or screen capture. Needs a transcript or an
  audio track conveying the same information (1.2.1).
- Synchronized media, prerecorded: video with meaningful audio. Needs captions (1.2.2), and
  audio description or a full media alternative at Level A (1.2.3), and audio description
  specifically at Level AA (1.2.5).
- Live audio-only: needs a text alternative only at AAA (1.2.9).
- Live synchronized media: needs real-time captions at AA (1.2.4).
- Media alternative for text, clearly labeled as such: exempt from 1.2.1 through 1.2.5.

Media used purely as decoration with no information still triggers 1.4.2 and 2.2.2 if it
plays automatically.

## Judging captions

Captions must convey dialogue and the non-speech audio needed to understand the content.
Check a sample of at least two minutes against the audio, including a passage with more
than one speaker.

Fails when:
- Speakers are not identified where more than one person talks.
- Meaningful sound effects, laughter, music cues, or off-screen audio are omitted.
- Automatic captions are shipped without correction. They mangle names, technical terms,
  and punctuation, and punctuation changes meaning.
- Captions are burned into the video with no way to turn them off and no ability to resize
  them. Open captions satisfy 1.2.2 but interact badly with 1.4.4 and user preferences.
- Captions run so fast or so far behind that they cannot be read alongside the picture.
- A transcript is offered instead of captions. A transcript does not satisfy 1.2.2, because
  captions are synchronized and a transcript is not.

## Judging audio description

Audio description covers visual information that the soundtrack does not carry: on-screen
text, actions, charts, expressions, scene changes.

Fails when: the narration says "as you can see here" or "click this button" with no
description; a demo shows a form being filled with no spoken account of the fields; a chart
appears with only the phrase "the results are striking".

If the existing narration already describes everything visual, no separate description
track is needed, and the audit should say why rather than reporting a missing track.

At Level A, 1.2.3 accepts a full text alternative instead of description. At Level AA,
1.2.5 requires the description itself, so a text alternative alone stops being enough.

## Judging transcripts

A transcript is a text version of everything the media conveys. For video it must include
the visual information as well as the dialogue, which is why a caption file exported as
text is not a sufficient transcript for video.

Good practice beyond conformance: put the transcript on the page rather than behind a
download, structure it with headings and speaker names, and link timestamps into the
player.

## Player controls

The player is a user interface component and carries the ordinary criteria. Check that
every control is reachable and operable by keyboard (2.1.1), that controls have accessible
names (4.1.2), that the focus indicator is visible over the video (2.4.7 and 1.4.11), that
the caption toggle is discoverable, and that keyboard shortcuts do not conflict with
assistive technology (2.1.4).

## Autoplay

Audio that plays automatically for more than three seconds must be pausable or stoppable,
or have an independent volume control (1.4.2). Motion that lasts more than five seconds
must be pausable, stoppable, or hideable (2.2.2). Both apply to the whole page under the
non-interference conformance requirement, so an autoplaying background video in a footer
breaks conformance for the entire page.

The safe default is to autoplay nothing with sound, and to respect `prefers-reduced-motion`
for anything that moves.
