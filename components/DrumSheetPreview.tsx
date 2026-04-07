import type { DrumMeasure, DrumNote, DrumPitch, GenerationResult } from "@/lib/types";

type DrumSheetPreviewProps = {
  result: GenerationResult | null;
};

const STAFF_LINES = [24, 38, 52, 66, 80];
const STAFF_TOP = STAFF_LINES[0];
const STAFF_BOTTOM = STAFF_LINES[STAFF_LINES.length - 1];
const STAFF_HEIGHT = 104;
const MEASURE_WIDTH = 250;
const LEFT_PAD = 48;

const PITCH_Y: Record<DrumPitch, number> = {
  "closed-hihat": 16,
  crash: 10,
  ride: 18,
  snare: 52,
  "high-tom": 38,
  "floor-tom": 72,
  kick: 90,
};

function beatToX(beat: number) {
  const normalized = (beat - 1) / 4;
  return 18 + normalized * (MEASURE_WIDTH - 36);
}

function noteGlyph(note: DrumNote, index: number) {
  const x = beatToX(note.beat);
  const y = PITCH_Y[note.pitch];
  const isCymbal = note.pitch === "closed-hihat" || note.pitch === "crash" || note.pitch === "ride";
  const stemTop = y - 26;

  return (
    <g key={`${note.pitch}-${note.beat}-${index}`}>
      {note.accent ? (
        <path d={`M ${x - 8} ${y - 30} L ${x} ${y - 36} L ${x + 8} ${y - 30}`} stroke="#f8fafc" strokeWidth="1.5" fill="none" />
      ) : null}

      {isCymbal ? (
        <g stroke="#f8fafc" strokeWidth="1.6">
          <line x1={x - 6} y1={y - 6} x2={x + 6} y2={y + 6} />
          <line x1={x - 6} y1={y + 6} x2={x + 6} y2={y - 6} />
        </g>
      ) : (
        <ellipse cx={x} cy={y} rx={7} ry={5.2} fill="#f8fafc" />
      )}

      <line x1={x + 7} y1={y} x2={x + 7} y2={stemTop} stroke="#f8fafc" strokeWidth="1.5" />

      {note.duration !== "quarter" ? (
        <path
          d={`M ${x + 7} ${stemTop} C ${x + 22} ${stemTop + 2}, ${x + 22} ${stemTop + 10}, ${x + 8} ${stemTop + 12}`}
          stroke="#f8fafc"
          strokeWidth="1.5"
          fill="none"
        />
      ) : null}
    </g>
  );
}

function MeasureSvg({ measure, index, timeSignature }: { measure: DrumMeasure; index: number; timeSignature?: string }) {
  return (
    <svg
      viewBox={`0 0 ${MEASURE_WIDTH} ${STAFF_HEIGHT}`}
      className="h-auto w-full rounded-xl border border-slate-800 bg-slate-950"
    >
      <rect width={MEASURE_WIDTH} height={STAFF_HEIGHT} fill="#020617" rx="12" />

      {STAFF_LINES.map((lineY) => (
        <line
          key={lineY}
          x1={LEFT_PAD}
          y1={lineY}
          x2={MEASURE_WIDTH - 16}
          y2={lineY}
          stroke="#475569"
          strokeWidth="1.2"
        />
      ))}

      <line x1={LEFT_PAD} y1={STAFF_TOP} x2={LEFT_PAD} y2={STAFF_BOTTOM} stroke="#94a3b8" strokeWidth="1.5" />
      <line x1={MEASURE_WIDTH - 16} y1={STAFF_TOP} x2={MEASURE_WIDTH - 16} y2={STAFF_BOTTOM} stroke="#94a3b8" strokeWidth="1.5" />

      {index === 0 ? (
        <text x={16} y={44} fill="#e2e8f0" fontSize="22" fontFamily="serif">
          𝄽
        </text>
      ) : null}

      {index === 0 && timeSignature ? (
        <g fill="#e2e8f0" fontSize="15" fontFamily="ui-sans-serif, system-ui, sans-serif" fontWeight="700">
          <text x={28} y={40}>{timeSignature.split("/")[0]}</text>
          <text x={28} y={60}>{timeSignature.split("/")[1]}</text>
        </g>
      ) : null}

      {measure.notes.map((note, noteIndex) => noteGlyph(note, noteIndex))}
    </svg>
  );
}

export default function DrumSheetPreview({ result }: DrumSheetPreviewProps) {
  if (!result) return null;

  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <div className="mb-5">
        <h2 className="text-2xl font-bold text-slate-100">{result.title}</h2>
        <p className="mt-2 text-sm text-slate-300">
          Difficulty: <strong className="capitalize">{result.difficulty}</strong> · Confidence: <strong>{Math.round(result.confidence * 100)}%</strong>
        </p>
        <p className="mt-3 text-sm leading-6 text-slate-400">{result.summary}</p>
      </div>

      <div className="space-y-6">
        {result.notationSections.map((section) => (
          <section
            key={section.name}
            className="border-t border-slate-800 pt-5 first:border-t-0 first:pt-0"
          >
            <div className="mb-3 flex items-center justify-between gap-3">
              <h3 className="text-lg font-semibold text-slate-100">{section.name}</h3>
              <span className="rounded-full border border-slate-700 px-3 py-1 text-xs font-medium text-slate-300">
                {section.timeSignature}
              </span>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              {section.measures.map((measure, index) => (
                <MeasureSvg
                  key={`${section.name}-${index}`}
                  measure={measure}
                  index={index}
                  timeSignature={index === 0 ? section.timeSignature : undefined}
                />
              ))}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
