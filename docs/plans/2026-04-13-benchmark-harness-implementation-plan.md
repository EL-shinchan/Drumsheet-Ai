# Benchmark Harness Implementation Plan

Date: 2026-04-13
Project: Drumsheet-Ai
Status: implementation plan
Depends on: `docs/plans/2026-04-13-benchmark-harness-design.md`

## Objective
Implement pass 1 of the benchmark harness so one command can run a real benchmark song through the transcription engine, save deterministic outputs, and report machine-checkable pass/warn/fail results.

## Pass 1 target
Ship a working benchmark harness for **Billie Jean only** with these deliverables:
- benchmark folder structure
- manifest file
- runner script
- results output format
- rule evaluation for core groove checks
- workflow/docs updates referencing benchmark results

## Non-goals for this plan
- browser UI for benchmarks
- automatic notation beauty scoring
- CI integration
- auto-download of benchmark audio
- multi-song pack

## Work breakdown

### Step 1 — Create benchmark repo structure
Create these paths:
- `benchmarks/`
- `benchmarks/audio/`
- `benchmarks/results/`
- `scripts/`

Add a small README if needed so the audio folder purpose is obvious.

#### Done when
- folders exist in repo
- repo layout clearly supports benchmark assets and outputs

---

### Step 2 — Define manifest schema
Create `benchmarks/manifest.json`.

Use a simple schema for pass 1. Avoid speculative fields.

### Proposed manifest shape
```json
{
  "version": 1,
  "benchmarks": [
    {
      "id": "billie-jean",
      "enabled": true,
      "songName": "Billie Jean",
      "artist": "Michael Jackson",
      "audioPath": "benchmarks/audio/billie-jean.mp3",
      "difficulties": ["beginner", "intermediate", "pro"],
      "expectations": {
        "bpmRange": [115, 121],
        "allowedHatPulseByDifficulty": {
          "beginner": ["8th"],
          "intermediate": ["8th", "16th"],
          "pro": ["8th", "16th"]
        },
        "requiredStepsByDifficulty": {
          "beginner": {
            "sn": [8, 24, 40, 56],
            "bd": [0]
          }
        },
        "minVisibleCountsByDifficulty": {
          "beginner": {
            "hh": 8,
            "sn": 4,
            "bd": 2
          }
        },
        "maxVisibleCountsByDifficulty": {
          "beginner": {
            "hh": 16
          }
        },
        "densityGuardrails": {
          "beginnerNotDenserThan": ["intermediate", "pro"]
        }
      }
    }
  ]
}
```

### Notes
- Use relative repo paths.
- Keep expectations focused on what the current engine can actually expose.
- Do not encode visual engraving expectations into the manifest.

#### Done when
- manifest exists
- manifest validates by structure in runner code
- Billie Jean benchmark entry is present

---

### Step 3 — Define result file format
The runner should save outputs under a deterministic folder per benchmark.

### Proposed layout
- `benchmarks/results/billie-jean/latest/summary.json`
- `benchmarks/results/billie-jean/latest/beginner.json`
- `benchmarks/results/billie-jean/latest/intermediate.json`
- `benchmarks/results/billie-jean/latest/pro.json`

Optional later:
- timestamped archive folders

For pass 1, `latest/` is enough.

### Proposed summary shape
```json
{
  "benchmarkId": "billie-jean",
  "songName": "Billie Jean",
  "overallStatus": "pass",
  "generatedAt": "2026-04-13T18:00:00+08:00",
  "resultsByDifficulty": {
    "beginner": {
      "status": "pass",
      "checks": [
        { "id": "engine-run", "status": "pass", "message": "Engine completed." },
        { "id": "bpm-range", "status": "pass", "message": "117 BPM within expected range." },
        { "id": "hat-pulse", "status": "pass", "message": "8th pulse allowed for beginner." }
      ]
    }
  },
  "crossDifficultyChecks": [
    { "id": "density-guardrail", "status": "pass", "message": "Beginner density did not exceed intermediate/pro." }
  ],
  "humanReviewReminder": [
    "Check notation readability manually.",
    "Check that hats are readable and not spammy.",
    "Check visual placement honesty in rendered score."
  ]
}
```

#### Done when
- raw per-difficulty outputs are written
- summary file exists and is readable
- status is deterministic from rule results

---

### Step 4 — Implement runner script
Create `scripts/run_benchmarks.py`.

### Runner responsibilities
1. locate repo root
2. load `benchmarks/manifest.json`
3. iterate enabled benchmarks
4. verify audio file exists
5. run `engine/process_song.py` for each difficulty
6. parse engine JSON output
7. save raw outputs to results folder
8. evaluate machine-checkable rules
9. write `summary.json`
10. print concise terminal summary

### Suggested implementation details
- use Python to stay close to the engine
- call the engine via `subprocess.run(["python3", "engine/process_song.py", ...])`
- fail clearly if any run exits non-zero
- treat JSON parse failures as benchmark failure
- keep runner logic separate from engine logic

### CLI behavior for pass 1
Support at least:
- `python3 scripts/run_benchmarks.py`

Optional nice additions if cheap:
- `--benchmark billie-jean`
- `--difficulty beginner`

#### Done when
- command runs locally
- runner exits non-zero on hard failures
- runner prints pass/warn/fail clearly

---

### Step 5 — Implement rule evaluation
Build explicit rule functions. Keep them small and readable.

### Per-difficulty rules
- `engine-run`
- `bpm-range`
- `hat-pulse`
- `beat-one-support`
- `snare-backbeat`
- `min-visible-counts`
- `max-visible-counts`

### Cross-difficulty rules
- `density-guardrail`
- `difficulty-separation`

### Suggested rule behavior
- `pass` = expectation clearly met
- `warn` = borderline / incomplete / expectation weakly met
- `fail` = expectation clearly violated

### How to derive data
Use engine result fields already available:
- `debug.bpm`
- `debug.hiHatPulse`
- `debug.acceptedHits`
- visible counts derived from output phrase or accepted hits

For kick/snare step checks, use `acceptedHits.step` + `kind`.

#### Done when
- summary contains explicit rule outcomes
- no hidden scoring math decides final result

---

### Step 6 — Wire Billie Jean benchmark asset expectation
Pass 1 assumes the actual benchmark audio file is manually placed at:
- `benchmarks/audio/billie-jean.mp3`

If missing:
- runner should fail clearly
- message should say exactly which path is missing

Also update the human-facing benchmark doc to reference the canonical manifest/audio path if needed.

#### Done when
- harness knows where Billie Jean audio should live
- missing asset error is explicit instead of vague

---

### Step 7 — Update benchmark docs
Update docs so repo guidance matches the harness.

Files likely to update:
- `docs/benchmarks/README.md`
- `docs/benchmarks/billie-jean.md`

Add:
- benchmark harness command
- manifest is canonical for machine checks
- docs remain human-facing review notes
- Billie Jean audio expected path

#### Done when
- docs do not conflict with harness behavior
- new benchmark workflow is understandable without chat context

---

### Step 8 — Update workflow/reporting docs
Update workflow docs so benchmark output becomes part of patch review.

Files likely to update:
- `docs/workflows/agent-workflow.md`
- `docs/workflows/reviewer-checklist.md`
- `docs/workflows/reviewer-brief.md`

Changes:
- meaningful transcription patches should mention benchmark outcome
- local lint/build is not enough by itself
- reviewer should note benchmark pass/warn/fail explicitly

#### Done when
- benchmark reporting is part of the documented workflow

---

### Step 9 — Local validation pass
After implementation:
- run harness locally
- inspect raw result JSON files
- inspect summary.json
- confirm missing-file behavior if Billie Jean audio is absent
- if audio exists, confirm rule outputs make sense

#### Done when
- harness behavior matches docs and plan
- output is clean enough to trust in future patch reports

## Implementation order
Recommended order:
1. create folders
2. add manifest
3. create runner skeleton
4. write result output handling
5. add rule evaluation
6. wire Billie Jean entry
7. update benchmark docs
8. update workflow docs
9. run validation

## Risks during implementation
### Too many speculative rules
Avoid building checks the engine cannot support yet.

### Overly complicated schema
Keep pass 1 manifest minimal.

### Result sprawl
Use `latest/` first; postpone archive/versioning.

### False confidence
Keep human review reminder in summary output.

## Success checkpoint for first coding pass
The first coding pass is successful if:
- `python3 scripts/run_benchmarks.py` works
- missing audio is reported cleanly
- Billie Jean benchmark can run when asset exists
- raw outputs and summary are saved
- summary contains explicit rule outcomes
- docs/workflow reflect the benchmark harness

## Suggested commit slicing
To keep review clean, prefer this commit order:
1. scaffold benchmark folders + manifest + runner skeleton
2. implement rule evaluation + result output
3. update docs/workflows
4. validate and refine

## Immediate next coding task
Implement pass 1 of the benchmark harness exactly as above, starting with:
- benchmark folders
- manifest
- runner skeleton
- Billie Jean wiring
