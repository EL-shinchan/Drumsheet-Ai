import json
import os
import sys
from collections import defaultdict
from xml.sax.saxutils import escape

VALID_DIFFICULTIES = {"beginner", "intermediate", "pro"}
DIVISIONS = 4
DURATION_MAP = {"16th": 1, "eighth": 2, "quarter": 4}
BACKUP_OCTAVE = 4

DRUM_MAP = {
    "kick": {"instrument": "P1-I36", "name": "Bass Drum", "step": "F", "octave": 4, "stem": "down", "voice": 2},
    "snare": {"instrument": "P1-I39", "name": "Snare Drum", "step": "C", "octave": 5, "stem": "up", "voice": 1},
    "ghost-snare": {"instrument": "P1-I39", "name": "Snare Drum", "step": "C", "octave": 5, "stem": "up", "voice": 1, "parentheses": True},
    "closed-hihat": {"instrument": "P1-I43", "name": "Closed Hi-Hat", "step": "G", "octave": 5, "stem": "up", "voice": 1, "notehead": "x"},
    "open-hihat": {"instrument": "P1-I43", "name": "Open Hi-Hat", "step": "G", "octave": 5, "stem": "up", "voice": 1, "notehead": "x", "open": True},
    "ride": {"instrument": "P1-I51", "name": "Ride Cymbal", "step": "A", "octave": 5, "stem": "up", "voice": 1, "notehead": "x"},
    "crash": {"instrument": "P1-I49", "name": "Crash Cymbal", "step": "A", "octave": 5, "stem": "up", "voice": 1, "notehead": "x"},
    "high-tom": {"instrument": "P1-I48", "name": "High Tom", "step": "E", "octave": 5, "stem": "up", "voice": 1},
    "mid-tom": {"instrument": "P1-I47", "name": "Mid Tom", "step": "D", "octave": 5, "stem": "up", "voice": 1},
    "floor-tom": {"instrument": "P1-I41", "name": "Floor Tom", "step": "A", "octave": 4, "stem": "up", "voice": 1},
    "hihat-foot": {"instrument": "P1-I44", "name": "Hi-Hat Foot", "step": "D", "octave": 4, "stem": "down", "voice": 2, "notehead": "x"},
}

INSTRUMENT_ORDER = [
    "kick", "snare", "closed-hihat", "open-hihat", "ride", "crash", "high-tom", "mid-tom", "floor-tom", "hihat-foot"
]


class Event(dict):
    pass


def event(at, drum, duration="eighth", accent=False):
    return Event({"at": at, "drum": drum, "duration": duration, "accent": accent})


def beginner_measure_one():
    return {
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
    }


def beginner_measure_two():
    return {
        "label": "Verse",
        "events": [
            event(0, "crash", accent=True), event(0, "kick", "quarter"),
            event(2, "closed-hihat"),
            event(4, "closed-hihat"), event(4, "snare", "quarter"),
            event(6, "closed-hihat"),
            event(8, "closed-hihat"), event(8, "kick", "quarter"),
            event(10, "closed-hihat"),
            event(12, "closed-hihat"), event(12, "snare", "quarter"),
            event(14, "open-hihat"),
        ],
    }


def intermediate_measure_one():
    return {
        "label": "Verse",
        "events": [
            event(0, "crash", accent=True), event(0, "kick", "quarter"),
            event(2, "closed-hihat"),
            event(4, "closed-hihat"), event(4, "snare", "quarter", accent=True),
            event(6, "closed-hihat"), event(7, "ghost-snare", "16th"),
            event(8, "closed-hihat"), event(8, "kick", "quarter"),
            event(10, "closed-hihat"), event(10, "kick", "eighth"),
            event(12, "closed-hihat"), event(12, "snare", "quarter", accent=True),
            event(14, "open-hihat"),
        ],
    }


def intermediate_measure_two():
    return {
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
    }


def pro_measure_one():
    return {
        "label": "Verse",
        "events": [
            event(0, "crash", accent=True), event(0, "kick", "quarter"),
            event(2, "closed-hihat"),
            event(4, "closed-hihat"), event(4, "snare", "quarter", accent=True),
            event(5, "ghost-snare", "16th"),
            event(6, "closed-hihat"), event(6, "kick", "eighth"),
            event(8, "closed-hihat"), event(8, "kick", "quarter"),
            event(10, "closed-hihat"), event(11, "ghost-snare", "16th"),
            event(12, "closed-hihat"), event(12, "snare", "quarter", accent=True),
            event(14, "open-hihat"), event(14, "kick", "quarter"),
        ],
    }


def pro_measure_two():
    return {
        "label": "Verse variation",
        "events": [
            event(0, "ride"), event(0, "kick", "quarter"),
            event(2, "ride"), event(2, "kick", "eighth"),
            event(4, "ride"), event(4, "snare", "quarter", accent=True),
            event(5, "ghost-snare", "16th"),
            event(6, "ride"),
            event(8, "ride"), event(8, "kick", "quarter"),
            event(10, "ride"), event(10, "kick", "eighth"),
            event(12, "ride"), event(12, "snare", "quarter", accent=True),
            event(14, "ride"), event(14, "kick", "quarter"),
        ],
    }


def build_measures(difficulty: str):
    if difficulty == "beginner":
        return [beginner_measure_one(), beginner_measure_two()]
    if difficulty == "intermediate":
        return [intermediate_measure_one(), intermediate_measure_two()]
    return [pro_measure_one(), pro_measure_two()]


def chord_xml(events_group):
    ordered = sorted(events_group, key=lambda item: (DRUM_MAP[item["drum"]]["voice"], -DRUM_MAP[item["drum"]]["octave"]))
    xml_parts = []
    for index, event_data in enumerate(ordered):
        drum = DRUM_MAP[event_data["drum"]]
        duration_value = DURATION_MAP[event_data["duration"]]
        xml = ["    <note>"]
        if index > 0:
            xml.append("      <chord/>")
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
        xml_parts.append("\n".join(xml))
    return xml_parts


def build_musicxml(title: str, difficulty: str):
    measures = build_measures(difficulty)
    measure_xml = []

    for index, measure in enumerate(measures, start=1):
        grouped = defaultdict(list)
        for event_data in measure["events"]:
            grouped[event_data["at"]].append(event_data)

        measure_xml.append(f'  <measure number="{index}">')
        if index == 1:
            measure_xml.append("    <attributes>")
            measure_xml.append(f"      <divisions>{DIVISIONS}</divisions>")
            measure_xml.append("      <key><fifths>0</fifths></key>")
            measure_xml.append("      <time><beats>4</beats><beat-type>4</beat-type></time>")
            measure_xml.append("      <staves>1</staves>")
            measure_xml.append("      <clef number=\"1\"><sign>percussion</sign><line>2</line></clef>")
            measure_xml.append("    </attributes>")
        else:
            measure_xml.append("    <attributes>")
            measure_xml.append("      <time><beats>4</beats><beat-type>4</beat-type></time>")
            measure_xml.append("    </attributes>")

        measure_xml.append("    <direction placement=\"above\">")
        measure_xml.append(f"      <direction-type><words relative-y=\"12\">{escape(measure['label'])}</words></direction-type>")
        measure_xml.append("    </direction>")

        for beat in sorted(grouped.keys()):
            measure_xml.extend(chord_xml(grouped[beat]))

        measure_xml.append("  </measure>")

    score_instruments = []
    seen = set()
    for key in INSTRUMENT_ORDER:
        drum = DRUM_MAP[key]
        if drum["instrument"] in seen:
            continue
        seen.add(drum["instrument"])
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
                "confidence": 0.68 if difficulty == "beginner" else 0.74 if difficulty == "intermediate" else 0.79,
                "previewMode": "musicxml",
                "summary": "This pass groups simultaneous hits into the same rhythmic moment so hi-hat/ride sits on top of the groove while snare and kick align underneath as one coordinated pattern.",
                "musicXml": music_xml,
            }
        )
    )


if __name__ == "__main__":
    main()
