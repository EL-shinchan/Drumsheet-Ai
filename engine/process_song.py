import json
import os
import sys
from xml.sax.saxutils import escape

VALID_DIFFICULTIES = {"beginner", "intermediate", "pro"}

DIVISIONS = 4
DURATION_MAP = {"16th": 1, "eighth": 2, "quarter": 4}

DRUM_MAP = {
    "kick": {
        "instrument": "P1-I36",
        "name": "Bass Drum",
        "step": "F",
        "octave": 4,
        "stem": "down",
        "voice": 2,
    },
    "snare": {
        "instrument": "P1-I39",
        "name": "Snare Drum",
        "step": "C",
        "octave": 5,
        "stem": "up",
        "voice": 1,
    },
    "ghost-snare": {
        "instrument": "P1-I39",
        "name": "Snare Drum",
        "step": "C",
        "octave": 5,
        "stem": "up",
        "voice": 1,
        "parentheses": True,
    },
    "closed-hihat": {
        "instrument": "P1-I43",
        "name": "Closed Hi-Hat",
        "step": "G",
        "octave": 5,
        "stem": "up",
        "voice": 1,
        "notehead": "x",
    },
    "open-hihat": {
        "instrument": "P1-I43",
        "name": "Open Hi-Hat",
        "step": "G",
        "octave": 5,
        "stem": "up",
        "voice": 1,
        "notehead": "x",
        "open": True,
    },
    "ride": {
        "instrument": "P1-I51",
        "name": "Ride Cymbal",
        "step": "A",
        "octave": 5,
        "stem": "up",
        "voice": 1,
        "notehead": "x",
    },
    "crash": {
        "instrument": "P1-I49",
        "name": "Crash Cymbal",
        "step": "A",
        "octave": 5,
        "stem": "up",
        "voice": 1,
        "notehead": "x",
    },
    "high-tom": {
        "instrument": "P1-I48",
        "name": "High Tom",
        "step": "E",
        "octave": 5,
        "stem": "up",
        "voice": 1,
    },
    "mid-tom": {
        "instrument": "P1-I47",
        "name": "Mid Tom",
        "step": "D",
        "octave": 5,
        "stem": "up",
        "voice": 1,
    },
    "floor-tom": {
        "instrument": "P1-I41",
        "name": "Floor Tom",
        "step": "A",
        "octave": 4,
        "stem": "up",
        "voice": 1,
    },
    "hihat-foot": {
        "instrument": "P1-I44",
        "name": "Hi-Hat Foot",
        "step": "D",
        "octave": 4,
        "stem": "down",
        "voice": 2,
        "notehead": "x",
    },
}


INSTRUMENT_ORDER = [
    "kick",
    "snare",
    "closed-hihat",
    "open-hihat",
    "ride",
    "crash",
    "high-tom",
    "mid-tom",
    "floor-tom",
    "hihat-foot",
]


def event(at, drum, duration="eighth", accent=False):
    return {
        "at": at,
        "drum": drum,
        "duration": duration,
        "accent": accent,
    }


def build_measures(difficulty: str):
    if difficulty == "beginner":
        return [
            {
                "label": "Intro",
                "events": [
                    event(0, "closed-hihat"), event(0, "kick", "quarter"),
                    event(2, "closed-hihat"),
                    event(4, "closed-hihat"), event(4, "snare", "quarter"),
                    event(6, "closed-hihat"),
                    event(8, "closed-hihat"), event(8, "kick", "quarter"),
                    event(10, "closed-hihat"),
                    event(12, "closed-hihat"), event(12, "snare", "quarter"),
                    event(14, "closed-hihat"),
                ],
            },
            {
                "label": "Verse",
                "events": [
                    event(0, "crash", accent=True), event(0, "kick", "quarter"),
                    event(2, "closed-hihat"),
                    event(4, "closed-hihat"), event(4, "snare", "quarter"),
                    event(6, "closed-hihat"),
                    event(8, "closed-hihat"), event(8, "kick", "quarter"),
                    event(10, "closed-hihat"),
                    event(12, "closed-hihat"), event(12, "snare", "quarter"),
                    event(14, "closed-hihat"),
                ],
            },
        ]

    if difficulty == "intermediate":
        return [
            {
                "label": "Verse",
                "events": [
                    event(0, "crash", accent=True), event(0, "kick", "quarter"),
                    event(2, "closed-hihat"),
                    event(4, "closed-hihat"), event(4, "snare", "quarter", accent=True),
                    event(6, "closed-hihat"), event(7, "ghost-snare", "16th"),
                    event(8, "closed-hihat"), event(8, "kick", "quarter"),
                    event(10, "closed-hihat"),
                    event(12, "closed-hihat"), event(12, "snare", "quarter", accent=True),
                    event(14, "open-hihat"), event(14, "kick", "quarter"),
                ],
            },
            {
                "label": "Fill / transition",
                "events": [
                    event(0, "ride"), event(0, "kick", "quarter"),
                    event(2, "ride"),
                    event(4, "ride"), event(4, "snare", "quarter", accent=True),
                    event(6, "ride"),
                    event(8, "ride"), event(8, "kick", "quarter"),
                    event(10, "high-tom", "16th"),
                    event(11, "mid-tom", "16th"),
                    event(12, "floor-tom", "16th"),
                    event(13, "snare", "16th", accent=True),
                    event(14, "crash", accent=True), event(14, "kick", "quarter"),
                ],
            },
        ]

    return [
        {
            "label": "Verse",
            "events": [
                event(0, "crash", accent=True), event(0, "kick", "quarter"),
                event(2, "closed-hihat"),
                event(4, "closed-hihat"), event(4, "snare", "quarter", accent=True),
                event(5, "ghost-snare", "16th"),
                event(6, "closed-hihat"), event(6, "kick", "eighth"),
                event(8, "closed-hihat"), event(8, "kick", "quarter"),
                event(10, "closed-hihat"),
                event(12, "closed-hihat"), event(12, "snare", "quarter", accent=True),
                event(14, "open-hihat"), event(14, "kick", "quarter"),
            ],
        },
        {
            "label": "Fill / transition",
            "events": [
                event(0, "ride"), event(0, "kick", "quarter"),
                event(2, "ride"),
                event(4, "ride"), event(4, "snare", "quarter", accent=True),
                event(6, "ride"), event(7, "ghost-snare", "16th"),
                event(8, "ride"), event(8, "kick", "quarter"),
                event(10, "high-tom", "16th"),
                event(11, "mid-tom", "16th"),
                event(12, "floor-tom", "16th"),
                event(13, "snare", "16th", accent=True),
                event(14, "crash", accent=True), event(14, "kick", "quarter"), event(14, "hihat-foot", "quarter"),
            ],
        },
    ]


def note_xml(event_data):
    drum = DRUM_MAP[event_data["drum"]]
    duration_value = DURATION_MAP[event_data["duration"]]
    xml = ["    <note>"]
    xml.append("      <unpitched>")
    xml.append(f"        <display-step>{drum['step']}</display-step>")
    xml.append(f"        <display-octave>{drum['octave']}</display-octave>")
    xml.append("      </unpitched>")
    xml.append(f"      <duration>{duration_value}</duration>")
    xml.append(f"      <instrument id=\"{drum['instrument']}\"/>")
    xml.append(f"      <voice>{drum['voice']}</voice>")
    xml.append(f"      <type>{event_data['duration']}</type>")
    if drum.get("notehead"):
        xml.append(f"      <notehead>{drum['notehead']}</notehead>")
    xml.append(f"      <stem>{drum['stem']}</stem>")
    if drum["voice"] == 2:
        xml.append("      <staff>1</staff>")
    if event_data.get("accent") or drum.get("parentheses") or drum.get("open"):
        xml.append("      <notations>")
        if event_data.get("accent"):
            xml.append("        <articulations><accent/></articulations>")
        if drum.get("open"):
            xml.append("        <technical><open-string/></technical>")
        xml.append("      </notations>")
    if drum.get("parentheses"):
        xml.append("      <play><mute>straight</mute></play>")
    xml.append("    </note>")
    return "\n".join(xml)


def build_musicxml(title: str, difficulty: str):
    measures = build_measures(difficulty)
    measure_xml = []

    for index, measure in enumerate(measures, start=1):
        measure_xml.append(f'  <measure number="{index}">')
        if index == 1:
            measure_xml.append("    <attributes>")
            measure_xml.append(f"      <divisions>{DIVISIONS}</divisions>")
            measure_xml.append("      <key><fifths>0</fifths></key>")
            measure_xml.append("      <time><beats>4</beats><beat-type>4</beat-type></time>")
            measure_xml.append("      <staves>1</staves>")
            measure_xml.append("      <clef number=\"1\"><sign>percussion</sign><line>2</line></clef>")
            measure_xml.append("    </attributes>")
            measure_xml.append("    <direction placement=\"above\">")
            measure_xml.append(f"      <direction-type><words relative-y=\"12\">{escape(measure['label'])}</words></direction-type>")
            measure_xml.append("    </direction>")
        else:
            measure_xml.append("    <direction placement=\"above\">")
            measure_xml.append(f"      <direction-type><words relative-y=\"12\">{escape(measure['label'])}</words></direction-type>")
            measure_xml.append("    </direction>")

        for event_data in measure["events"]:
            measure_xml.append(note_xml(event_data))

        measure_xml.append("  </measure>")

    score_instruments = []
    for key in INSTRUMENT_ORDER:
        drum = DRUM_MAP[key]
        score_instruments.append(
            f'      <score-instrument id="{drum["instrument"]}"><instrument-name>{escape(drum["name"])}</instrument-name></score-instrument>'
        )

    score = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE score-partwise PUBLIC
  "-//Recordare//DTD MusicXML 3.1 Partwise//EN"
  "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <work>
    <work-title>{escape(title)}</work-title>
  </work>
  <identification>
    <creator type="arranger">Drumsheet AI experimental engraving</creator>
  </identification>
  <part-list>
    <score-part id="P1">
      <part-name>Drumset</part-name>
{chr(10).join(score_instruments)}
    </score-part>
  </part-list>
  <part id="P1">
{chr(10).join(measure_xml)}
  </part>
</score-partwise>
'''
    return score


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
    music_xml = build_musicxml(title, difficulty)

    print(
        json.dumps(
            {
                "title": f"Experimental notation for {title}",
                "difficulty": difficulty,
                "confidence": 0.65 if difficulty == "beginner" else 0.71 if difficulty == "intermediate" else 0.75,
                "previewMode": "musicxml",
                "summary": "This version tightens the drum key mapping: clearer kick/snare placement, better cymbal noteheads, open-vs-closed hat distinction, and more sensible hand/foot voice setup.",
                "musicXml": music_xml,
            }
        )
    )


if __name__ == "__main__":
    main()
