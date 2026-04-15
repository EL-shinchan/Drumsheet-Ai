# Benchmark: In the End

## Song
- Name: In the End
- Artist: Linkin Park
- Use: clean 16th-note hi-hat benchmark
- Canonical benchmark manifest entry: `benchmarks/manifest.json`
- Expected audio path for pass 1: `benchmarks/audio/in-the-end.mp3`
- Harness command: `python3 scripts/run_benchmarks.py --benchmark in-the-end`

## Why this benchmark matters
This song gives the harness a different failure mode from Billie Jean. It should expose whether the system over-clamps everything toward simple 8th-note hats when the groove pressure wants denser subdivision.

## Expected behavior
### BPM
- Expected range: 100-110 BPM
- Working expectation for current review baseline: about 105 BPM

### Beginner baseline expectation
- beat 1 must still be visible
- snare should keep a believable backbeat anchor
- hi-hat density should not collapse into obviously wrong sparse 8ths if the groove wants more subdivision
- notation should remain readable, not spammy

### Difficulty expectations
- Beginner: simplified but still rhythmically honest
- Intermediate: should allow clearer subdivision movement than beginner
- Pro: can keep the most detected movement, but not at the cost of readability

## Known failure modes to watch
- over-clamping 16th pressure into flat 8ths
- pro still resolving to 8th-note hats when this benchmark should force 16th honesty
- hats becoming unreadable spam instead of controlled subdivision
- backbeat support getting lost while chasing hat density
- difficulty levels looking too similar

## Last reviewed result
- Status: pending first run

## Reviewer use
When reviewing hi-hat-density or subdivision fixes, compare against this benchmark after Billie Jean. Use it to catch regressions where beginner/intermediate/pro all collapse to the same pulse or where dense hats become dishonest notation.
