# Phase 1 Real MP3-to-Drum-Sheet Transcription Design

Date: 2026-04-09

## Goal
Replace the fixed fake groove generator with a real local analysis pipeline that extracts a drum-oriented two-bar preview from uploaded audio.

## Product target
- Works for both drum-heavy songs and mixed songs.
- Optimized first for drum-heavy material.
- Outputs a readable 2-bar MusicXML preview.

## Constraints
- Keep the current Next.js UI and API route.
- Keep Python as the analysis engine.
- Avoid heavy external ML dependencies for phase 1.
- Use local tools available on the machine.
- Favor a working prototype over false claims of perfect transcription.

## Available local stack
- Python 3.14
- numpy available
- ffmpeg available
- librosa/scipy/soundfile/pydub/audioread not available

## Chosen approach
Use a lightweight local DSP pipeline built with ffmpeg + numpy.

### Why this approach
- It works with the actual machine state now.
- It keeps control inside the repo.
- It creates a real analysis-based result instead of another fake template.
- It leaves room to swap in stronger audio libraries later.

## Pipeline
1. Decode uploaded audio with ffmpeg into mono PCM WAV.
2. Normalize waveform and derive a transient-friendly analysis signal.
3. Compute a simple onset envelope from frame energy changes.
4. Estimate tempo from onset autocorrelation.
5. Build a beat grid and a 16th-note quantization grid.
6. Score onset candidates against the grid.
7. Classify events with simple spectral-band heuristics:
   - kick: stronger low-band energy
   - snare: stronger mid/noise energy
   - hi-hat: stronger high-band energy
8. Pick a strong two-bar window from the analyzed material.
9. Convert cleaned events into MusicXML using the current notation mapping.

## Scope for phase 1
Included:
- MP3 decoding
- Tempo estimate
- Onset detection
- Kick/snare/hi-hat classification
- 2-bar MusicXML preview
- Difficulty-aware filtering density

Not included yet:
- Tom transcription
- Ride nuance
- Full-song charting
- Perfect ghost-note recovery from dense mixes
- Production-grade stem separation

## Difficulty behavior in phase 1
Difficulty does not invent different grooves anymore. It filters and presents the real detected material at different readability levels.
- Beginner: strongest core backbeat events only.
- Intermediate: more supporting kicks and hats.
- Pro: denser accepted event set and more syncopation retention.

## Success criteria
- Uploaded audio produces an analysis-based preview.
- Tempo estimate is surfaced in the summary.
- Resulting 2-bar phrase is derived from the audio, not from a fixed hard-coded groove.
- Preview remains readable and stable in MusicXML.
