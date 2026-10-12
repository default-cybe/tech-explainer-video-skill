#!/usr/bin/env python
"""Synthesize one wav per scene with Kokoro; write audio/durations.json."""
import json, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from script import SCENES

VOICE, SPEED, SR = "am_michael", 0.95, 24000
LEAD, TRAIL = 0.35, 0.65   # seconds of silence padding

k = Kokoro("assets/kokoro-v1.0.onnx", "assets/voices-v1.0.bin")
durations = {}
for s in SCENES:
    samples, sr = k.create(s["narration"], voice=VOICE, speed=SPEED, lang="en-us")
    pad_l = np.zeros(int(LEAD * sr), dtype=samples.dtype)
    pad_r = np.zeros(int(TRAIL * sr), dtype=samples.dtype)
    clip = np.concatenate([pad_l, samples, pad_r])
    path = f"audio/{s['key']}.wav"
    sf.write(path, clip, sr)
    dur = round(len(clip) / sr, 3)
    durations[s["key"]] = dur
    print(f"{s['key']:16s} {dur:6.2f}s  -> {path}")

json.dump(durations, open("audio/durations.json", "w"), indent=2)
print(f"\nTOTAL {sum(durations.values())/60:.1f} min across {len(durations)} clips")
