import json
import os
import sys

VALID_DIFFICULTIES = {"beginner", "intermediate", "pro"}


def build_sections(difficulty: str):
    if difficulty == "beginner":
        return {
            "confidence": 0.72,
            "sections": [
                {"name": "Intro", "bars": ["HH x-x-x-x-\nSD ----o---\nBD o---o---"]},
                {"name": "Verse", "bars": ["HH x-x-x-x-\nSD ----o---\nBD o-o---o-"]},
            ],
        }

    if difficulty == "intermediate":
        return {
            "confidence": 0.78,
            "sections": [
                {"name": "Intro", "bars": ["HH x-xx-x-x\nSD ----o---\nBD o---o-o-"]},
                {"name": "Verse", "bars": ["HH x-xx-x-x\nSD ----o-g-\nBD o-o---o-"]},
            ],
        }

    return {
        "confidence": 0.84,
        "sections": [
            {"name": "Intro", "bars": ["HH x-xx-x-x\nSD --g-o-g-\nBD o---o-o-"]},
            {"name": "Verse", "bars": ["HH x-xx-xx-\nSD ----o-g-\nBD oo--o---"]},
            {"name": "Fill", "bars": ["T1 ----oo--\nT2 --oo----\nFT oo------"]},
        ],
    }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: process_song.py <file_path> <difficulty>"}))
        sys.exit(1)

    file_path = sys.argv[1]
    difficulty = sys.argv[2].lower()

    if difficulty not in VALID_DIFFICULTIES:
        print(json.dumps({"error": "Invalid difficulty"}))
        sys.exit(1)

    title = os.path.basename(file_path)
    data = build_sections(difficulty)

    print(
        json.dumps(
            {
                "title": f"Demo chart for {title}",
                "difficulty": difficulty,
                "confidence": data["confidence"],
                "sections": data["sections"],
            }
        )
    )


if __name__ == "__main__":
    main()
