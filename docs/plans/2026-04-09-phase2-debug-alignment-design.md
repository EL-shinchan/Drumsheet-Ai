# Phase 2 Debug + Alignment + Classification Design

Date: 2026-04-09

## Goal
Make transcription failures diagnosable and improve core groove accuracy on obvious songs by adding debug visibility, stronger bar alignment, and clearer kick/snare/hi-hat classification.

## Why this phase exists
Phase 1 proved the pipeline can analyze audio and emit a 2-bar MusicXML preview, but benchmark-style feedback showed the output is still not accurate enough on simple recognizable grooves like Billie Jean. That means the next priority is not more notation complexity, but better visibility and stronger core detection.

## Chosen approach
Use a layered debug design plus targeted engine improvements.

### Debug UI
Default simple panel:
- BPM
- selected 2-bar window
- 16th-note grid
- detected/accepted kick-snare-hi-hat layout

Expandable advanced panel:
- raw detected hit count
- quantized hits
- accepted hits
- strengths/confidence-like values
- filtering behavior by difficulty

## Engine work
1. Extend Python JSON output with structured debug information.
2. Improve preview window scoring so bar selection prefers stronger backbeat structure.
3. Tighten hit classification heuristics to reduce false hi-hat spam and improve kick/snare separation.
4. Keep raw detections separate from accepted notation events so the UI can explain what happened.

## Constraints
- Keep current UI and MusicXML rendering path.
- Do not add heavy ML dependencies in this phase.
- Do not expand to toms/ride/fills yet.
- Optimize for diagnosing and improving basic groove accuracy.

## Success criteria
- The user can see why a transcription is wrong.
- Songs with obvious grooves become easier to tune against.
- Debug output clearly separates timing issues from classification/filtering issues.
- The app remains usable for normal previewing while offering deeper diagnostics when needed.
