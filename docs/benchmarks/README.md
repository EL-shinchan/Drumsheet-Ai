# Benchmark Workflow

This folder tracks benchmark songs and expected groove behavior.

## Purpose
Reduce repeat debugging of the same class of bugs by testing every major patch against a fixed set of songs.

## Per-song benchmark record should include
- song name
- source file/location
- expected BPM range
- expected hi-hat pulse (8th / 16th / mixed)
- expected snare behavior
- expected kick backbone
- known failure modes
- last reviewed result

## Minimum benchmark pack target
- 1 simple pop groove
- 1 clean 16th-hat groove
- 1 straight rock groove
- 1 drum-heavy mix
- 1 harder mixed track

## Current concrete pack
- `billie-jean` — simple pop backbone baseline
- `in-the-end` — subdivision / 16th-hat pressure check

## Current immediate benchmark
- Billie Jean should become a reference for obvious pop backbone behavior.
- Concrete record: `docs/benchmarks/billie-jean.md`

## Canonical beginner pop backbone expectation
Use this as the default review baseline for obvious pop/rock grooves unless strong song evidence contradicts it:
- beat 1 must be visually present
- snare should land on 2/4
- kick should show clear downbeat support, especially beat 1
- hi-hat pulse should resolve to a readable 8th or 16th pattern, not unstable over-segmentation
- notation should visually reflect the chosen timing honestly

## Source of truth
- `benchmarks/manifest.json` is the canonical source for machine-checkable benchmark expectations.
- `docs/benchmarks/*.md` remain human-facing notes and review context.
- The harness does not judge notation beauty automatically; rendered score review is still required.
