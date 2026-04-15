import json
import os
import re
import subprocess
import sys
import tempfile
import wave
from dataclasses import dataclass
from xml.sax.saxutils import escape

import numpy as np

VALID_DIFFICULTIES = {"beginner", "intermediate", "pro"}
DIVISIONS = 8
SAMPLE_RATE = 22050
FRAME_SIZE = 1024
HOP_SIZE = 256
QUANTIZATION_STEPS_PER_BAR = 32
BARS_PER_PREVIEW = 2
TOTAL_STEPS = QUANTIZATION_STEPS_PER_BAR * BARS_PER_PREVIEW

HI_HAT_SYMBOLS = {
    "hh": "+",
    "oh": "o",
}

NOTE_PRIORITY = {"cr": 0, "hh": 1, "oh": 1, "gh": 2, "sn": 3, "bd": 4}


@dataclass
class AnalysisEvent:
    time: float
    kind: str
    strength: float
    low_ratio: float
    mid_ratio: float
    high_ratio: float


def clean_title(file_path: str) -> str:
    base = os.path.basename(file_path)
    name, _ext = os.path.splitext(base)
    name = re.sub(r"^\d+-", "", name)
    name = name.replace("---", " - ")
    name = name.replace("_", " ")
    name = name.replace("-Lyrics", "")
    name = re.sub(r"\s+", " ", name).strip(" -_")
    return name or "Experimental Drum Preview"


def decode_audio_to_wav(input_path: str) -> str:
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_file.close()
    command = [
        "ffmpeg",
        "-y",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        str(SAMPLE_RATE),
        "-f",
        "wav",
        temp_file.name,
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "ffmpeg failed to decode audio")
    return temp_file.name


def load_wav_mono(path: str) -> np.ndarray:
    with wave.open(path, "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        frame_rate = wav_file.getframerate()
        frame_count = wav_file.getnframes()
        raw = wav_file.readframes(frame_count)

    if sample_width != 2:
        raise RuntimeError("Expected 16-bit PCM WAV from ffmpeg decode")
    if frame_rate != SAMPLE_RATE:
        raise RuntimeError(f"Expected sample rate {SAMPLE_RATE}, got {frame_rate}")

    audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)
    if audio.size == 0:
        raise RuntimeError("Decoded audio is empty")

    peak = float(np.max(np.abs(audio)))
    if peak > 0:
        audio = audio / peak
    return audio


def frame_audio(audio: np.ndarray, frame_size: int, hop_size: int) -> np.ndarray:
    if len(audio) < frame_size:
        padded = np.pad(audio, (0, frame_size - len(audio)))
        return padded[np.newaxis, :]

    frame_count = 1 + (len(audio) - frame_size) // hop_size
    strides = (audio.strides[0] * hop_size, audio.strides[0])
    shape = (frame_count, frame_size)
    frames = np.lib.stride_tricks.as_strided(audio, shape=shape, strides=strides)
    return np.array(frames, copy=True)


def compute_onset_envelope(audio: np.ndarray):
    frames = frame_audio(audio, FRAME_SIZE, HOP_SIZE)
    window = np.hanning(FRAME_SIZE)
    spectrum = np.abs(np.fft.rfft(frames * window, axis=1))
    freqs = np.fft.rfftfreq(FRAME_SIZE, d=1.0 / SAMPLE_RATE)

    low_band = spectrum[:, freqs < 160].sum(axis=1)
    mid_band = spectrum[:, (freqs >= 160) & (freqs < 2200)].sum(axis=1)
    high_band = spectrum[:, freqs >= 2200].sum(axis=1)
    total_energy = spectrum.sum(axis=1) + 1e-9

    weighted_flux = (
        np.maximum(0.0, np.diff(low_band, prepend=low_band[:1])) * 0.95
        + np.maximum(0.0, np.diff(mid_band, prepend=mid_band[:1])) * 1.0
        + np.maximum(0.0, np.diff(high_band, prepend=high_band[:1])) * 0.65
    )
    smoothed = np.convolve(weighted_flux, np.ones(4) / 4, mode="same")
    times = (np.arange(len(smoothed)) * HOP_SIZE) / SAMPLE_RATE
    return times, smoothed, low_band, mid_band, high_band, total_energy


def estimate_tempo(onset_envelope: np.ndarray) -> float:
    if onset_envelope.size < 8 or float(onset_envelope.max()) <= 0:
        return 120.0

    envelope = onset_envelope - float(onset_envelope.mean())
    autocorr = np.correlate(envelope, envelope, mode="full")
    autocorr = autocorr[autocorr.size // 2 :]

    min_bpm = 70.0
    max_bpm = 190.0
    min_lag = max(1, int((60.0 / max_bpm) * SAMPLE_RATE / HOP_SIZE))
    max_lag = min(len(autocorr) - 1, int((60.0 / min_bpm) * SAMPLE_RATE / HOP_SIZE))
    if max_lag <= min_lag:
        return 120.0

    lag = int(np.argmax(autocorr[min_lag : max_lag + 1]) + min_lag)
    bpm = 60.0 * SAMPLE_RATE / (lag * HOP_SIZE)
    while bpm < 80:
        bpm *= 2
    while bpm > 180:
        bpm /= 2
    return float(max(80.0, min(180.0, bpm)))


def classify_event(low_ratio: float, mid_ratio: float, high_ratio: float, strength: float) -> str | None:
    if low_ratio > 0.48 and low_ratio > high_ratio * 1.7:
        return "bd"
    if mid_ratio > 0.42 and high_ratio < 0.52:
        return "sn"
    if high_ratio > 0.44 and low_ratio < 0.22 and strength > 0.008:
        return "hh"
    if low_ratio > 0.38 and mid_ratio < 0.48:
        return "bd"
    if mid_ratio > 0.33 and high_ratio < 0.62:
        return "sn"
    if high_ratio > 0.33 and low_ratio < 0.30:
        return "hh"
    return None


def detect_events(audio: np.ndarray):
    times, onset_env, low_band, mid_band, high_band, total_energy = compute_onset_envelope(audio)
    threshold = float(np.percentile(onset_env, 88)) if onset_env.size else 0.0
    if threshold <= 0:
        threshold = float(onset_env.max()) * 0.5 if onset_env.size else 0.0

    events: list[AnalysisEvent] = []
    for i in range(1, len(onset_env) - 1):
        value = float(onset_env[i])
        if value < threshold:
            continue
        if value < onset_env[i - 1] or value < onset_env[i + 1]:
            continue

        total = float(total_energy[i]) + 1e-9
        low_ratio = float(low_band[i] / total)
        mid_ratio = float(mid_band[i] / total)
        high_ratio = float(high_band[i] / total)
        kind = classify_event(low_ratio, mid_ratio, high_ratio, value)
        if not kind:
            continue

        if events and (times[i] - events[-1].time) < 0.055:
            if value > events[-1].strength:
                events[-1] = AnalysisEvent(times[i], kind, value, low_ratio, mid_ratio, high_ratio)
            continue

        events.append(AnalysisEvent(times[i], kind, value, low_ratio, mid_ratio, high_ratio))

    return events, onset_env


def step_backbeat_bonus(step: int, kind: str) -> float:
    pos_in_bar = step % QUANTIZATION_STEPS_PER_BAR
    if kind == "sn" and pos_in_bar in {8, 24}:
        return 0.28
    if kind == "bd" and pos_in_bar in {0, 16}:
        return 0.18
    if kind == "hh" and pos_in_bar % 4 == 0:
        return 0.08
    return 0.0


def choose_preview_window(events: list[AnalysisEvent], bpm: float, audio_duration: float) -> tuple[float, float]:
    beat_duration = 60.0 / bpm
    bar_duration = beat_duration * 4.0
    phrase_duration = bar_duration * BARS_PER_PREVIEW
    step_duration = beat_duration / 8.0

    if audio_duration <= phrase_duration + 0.5:
        return 0.0, min(audio_duration, phrase_duration)

    if not events:
        return 0.0, phrase_duration

    best_start = 0.0
    best_score = -1.0
    latest_start = max(0.0, audio_duration - phrase_duration)
    cursor = 0.0
    while cursor <= latest_start:
        end = cursor + phrase_duration
        score = 0.0
        for event in events:
            if cursor <= event.time < end:
                step = int(round((event.time - cursor) / step_duration))
                step = max(0, min(TOTAL_STEPS - 1, step))
                score += event.strength
                score += step_backbeat_bonus(step, event.kind)
                if event.kind == "sn":
                    score += event.mid_ratio * 0.12
                elif event.kind == "bd":
                    score += event.low_ratio * 0.1
                elif event.kind == "hh":
                    score -= max(0.0, event.high_ratio - 0.72) * 0.05
        if score > best_score:
            best_score = score
            best_start = cursor
        cursor += beat_duration / 4.0

    return best_start, min(audio_duration, best_start + phrase_duration)


def quantize_events(events: list[AnalysisEvent], bpm: float, window_start: float):
    beat_duration = 60.0 / bpm
    step_duration = beat_duration / 8.0
    window_end = window_start + beat_duration * 8
    window_events = [event for event in events if window_start <= event.time < window_end]

    grouped: dict[int, list[AnalysisEvent]] = {}
    for event in window_events:
        step = int(round((event.time - window_start) / step_duration))
        step = max(0, min(TOTAL_STEPS - 1, step))
        grouped.setdefault(step, []).append(event)

    quantized_hits = []
    for step in sorted(grouped):
        bucket = sorted(grouped[step], key=lambda event: event.strength, reverse=True)
        per_kind: dict[str, AnalysisEvent] = {}
        for event in bucket:
            per_kind.setdefault(event.kind, event)
        for kind, event in per_kind.items():
            quantized_hits.append((kind, step, event, False, "detected"))

    quantized_hits.sort(key=lambda item: (item[1], NOTE_PRIORITY[item[0]]))
    return quantized_hits, window_end


def infer_hi_hat_pulse(quantized_hits, difficulty: str = "intermediate"):
    hat_hits = [
        (step, event)
        for kind, step, event, _accepted, source in quantized_hits
        if source == "detected" and kind == "hh" and event is not None
    ]
    if not hat_hits:
        return 4

    eighth_slots = {step for step in range(0, TOTAL_STEPS, 4)}
    sixteenth_slots = {step for step in range(0, TOTAL_STEPS, 2)}
    sixteenth_only_slots = {step for step in range(0, TOTAL_STEPS, 2) if step not in eighth_slots}

    eighth_score = 0.0
    sixteenth_score = 0.0
    sixteenth_only_score = 0.0
    sixteenth_only_hits = 0
    strongest_sixteenth_only = 0.0
    strongest_hat_strength = 0.0

    for kind, step, event, _accepted, source in quantized_hits:
        if source != "detected" or kind != "hh" or event is None:
            continue
        strength = event.strength
        strongest_hat_strength = max(strongest_hat_strength, strength)
        if step in eighth_slots:
            eighth_score += strength * 1.2
        elif min(abs(step - slot) for slot in eighth_slots) == 1:
            eighth_score += strength * 0.35
        else:
            eighth_score -= strength * 0.4

        if step in sixteenth_slots:
            sixteenth_score += strength
        elif min(abs(step - slot) for slot in sixteenth_slots) == 1:
            sixteenth_score += strength * 0.2
        else:
            sixteenth_score -= strength * 0.35

        if step in sixteenth_only_slots:
            sixteenth_only_score += strength
            sixteenth_only_hits += 1
            strongest_sixteenth_only = max(strongest_sixteenth_only, strength)

    if difficulty == "beginner":
        enough_dense_hits = sixteenth_only_hits >= 6
        enough_dense_energy = sixteenth_only_score > max(0.18, eighth_score * 0.52)
        standout_dense_hit = strongest_sixteenth_only > 0.03
        sixteenth_clearly_wins = sixteenth_score > eighth_score * 1.65
        if enough_dense_hits and enough_dense_energy and standout_dense_hit and sixteenth_clearly_wins:
            return 2
        return 4

    if difficulty == "pro":
        strong_bridge_hit = strongest_sixteenth_only >= strongest_hat_strength * 0.5 if strongest_hat_strength > 0 else False
        enough_hat_presence = len(hat_hits) >= 6
        if sixteenth_score > eighth_score * 1.28:
            return 2
        if sixteenth_only_hits >= 1 and enough_hat_presence and strong_bridge_hit:
            return 2
        return 4

    if sixteenth_score > eighth_score * 1.28:
        return 2
    return 4


def skeleton_for_difficulty(difficulty: str, hi_hat_step: int):
    hats = [step for step in range(0, TOTAL_STEPS, hi_hat_step)]
    snares = [8, 24, 40, 56]
    kicks = [0, 16, 32, 48]

    if difficulty == "intermediate":
        kicks = [0, 12, 16, 28, 32, 48]
    elif difficulty == "pro":
        kicks = [0, 12, 16, 20, 32, 44, 48, 60]

    skeleton = []
    for step in hats:
        skeleton.append(("hh", step, None, True, "skeleton"))
    for step in snares:
        skeleton.append(("sn", step, None, True, "skeleton"))
    for step in kicks:
        skeleton.append(("bd", step, None, True, "skeleton"))
    skeleton.sort(key=lambda item: (item[1], NOTE_PRIORITY[item[0]]))
    return skeleton


def best_detected_near_step(quantized_hits, kind: str, target_step: int, max_distance: int):
    best = None
    best_score = -1.0
    for hit_kind, step, event, _accepted, source in quantized_hits:
        if source != "detected" or hit_kind != kind or event is None:
            continue
        distance = abs(step - target_step)
        if distance > max_distance:
            continue
        score = event.strength - (distance * 0.12) + step_backbeat_bonus(target_step, kind)
        if score > best_score:
            best_score = score
            best = (hit_kind, target_step, event, True, "override")
    return best


def merge_with_backbone(quantized_hits, difficulty: str):
    hi_hat_step = infer_hi_hat_pulse(quantized_hits, difficulty)
    skeleton = skeleton_for_difficulty(difficulty, hi_hat_step)
    accepted = []
    used_steps = set()

    for kind, step, _event, _accepted, _source in skeleton:
        override = None
        if kind == "sn":
            override = best_detected_near_step(quantized_hits, "sn", step, 2)
        elif kind == "bd":
            override = best_detected_near_step(quantized_hits, "bd", step, 3)
        elif kind == "hh":
            override = best_detected_near_step(quantized_hits, "hh", step, 0 if hi_hat_step == 2 else 1)

        if override is not None:
            accepted.append(override)
            used_steps.add((override[0], override[1]))
        else:
            accepted.append((kind, step, None, True, "skeleton"))
            used_steps.add((kind, step))

    if difficulty in {"intermediate", "pro"}:
        extra_limits = {
            "intermediate": {"bd": 2, "hh": 1 if hi_hat_step == 4 else 2},
            "pro": {"bd": 3, "hh": 2 if hi_hat_step == 4 else 6, "sn": 1},
        }[difficulty]
        added = {"bd": 0, "sn": 0, "hh": 0}
        for hit_kind, step, event, _accepted, source in quantized_hits:
            if source != "detected" or event is None:
                continue
            if (hit_kind, step) in used_steps:
                continue
            if hit_kind not in extra_limits:
                continue
            if added[hit_kind] >= extra_limits[hit_kind]:
                continue
            pos_in_bar = step % QUANTIZATION_STEPS_PER_BAR
            if hit_kind == "hh":
                if hi_hat_step == 4 and pos_in_bar % 4 != 2:
                    continue
                if hi_hat_step == 2 and pos_in_bar % 2 != 1:
                    continue
            if hit_kind == "sn" and pos_in_bar in {8, 24}:
                continue
            accepted.append((hit_kind, step, event, True, "detected"))
            added[hit_kind] += 1
            used_steps.add((hit_kind, step))

    accepted.sort(key=lambda item: (item[1], NOTE_PRIORITY[item[0]]))
    return accepted, hi_hat_step


def events_to_phrase(accepted_events, difficulty: str):
    phrase = [[], []]
    hi_hat_open_steps = set()

    if difficulty != "beginner":
        for kind, step, event, _accepted, source in accepted_events:
            if kind != "hh" or event is None or source == "skeleton":
                continue
            if event.high_ratio > 0.58 and event.low_ratio < 0.16:
                hi_hat_open_steps.add(step)

    for kind, step, event, _accepted, _source in accepted_events:
        measure_index = min(1, step // QUANTIZATION_STEPS_PER_BAR)
        measure_step = step % QUANTIZATION_STEPS_PER_BAR
        mapped_kind = kind
        if kind == "hh" and step in hi_hat_open_steps:
            mapped_kind = "oh"
        phrase[measure_index].append((mapped_kind, measure_step))

    if difficulty == "intermediate" and phrase[0] and not any(kind == "cr" and step == 0 for kind, step in phrase[0]):
        phrase[0].append(("cr", 0))
        phrase[0].sort(key=lambda item: (item[1], NOTE_PRIORITY[item[0]]))

    if difficulty == "pro" and phrase[1] and not any(kind == "cr" for kind, _step in phrase[1]):
        phrase[1].append(("cr", 30))
        phrase[1].sort(key=lambda item: (item[1], NOTE_PRIORITY[item[0]]))

    return phrase


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


def note_xml(kind: str, duration: int = 2, note_type: str = "16th", voice: int = 1, chord: bool = False) -> str:
    if kind == "hh":
        step, octave, inst, notehead, stem = "G", 5, "P1-I43", "x", "up"
        extra = ""
    elif kind == "oh":
        step, octave, inst, notehead, stem = "G", 5, "P1-I43", "x", "up"
        extra = ""
    elif kind == "cr":
        step, octave, inst, notehead, stem = "A", 5, "P1-I49", "x", "up"
        extra = "      <notations><articulations><accent/></articulations></notations>\n"
    elif kind == "sn":
        step, octave, inst, notehead, stem = "C", 5, "P1-I39", None, "up"
        extra = ""
    elif kind == "gh":
        step, octave, inst, notehead, stem = "C", 5, "P1-I39", None, "up"
        extra = "      <notehead parentheses=\"yes\">normal</notehead>\n"
    elif kind == "bd":
        step, octave, inst, notehead, stem = "F", 4, "P1-I36", None, "down"
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
        f"      <voice>{voice}</voice>",
        f"      <type>{note_type}</type>",
    ])
    if notehead:
        parts.append(f"      <notehead>{notehead}</notehead>")
    parts.append(f"      <stem>{stem}</stem>")
    parts.append("      <staff>1</staff>")
    if extra:
        parts.append(extra.rstrip("\n"))
    parts.append("    </note>")
    return "\n".join(parts)


def rest_xml(duration: int = 2, note_type: str = "16th", voice: int = 1) -> str:
    return "\n".join([
        "    <note>",
        "      <rest/>",
        f"      <duration>{duration}</duration>",
        f"      <voice>{voice}</voice>",
        f"      <type>{note_type}</type>",
        "      <staff>1</staff>",
        "    </note>",
    ])


def backup_xml(duration: int) -> str:
    return "\n".join([
        "    <backup>",
        f"      <duration>{duration}</duration>",
        "    </backup>",
    ])


def measure_xml(measure_number: int, events, include_attributes: bool = False, is_last: bool = False) -> str:
    grouped = {}
    for kind, pos in events:
        grouped.setdefault(pos, []).append(kind)

    body = []
    if include_attributes:
        body.extend([
            "      <attributes>",
            f"        <divisions>{DIVISIONS}</divisions>",
            "        <key><fifths>0</fifths></key>",
            "        <time><beats>4</beats><beat-type>4</beat-type></time>",
            "        <staves>1</staves>",
            "        <clef number=\"1\"><sign>percussion</sign><line>2</line></clef>",
            "      </attributes>",
        ])

    voice1_map = {}
    voice2_map = {}
    for step in range(QUANTIZATION_STEPS_PER_BAR):
        kinds = sorted(grouped.get(step, []), key=lambda k: NOTE_PRIORITY[k])
        voice1_map[step] = [kind for kind in kinds if kind != "bd"]
        voice2_map[step] = [kind for kind in kinds if kind == "bd"]

    for step in range(QUANTIZATION_STEPS_PER_BAR):
        kinds = voice1_map[step]
        hi_hat_kind = next((kind for kind in kinds if kind in HI_HAT_SYMBOLS), None)
        if hi_hat_kind:
            body.append(hi_hat_direction_xml(hi_hat_kind))

        if not kinds:
            body.append(rest_xml(voice=1))
            continue

        for index, kind in enumerate(kinds):
            body.append(note_xml(kind, voice=1, chord=index > 0))

    body.append(backup_xml(QUANTIZATION_STEPS_PER_BAR * 2))

    for step in range(QUANTIZATION_STEPS_PER_BAR):
        kinds = voice2_map[step]
        if not kinds:
            body.append(rest_xml(voice=2))
            continue
        for index, kind in enumerate(kinds):
            body.append(note_xml(kind, voice=2, chord=index > 0))

    barline = "      <barline location=\"right\"><bar-style>light-heavy</bar-style></barline>" if is_last else ""
    if barline:
        body.append(barline)

    joined = "\n".join(body)
    return f'''    <measure number="{measure_number}">
{joined}
    </measure>'''


def build_musicxml(score_title: str, phrase) -> str:
    measures_xml = [
        measure_xml(index + 1, events, include_attributes=index == 0, is_last=index == len(phrase) - 1)
        for index, events in enumerate(phrase)
    ]

    return f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE score-partwise PUBLIC
  "-//Recordare//DTD MusicXML 3.1 Partwise//EN"
  "http://www.musicxml.org/dtds/partwise.dtd">
<score-partwise version="3.1">
  <work>
    <work-title>{escape(score_title)}</work-title>
  </work>
  <identification>
    <creator type="arranger">Drumsheet AI backbone reconstruction</creator>
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
{chr(10).join(measures_xml)}
  </part>
</score-partwise>
'''


def summarize_result(difficulty: str, bpm: float, phrase, analysis_count: int, window_start: float, hi_hat_step: int) -> str:
    visible_counts = {"bd": 0, "sn": 0, "hh": 0, "oh": 0, "cr": 0}
    for measure in phrase:
        for kind, _step in measure:
            visible_counts[kind] = visible_counts.get(kind, 0) + 1

    difficulty_text = {
        "beginner": "Beginner view keeps a clean pop/rock backbone first.",
        "intermediate": "Intermediate view keeps the backbone and allows a bit more real variation.",
        "pro": "Pro view preserves the backbone while letting in more detected syncopation.",
    }[difficulty]

    pulse_text = "16th" if hi_hat_step == 2 else "8th"
    return (
        f"Backbone-reconstructed 2-bar preview at about {round(bpm)} BPM from {analysis_count} detected hits. "
        f"Window starts at {window_start:.2f}s. Inferred hi-hat pulse: {pulse_text}. Visible events: kick {visible_counts.get('bd', 0)}, "
        f"snare {visible_counts.get('sn', 0)}, hi-hat {visible_counts.get('hh', 0) + visible_counts.get('oh', 0)}. {difficulty_text}"
    )


def build_debug_grid() -> list[str]:
    grid = []
    for step in range(TOTAL_STEPS):
        pos_in_bar = step % QUANTIZATION_STEPS_PER_BAR
        if pos_in_bar in {0, 8, 16, 24}:
            grid.append("|")
        elif pos_in_bar % 4 == 0:
            grid.append(":")
        else:
            grid.append(".")
    return grid


def serialize_hit(kind: str, step: int, event: AnalysisEvent | None, accepted: bool, source: str):
    return {
        "step": step,
        "kind": kind,
        "strength": round(float(event.strength), 6) if event is not None else 0.0,
        "time": round(float(event.time), 4) if event is not None else 0.0,
        "lowRatio": round(float(event.low_ratio), 4) if event is not None else 0.0,
        "midRatio": round(float(event.mid_ratio), 4) if event is not None else 0.0,
        "highRatio": round(float(event.high_ratio), 4) if event is not None else 0.0,
        "accepted": accepted,
        "source": source,
    }


def analyze_file(file_path: str, difficulty: str):
    wav_path = decode_audio_to_wav(file_path)
    try:
        audio = load_wav_mono(wav_path)
        onset_env = compute_onset_envelope(audio)[1]
        bpm = estimate_tempo(onset_env)
        detected_events, _ = detect_events(audio)
        audio_duration = len(audio) / SAMPLE_RATE
        window_start, window_end = choose_preview_window(detected_events, bpm, audio_duration)
        quantized_hits, quantized_window_end = quantize_events(detected_events, bpm, window_start)
        accepted_events, hi_hat_step = merge_with_backbone(quantized_hits, difficulty)
        phrase = events_to_phrase(accepted_events, difficulty)
        debug = {
            "bpm": round(bpm, 2),
            "windowStart": round(window_start, 3),
            "windowEnd": round(min(window_end, quantized_window_end), 3),
            "rawDetectedCount": len(detected_events),
            "quantizedDetectedCount": len(quantized_hits),
            "acceptedCount": len(accepted_events),
            "grid": build_debug_grid(),
            "hiHatPulse": "16th" if hi_hat_step == 2 else "8th",
            "quantizedHits": [serialize_hit(kind, step, event, accepted, source) for kind, step, event, accepted, source in quantized_hits],
            "acceptedHits": [serialize_hit(kind, step, event, accepted, source) for kind, step, event, accepted, source in accepted_events],
        }
        return bpm, detected_events, phrase, debug, window_start, hi_hat_step
    finally:
        if os.path.exists(wav_path):
            os.unlink(wav_path)


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

    try:
        bpm, detected_events, phrase, debug, window_start, hi_hat_step = analyze_file(file_path, difficulty)
        music_xml = build_musicxml(clean_score_title, phrase)
        summary = summarize_result(difficulty, bpm, phrase, len(detected_events), window_start, hi_hat_step)
    except Exception as error:
        print(json.dumps({"error": f"Audio analysis failed: {error}"}))
        sys.exit(1)

    print(json.dumps({
        "title": f"Backbone transcription for {clean_score_title}",
        "difficulty": difficulty,
        "confidence": 0.72,
        "previewMode": "musicxml",
        "summary": summary,
        "musicXml": music_xml,
        "debug": debug,
    }))


if __name__ == "__main__":
    main()
