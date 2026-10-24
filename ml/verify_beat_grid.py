"""Automatic checks for Step 2's beat grid on the benchmark songs.

Implements the "Automatic checks" table in
docs/plans/2026-10-24-step2-beat-grid-design.md. Needs each song's drums stem
from Step 1 (ml/separate_drums.py) for the snare check.

Usage:
    ml/.venv/bin/python ml/verify_beat_grid.py [--benchmark ID]

Exits 1 if any check fails.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import beat_grid  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / "benchmarks" / "manifest.json"
STEMS = Path(__file__).resolve().parent / "output" / "htdemucs"
REF_TOLERANCE = 0.07
GAP_TOLERANCE = 0.15
LOCAL_GAPS_EACH_SIDE = 4


def check_bpm(grid, expectations):
    lo, hi = expectations["bpmRange"]
    return lo <= grid["bpm"] <= hi, f"fitted {grid['bpm']} BPM, expected {lo}-{hi}"


def check_refs(grid, expectations):
    refs = expectations.get("downbeatRefs")
    if not refs:
        return None, "no downbeatRefs yet: waiting for Eddie's ear check"
    downbeats = np.asarray(grid["downbeats"])
    misses = [r for r in refs if np.abs(downbeats - r).min() > REF_TOLERANCE]
    if misses:
        return False, f"no beat 1 within 70 ms of {misses}"
    return True, f"all {len(refs)} refs land on a beat 1"


def check_gaps(grid):
    span = grid["stats"]["checkedSpan"]
    if span is None:
        return False, "no checked span (grid not confident)"
    beats = np.asarray(grid["beats"])
    gaps = np.diff(beats)
    bad = []
    for i, gap in enumerate(gaps):
        if not (span[0] <= beats[i] and beats[i + 1] <= span[1]):
            continue
        around = np.concatenate([
            gaps[max(0, i - LOCAL_GAPS_EACH_SIDE):i],
            gaps[i + 1:i + 1 + LOCAL_GAPS_EACH_SIDE],
        ])
        local = float(np.median(around))
        if abs(gap - local) > GAP_TOLERANCE * local:
            bad.append(f"{beats[i]:.2f}s ({gap / local:.2f}x)")
    if bad:
        return False, f"{len(bad)} uneven gaps: {', '.join(bad[:5])}"
    return True, "every gap in the checked span within 15% of local tempo"


def check_snare(grid, song_stem):
    stem = STEMS / song_stem / "drums.mp3"
    if not stem.exists():
        return False, f"missing drums stem {stem} (run ml/separate_drums.py first)"
    span = grid["stats"]["checkedSpan"]
    if span is None:
        return False, "no checked span (grid not confident)"
    audio, sr = beat_grid.load_mono(stem)
    window = int(0.06 * sr)
    freqs = np.fft.rfftfreq(window, 1 / sr)
    band = (freqs >= 200) & (freqs < 1000)
    hann = np.hanning(window)

    downbeats = set(grid["downbeats"])
    sums = {1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0}
    position = 0
    for b in grid["beats"]:
        if b in downbeats:
            position = 1
        elif position:  # stays 0 through a pickup, before the first beat 1
            position += 1
        if not (span[0] <= b <= span[1]) or not 1 <= position <= 4:
            continue
        start = int(b * sr)
        segment = audio[start:start + window]
        if len(segment) < window:
            continue
        sums[position] += float(np.abs(np.fft.rfft(segment * hann))[band].sum())
    backbeat, onbeat = sums[2] + sums[4], sums[1] + sums[3]
    ratio = backbeat / onbeat if onbeat else float("inf")
    return backbeat > onbeat, f"snare on 2+4 is {ratio:.1f}x beats 1+3"


def verify(benchmark) -> bool:
    song = REPO / benchmark["audioPath"]
    grid_path = beat_grid.analyze(song, click=True)
    grid = json.loads(grid_path.read_text())
    expectations = benchmark["expectations"]

    print(f"\n{benchmark['songName']}  ({grid_path.parent})")
    checks = [
        ("tempo", check_bpm(grid, expectations)),
        ("beat 1 vs Eddie's refs", check_refs(grid, expectations)),
        ("even beats", check_gaps(grid)),
        ("snare on 2 and 4", check_snare(grid, song.stem)),
    ]
    passed = True
    for name, (ok, detail) in checks:
        mark = {True: "PASS", False: "FAIL", None: "WAIT"}[ok]
        print(f"  {mark}  {name}: {detail}")
        passed = passed and ok is not False
    stats = grid["stats"]
    print(
        f"  info  confident={grid['confident']}, first beat 1 at {grid['downbeats'][0]:.2f}s, "
        f"raw non-4 bars {stats['rawNon4Bars']}, trimmed {stats['trimmed']}, "
        f"removed {stats['removed']}, inserted {stats['inserted']}, checked span {stats['checkedSpan']}"
    )
    for warning in grid["warnings"]:
        print(f"  warn  {warning}")
    return passed


def main() -> None:
    parser = argparse.ArgumentParser(description="Check Step 2's beat grid on the benchmarks.")
    parser.add_argument("--benchmark", help="Only this benchmark id")
    args = parser.parse_args()
    benchmarks = [
        b for b in json.loads(MANIFEST.read_text())["benchmarks"]
        if b.get("enabled") and (args.benchmark is None or b["id"] == args.benchmark)
    ]
    results = [verify(b) for b in benchmarks]
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
