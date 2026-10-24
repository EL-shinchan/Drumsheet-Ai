# Step 2 — Beat Grid Design

Date: 2026-10-24

## Goal
Produce a correct beat grid for a song: the time of every beat, and which of those
beats is **beat 1** of each bar. Step 3 snaps detected drum hits onto this grid, so
if the grid is wrong, every note lands in the wrong slot no matter how well the
drums are detected.

## Why this step exists
The old engine guesses the grid. `estimate_tempo()` uses autocorrelation, which
often lands on half or double the real tempo, and `choose_preview_window()` guesses
where bar 1 starts by scoring backbeat bonuses. If either guess is off by an 8th
note, the sheet is unreadable even when the hits are right.

## Tool: beat_this (not madmom)
- **beat_this 1.1.0** (CPJKU, 2024), from the team that made madmom and built to
  replace it. It returns beat times and downbeat (beat 1) times.
- madmom 0.16.1 (last release 2018) **fails to build** on our Python 3.14.
- beat_this's first audio loader (torchaudio 2.11) can't read our mp3s, so it needs
  **soundfile** installed as the fallback loader.
- Settings: checkpoint `final0`, `device="cpu"`, `dbn=False`.
- Speed: about 5 s for a full song on CPU.

## Input: the full song, not the drums stem
Bass lines and chord changes are what locate beat 1, and Demucs removes them from
the drums stem. So the grid comes from the **full mix**, and Step 3 reads the hits
from the **drums stem**.

Evidence (Billie Jean, full mix): 133 of 151 bars came out as 4 beats. 15 of the
16 two-beat bars sit in the first 18 s, where the drum machine plays alone before
the bass enters. Without bass or chords, the model can't tell which beat is 1.

## Repairs on top of the raw model output

### 1. Drop phantom beats before the music starts
beat_this can put beats in the silence before the first sound. On Billie Jean it
put a beat at 0.72 s, but the music starts at 1.28 s. That one extra beat would
shift every bar count by one.

Rule: find the first sound in the **full mix** (energy above a threshold) and drop
every beat more than ~50 ms before it. We use the full mix, not the drums stem,
because a song can open with vocals or guitar, and the beats there are real.

### 2. Repair beat 1 by counting in 4s from confident stretches
Model downbeats are trusted only inside a **confident run**: at least 8 bars in a
row of exactly 4 beats each. Every other bar is renumbered by counting in 4s from
the nearest confident run, backwards through intros and forwards through hiccups.
This works whether a song starts on beat 1 or with a pickup.

Evidence (Billie Jean): the first confident run starts at 30.06 s. Counting back
from there in 4s puts beat 1 at 1.24 s, the first drum hit. That matches what a
drummer would count, and the kick pattern agrees: kicks fall on beats 1 and 3,
not 2 and 4.

If a song has **no** confident run, don't force a grid. Report it as low
confidence instead.

## Output
`ml/beat_grid.py <song>` writes JSON:
- `bpm`: median tempo
- `firstSound`: seconds
- `beats`: list of beat times
- `downbeats`: list of beat-1 times after repair
- `bars`: one entry per bar with `start` and `source` (`model` or `repaired`), so
  we can see what was fixed
- `confident`: false when no confident run was found

It also writes a **click track**: the song with a click mixed in, accented on
beat 1 (`ml/output/<song>/click.mp3`). A drummer can hear in seconds whether the
grid is right.

## Verification
For both benchmark songs:

| Check | Billie Jean | In the End |
| --- | --- | --- |
| BPM inside the manifest range | 115–121 | 100–110 |
| Every bar is 4 beats, except at most the final fade bar | ✓ | ✓ |
| Kick energy on beats 1 and 3 is higher than on 2 and 4 | ✓ | ✓ |
| First beat 1 matches the first drum hit, within 50 ms | 1.24 s | to be checked |
| **Eddie listens to the click track at three spots (intro, middle, end) and confirms beat 1** | ✓ | ✓ |

The listening check is the one that counts. The numbers only catch obvious
breakage.

## Dependencies to add
`beat-this==1.1.0`, `soundfile==0.14.0`, `torchaudio==2.11.0` (pulled in by
beat_this; pinned so it doesn't drift).

## Out of scope for this step
- Time-signature changes and odd meters: this step assumes 4/4 throughout.
- Swing and triplet feel.
- Snapping drum hits to the grid (Step 3).
- Connecting to the Next.js API route.
