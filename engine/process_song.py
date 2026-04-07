import json
import os
import sys
from xml.sax.saxutils import escape

VALID_DIFFICULTIES = {"beginner", "intermediate", "pro"}


def build_measures(difficulty: str):
    if difficulty == "beginner":
        return [
            [
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 2, "type": "quarter", "instrument": "P1-I39", "display_step": "C", "display_octave": 5},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 2, "type": "quarter", "instrument": "P1-I39", "display_step": "C", "display_octave": 5},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
            ],
            [
                {"voice": 1, "type": "eighth", "instrument": "P1-I49", "display_step": "A", "display_octave": 5, "notehead": "x", "accent": True},
                {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 2, "type": "quarter", "instrument": "P1-I39", "display_step": "C", "display_octave": 5},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 2, "type": "quarter", "instrument": "P1-I39", "display_step": "C", "display_octave": 5},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
            ],
        ]

    if difficulty == "intermediate":
        return [
            [
                {"voice": 1, "type": "eighth", "instrument": "P1-I49", "display_step": "A", "display_octave": 5, "notehead": "x", "accent": True},
                {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 2, "type": "quarter", "instrument": "P1-I39", "display_step": "C", "display_octave": 5, "accent": True},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x", "ghost": True},
                {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
                {"voice": 2, "type": "quarter", "instrument": "P1-I39", "display_step": "C", "display_octave": 5, "accent": True},
                {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
            ],
            [
                {"voice": 1, "type": "eighth", "instrument": "P1-I51", "display_step": "A", "display_octave": 5, "notehead": "x"},
                {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
                {"voice": 1, "type": "eighth", "instrument": "P1-I51", "display_step": "A", "display_octave": 5, "notehead": "x"},
                {"voice": 1, "type": "eighth", "instrument": "P1-I51", "display_step": "A", "display_octave": 5, "notehead": "x"},
                {"voice": 2, "type": "quarter", "instrument": "P1-I39", "display_step": "C", "display_octave": 5, "accent": True},
                {"voice": 1, "type": "eighth", "instrument": "P1-I51", "display_step": "A", "display_octave": 5, "notehead": "x"},
                {"voice": 1, "type": "eighth", "instrument": "P1-I51", "display_step": "A", "display_octave": 5, "notehead": "x"},
                {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
                {"voice": 1, "type": "eighth", "instrument": "P1-I51", "display_step": "A", "display_octave": 5, "notehead": "x"},
                {"voice": 1, "type": "eighth", "instrument": "P1-I48", "display_step": "E", "display_octave": 5},
                {"voice": 1, "type": "eighth", "instrument": "P1-I45", "display_step": "D", "display_octave": 5},
                {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
            ],
        ]

    return [
        [
            {"voice": 1, "type": "eighth", "instrument": "P1-I49", "display_step": "A", "display_octave": 5, "notehead": "x", "accent": True},
            {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
            {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
            {"voice": 1, "type": "16th", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
            {"voice": 1, "type": "16th", "instrument": "P1-I39", "display_step": "C", "display_octave": 5, "ghost": True},
            {"voice": 2, "type": "quarter", "instrument": "P1-I39", "display_step": "C", "display_octave": 5, "accent": True},
            {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
            {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
            {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
            {"voice": 1, "type": "eighth", "instrument": "P1-I43", "display_step": "G", "display_octave": 5, "notehead": "x"},
            {"voice": 1, "type": "16th", "instrument": "P1-I48", "display_step": "E", "display_octave": 5},
            {"voice": 1, "type": "16th", "instrument": "P1-I45", "display_step": "D", "display_octave": 5},
            {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
        ],
        [
            {"voice": 1, "type": "eighth", "instrument": "P1-I51", "display_step": "A", "display_octave": 5, "notehead": "x"},
            {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
            {"voice": 1, "type": "eighth", "instrument": "P1-I51", "display_step": "A", "display_octave": 5, "notehead": "x"},
            {"voice": 1, "type": "16th", "instrument": "P1-I51", "display_step": "A", "display_octave": 5, "notehead": "x"},
            {"voice": 1, "type": "16th", "instrument": "P1-I39", "display_step": "C", "display_octave": 5, "ghost": True},
            {"voice": 2, "type": "quarter", "instrument": "P1-I39", "display_step": "C", "display_octave": 5, "accent": True},
            {"voice": 1, "type": "eighth", "instrument": "P1-I51", "display_step": "A", "display_octave": 5, "notehead": "x"},
            {"voice": 1, "type": "eighth", "instrument": "P1-I51", "display_step": "A", "display_octave": 5, "notehead": "x"},
            {"voice": 2, "type": "quarter", "instrument": "P1-I36", "display_step": "F", "display_octave": 4},
            {"voice": 1, "type": "16th", "instrument": "P1-I48", "display_step": "E", "display_octave": 5},
            {"voice": 1, "type": "16th", "instrument": "P1-I47", "display_step": "C", "display_octave": 5},
            {"voice": 1, "type": "16th", "instrument": "P1-I45", "display_step": "D", "display_octave": 5},
            {"voice": 1, "type": "16th", "instrument": "P1-I41", "display_step": "A", "display_octave": 4},
        ],
    ]


def note_xml(note):
    duration_map = {"16th": 1, "eighth": 2, "quarter": 4}
    duration_value = duration_map[note["type"]]
    xml = ["    <note>"]
    xml.append("      <unpitched>")
    xml.append(f"        <display-step>{note['display_step']}</display-step>")
    xml.append(f"        <display-octave>{note['display_octave']}</display-octave>")
    xml.append("      </unpitched>")
    xml.append(f"      <duration>{duration_value}</duration>")
    xml.append(f"      <instrument id=\"{note['instrument']}\"/>")
    xml.append(f"      <voice>{note['voice']}</voice>")
    xml.append("      <type>{}</type>".format(note["type"]))
    if note.get("notehead"):
        xml.append(f"      <notehead>{note['notehead']}</notehead>")
    xml.append("      <stem>up</stem>")
    if note.get("accent") or note.get("ghost"):
        xml.append("      <notations>")
        xml.append("        <articulations>")
        if note.get("accent"):
            xml.append("          <accent/>")
        xml.append("        </articulations>")
        if note.get("ghost"):
            xml.append("        <ornaments>")
            xml.append("          <other-ornament>ghost</other-ornament>")
            xml.append("        </ornaments>")
        xml.append("      </notations>")
    xml.append("    </note>")
    return "\n".join(xml)


def build_musicxml(title: str, difficulty: str):
    measures = build_measures(difficulty)
    measure_xml = []

    for index, notes in enumerate(measures, start=1):
        measure_xml.append(f'  <measure number="{index}">')
        if index == 1:
            measure_xml.append("    <attributes>")
            measure_xml.append("      <divisions>4</divisions>")
            measure_xml.append("      <key><fifths>0</fifths></key>")
            measure_xml.append("      <time><beats>4</beats><beat-type>4</beat-type></time>")
            measure_xml.append("      <staves>1</staves>")
            measure_xml.append("      <clef number=\"1\"><sign>percussion</sign><line>2</line></clef>")
            measure_xml.append("    </attributes>")
            measure_xml.append("    <direction placement=\"above\">")
            measure_xml.append("      <direction-type><words relative-y=\"12\">Intro</words></direction-type>")
            measure_xml.append("    </direction>")
        if index == 2:
            measure_xml.append("    <direction placement=\"above\">")
            measure_xml.append("      <direction-type><words relative-y=\"12\">Fill / transition</words></direction-type>")
            measure_xml.append("    </direction>")

        for note in notes:
            measure_xml.append(note_xml(note))

        measure_xml.append("  </measure>")

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
      <score-instrument id="P1-I36"><instrument-name>Bass Drum</instrument-name></score-instrument>
      <score-instrument id="P1-I39"><instrument-name>Snare Drum</instrument-name></score-instrument>
      <score-instrument id="P1-I41"><instrument-name>Floor Tom</instrument-name></score-instrument>
      <score-instrument id="P1-I43"><instrument-name>Closed Hi-Hat</instrument-name></score-instrument>
      <score-instrument id="P1-I45"><instrument-name>Low Tom</instrument-name></score-instrument>
      <score-instrument id="P1-I47"><instrument-name>Mid Tom</instrument-name></score-instrument>
      <score-instrument id="P1-I48"><instrument-name>High Tom</instrument-name></score-instrument>
      <score-instrument id="P1-I49"><instrument-name>Crash Cymbal</instrument-name></score-instrument>
      <score-instrument id="P1-I51"><instrument-name>Ride Cymbal</instrument-name></score-instrument>
      <midi-device id="P1-I36" port="1"></midi-device>
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
                "confidence": 0.62 if difficulty == "beginner" else 0.68 if difficulty == "intermediate" else 0.71,
                "previewMode": "musicxml",
                "summary": "This preview is now driven by MusicXML-style score data so spacing, noteheads, and engraving can move toward real notation rules instead of hand-drawn SVG sketches.",
                "musicXml": music_xml,
            }
        )
    )


if __name__ == "__main__":
    main()
