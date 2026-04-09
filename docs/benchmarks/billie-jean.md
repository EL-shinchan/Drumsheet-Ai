# Benchmark: Billie Jean

## Song
- Name: Billie Jean
- Artist: Michael Jackson
- Use: canonical simple pop backbone benchmark

## Why this benchmark matters
This song should expose basic groove mistakes immediately. If the system cannot produce a recognizably correct beginner backbone here, the core pipeline is still failing.

## Expected behavior
### BPM
- Expected range: 115-121 BPM
- Working expectation for current review baseline: about 117 BPM

### Beginner baseline expectation
- beat 1 must be visually present
- hi-hat pulse should resolve to a stable readable pulse, not over-segmented note spam
- snare should land on 2 / 4 / 6 / 8 over the 2-bar phrase
- kick should clearly support the backbone and visibly include beat 1

### Difficulty expectations
- Beginner: clean backbone first, minimal extra variation
- Intermediate: same backbone with limited added movement
- Pro: same backbone preserved, more variation allowed, but not at the cost of pulse clarity

## Known failure modes seen so far
- hi-hat over-segmentation / 32nd-like spam
- beat 1 hi-hat missing
- snare not rendering clearly on 2/4
- kick selected logically but not rendered honestly
- notation timing lying about placement

## Last reviewed result
- Status: in progress
- Most recent human review summary:
  - beginner hi-hat still wrong / over-dense
  - snare and kick improved after backbone/timing fixes
  - timing still needs cleanup when hat lane gets noisy

## Reviewer use
When reviewing beginner-mode patches for obvious pop grooves, compare against this benchmark first unless a more specific song benchmark exists.
