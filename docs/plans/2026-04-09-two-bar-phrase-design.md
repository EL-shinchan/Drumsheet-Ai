# Two-Bar Phrase Design

Date: 2026-04-09

## Goal
Extend the current one-bar notation baseline into a two-bar phrase for all three difficulty levels while preserving the accepted drum placement baseline.

## Constraints
- Do not remap staff positions.
- Do not change hi-hat / snare / kick display placement.
- Keep hi-hat open/closed markings above the staff using explicit direction symbols.
- Keep the MusicXML + OpenSheetMusicDisplay preview path.
- Change generation logic, measure generation, and summaries only.

## Approaches considered

### 1. Clone + light variation
Duplicate bar 1 and make small edits in bar 2.
- Pros: safest
- Cons: can feel repetitive and under-musical

### 2. Level-shaped variation (chosen)
Keep bar 1 anchored to the current baseline and give bar 2 a controlled variation per difficulty.
- Pros: best balance of realism, control, and clear difficulty separation
- Cons: slightly more template logic

### 3. Full phrase design
Treat the two bars as one stronger musical sentence with bigger development.
- Pros: most musical
- Cons: highest regression risk right now

## Chosen design
Each difficulty becomes a two-bar phrase.
- Bar 1 preserves the accepted identity of the level.
- Bar 2 adds controlled variation without changing notation placement rules.

### Difficulty behavior
- Beginner: bar 2 is very close to bar 1 with only a small safe variation.
- Intermediate: bar 2 adds clearer kick and hi-hat variation.
- Pro: bar 2 adds more phrase motion, syncopation, ghost-note flavor, and light loop-back energy.

## Implementation plan
1. Replace the single-bar groove template with two-bar phrase templates.
2. Generate separate MusicXML measures instead of one combined measure.
3. Reuse the current note rendering and hi-hat direction logic.
4. Update summaries to describe the new two-bar behavior.
5. Validate that all three levels render as two measures and remain visually stable.

## Success criteria
- Beginner / Intermediate / Pro all render as 2 bars.
- Difficulty separation is clearer through phrase behavior, not random density.
- The accepted visual baseline stays intact.
- The second bar feels like a musical variation rather than a duplicate or noisy fill.
