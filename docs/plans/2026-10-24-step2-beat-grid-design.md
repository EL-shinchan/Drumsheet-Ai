# Step 2 — Beat Grid Design

Date: 2026-10-24
Status: Draft, revised after review. Awaiting Eddie's approval.

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
Bass lines, chord changes and vocal entries all help locate beat 1, and Demucs
removes them from the drums stem. So the grid comes from the **full mix**, and
Step 3 reads the hits from the **drums stem**.

Evidence (Billie Jean): on the full mix, 16 bars come out with only 2 beats. On the
drums stem it's 94, plus two phantom beats.

## What the raw model gets wrong (Billie Jean)
In the stems, the drum machine is alone from 1.2–5 s, bass enters around 5 s, synth
around 21.5 s and vocals around 30 s.
- **1.2–18 s:** beat 1 is marked on every other beat (two-beat bars).
- **18.8–29 s:** five 4-beat bars in a row with **beat 3 labelled as beat 1**, even
  with bass and synth playing. The model only locks onto the right beat once the
  vocal comes in.
- **0.72 s:** a phantom beat in the digital silence before the music (which starts
  at about 1.21 s).

The 18.8–29 s stretch is the dangerous one. A few more wrong bars would have
looked like a confident run, and the whole song would have been numbered from the
wrong beat.

How we know the right answer is beat 1 at 1.24 s: in the bass stem, the bass notes
on beats 1–4 come out as F#, E, E, B, which is the riff's actual order. (Kick
energy can't settle it, because "kicks on 1 and 3" also fits a grid that's off by
two beats.)

## Repairs, in order

### 1. Repair the beats themselves
Counting in 4s only works if the beat list is right.
- Work out the normal beat gap (fitted from all beat times; see Tempo below).
- Where a gap is about **2×** normal, a beat was missed: insert one in the middle.
- Where two neighbouring gaps are each about **0.5×** normal, an extra beat was
  added: remove it.
- Trim the ends. Drop beats more than **half a beat before the first sound** and
  more than half a beat after the last sound. "Sound" means full-mix energy above
  **peak − 50 dB**. The threshold is set relative to the song's peak so that real
  beats in a quiet intro or fade aren't dropped. It uses the full mix because a
  song can open on vocals or guitar, and those beats are real.

A phantom beat left in doesn't shift the bar count (counting starts from a
confident run, below). It becomes a fake one-beat pickup, which still has to go.

### 2. Pick one beat-1 position for the whole song
We assume 4/4 for the whole song, so after the beat repair, beat 1 should be the
same position in every bar (beat index mod 4) from start to finish.
- A **confident run** is at least 8 model bars in a row with exactly 4 beats each.
- **If every confident run agrees** on the position: use it for the whole song.
- **If runs disagree:** look between them for a beat gap that was about 2× or 0.5×
  normal *before* repair. If there is one, the position changes there. If there
  isn't, use the position covering the most bars and add a `warnings` entry.
- **If there's no confident run at all:** don't force a grid. Set
  `confident: false`.

Test this with a unit test on a modified copy of Billie Jean's beat list: add a
phase flip mid-song, drop a beat, and add an extra one.

## Tempo
Report the **fitted** tempo: a straight-line fit of beat number against beat time.
Don't use the median gap. beat_this places beats on a 20 ms grid, so the median
can only take a few values: Billie Jean's median gives 115.4 against a true 116.8,
which passes the 115 floor by only 0.4.

## Output
`ml/beat_grid.py <song>` writes JSON:
- `bpm`: fitted tempo
- `firstSound`, `lastSound`: seconds
- `beats`: beat times after repair
- `downbeats`: beat-1 times. When `confident` is false, these are the model's raw
  downbeats, unrepaired, so Step 3 knows not to trust them.
- `bars`: one entry per bar with `start` and `source` (`model` or `repaired`)
- `confident`: false when no confident run was found
- `warnings`: e.g. runs that disagreed with no beat gap to explain it
- `stats`: the raw model's non-4-beat bars, and inserted and dropped beats

It also writes a **click track**: the song with a click mixed in, accented on
beat 1 (`ml/output/<song>/click.mp3`).

## Verification

### Eddie's ear makes the reference
For each benchmark song, Eddie listens to the click track and confirms that beat 1
is right. Start where bars were repaired (Billie Jean 18–30 s, In the End's outro),
then check one normal stretch. Once he confirms it, three of those beat-1 times go
into `benchmarks/manifest.json` as `downbeatRefs`. From then on, every run checks
that its grid hits those times within about 70 ms. His ear check becomes a
regression test.

### Automatic checks, for both songs
| Check | Catches |
| --- | --- |
| Fitted BPM inside the manifest range (Billie Jean 115–121, In the End 100–110) | half or double tempo |
| Every beat gap within ±15% of normal after repair | missed or extra beats left in |
| Grid hits every `downbeatRefs` time within 70 ms | beat 1 in the wrong place, including off by two beats |
| Drums stem: snare energy summed over beats 2+4 > summed over 1+3 | beat 1 off by one beat (can't see an off-by-two error) |
| Reported, not checked: raw non-4 bars, beats inserted and dropped | how much repairing happened |

The `downbeatRefs` check is the one that matters. The others catch obvious
breakage.

## Dependencies to add
`beat-this==1.1.0`, `soundfile==0.14.0`, plus everything beat_this pulls in, pinned
at their installed versions (`torchaudio`, `einops`, `rotary-embedding-torch`,
`soxr`) so nothing drifts.

## Out of scope for this step
- **Anything not in 4/4.** Eddie's call: get 4/4 right first.
  - 3/4 (waltzes): the run rule would find no confident run and report
    `confident: false`, which is safe but not useful. The later fix is to accept
    runs of any one bar length and count in that length.
  - 12/8 (blues and soul shuffles): Step 2 still finds 4 big beats per bar. The
    problem is in Step 3, which must snap hits to triplets, not 16ths.
  - Funk off-beat snares: still 4/4, so Step 2 is fine. Step 3 has to place hits
    that fall between beats. The snare check above may also mislead on funk.
- Swing feel.
- Snapping drum hits to the grid (Step 3).
- Connecting to the Next.js API route.
