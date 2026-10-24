"""Step 2 of the new engine: the beat grid.

Finds every beat in a song and which beat is beat 1 of each bar, using beat_this
on the full mix, then repairs the model's output. The rules are specified in
docs/plans/2026-10-24-step2-beat-grid-design.md; section names below match it.

Usage:
    ml/.venv/bin/python ml/beat_grid.py <song> [--out DIR] [--no-click]

Writes <out>/<song>/beat_grid.json and <out>/<song>/click.mp3 (the song with a
click on every beat, accented on beat 1) and prints the JSON path.

Assumes 4/4 throughout (Eddie's call: get 4/4 right first).
"""

import argparse
import json
from pathlib import Path

import numpy as np

DEFAULT_OUT = Path(__file__).resolve().parent / "output"
BEATS_PER_BAR = 4
MIN_CONFIDENT_BARS = 8
SNAP_TOLERANCE = 0.07  # model downbeat -> nearest repaired beat, seconds
SOUND_FLOOR_DB = -50.0  # "sound" = frame energy above peak - 50 dB
SHORT_GAP = 0.75  # gaps shorter than 0.75 T can belong to an extra beat
PAIR_TOLERANCE = 0.25  # two short gaps that sum to T +/- 25% -> one extra beat
INSERT_TOLERANCE = 0.25  # a gap within 0.25 of n*T (n >= 2) -> n - 1 missed beats


# --- Audio and model (everything that needs a real song) ---------------------

def load_mono(path: Path):
    import soundfile as sf

    audio, sr = sf.read(str(path), dtype="float64", always_2d=True)
    return audio.mean(axis=1), sr


def sound_bounds(audio: np.ndarray, sr: int, hop_seconds: float = 0.01):
    """First and last moment the full mix is above peak - 50 dB."""
    hop = max(1, int(sr * hop_seconds))
    usable = len(audio) // hop * hop
    rms = np.sqrt(np.mean(audio[:usable].reshape(-1, hop) ** 2, axis=1))
    threshold = rms.max() * 10 ** (SOUND_FLOOR_DB / 20)
    loud = np.flatnonzero(rms > threshold)
    if loud.size == 0:
        return 0.0, len(audio) / sr
    return loud[0] * hop_seconds, (loud[-1] + 1) * hop_seconds


def run_model(audio: np.ndarray, sr: int):
    from beat_this.inference import Audio2Beats

    beats, downbeats = Audio2Beats(checkpoint_path="final0", device="cpu", dbn=False)(audio, sr)
    return np.asarray(beats, dtype=float), np.asarray(downbeats, dtype=float)


def write_click_track(audio: np.ndarray, sr: int, grid: dict, path: Path) -> None:
    import soundfile as sf

    def tone(freq, gain):
        t = np.arange(int(0.03 * sr)) / sr
        return gain * np.sin(2 * np.pi * freq * t) * np.exp(-t * 120)

    beat_1 = set(round(d, 4) for d in grid["downbeats"])
    mix = audio / (np.abs(audio).max() or 1.0) * 0.6
    accent, normal = tone(1760, 0.9), tone(880, 0.45)
    for b in grid["beats"]:
        click = accent if round(b, 4) in beat_1 else normal
        start = int(b * sr)
        end = min(len(mix), start + len(click))
        if start < len(mix):
            mix[start:end] += click[: end - start]
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(str(path), np.clip(mix, -1, 1), sr, format="MP3")


# --- Repairs (pure: beat times in, grid out) -----------------------------------

def repair_beats(beats, first_sound: float, last_sound: float):
    """Repairs 1-3: trim the ends, remove extra beats, insert missed beats."""
    beats = list(beats)
    stats = {"trimmed": 0, "removed": 0, "inserted": 0}
    if len(beats) < 3:
        return beats, stats
    T = float(np.median(np.diff(beats)))

    # 1. Trim: beats more than T/2 outside the sound, then a lone short end gap.
    kept = [b for b in beats if first_sound - T / 2 <= b <= last_sound + T / 2]
    stats["trimmed"] += len(beats) - len(kept)
    beats = kept
    def is_extra_pair(g1, g2):
        """Step 2's test: two short gaps that add up to about one beat."""
        return g1 < SHORT_GAP * T and g2 < SHORT_GAP * T and abs(g1 + g2 - T) <= PAIR_TOLERANCE * T

    # Drop a lone short end gap's end beat, unless the two end gaps look like one
    # beat split in two: then the extra beat is the one just inside the end, and
    # step 2 removes that one instead.
    if len(beats) >= 3:
        g1, g2 = beats[1] - beats[0], beats[2] - beats[1]
        if g1 < SHORT_GAP * T and not is_extra_pair(g1, g2):
            beats.pop(0)
            stats["trimmed"] += 1
    if len(beats) >= 3:
        g1, g2 = beats[-1] - beats[-2], beats[-2] - beats[-3]
        if g1 < SHORT_GAP * T and not is_extra_pair(g1, g2):
            beats.pop()
            stats["trimmed"] += 1

    # 2. Remove extra beats, left to right, recomputing after each removal.
    i = 1
    while i < len(beats) - 1:
        if is_extra_pair(beats[i] - beats[i - 1], beats[i + 1] - beats[i]):
            beats.pop(i)
            stats["removed"] += 1
        else:
            i += 1

    # 3. Insert missed beats: n - 1 evenly spaced beats in a gap of about n*T.
    repaired = [beats[0]]
    for a, b in zip(beats[:-1], beats[1:]):
        ratio = (b - a) / T
        n = round(ratio)
        if n >= 2 and abs(ratio - n) <= INSERT_TOLERANCE:
            repaired.extend(a + (b - a) * k / n for k in range(1, n))
            stats["inserted"] += n - 1
        repaired.append(b)
    return repaired, stats


def snap_downbeats(beats, downbeats):
    """Index of the repaired beat each model downbeat lands on (within 70 ms)."""
    beats = np.asarray(beats)
    indices = []
    for d in downbeats:
        i = int(np.argmin(np.abs(beats - d)))
        if abs(beats[i] - d) <= SNAP_TOLERANCE and (not indices or i > indices[-1]):
            indices.append(i)
    return indices


def confident_runs(db_indices):
    """Repair 4: runs of at least 8 bars in a row of exactly 4 beats.

    Returns (first_downbeat_index, bar_count) per run, indices into the beats.
    """
    runs, start = [], 0
    for k in range(1, len(db_indices) + 1):
        bar_ok = k < len(db_indices) and db_indices[k] - db_indices[k - 1] == BEATS_PER_BAR
        if not bar_ok:
            bars = k - 1 - start
            if bars >= MIN_CONFIDENT_BARS:
                runs.append((db_indices[start], bars))
            start = k
    return runs


def raw_non4_bars(beats, downbeats):
    beats = np.asarray(beats)
    return sum(
        1 for a, b in zip(downbeats[:-1], downbeats[1:])
        if int(((beats >= a) & (beats < b)).sum()) != BEATS_PER_BAR
    )


def fitted_bpm(beats) -> float:
    slope = np.polyfit(np.arange(len(beats)), beats, 1)[0]
    return float(60.0 / slope)


def make_bars(beats, starts, bpm, model_starts=None, pickup_end=None):
    """Bar entries from beat indices where bars start.

    A bar's source is "model" only if the model put beat 1 exactly where the bar
    starts and nowhere else inside it; otherwise the repair changed it.
    """
    def source(first, end, starts_on_model):
        if model_starts is None:
            return "model"
        split = any(first < m < end for m in model_starts)
        return "model" if starts_on_model and not split else "repaired"

    bars = []
    one_beat = 60.0 / bpm
    if pickup_end:
        bars.append({
            "start": beats[0], "beats": pickup_end,
            "source": source(-1, pickup_end, True), "pickup": True,
        })
    for k, i in enumerate(starts):
        nxt = starts[k + 1] if k + 1 < len(starts) else len(beats)
        on_model = model_starts is None or i in model_starts
        bars.append({"start": beats[i], "beats": nxt - i, "source": source(i, nxt, on_model), "pickup": False})
    for k, bar in enumerate(bars):
        if k + 1 < len(bars):
            bar["end"] = bars[k + 1]["start"]
        else:
            bar["end"] = beats[-1] + one_beat
    return [{key: (round(v, 4) if isinstance(v, float) else v) for key, v in bar.items()} for bar in bars]


def build_grid(raw_beats, raw_downbeats, first_sound: float, last_sound: float) -> dict:
    """Everything after the model: repairs, beat-1 position, tempo, bars."""
    raw_beats, raw_downbeats = list(raw_beats), list(raw_downbeats)
    beats, stats = repair_beats(raw_beats, first_sound, last_sound)
    stats["rawNon4Bars"] = raw_non4_bars(raw_beats, raw_downbeats)
    if len(beats) < 2:
        stats["checkedSpan"] = None
        return {
            "bpm": 0.0, "firstSound": round(first_sound, 3), "lastSound": round(last_sound, 3),
            "confident": False, "beats": [round(b, 4) for b in beats], "downbeats": [],
            "bars": [], "warnings": ["fewer than 2 beats after repair: no grid"], "stats": stats,
        }
    bpm = fitted_bpm(beats)
    db_indices = snap_downbeats(beats, raw_downbeats)
    runs = confident_runs(db_indices)
    warnings = []

    # 5. One beat-1 position for the whole song: majority of confident-run bars.
    votes = {}
    for first, bars in runs:
        votes[first % BEATS_PER_BAR] = votes.get(first % BEATS_PER_BAR, 0) + bars
    ranked = sorted(votes.items(), key=lambda kv: kv[1], reverse=True)
    confident = bool(ranked) and (len(ranked) == 1 or ranked[0][1] > ranked[1][1])
    if len(ranked) > 1:
        detail = ", ".join(
            f"{bars} bars from {beats[first]:.2f}s at position {first % BEATS_PER_BAR}"
            for first, bars in runs
        )
        warnings.append(f"confident runs disagree on beat 1: {detail}")

    if runs:
        last_first, last_bars = runs[-1]
        span_end_index = min(last_first + last_bars * BEATS_PER_BAR, len(beats) - 1)
        stats["checkedSpan"] = [round(beats[runs[0][0]], 4), round(beats[span_end_index], 4)]
    else:
        stats["checkedSpan"] = None

    if confident:
        phase = ranked[0][0]
        starts = list(range(phase, len(beats), BEATS_PER_BAR))
        bars = make_bars(beats, starts, bpm, model_starts=set(db_indices), pickup_end=phase)
    else:
        if not ranked:
            warnings.append("no confident run: beat 1 positions are the model's, unrepaired")
        else:
            warnings.append("confident runs tie: beat 1 positions are the model's, unrepaired")
        # The model's own beat 1s, but only those that land on a kept beat, so
        # downbeats and bars line up with beats (a trimmed phantom can't appear).
        starts = db_indices
        if starts:
            bars = make_bars(beats, starts, bpm, pickup_end=starts[0])
        else:
            bars = []
            warnings.append("the model gave no beat 1 on a kept beat: no bars")
    downbeats = [beats[i] for i in starts]

    return {
        "bpm": round(bpm, 2),
        "firstSound": round(first_sound, 3),
        "lastSound": round(last_sound, 3),
        "confident": confident,
        "beats": [round(b, 4) for b in beats],
        "downbeats": [round(d, 4) for d in downbeats],
        "bars": bars,
        "warnings": warnings,
        "stats": stats,
    }


# --- Entry point ----------------------------------------------------------------

def analyze(song: Path, out_dir: Path = DEFAULT_OUT, click: bool = True) -> Path:
    audio, sr = load_mono(song)
    first, last = sound_bounds(audio, sr)
    raw_beats, raw_downbeats = run_model(audio, sr)
    grid = build_grid(raw_beats, raw_downbeats, first, last)

    folder = out_dir / song.stem
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "raw_beat_this.json").write_text(json.dumps(
        {"beats": raw_beats.tolist(), "downbeats": raw_downbeats.tolist(),
         "firstSound": first, "lastSound": last}
    ))
    json_path = folder / "beat_grid.json"
    json_path.write_text(json.dumps(grid, indent=2))
    if click:
        write_click_track(audio, sr, grid, folder / "click.mp3")
    return json_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Find the beats and beat 1 of a song.")
    parser.add_argument("song", type=Path, help="Path to the full song (mp3/wav/...)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output directory")
    parser.add_argument("--no-click", action="store_true", help="Skip writing the click track")
    args = parser.parse_args()
    print(analyze(args.song, args.out, click=not args.no_click))


if __name__ == "__main__":
    main()
