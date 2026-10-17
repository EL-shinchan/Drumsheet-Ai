# ML engine (the new drum-transcription pipeline)

This folder is the start of a rewritten engine. The goal is a drum sheet that is
~90% accurate and reads like a real, human-readable chart — not a generic groove
stamped over the audio (which is what the old `engine/process_song.py` does).

## The idea in plain words

The old engine listens to the **whole song at once** and **guesses** with
hand-written rules ("low sound = kick"), then fills in a fixed drum pattern.
That is why it sounds generic and cannot get accurate.

The new engine has four steps, each a tool that was *trained on examples* instead
of guessed:

1. **Clean the audio** — split the song so we only hear the drums. *(Demucs)* ← done
2. **Find the beat** — figure out exactly where each beat lands. *(madmom — next)*
3. **Recognize the drums** — a model that learned from thousands of examples says
   "kick here, snare there." *(MT3 / Omnizart / ADT — later)*
4. **Print it nicely** — lay it out as a clean, readable sheet. *(MuseScore / LilyPond — later)*

The website and API stay the same. We only swap out the "brain."

## Status

| Step | Tool | State |
| --- | --- | --- |
| 1. Separate drums | Demucs 4.1.0 | ✅ working on CPU (`separate_drums.py`) |
| 2. Beat tracking | madmom | ⬜ not started |
| 3. Drum transcription | TBD | ⬜ not started |
| 4. Engraving | TBD | ⬜ not started |

## Setup (one time)

```bash
# from the repo root
python3.14 -m venv ml/.venv
ml/.venv/bin/python -m pip install -r ml/requirements.txt
```

Needs `ffmpeg` on the PATH (already installed via Homebrew).

## Step 1: separate the drums

```bash
ml/.venv/bin/python ml/separate_drums.py benchmarks/audio/billie-jean.mp3
# -> writes ml/output/htdemucs/billie-jean/drums.mp3 (+ bass/vocals/other)
```

Notes:
- Runs on CPU (`-d cpu`). Apple-GPU (MPS) currently errors on this model.
- ~3–4 minutes for a full song on an M-series Mac.
- `ml/.venv` and `ml/output` are git-ignored (too big / generated).
