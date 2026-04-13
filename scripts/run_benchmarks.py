#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

STATUS_ORDER = {"pass": 0, "warn": 1, "fail": 2}
DIFFICULTY_ORDER = ["beginner", "intermediate", "pro"]


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_manifest(root: Path) -> dict[str, Any]:
    manifest_path = root / "benchmarks" / "manifest.json"
    return json.loads(manifest_path.read_text())


def ensure_result_dir(root: Path, benchmark_id: str) -> Path:
    result_dir = root / "benchmarks" / "results" / benchmark_id / "latest"
    result_dir.mkdir(parents=True, exist_ok=True)
    return result_dir


def run_engine(root: Path, audio_path: Path, difficulty: str) -> dict[str, Any]:
    command = [
        "python3",
        str(root / "engine" / "process_song.py"),
        str(audio_path),
        difficulty,
    ]
    result = subprocess.run(command, capture_output=True, text=True, cwd=root)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or f"Engine failed for {difficulty}")

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Engine returned invalid JSON for {difficulty}: {exc}") from exc


def count_visible_events(engine_result: dict[str, Any]) -> dict[str, int]:
    counts = {"bd": 0, "sn": 0, "hh": 0, "oh": 0, "cr": 0}
    for hit in engine_result.get("debug", {}).get("acceptedHits", []):
        kind = hit.get("kind")
        if kind in counts:
            counts[kind] += 1
    return counts


def accepted_steps_by_kind(engine_result: dict[str, Any]) -> dict[str, set[int]]:
    steps: dict[str, set[int]] = {}
    for hit in engine_result.get("debug", {}).get("acceptedHits", []):
        kind = hit.get("kind")
        step = hit.get("step")
        if not isinstance(kind, str) or not isinstance(step, int):
            continue
        steps.setdefault(kind, set()).add(step)
    return steps


def make_check(check_id: str, status: str, message: str) -> dict[str, str]:
    return {"id": check_id, "status": status, "message": message}


def worst_status(statuses: list[str]) -> str:
    if not statuses:
        return "pass"
    return max(statuses, key=lambda status: STATUS_ORDER[status])


def evaluate_per_difficulty(engine_result: dict[str, Any], benchmark: dict[str, Any], difficulty: str) -> dict[str, Any]:
    expectations = benchmark.get("expectations", {})
    checks: list[dict[str, str]] = [make_check("engine-run", "pass", "Engine completed.")]
    debug = engine_result.get("debug", {})
    bpm = debug.get("bpm")
    pulse = debug.get("hiHatPulse")
    counts = count_visible_events(engine_result)
    counts_with_open = dict(counts)
    counts_with_open["hh"] = counts.get("hh", 0) + counts.get("oh", 0)
    steps = accepted_steps_by_kind(engine_result)

    bpm_range = expectations.get("bpmRange")
    if isinstance(bpm_range, list) and len(bpm_range) == 2 and isinstance(bpm, (int, float)):
        low, high = bpm_range
        if low <= bpm <= high:
            checks.append(make_check("bpm-range", "pass", f"{bpm} BPM within expected range {low}-{high}."))
        else:
            checks.append(make_check("bpm-range", "fail", f"{bpm} BPM outside expected range {low}-{high}."))
    else:
        checks.append(make_check("bpm-range", "warn", "No usable BPM expectation found."))

    allowed_pulse = expectations.get("allowedHatPulseByDifficulty", {}).get(difficulty)
    if isinstance(allowed_pulse, list) and pulse:
        if pulse in allowed_pulse:
            checks.append(make_check("hat-pulse", "pass", f"{pulse} pulse allowed for {difficulty}."))
        else:
            checks.append(make_check("hat-pulse", "fail", f"{pulse} pulse not allowed for {difficulty}; expected one of {allowed_pulse}."))
    else:
        checks.append(make_check("hat-pulse", "warn", "No usable hat-pulse expectation found."))

    required_steps = expectations.get("requiredStepsByDifficulty", {}).get(difficulty, {})
    for kind, required in required_steps.items():
        actual_steps = steps.get(kind, set())
        if all(step in actual_steps for step in required):
            checks.append(make_check(f"required-steps-{kind}", "pass", f"Required {kind} steps present: {required}."))
        else:
            missing = [step for step in required if step not in actual_steps]
            checks.append(make_check(f"required-steps-{kind}", "fail", f"Missing required {kind} steps: {missing}."))

    min_counts = expectations.get("minVisibleCountsByDifficulty", {}).get(difficulty, {})
    for kind, minimum in min_counts.items():
        actual = counts_with_open.get(kind, counts.get(kind, 0))
        if actual >= minimum:
            checks.append(make_check(f"min-visible-{kind}", "pass", f"Visible {kind} count {actual} meets minimum {minimum}."))
        else:
            checks.append(make_check(f"min-visible-{kind}", "fail", f"Visible {kind} count {actual} below minimum {minimum}."))

    max_counts = expectations.get("maxVisibleCountsByDifficulty", {}).get(difficulty, {})
    for kind, maximum in max_counts.items():
        actual = counts_with_open.get(kind, counts.get(kind, 0))
        if actual <= maximum:
            checks.append(make_check(f"max-visible-{kind}", "pass", f"Visible {kind} count {actual} within maximum {maximum}."))
        else:
            checks.append(make_check(f"max-visible-{kind}", "fail", f"Visible {kind} count {actual} exceeds maximum {maximum}."))

    status = worst_status([check["status"] for check in checks])
    return {
        "status": status,
        "checks": checks,
        "visibleCounts": counts_with_open,
        "bpm": bpm,
        "hiHatPulse": pulse,
    }


def total_density(result_summary: dict[str, Any]) -> int:
    counts = result_summary.get("visibleCounts", {})
    return int(sum(counts.get(kind, 0) for kind in ["hh", "sn", "bd", "cr"]))


def evaluate_cross_difficulty(results_by_difficulty: dict[str, dict[str, Any]], benchmark: dict[str, Any]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    available_difficulties = set(results_by_difficulty)
    guardrails = benchmark.get("expectations", {}).get("densityGuardrails", {})
    beginner_targets = guardrails.get("beginnerNotDenserThan", [])
    beginner = results_by_difficulty.get("beginner")
    if beginner and isinstance(beginner_targets, list):
        comparable_targets = [target for target in beginner_targets if target in available_difficulties]
        if comparable_targets:
            beginner_density = total_density(beginner)
            for target in comparable_targets:
                target_summary = results_by_difficulty[target]
                target_density = total_density(target_summary)
                if beginner_density <= target_density:
                    checks.append(make_check("density-guardrail", "pass", f"Beginner density {beginner_density} did not exceed {target} density {target_density}."))
                else:
                    checks.append(make_check("density-guardrail", "fail", f"Beginner density {beginner_density} exceeded {target} density {target_density}."))

    if {"beginner", "intermediate"}.issubset(available_difficulties):
        beginner_counts = results_by_difficulty["beginner"].get("visibleCounts", {})
        intermediate_counts = results_by_difficulty["intermediate"].get("visibleCounts", {})
        if beginner_counts != intermediate_counts:
            checks.append(make_check("difficulty-separation", "pass", "Beginner and intermediate outputs differ."))
        else:
            checks.append(make_check("difficulty-separation", "warn", "Beginner and intermediate outputs are identical."))

    return checks


def benchmark_status(per_difficulty: dict[str, Any], cross_checks: list[dict[str, str]]) -> str:
    statuses = [entry.get("status", "pass") for entry in per_difficulty.values()]
    statuses.extend(check["status"] for check in cross_checks)
    return worst_status(statuses)


def summarize_to_stdout(summary: dict[str, Any]) -> None:
    print(f"Benchmark: {summary['benchmarkId']} -> {summary['overallStatus']}")
    for difficulty in DIFFICULTY_ORDER:
        if difficulty not in summary["resultsByDifficulty"]:
            continue
        result = summary["resultsByDifficulty"][difficulty]
        print(f"  {difficulty}: {result['status']} | bpm={result.get('bpm')} | pulse={result.get('hiHatPulse')}")
        for check in result["checks"]:
            print(f"    - {check['id']}: {check['status']} — {check['message']}")
    for check in summary["crossDifficultyChecks"]:
        print(f"  cross: {check['id']}: {check['status']} — {check['message']}")


def run_benchmark(root: Path, benchmark: dict[str, Any], difficulty_filter: str | None = None) -> tuple[dict[str, Any], bool]:
    benchmark_id = benchmark["id"]
    audio_path = root / benchmark["audioPath"]
    result_dir = ensure_result_dir(root, benchmark_id)
    requested_difficulties = benchmark.get("difficulties", DIFFICULTY_ORDER)
    if difficulty_filter:
        requested_difficulties = [difficulty for difficulty in requested_difficulties if difficulty == difficulty_filter]

    results_by_difficulty: dict[str, dict[str, Any]] = {}
    hard_failure = False

    if not audio_path.exists():
        summary = {
            "benchmarkId": benchmark_id,
            "songName": benchmark.get("songName"),
            "overallStatus": "fail",
            "generatedAt": datetime.now().astimezone().isoformat(),
            "resultsByDifficulty": {},
            "crossDifficultyChecks": [
                make_check("audio-file", "fail", f"Missing benchmark audio file: {benchmark['audioPath']}")
            ],
            "humanReviewReminder": [
                "Add the benchmark audio file before trusting benchmark output.",
                "Machine checks do not replace rendered notation review.",
            ],
        }
        (result_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
        return summary, True

    for difficulty in requested_difficulties:
        try:
            engine_result = run_engine(root, audio_path, difficulty)
            (result_dir / f"{difficulty}.json").write_text(json.dumps(engine_result, indent=2) + "\n")
            results_by_difficulty[difficulty] = evaluate_per_difficulty(engine_result, benchmark, difficulty)
        except Exception as exc:  # noqa: BLE001
            hard_failure = True
            results_by_difficulty[difficulty] = {
                "status": "fail",
                "checks": [make_check("engine-run", "fail", str(exc))],
                "visibleCounts": {},
                "bpm": None,
                "hiHatPulse": None,
            }

    cross_checks = evaluate_cross_difficulty(results_by_difficulty, benchmark)
    summary = {
        "benchmarkId": benchmark_id,
        "songName": benchmark.get("songName"),
        "overallStatus": benchmark_status(results_by_difficulty, cross_checks),
        "generatedAt": datetime.now().astimezone().isoformat(),
        "resultsByDifficulty": results_by_difficulty,
        "crossDifficultyChecks": cross_checks,
        "humanReviewReminder": [
            "Check notation readability manually.",
            "Check that hats are readable and not spammy.",
            "Check visual placement honesty in the rendered score.",
        ],
    }
    (result_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary, hard_failure


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Drumsheet-Ai benchmark harness")
    parser.add_argument("--benchmark", help="Run only one benchmark id")
    parser.add_argument("--difficulty", choices=DIFFICULTY_ORDER, help="Run only one difficulty")
    args = parser.parse_args()

    root = repo_root()
    manifest = load_manifest(root)
    benchmarks = [entry for entry in manifest.get("benchmarks", []) if entry.get("enabled", False)]
    if args.benchmark:
        benchmarks = [entry for entry in benchmarks if entry.get("id") == args.benchmark]

    if not benchmarks:
        print("No matching enabled benchmarks found.", file=sys.stderr)
        return 1

    hard_failure = False
    summaries = []
    for benchmark in benchmarks:
        summary, benchmark_failed_hard = run_benchmark(root, benchmark, args.difficulty)
        summaries.append(summary)
        summarize_to_stdout(summary)
        hard_failure = hard_failure or benchmark_failed_hard or summary["overallStatus"] == "fail"

    return 1 if hard_failure else 0


if __name__ == "__main__":
    raise SystemExit(main())
