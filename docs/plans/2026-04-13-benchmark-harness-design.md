# Benchmark Harness Design

Date: 2026-04-13
Project: Drumsheet-Ai
Status: approved design

## Goal
Build a real benchmark harness so transcription patches can be judged against fixed songs instead of vague impressions.

## Problem
Current benchmarking is too loose:
- benchmark intent exists in docs
- Billie Jean exists as a benchmark note
- but there is no repeatable run loop
- patches can look directionally right without being measured consistently

This causes wasted iteration and weak confidence in groove fixes.

## Decision
Build a **script + manifest benchmark harness**.

This will be the long-term benchmark architecture, but rollout will start small.

## Chosen approach
### Architecture
Use a repo-local harness with these parts:
- `benchmarks/manifest.json` — canonical benchmark definitions
- `benchmarks/audio/` — local benchmark audio files
- `benchmarks/results/` — structured saved outputs from benchmark runs
- `scripts/run_benchmarks.py` — benchmark runner
- `docs/benchmarks/` — human-readable benchmark notes and review context

### Why this approach
This approach is strong enough to scale, but simple enough to ship now.

Compared with alternatives:
- **Docs-only manual loop** is too weak and still depends on memory/human discipline.
- **UI-integrated benchmark system** is premature and would distract from engine truth.
- **Script + manifest** keeps benchmark logic explicit, automatable, and versioned in the repo.

## Scope
### In scope
- benchmark manifest format
- benchmark audio storage convention
- runner command for all benchmarks
- structured result files per benchmark and difficulty
- rule-based pass/warn/fail summary
- initial harness rollout with a single real benchmark song
- workflow/docs updates so benchmark outcome becomes part of patch evaluation

### Out of scope for first pass
- automatic scoring of notation beauty
- browser-based benchmark UI
- audio asset downloading
- full CI enforcement
- multi-song benchmark pack on day one

## Evaluation model
Split evaluation into two categories.

### Machine-checkable rules
The harness should validate:
- benchmark audio file exists
- engine runs successfully
- all requested difficulties run successfully
- BPM falls inside expected range
- inferred hi-hat pulse matches allowed expectation
- event counts are sane by difficulty
- beginner does not become denser than allowed
- beat 1 support exists
- snare/backbeat support exists where expected

### Human-review-only checks
The harness must not pretend to solve these automatically:
- notation engraving quality
- whether the chart visually looks like a real drum sheet
- whether timing feels musically honest
- whether hats look readable instead of spammy in notation

These remain explicit human review tasks.

## Output model
Each benchmark run should write:
- raw engine result JSON per benchmark and difficulty
- a compact summary file containing checks and outcomes
- an overall benchmark status using:
  - `pass`
  - `warn`
  - `fail`

The harness should prefer rule-by-rule results over one fake aggregate quality score.

## Rule style
Use explicit rules instead of a single numeric score.

Example rule categories:
- bpm-range
- hat-pulse
- beat-one-support
- snare-backbeat
- difficulty-separation
- density-guardrail

Why:
- easier to debug
- easier to explain to Eddie
- less fake precision

## Manifest design
The manifest should define benchmarks as structured entries.

Example fields:
- id
- songName
- artist
- audioPath
- enabled
- expectations

Example expectation fields:
- bpmRange
- allowedHatPulseByDifficulty
- minVisibleCounts
- maxVisibleCounts
- requiredSteps
- forbiddenPatterns
- notes

The manifest should be strict enough for repeatability, but not so rich that it turns into a second transcription engine.

## Data flow
1. Runner reads `benchmarks/manifest.json`.
2. Runner loads each enabled benchmark audio file.
3. Runner executes the transcription engine for beginner / intermediate / pro.
4. Runner saves per-difficulty raw outputs.
5. Runner derives machine-checkable rule results.
6. Runner writes a compact pass/warn/fail summary.
7. Human review still checks the rendered notation where needed.

## Rollout plan
### Pass 1 — single-song real harness
- create harness structure
- add manifest
- wire one real audio benchmark
- Billie Jean only
- save results and summary
- update docs/workflow to reference benchmark output

### Pass 2 — multi-song harness
- add more benchmark songs
- expose per-song failure breakdown
- improve rule coverage without overfitting

### Pass 3 — workflow enforcement
- require benchmark outcome in patch reports
- reviewer must mention benchmark result explicitly
- local lint/build alone is no longer enough for transcription patches

## Workflow impact
After rollout, meaningful transcription changes should report:
- what changed
- what local tests passed
- what benchmark(s) passed/warned/failed
- what reviewer found
- what still looks risky

If a benchmark fails, the patch should not be presented as clearly good.

## Risks
### 1. Fake certainty
Risk: the harness may look scientific while checking shallow proxies only.
Mitigation: clearly separate machine rules from human review.

### 2. Overfitting to one song
Risk: tuning too hard to Billie Jean.
Mitigation: treat Billie Jean as pass 1 only; expand later.

### 3. Benchmark drift
Risk: benchmark docs and manifest disagree.
Mitigation: manifest becomes canonical for machine checks; docs stay human-facing.

### 4. Asset friction
Risk: benchmark audio may be missing or awkward to store.
Mitigation: first pass assumes manually supplied local files under `benchmarks/audio/`.

## Success criteria
Pass 1 is successful when:
- one command runs the benchmark harness
- Billie Jean benchmark can be executed from repo state
- outputs are saved deterministically
- machine-checkable rules produce pass/warn/fail
- workflow/reporting can mention benchmark outcome explicitly

## Recommended first implementation
Implement the full-harness architecture, but only for **Pass 1**:
- `benchmarks/manifest.json`
- `benchmarks/audio/`
- `benchmarks/results/`
- `scripts/run_benchmarks.py`
- Billie Jean benchmark entry
- docs/workflow updates

This keeps the architecture future-proof while avoiding premature complexity.

## Next planning target
Translate this design into an implementation plan for:
1. manifest schema
2. runner behavior
3. result file format
4. Billie Jean first benchmark wiring
5. workflow/reporting updates
