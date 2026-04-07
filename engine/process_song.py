import json
import os
import re
import sys
from xml.sax.saxutils import escape

VALID_DIFFICULTIES = {"beginner", "intermediate", "pro"}
DIVISIONS = 8


def clean_title(file_path: str) -> str:
    base = os.path.basename(file_path)
    name, _ext = os.path.splitext(base)
    name = re.sub(r"^\d+-", "", name)
    name = name.replace("---", " - ")
    name = name.replace("_", " ")
    name = name.replace("-Lyrics", "")
    name = re.sub(r"\s+", " ", name).strip(" -_")
    return name or "Experimental Drum Preview"


def build_musicxml(score_title: str) -> str:
    # Reset pass: one single reference-style rock groove bar.
    # Goal: lock placement before adding complexity again.
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE score-partwise PUBLIC
  "-//Recordare//DTD MusicXML 3.1 Partwise//EN"
  "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <work>
    <work-title>{escape(score_title)}</work-title>
  </work>
  <identification>
    <creator type="arranger">Drumsheet AI notation reset baseline</creator>
  </identification>
  <part-list>
    <score-part id="P1">
      <part-name>Drumset</part-name>
      <score-instrument id="P1-I36"><instrument-name>Bass Drum</instrument-name></score-instrument>
      <score-instrument id="P1-I39"><instrument-name>Snare Drum</instrument-name></score-instrument>
      <score-instrument id="P1-I43"><instrument-name>Closed Hi-Hat</instrument-name></score-instrument>
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

      <note>
        <unpitched>
          <display-step>G</display-step>
          <display-octave>5</display-octave>
        </unpitched>
        <duration>4</duration>
        <instrument id="P1-I43"/>
        <voice>1</voice>
        <type>eighth</type>
        <notehead>x</notehead>
        <stem>up</stem>
        <staff>1</staff>
      </note>
      <note>
        <chord/>
        <unpitched>
          <display-step>F</display-step>
          <display-octave>4</display-octave>
        </unpitched>
        <duration>8</duration>
        <instrument id="P1-I36"/>
        <voice>2</voice>
        <type>quarter</type>
        <stem>down</stem>
        <staff>1</staff>
      </note>

      <note>
        <unpitched>
          <display-step>G</display-step>
          <display-octave>5</display-octave>
        </unpitched>
        <duration>4</duration>
        <instrument id="P1-I43"/>
        <voice>1</voice>
        <type>eighth</type>
        <notehead>x</notehead>
        <stem>up</stem>
        <staff>1</staff>
      </note>

      <note>
        <unpitched>
          <display-step>G</display-step>
          <display-octave>5</display-octave>
        </unpitched>
        <duration>4</duration>
        <instrument id="P1-I43"/>
        <voice>1</voice>
        <type>eighth</type>
        <notehead>x</notehead>
        <stem>up</stem>
        <staff>1</staff>
      </note>
      <note>
        <chord/>
        <unpitched>
          <display-step>C</display-step>
          <display-octave>5</display-octave>
        </unpitched>
        <duration>8</duration>
        <instrument id="P1-I39"/>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <staff>1</staff>
      </note>

      <note>
        <unpitched>
          <display-step>G</display-step>
          <display-octave>5</display-octave>
        </unpitched>
        <duration>4</duration>
        <instrument id="P1-I43"/>
        <voice>1</voice>
        <type>eighth</type>
        <notehead>x</notehead>
        <stem>up</stem>
        <staff>1</staff>
      </note>

      <note>
        <unpitched>
          <display-step>G</display-step>
          <display-octave>5</display-octave>
        </unpitched>
        <duration>4</duration>
        <instrument id="P1-I43"/>
        <voice>1</voice>
        <type>eighth</type>
        <notehead>x</notehead>
        <stem>up</stem>
        <staff>1</staff>
      </note>
      <note>
        <chord/>
        <unpitched>
          <display-step>F</display-step>
          <display-octave>4</display-octave>
        </unpitched>
        <duration>8</duration>
        <instrument id="P1-I36"/>
        <voice>2</voice>
        <type>quarter</type>
        <stem>down</stem>
        <staff>1</staff>
      </note>

      <note>
        <unpitched>
          <display-step>G</display-step>
          <display-octave>5</display-octave>
        </unpitched>
        <duration>4</duration>
        <instrument id="P1-I43"/>
        <voice>1</voice>
        <type>eighth</type>
        <notehead>x</notehead>
        <stem>up</stem>
        <staff>1</staff>
      </note>

      <note>
        <unpitched>
          <display-step>G</display-step>
          <display-octave>5</display-octave>
        </unpitched>
        <duration>4</duration>
        <instrument id="P1-I43"/>
        <voice>1</voice>
        <type>eighth</type>
        <notehead>x</notehead>
        <stem>up</stem>
        <staff>1</staff>
      </note>
      <note>
        <chord/>
        <unpitched>
          <display-step>C</display-step>
          <display-octave>5</display-octave>
        </unpitched>
        <duration>8</duration>
        <instrument id="P1-I39"/>
        <voice>1</voice>
        <type>quarter</type>
        <stem>up</stem>
        <staff>1</staff>
      </note>

      <note>
        <unpitched>
          <display-step>G</display-step>
          <display-octave>5</display-octave>
        </unpitched>
        <duration>4</duration>
        <instrument id="P1-I43"/>
        <voice>1</voice>
        <type>eighth</type>
        <notehead>x</notehead>
        <stem>up</stem>
        <staff>1</staff>
      </note>

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
    music_xml = build_musicxml(clean_score_title)

    print(
        json.dumps(
            {
                "title": f"Notation reset baseline for {clean_score_title}",
                "difficulty": difficulty,
                "confidence": 0.9,
                "previewMode": "musicxml",
                "summary": "Reset pass: one single 4/4 rock groove bar only. No extra sections, fills, or clutter. The goal is to lock hi-hat/snare/kick placement before rebuilding complexity.",
                "musicXml": music_xml,
            }
        )
    )


if __name__ == "__main__":
    main()
