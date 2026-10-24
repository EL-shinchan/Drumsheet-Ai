"""Unit tests for Step 2's repair rules (no audio or model needed).

The fixture is beat_this's raw output for Billie Jean (beat times only, no
audio). Each test damages it the way the model might, then checks the repairs
put it back. Scenarios come from the "Unit tests" section of
docs/plans/2026-10-24-step2-beat-grid-design.md.

Run:
    ml/.venv/bin/python -m unittest discover ml/tests
"""

import json
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import beat_grid  # noqa: E402

FIXTURE = json.loads((HERE / "fixtures" / "billie_jean_beat_this.json").read_text())


def grid_from(beats, downbeats):
    return beat_grid.build_grid(beats, downbeats, FIXTURE["firstSound"], FIXTURE["lastSound"])


def nearest_index(values, t):
    return int(np.argmin(np.abs(np.asarray(values) - t)))


class BeatGridTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.beats = list(FIXTURE["beats"])
        cls.downbeats = list(FIXTURE["downbeats"])
        cls.baseline = grid_from(cls.beats, cls.downbeats)

    def assertDownbeatsMatch(self, grid, tolerance):
        expected = np.asarray(self.baseline["downbeats"])
        actual = np.asarray(grid["downbeats"])
        self.assertEqual(len(actual), len(expected))
        self.assertLessEqual(float(np.abs(actual - expected).max()), tolerance)

    def test_baseline_billie_jean(self):
        grid = self.baseline
        self.assertTrue(grid["confident"])
        self.assertAlmostEqual(grid["downbeats"][0], 1.24, delta=0.02)
        self.assertTrue(115 <= grid["bpm"] <= 121)
        self.assertEqual(grid["warnings"], [])
        self.assertTrue(all(bar["beats"] == 4 for bar in grid["bars"][:-1]))
        self.assertFalse(grid["bars"][0]["pickup"])

    def test_phantom_beat_trimmed(self):
        self.assertAlmostEqual(self.beats[0], 0.72, delta=0.02)
        grid = self.baseline
        self.assertGreater(grid["beats"][0], 1.0)
        self.assertEqual(grid["stats"]["trimmed"], 1)

    def test_missed_beat_is_inserted(self):
        i = nearest_index(self.beats, 100.0)
        missing = self.beats[i]
        grid = grid_from(self.beats[:i] + self.beats[i + 1:], self.downbeats)
        self.assertEqual(grid["stats"]["inserted"], 1)
        self.assertLessEqual(abs(grid["beats"][nearest_index(grid["beats"], missing)] - missing), 0.02)
        self.assertDownbeatsMatch(grid, 0.02)

    def test_extra_beat_is_removed(self):
        i = nearest_index(self.beats, 150.0)
        extra = (self.beats[i] + self.beats[i + 1]) / 2
        grid = grid_from(self.beats[: i + 1] + [extra] + self.beats[i + 1:], self.downbeats)
        self.assertEqual(grid["stats"]["removed"], 1)
        self.assertNotIn(round(extra, 4), grid["beats"])
        self.assertDownbeatsMatch(grid, 0.0)

    def test_disagreeing_run_is_outvoted(self):
        # Shift the model's beat 1 by one beat for 10 bars near 200 s.
        beats = np.asarray(self.beats)
        k = nearest_index(self.downbeats, 200.0)
        shifted = list(self.downbeats)
        for j in range(k, k + 10):
            shifted[j] = float(beats[nearest_index(beats, shifted[j]) + 1])
        grid = grid_from(self.beats, shifted)
        self.assertTrue(grid["confident"])
        self.assertEqual(len(grid["warnings"]), 1)
        self.assertIn("disagree", grid["warnings"][0])
        self.assertDownbeatsMatch(grid, 0.0)

    def test_no_confident_run(self):
        # Beat 1 on every other beat everywhere: no run of 4-beat bars at all.
        grid = grid_from(self.beats, self.beats[::2])
        self.assertFalse(grid["confident"])
        self.assertIsNone(grid["stats"]["checkedSpan"])
        self.assertTrue(all(bar["source"] == "model" for bar in grid["bars"]))
        # Downbeats and bars still line up with the kept beats (no 0.72 s phantom).
        self.assertTrue(set(grid["downbeats"]) <= set(grid["beats"]))
        self.assertEqual(len(grid["bars"]), len(grid["downbeats"]) + int(grid["bars"][0]["pickup"]))

    def test_tie_is_not_confident(self):
        # Synthetic: 100 even beats, two 10-bar runs at different positions.
        beats = [i * 0.5 for i in range(100)]
        downbeats = [beats[i] for i in range(0, 41, 4)] + [beats[i] for i in range(41, 82, 4)]
        grid = beat_grid.build_grid(beats, downbeats, 0.0, 50.0)
        self.assertFalse(grid["confident"])
        self.assertTrue(any("tie" in w for w in grid["warnings"]))
        self.assertIsNotNone(grid["stats"]["checkedSpan"])

    def test_split_and_wrong_bars_are_marked_repaired(self):
        bars = {bar["start"]: bar["source"] for bar in self.baseline["bars"]}
        # 1.2-18 s: the model put beat 1 on every other beat, so it split these bars.
        self.assertEqual(bars[1.24], "repaired")
        # 18.8-29 s: the model had beat 1 on the wrong beat.
        self.assertTrue(all(bars[s] == "repaired" for s in bars if 19.5 < s < 29.0))
        # From the vocal entry on, the model was right.
        self.assertEqual(bars[min(bars, key=lambda s: abs(s - 100.0))], "model")

    def test_lone_extra_beat_at_start_is_trimmed(self):
        T = float(np.median(np.diff(self.beats)))
        first = self.baseline["beats"][0]
        grid = grid_from(sorted(self.beats + [first - 0.3 * T]), self.downbeats)
        self.assertEqual(grid["beats"][0], self.baseline["beats"][0])
        self.assertDownbeatsMatch(grid, 0.0)

    def test_extra_beat_just_inside_start_keeps_real_first_beat(self):
        T = float(np.median(np.diff(self.beats)))
        first = self.baseline["beats"][0]
        grid = grid_from(sorted(self.beats + [first + 0.3 * T]), self.downbeats)
        self.assertEqual(grid["beats"][0], first)
        self.assertEqual(grid["stats"]["removed"], 1)
        self.assertDownbeatsMatch(grid, 0.0)

    def test_lone_extra_beat_at_end_is_trimmed(self):
        T = float(np.median(np.diff(self.beats)))
        last = self.baseline["beats"][-1]
        for offset in (0.3, 0.6):
            grid = grid_from(sorted(self.beats + [last + offset * T]), self.downbeats)
            self.assertEqual(grid["beats"][-1], last, f"extra beat at +{offset}T")

    def test_extra_beat_just_inside_end_keeps_real_last_beat(self):
        T = float(np.median(np.diff(self.beats)))
        last = self.baseline["beats"][-1]
        grid = grid_from(sorted(self.beats + [last - 0.3 * T]), self.downbeats)
        self.assertEqual(grid["beats"][-1], last)
        self.assertEqual(grid["stats"]["removed"], 1)
        self.assertEqual(len(grid["beats"]), len(self.baseline["beats"]))

    def test_extra_beat_after_a_short_real_gap_is_trimmed(self):
        # Like In the End's free outro: the real last gap is short (0.72T), then
        # an extra beat 0.6T later. The two gaps don't add up to one beat, so the
        # extra beat is the lone one at the end and must go.
        T = float(np.median(np.diff(self.beats)))
        body = self.baseline["beats"][:-1]
        real_last = body[-1] + 0.72 * T
        beats = body + [real_last, real_last + 0.6 * T]
        grid = beat_grid.build_grid(beats, self.downbeats, FIXTURE["firstSound"], 1e9)
        self.assertAlmostEqual(grid["beats"][-1], real_last, places=3)

    def test_no_beat_1_gives_no_bars(self):
        grid = grid_from(self.beats, [])
        self.assertFalse(grid["confident"])
        self.assertEqual(grid["bars"], [])
        self.assertEqual(grid["downbeats"], [])
        self.assertTrue(any("no beat 1" in w for w in grid["warnings"]))

    def test_two_missed_beats_in_a_row(self):
        i = nearest_index(self.beats, 120.0)
        grid = grid_from(self.beats[:i] + self.beats[i + 2:], self.downbeats)
        self.assertEqual(grid["stats"]["inserted"], 2)
        self.assertDownbeatsMatch(grid, 0.02)

    def test_off_centre_extra_beat(self):
        i = nearest_index(self.beats, 160.0)
        extra = self.beats[i] + 0.3 * (self.beats[i + 1] - self.beats[i])
        grid = grid_from(self.beats[: i + 1] + [extra] + self.beats[i + 1:], self.downbeats)
        self.assertEqual(grid["stats"]["removed"], 1)
        self.assertDownbeatsMatch(grid, 0.0)

    def test_too_few_beats(self):
        grid = beat_grid.build_grid([1.0], [1.0], 0.0, 2.0)
        self.assertFalse(grid["confident"])
        self.assertEqual(grid["bars"], [])

    def test_pickup_bar(self):
        # Drop the first beat 1 so the song opens with a 3-beat pickup.
        grid = grid_from(self.beats, self.downbeats)
        start = grid["downbeats"][0]
        later = [b for b in self.beats if b > start + 0.05]
        grid = grid_from(later, [d for d in self.downbeats if d > start + 0.05])
        first = grid["bars"][0]
        self.assertTrue(first["pickup"])
        self.assertEqual(first["beats"], 3)
        self.assertEqual(grid["bars"][1]["start"], grid["downbeats"][0])
        self.assertEqual(len(grid["bars"]), len(grid["downbeats"]) + 1)


if __name__ == "__main__":
    unittest.main()
