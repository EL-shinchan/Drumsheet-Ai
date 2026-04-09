import json
import os
import re
import sys
from xml.sax.saxutils import escape

VALID_DIFFICULTIES = {"beginner", "intermediate", "pro"}
DIVISIONS = 8


HI_HAT_SYMBOLS = {
    "hh": "+",
    "oh": "o",
}


def clean_title(file_path: str) -> str:
    base = os.path.basename(file_path)
    name, _ext = os.path.splitext(base)
    name = re.sub(r"^\d+-", "", name)
    name = name.replace("---", " - ")
    name = name.replace("_", " ")
    name = name.replace("-Lyrics", "")
    name = re.sub(r"\s+", " ", name).strip(" -_")
    return name or "Experimental Drum Preview"


def groove_for_difficulty(difficulty: str):
    if difficulty == "beginner":
        return [
            ("hh", 0), ("bd", 0),
            ("hh", 4),
            ("hh", 8), ("sn", 8),
            ("hh", 12),
            ("hh", 16), ("bd", 16),
            ("hh", 20),
            ("hh", 24), ("sn", 24),
            ("hh", 28),
        ]
    if difficulty == "intermediate":
        return [
            ("cr", 0), ("bd", 0),
            ("hh", 4),
            ("hh", 8), ("sn", 8),
            ("hh", 10),
            ("hh", 12), ("bd", 12),
            ("hh", 16), ("bd", 16),
            ("hh", 20),
            ("hh", 24), ("sn", 24),
            ("oh", 28), ("bd", 28),
        ]
    return [
        ("cr", 0), ("bd", 0),
        ("hh", 2),
        ("hh", 4),
        ("gh", 6),
        ("hh", 8), ("sn", 8),
        ("hh", 10),
        ("hh", 12), ("bd", 12),
        ("hh", 14),
        ("hh", 16), ("bd", 16),
        ("gh", 18),
        ("hh", 20), ("bd", 20),
        ("hh", 22),
        ("hh", 24), ("sn", 24),
        ("oh", 28), ("bd", 28),
        ("hh", 30),
    ]


def hi_hat_direction_xml(kind: str) -> str:
    symbol = HI_HAT_SYMBOLS.get(kind)
    if not symbol:
        return ""

    return f'''    <direction placement="above">
      <direction-type>
        <words relative-y="18" font-size="12" font-weight="bold">{symbol}</words>
      </direction-type>
      <staff>1</staff>
    </direction>'''


def note_xml(kind: str, chord: bool = False) -> str:
    if kind == "hh":
        step, octave, inst, typ, notehead, stem, duration = "G", 5, "P1-I43", "eighth", "x", "up", 4
        extra = ""
    elif kind == "oh":
        step, octave, inst, typ, notehead, stem, duration = "G", 5, "P1-I43", "eighth", "x", "up", 4
        extra = ""
    elif kind == "cr":
        step, octave, inst, typ, notehead, stem, duration = "A", 5, "P1-I49", "eighth", "x", "up", 4
        extra = "      <notations><articulations><accent/></articulations></notations>\n"
    elif kind == "sn":
        step, octave, inst, typ, notehead, stem, duration = "C", 5, "P1-I39", "quarter", None, "up", 8
        extra = ""
    elif kind == "gh":
        step, octave, inst, typ, notehead, stem, duration = "C", 5, "P1-I39", "16th", None, "up", 2
        extra = "      <notehead parentheses=\"yes\">normal</notehead>\n"
    elif kind == "bd":
        step, octave, inst, typ, notehead, stem, duration = "F", 4, "P1-I36", "quarter", None, "down", 8
        extra = ""
    else:
        raise ValueError(kind)

    parts = ["    <note>"]
    if chord:
        parts.append("      <chord/>")
    parts.extend([
        "      <unpitched>",
        f"        <display-step>{step}</display-step>",
        f"        <display-octave>{octave}</display-octave>",
        "      </unpitched>",
        f"      <duration>{duration}</duration>",
        f"      <instrument id=\"{inst}\"/>",
        f"      <voice>{'2' if kind == 'bd' else '1'}</voice>",
        f"      <type>{typ}</type>",
    ])
    if notehead:
        parts.append(f"      <notehead>{notehead}</notehead>")
    parts.append(f"      <stem>{stem}</stem>")
    parts.append("      <staff>1</staff>")
    if extra:
        parts.append(extra.rstrip("\n"))
    parts.append("    </note>")
    return "\n".join(parts)


def build_musicxml(score_title: str, difficulty: str) -> str:
    events = groove_for_difficulty(difficulty)
    grouped = {}
    for kind, pos in events:
        grouped.setdefault(pos, []).append(kind)

    notes_xml = []
    for pos in sorted(grouped):
        kinds = grouped[pos]
        hi_hat_kind = next((kind for kind in kinds if kind in HI_HAT_SYMBOLS), None)
        if hi_hat_kind:
            notes_xml.append(hi_hat_direction_xml(hi_hat_kind))

        order = sorted(kinds, key=lambda k: (k == "bd", {"cr": 0, "hh": 1, "oh": 1, "gh": 2, "sn": 3, "bd": 4}[k]))
        for i, kind in enumerate(order):
            notes_xml.append(note_xml(kind, chord=i > 0))

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE score-partwise PUBLIC
  "-//Recordare//DTD MusicXML 3.1 Partwise//EN"
  "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <work>
    <work-title>{escape(score_title)}</work-title>
  </work>
  <identification>
    <creator type="arranger">Drumsheet AI notation baseline</creator>
  </identification>
  <part-list>
    <score-part id="P1">
      <part-name>Drumset</part-name>
      <score-instrument id="P1-I36"><instrument-name>Bass Drum</instrument-name></score-instrument>
      <score-instrument id="P1-I39"><instrument-name>Snare Drum</instrument-name></score-instrument>
      <score-instrument id="P1-I43"><instrument-name>Closed Hi-Hat</instrument-name></score-instrument>
      <score-instrument id="P1-I49"><instrument-name>Crash Cymbal</instrument-name></score-instrument>
    </score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>{DIVISIONS}</divisions>
        <key><fifths>0</fifths></key>
        <time><beats>4</beats><beat-type>4</beat-type></time>
        <staves>1</staves>
        <clef number="1"><sign>percussion</sign><line>2</line></clef>
      </attributes>
{chr(10).join(notes_xml)}
      <barline location="right"><bar-style>light-heavy</bar-style></barline>
    </measure>
  </part>
</score-partwise>
'''


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: process_song.py <file_path> <difficulty>"}))
        sys.exit(1)

    file_path = sys.argv[1]
    difficulty = sys.argv[2].lower()
    if difficulty not in VALID_DIFFICULTIES:
        print(json.dumps({"error": "Invalid difficulty"}))
        sys.exit(1)

    clean_score_title = clean_title(file_path)
    music_xml = build_musicxml(clean_score_title, difficulty)
    summary = {
        "beginner": "Beginner: straight eighth-note hats with kick on 1 and 3, snare on 2 and 4, and a stable no-surprises groove.",
        "intermediate": "Intermediate: keeps the same core backbeat but adds a crash entry, extra kick push, tighter hat motion, and an open-hat release.",
        "pro": "Pro: much denser one-bar groove with offbeat hats, ghost-note color, added kick syncopation, crash entry, and an open-hat exit while preserving the same core placement.",
    }[difficulty]

    print(json.dumps({
        "title": f"Notation baseline for {clean_score_title}",
        "difficulty": difficulty,
        "confidence": 0.9,
        "previewMode": "musicxml",
        "summary": summary,
        "musicXml": music_xml,
    }))


if __name__ == "__main__":
    main()
