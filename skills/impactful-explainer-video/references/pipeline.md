# Pipeline reference

Working code lives in the repo's `engine/` folder (`theme3.py`, `tts.py`, `captions.py`, `sfx.py`) and
`example/scenes.py`. Copy them next to your `script.py` and adapt.

## Colours and fonts

```python
BLACK="#000000"; INK="#f2f2f2"; DIM="#8a8a8a"; FAINT="#555555"; LINE="#2a2a2a"; CARD="#111216"
BLUE="#539bf5"; GREEN="#56d364"; RED="#ff7b72"; AMBER="#e3b341"
SANS="Noto Sans"; MONO="JetBrains Mono"
```

The accents are the softer GitHub dark mode shades. Fully saturated red and green speckle badly on
black after H.264 compression.

## Building blocks in theme3.py

- `card(title, subtitle, body, w, h)` draws a window style card: icon, bold title, grey subtitle,
  divider, body.
- `status(text)` is the pill at the bottom. In a scene, call `self.show_status(text, old=previous)` to
  swap it.
- `chip(text, accent=False, danger=False)` is a small rounded label.
- `dotcube()`, `dotcyl()`, `dotsphere()` make dotted point cloud objects. `spin(m)` turns them slowly.
- `mode_cells("0o4755")` shows a value as a row of tiles.
- `mline([(text, colour), ...])` builds a line of code with each token as its own `Text`, so colours
  don't bleed.
- `avatar(label)`, `node(label)`, `toggle(label, on)` cover people, diagram nodes and switches.
- `Base` is the scene class. It sets the black background, tracks time, logs sound cues with
  `self.sfx(name)`, has `head()` and `big_title()` for the numbered label and title, `glow(obj)` for a
  clean highlight ring, and `finish()` to pad the scene to its narration and save the cue log.

## Rendering

```bash
manim --resolution 2560,1440 --fps 30 scenes.py SceneName
```

Render at 2560x1440 and scale down to 1080p when assembling. It cleans up text edges.

## Captions

`captions.py out.ass KEY1:audio/KEY1.wav KEY2:audio/KEY2.wav` runs faster-whisper (CPU, `small.en`) on
each scene, groups words into lines of up to seven, and writes `{\kf}` karaoke timing. It finds where
speech starts in each wav and shifts that scene's captions so the first word lines up with the voice.

## Sound

`sfx.py TOTAL_SECONDS KEY1 KEY2 ...` reads `out/events_KEY.json` from each scene and writes `out/sfx.wav`
and `out/music.wav`. The effects (pop, click, tick, whoosh, ding, impact, rise) and the music bed are
made with numpy, nothing is downloaded.

## Putting it together

```bash
# 1. each scene: scale down, hold the last frame until the narration ends, add the narration
ffmpeg -i scene.mp4 -i scene.wav -filter_complex \
  "[0:v]tpad=stop_mode=clone:stop_duration=30,scale=1920:1080:flags=lanczos,fps=30[v]" \
  -map "[v]" -map 1:a -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
  -c:a aac -b:a 192k -shortest seg.mp4

# 2. join the scenes (list them in segs.txt as: file 'seg.mp4')
ffmpeg -f concat -safe 0 -i segs.txt -c copy joined.mp4

# 3. mix effects and music under the narration
ffmpeg -i joined.mp4 -i out/sfx.wav -i out/music.wav -filter_complex \
  "[0:a]volume=1.0[v0];[1:a]volume=0.7[s];[2:a]volume=0.5[m];\
   [v0][s]amix=inputs=2:duration=first:dropout_transition=0[vm];\
   [vm][m]amix=inputs=2:duration=first:dropout_transition=0,dynaudnorm=f=250:g=5[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k mixed.mp4

# 4. burn in the captions
ffmpeg -i mixed.mp4 -vf "ass=out/subs.ass" -c:v libx264 -preset slow -crf 16 \
  -pix_fmt yuv420p -c:a copy final.mp4
```

## Things that will bite you

- Use uv with Python 3.12.
- Draw a card before the things that sit on top of it, or the card hides them.
- A blank code line made with an empty Text has no points and crashes. Use a small invisible spacer.
- File names starting with a dash confuse grep and ffmpeg. Prefix them with ./ or pass -- first.
