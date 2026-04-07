import json
import os
import sys

VALID_DIFFICULTIES = {"beginner", "intermediate", "pro"}


def note(beat, pitch, duration="eighth", accent=False):
    return {
        "beat": beat,
        "pitch": pitch,
        "duration": duration,
        "accent": accent,
    }


def measure(*notes):
    return {"notes": list(notes)}


def build_notation_sections(difficulty: str):
    if difficulty == "beginner":
        intro = [
            measure(
                note(1.0, "closed-hihat"), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare"), note(2.5, "closed-hihat"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare"), note(4.5, "closed-hihat"),
            ),
            measure(
                note(1.0, "closed-hihat"), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare"), note(2.5, "closed-hihat"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare"), note(4.5, "closed-hihat"),
            ),
            measure(
                note(1.0, "closed-hihat"), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare"), note(2.5, "closed-hihat"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare"), note(4.5, "closed-hihat"),
            ),
            measure(
                note(1.0, "crash", accent=True), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare"), note(2.5, "closed-hihat"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare"), note(4.5, "closed-hihat"),
            ),
        ]
        verse = [
            measure(
                note(1.0, "closed-hihat"), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare"), note(2.5, "closed-hihat"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare"), note(4.5, "closed-hihat"),
            ),
            measure(
                note(1.0, "closed-hihat"), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare"), note(2.5, "closed-hihat"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare"), note(4.5, "closed-hihat"),
            ),
            measure(
                note(1.0, "closed-hihat"), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare"), note(2.5, "closed-hihat"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare"), note(4.5, "closed-hihat"),
            ),
            measure(
                note(1.0, "crash", accent=True), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare"), note(2.5, "closed-hihat"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare"), note(4.5, "closed-hihat"),
            ),
        ]
        confidence = 0.74
    elif difficulty == "intermediate":
        intro = [
            measure(
                note(1.0, "closed-hihat"), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare", accent=True), note(2.5, "closed-hihat"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare", accent=True), note(4.5, "closed-hihat"), note(4.5, "kick"),
            ),
            measure(
                note(1.0, "closed-hihat"), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare", accent=True), note(2.5, "closed-hihat"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare", accent=True), note(4.5, "closed-hihat"), note(4.5, "kick"),
            ),
            measure(
                note(1.0, "crash", accent=True), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare", accent=True), note(2.5, "closed-hihat"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare", accent=True), note(4.5, "closed-hihat"), note(4.5, "kick"),
            ),
            measure(
                note(1.0, "closed-hihat"), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare", accent=True), note(2.5, "closed-hihat"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare", accent=True), note(4.5, "closed-hihat"), note(4.5, "kick"),
            ),
        ]
        verse = intro
        confidence = 0.8
    else:
        intro = [
            measure(
                note(1.0, "crash", accent=True), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare", accent=True), note(2.5, "closed-hihat"), note(2.5, "kick"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare", accent=True), note(4.5, "closed-hihat"), note(4.5, "kick"),
            ),
            measure(
                note(1.0, "ride"), note(1.0, "kick"), note(1.5, "ride"),
                note(2.0, "ride"), note(2.0, "snare", accent=True), note(2.5, "ride"),
                note(3.0, "ride"), note(3.0, "kick"), note(3.5, "ride"),
                note(4.0, "ride"), note(4.0, "snare", accent=True), note(4.25, "high-tom"), note(4.5, "floor-tom"), note(4.5, "kick"),
            ),
            measure(
                note(1.0, "ride"), note(1.0, "kick"), note(1.5, "ride"),
                note(2.0, "ride"), note(2.0, "snare", accent=True), note(2.5, "ride"),
                note(3.0, "ride"), note(3.0, "kick"), note(3.5, "ride"),
                note(4.0, "ride"), note(4.0, "snare", accent=True), note(4.25, "high-tom"), note(4.5, "floor-tom"), note(4.5, "kick"),
            ),
            measure(
                note(1.0, "crash", accent=True), note(1.0, "kick"), note(1.5, "closed-hihat"),
                note(2.0, "closed-hihat"), note(2.0, "snare", accent=True), note(2.5, "closed-hihat"), note(2.5, "kick"),
                note(3.0, "closed-hihat"), note(3.0, "kick"), note(3.5, "closed-hihat"),
                note(4.0, "closed-hihat"), note(4.0, "snare", accent=True), note(4.5, "closed-hihat"), note(4.5, "kick"),
            ),
        ]
        verse = intro
        confidence = 0.85

    return {
        "confidence": confidence,
        "notationSections": [
            {"name": "Intro", "timeSignature": "4/4", "measures": intro},
            {"name": "Verse", "timeSignature": "4/4", "measures": verse},
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
    data = build_notation_sections(difficulty)

    print(
        json.dumps(
            {
                "title": f"Experimental notation for {title}",
                "difficulty": difficulty,
                "confidence": data["confidence"],
                "previewMode": "experimental-notation",
                "summary": "This is a page-style notation experiment focused on readability, system layout, and more realistic drum-sheet presentation. It is still not full-song audio transcription yet.",
                "notationSections": data["notationSections"],
            }
        )
    )


if __name__ == "__main__":
    main()
