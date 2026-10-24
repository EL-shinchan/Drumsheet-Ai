# Step 2 — Beat Grid Design

Date: 2026-10-24
Status: Draft, second revision after review. Awaiting Eddie's approval.

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
  at about 1.22 s).

The 18.8–29 s stretch is the dangerous one. A few more wrong bars would have
looked like a confident run.

How we know the right answer is beat 1 at 1.24 s: in the bass stem, the bass notes
on beats 1–4 come out as F#, E, E, B, which is the riff's actual order. (Kick
energy can't settle it, because "kicks on 1 and 3" also fits a grid that's off by
two beats.)

## Repairs, in order

`T` is the normal beat gap. For the repairs, `T` is the median gap of the raw
beats. That's precise enough for spotting missing and extra beats, but not for the
reported tempo (see Tempo).

### 1. Trim the ends
"Sound" means full-mix energy above **peak − 50 dB**. The threshold is relative to
the song's peak so that real beats in a quiet intro or fade aren't dropped. It
uses the full mix because a song can open on vocals or guitar, and those beats are
real.
- Drop beats more than `T/2` before the first sound or after the last sound.
- Then, if the first or last gap is shorter than `0.75T`, drop that end beat. It's
  an extra beat with only one neighbour, so step 2 can't catch it.

At peak − 50 dB, Billie Jean's first sound is at 1.22 s, so the 0.72 s phantom is
dropped. In the End's first sound is at 0.03 s, so its 0.32 s beat stays.

### 2. Remove extra beats
Go left to right. Where two neighbouring gaps are each shorter than `0.75T` and add
up to `T ± 25%`, remove the beat between them. Recompute the gaps after each
removal and carry on. This also handles extra beats that aren't centred (gaps of
0.3× and 0.7×) and a short run where the model doubled the tempo.

### 3. Insert missed beats
For each gap, let `n = round(gap / T)`. If `n ≥ 2` and `gap / T` is within `0.25`
of `n`, insert `n − 1` evenly spaced beats. This covers one or several missed
beats in a row.

Gaps that are irregular but nowhere near a whole number of beats (e.g. 1.44×) are
left alone. That's real tempo change, such as In the End's free piano outro.

### 4. Find the confident runs (on the repaired beats)
Map each model downbeat to the nearest repaired beat (within 70 ms; downbeats
with no beat that close are ignored). A bar's length is the number of beats
between consecutive downbeats. A **confident run** is at least 8 bars in a row of
exactly 4 beats.

Runs are counted after repair, so a single missed beat doesn't split a run into
two short ones.

### 5. Pick one beat-1 position for the whole song
We assume 4/4 throughout, so beat 1 should be the same position in every bar
(repaired beat index mod 4) from start to finish.
- Count only bars inside confident runs. The position with the most bars wins and
  is used for the whole song.
- If the runs don't all agree, add a `warnings` entry naming where they disagree.
- If two positions tie, or there's no confident run, set `confident: false`.

Every bar then has exactly 4 beats, except possibly a short pickup at the start
and a short final bar.

## Tempo
After repair, report the **fitted** tempo: a straight-line fit of beat number
against beat time over the repaired beats. Don't use the median gap. beat_this
places beats on a 20 ms grid, so the median can only take a few values. Billie
Jean's median gives 115.4 against a fitted 116.8; In the End gives 103.4 against
105.1.

## Output
`ml/beat_grid.py <song>` writes JSON:
- `bpm`: fitted tempo after repair
- `firstSound`, `lastSound`: seconds
- `beats`: beat times after repair
- `downbeats`: beat-1 times
- `bars`: one entry per bar with `start`, `beats` and `source`. `source` is
  `model` when the model's downbeat agreed with the chosen position and
  `repaired` when the position rule overrode it.
- `confident`: false on a tie or with no confident run. In that case `beats` are
  still repaired, but `downbeats` and `bars` come straight from the model,
  unrepaired, with every `source` set to `model`. Step 3 must not trust them.
- `warnings`: e.g. confident runs that disagreed
- `stats`: the raw model's non-4-beat bars, beats trimmed, removed and inserted,
  and the span from the start of the first confident run to the end of the last
  (the "checked span")

It also writes a **click track**: the song with a click on every beat, accented on
beat 1 (`ml/output/<song>/click.mp3`).

## Verification

### Eddie's ear makes the reference
For each benchmark song, Eddie listens to the click track at three spots:
- **Billie Jean:** 18–30 s (where the model was wrong), the vocal entry around
  30 s, and one stretch later on.
- **In the End:** the drum entry around 18.6 s (the drums come in with a pickup),
  one stretch in the middle, and the last confident bars before the outro.

At each spot he either confirms that the loud click is beat 1, or says which click
(2, 3 or 4, counting from the loud one) is the real beat 1. That beat's time is
saved as a reference. Three references per song go into `benchmarks/manifest.json`
as `downbeatRefs`. From then on, every run is checked against his ear
automatically.

### Automatic checks, for both songs
| Check | Catches |
| --- | --- |
| Fitted BPM inside the manifest range (Billie Jean 115–121, In the End 100–110) | half or double tempo |
| Each `downbeatRefs` time has a **`downbeats`** entry within 70 ms (not just any beat) | beat 1 in the wrong place, including off by one or two beats |
| Within the checked span, every beat gap is within ±15% of the median of the 4 gaps on each side, not counting this gap (fewer near the start or end of the song) (local tempo, not a song-wide `T`, so a real slowdown like In the End's outro passes) | missed or extra beats left in |
| Drums stem, 200–1000 Hz, 60 ms after each beat, summed over the checked span: beats 2+4 > beats 1+3 | beat 1 off by one beat |
| Reported, not checked: gaps outside the checked span, raw non-4 bars, beats trimmed, removed and inserted | how much repairing happened |

The `downbeatRefs` check is the one that matters. It's the only one that catches a
grid that's off by two beats.

### Unit tests (repair rules)
Using Billie Jean's raw beat_this output, saved as a test fixture:
- **Missed beat:** delete the beat nearest 100 s. Expected: a beat is inserted
  within 20 ms of where it was, and `downbeats` are unchanged within 20 ms (the
  deleted beat at 99.98 s is itself a downbeat, and its replacement lands 10 ms
  away).
- **Extra beat:** add a beat halfway between two beats near 150 s. Expected: it's
  removed, and `downbeats` are unchanged.
- **Disagreeing run:** shift the model downbeats by one beat for 10 bars near
  200 s. Expected: the majority position wins, a warning is raised, and
  `downbeats` are unchanged.
- **Phantom beat:** the real 0.72 s beat. Expected: trimmed.

## Dependencies to add
Pinned at the versions installed and tested: `beat-this==1.1.0`,
`soundfile==0.14.0`, `torchaudio==2.11.0`, `einops==0.8.2`,
`rotary-embedding-torch==0.9.1`, `soxr==1.1.0`, `cffi==2.1.1`.

## Out of scope for this step
- **Anything not in 4/4.** Eddie's call: get 4/4 right first.
  - 3/4 (waltzes): the run rule would find no confident run and report
    `confident: false`, which is safe but not useful. The later fix is to accept
    runs of any one bar length and count in that length.
  - 12/8 (blues and soul shuffles): Step 2 still finds 4 big beats per bar. The
    problem is in Step 3, which must snap hits to triplets, not 16ths.
  - Funk off-beat snares: still 4/4, so Step 2 is fine. Step 3 has to place hits
    that fall between beats. The snare check above may also mislead on funk.
- Swing feel, and songs that change tempo freely (they'd show up as gaps outside
  the checked span, reported but not fixed).
- Snapping drum hits to the grid (Step 3).
- Connecting to the Next.js API route.

## Later use of this output: play-along cursor (Eddie's idea)
In Step 4, the drum sheet plays alongside the song with a box highlighting the bar
that's sounding, so you can see whether the written notes match the drums you
hear. Each `bars[].start` from this step is the moment the box moves to that bar,
so the cursor needs nothing beyond this output. It gets built in Step 4 and shown
as a standalone mockup before it's wired into the app.
