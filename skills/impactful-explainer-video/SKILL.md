---
name: impactful-explainer-video
description: Make an animated explainer video that helps someone understand a technical idea, such as a bug, a system design question or an algorithm. Runs fully on the local machine with no paid APIs (manim for animation, Kokoro for narration, faster-whisper for captions, generated sound effects, ffmpeg to put it together). The look is minimal: black background, one accent colour, one diagram that keeps changing, small UI cards and a status line at the bottom. Use it when someone asks for an animated or explainer video, something "like Engineering Digest", or a narrated walkthrough of a concept with captions and sound.
---

# Explainer video

The goal is a video someone can watch once and actually understand. Calm, clear and dense with
information. Not loud, not shaky, not colourful for the sake of it.

## How it should look

1. **Pure black background.** Depth comes from type and layout, not gradients or glows.
2. **White and grey text with one accent colour.** Blue works well. Use red only for the thing that is
   actually broken or dangerous, and use it sparingly.
3. **One diagram per topic that stays on screen.** Build the stage once (boxes joined by thin lines, a
   bucket, a file, a request path) and keep changing it as the narration moves on. Cutting to a fresh
   layout for every point is what makes a video feel like slides. Keeping one stage is the main trick.
4. **A status pill at the bottom.** A small rounded pill with a dot and a short line of text that
   updates on each step, like "checking cache first" or "set-UID is back". It carries the story.
5. **UI cards that look like real windows.** Rounded dark card, thin border, a header with a small icon,
   a bold title and a grey subtitle, a divider, then the content.
6. **Monospace for anything technical, a clean sans serif for titles.** Each scene has a small numbered
   label like `02 · the runtime` above a bold title.
7. **Show the idea as an object.** A token bucket that fills and drains. A file as a card. A permission
   mode as a row of digit tiles. Infrastructure as dotted point clouds (a cube for a cache, a cylinder
   for a database).
8. **Big numbers for the key value**, plus chips, toggles and `// approach 1:` style comments to label
   options.
9. **Slow, smooth motion.** Fades, slides, lines drawing on, gentle morphs, a slow spin on dotted
   objects. No camera shake, no bouncy pops everywhere. Move one thing at a time.
10. **Quiet sound.** Soft ticks when something changes, a small chime on a reveal, a low note on the main
    point, and a quiet music bed under the voice.
11. **The narration leads.** Each sentence should change something on screen, but calmly.

### Things that make it look cheap

- A title bar across the top, a flat background and bullet points fading in. That's a slideshow.
- A brand new layout in every scene with nothing carried over.
- Lots of bright colours, camera shake, stick figures and bouncing text.
- manim's `Flash` and `Circumscribe`. Their dashed lines look like render glitches. Use a plain ring
  that grows and fades instead.
- Colouring code with manim's `t2c`. It bleeds colour into the next letter in monospace fonts. Build
  each coloured token as its own `Text` object.
- Saturated red or green on pure black. H.264 compression adds speckles around it. Use softer, brighter
  shades (for example `#ff7b72`, `#56d364`, `#539bf5`) and render at 2x before scaling down.
- Narration that keeps talking while nothing on screen moves.

## Pipeline

Set up with `uv venv --python 3.12` and `uv pip install manim kokoro-onnx soundfile numpy
faster-whisper`. Python 3.14 is too new for some of these. You also need ffmpeg and the fonts
JetBrains Mono and Noto Sans. Don't use LaTeX, use manim's `Text`.

1. **Script.** `script.py` holds a list of scenes, each with a key, a title and short narration written
   to be read aloud.
2. **Voice.** Kokoro (voice `am_michael`, speed about 0.95) makes one wav per scene and a
   `durations.json` with their lengths.
3. **Scenes.** Each scene subclasses the engine's `Base` in `theme3.py`. It runs as long as its narration,
   logs sound cues with `self.sfx(name)` and ends with `self.finish()`.
4. **Captions.** faster-whisper gives word timings, which become karaoke captions in an ASS file. Pass
   whisper a 16 kHz numpy array rather than a file path, since its file decoder can break. Whisper
   often puts the first word at 0 seconds, so measure where speech really starts and shift each scene
   to match.
5. **Sound.** `sfx.py` places generated sound effects at the logged cue times and adds a soft music bed.
6. **Assemble.** Pad each scene's video to the length of its audio, join the scenes, mix the effects and
   music under the narration, then burn in the captions. Render at 2560x1440 and scale to 1920x1080.

### Checking your work

Render a quick low quality pass first. Pull the last frame of each scene into a contact sheet and look
at it. Fix anything that overlaps, runs off the edge or hides behind a card (draw a card before the
things that sit on top of it). Then do the full render. At the end, make sure the video, audio and
caption tracks are the same length, the audio isn't silent, and crop a coloured area at full size to
check for speckles.

The exact helper code and ffmpeg commands are in `references/pipeline.md` and the `engine/` folder.
