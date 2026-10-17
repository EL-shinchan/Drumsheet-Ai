"""Step 1 of the new engine: isolate the drums from a full song.

Wraps Demucs so the rest of the pipeline can listen to a clean drums-only track
instead of the whole mix (where bass gets mistaken for kick, vocals for hi-hat).

Usage:
    ml/.venv/bin/python ml/separate_drums.py <audio_file> [--out DIR]

Writes <out>/htdemucs/<song>/drums.mp3 (plus bass/vocals/other) and prints the
path to the drums stem on the last line.
"""

import argparse
import subprocess
import sys
from pathlib import Path

DEFAULT_OUT = Path("ml/output")


def separate_drums(audio_path: Path, out_dir: Path = DEFAULT_OUT) -> Path:
    if not audio_path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    # -d cpu: Apple-GPU (MPS) currently errors on this model.
    # --mp3: emit mp3 stems (smaller than wav, good enough for analysis).
    command = [
        sys.executable, "-m", "demucs",
        "-d", "cpu",
        "--mp3",
        "-o", str(out_dir),
        str(audio_path),
    ]
    result = subprocess.run(command)
    if result.returncode != 0:
        raise RuntimeError("Demucs separation failed")

    song = audio_path.stem
    drums = out_dir / "htdemucs" / song / "drums.mp3"
    if not drums.exists():
        raise RuntimeError(f"Expected drums stem not found at {drums}")
    return drums


def main() -> None:
    parser = argparse.ArgumentParser(description="Isolate the drum stem from a song.")
    parser.add_argument("audio", type=Path, help="Path to the input song (mp3/wav/...)")
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT, help="Output directory")
    args = parser.parse_args()

    drums = separate_drums(args.audio, args.out)
    print(drums)


if __name__ == "__main__":
    main()
