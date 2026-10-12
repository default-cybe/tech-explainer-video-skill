# tech-explainer-video-skill

A Claude Code skill for making animated explainer videos about technical stuff: a bug, a system design
question, an algorithm. Everything runs on your own machine. No paid APIs, no API keys.

I built this because I wanted to actually understand my own security findings, and reading a writeup
three times wasn't doing it. A short animated walkthrough with narration did.

The visual style is minimal on purpose. Black background, white and grey text, one accent colour, and
one diagram that stays on screen and changes as the explanation moves along. If you've seen the system
design reels from Engineering Digest, it's that kind of look.

## What's in here

- `skills/impactful-explainer-video/` is the skill itself. Claude reads `SKILL.md` and follows it.
- `engine/` has the Python pieces the skill uses:
  - `theme3.py` for the visual style and reusable parts (cards, status pill, dotted cube, mode cells)
  - `tts.py` for narration with Kokoro, a local text to speech model
  - `captions.py` for word level captions using faster-whisper
  - `sfx.py` for sound effects and a quiet music bed, generated in code
- `example/scenes.py` is a two scene demo you can render to check your setup.

## Install the tools

You need Python 3.12 (3.14 is too new for some of the packages), ffmpeg, and the fonts JetBrains Mono
and Noto Sans.

```bash
uv venv --python 3.12 .venv
source .venv/bin/activate
uv pip install manim kokoro-onnx soundfile numpy faster-whisper
```

Then download the Kokoro voice model once:

```bash
mkdir -p assets && cd assets
curl -fL -O https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
curl -fL -O https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
```

## Add the skill to Claude Code

As a plugin:

```
/plugin marketplace add default-cybe/tech-explainer-video-skill
/plugin install impactful-explainer-video@tech-explainer-video-skill
```

On Claude Code 2.1.275 or newer you can do it in one line:

```
/plugin install impactful-explainer-video --marketplace default-cybe/tech-explainer-video-skill
```

Or copy the folder in by hand:

```bash
cp -r skills/impactful-explainer-video ~/.claude/skills/
```

After that, ask Claude something like "make an animated explainer video about how a token bucket rate
limiter works" and it will follow the skill.

## How a video gets made

1. Write the script as a list of scenes, each with a short narration.
2. `tts.py` turns each narration into a wav file and records how long it is.
3. Each scene is a manim animation that runs as long as its narration.
4. `captions.py` gets word timings from the audio and writes karaoke style captions.
5. `sfx.py` places small sound effects where the animation logged them, plus a soft music bed.
6. ffmpeg puts it together: video, narration, sound, and burned in captions.

The exact ffmpeg commands are in `skills/impactful-explainer-video/references/pipeline.md`.

## A few things I learned the hard way

- Saturated red or green text on pure black gets ugly speckles after H.264 compression. Use the
  softer, brighter versions of those colours, render at 2x and scale down.
- Whisper tends to put the first word at 0 seconds even when there's silence before it. The caption
  script measures where speech really starts and shifts the captions to match.
- manim's `Flash` and `Circumscribe` draw dashed lines that look like render glitches in a final
  video. The engine uses a plain glow ring instead.
- If every scene is a new layout, it feels like a slideshow. Keep one diagram and change it.

## License

MIT. See `LICENSE`.

Made by Kaivalya Ahir ([@default-cybe](https://github.com/default-cybe)). Built on
[manim](https://www.manim.community/), [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) and
[faster-whisper](https://github.com/SYSTRAN/faster-whisper).
