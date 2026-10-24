# Benchmark Audio

Put canonical benchmark audio files here.

## Expected files
- `billie-jean.mp3`
- `in-the-end.mp3`

The songs are copyrighted, so they are git-ignored (`benchmarks/audio/*.mp3`) and
never pushed. On a fresh clone, copy them in here yourself before running the
harness — the filenames must match `audioPath` in `benchmarks/manifest.json`.
The benchmark manifest at `benchmarks/manifest.json` is the canonical source for machine-checkable expectations.

Human review still matters:
- notation readability
- timing honesty
- visual drum-sheet quality
