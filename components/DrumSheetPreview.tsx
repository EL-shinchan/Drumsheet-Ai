import type { DrumMeasure, DrumNote, DrumPitch, GenerationResult } from "@/lib/types";

type DrumSheetPreviewProps = {
  result: GenerationResult | null;
};

const STAFF_LINES = [28, 42, 56, 70, 84];
const STAFF_TOP = STAFF_LINES[0];
const STAFF_BOTTOM = STAFF_LINES[STAFF_LINES.length - 1];
const SYSTEM_HEIGHT = 132;
const MEASURE_WIDTH = 210;
const SYSTEM_LEFT_PAD = 72;
const TIME_SIGNATURE_WIDTH = 28;
const MEASURES_PER_SYSTEM = 4;

const PITCH_Y: Record<DrumPitch, number> = {
  "closed-hihat": 18,
  crash: 12,
  ride: 20,
  "high-tom": 44,
  snare: 56,
  "floor-tom": 76,
  kick: 94,
};

function chunkMeasures<T>(items: T[], size: number) {
  const chunks: T[][] = [];
  for (let i = 0; i < items.length; i += size) {
    chunks.push(items.slice(i, i + size));
  }
  return chunks;
}

function beatToX(beat: number) {
  const normalized = (beat - 1) / 4;
  return 16 + normalized * (MEASURE_WIDTH - 32);
}

function noteGlyph(note: DrumNote, index: number) {
  const x = beatToX(note.beat);
  const y = PITCH_Y[note.pitch];
  const isCymbal = note.pitch === "closed-hihat" || note.pitch === "crash" || note.pitch === "ride";
  const stemTop = y - 28;

  return (
    <g key={`${note.pitch}-${note.beat}-${index}`}>
      {note.accent ? (
        <path d={`M ${x - 7} ${y - 34} L ${x} ${y - 39} L ${x + 7} ${y - 34}`} stroke="#0f172a" strokeWidth="1.3" fill="none" />
      ) : null}

      {isCymbal ? (
        <g stroke="#0f172a" strokeWidth="1.5">
          <line x1={x - 5.5} y1={y - 5.5} x2={x + 5.5} y2={y + 5.5} />
          <line x1={x - 5.5} y1={y + 5.5} x2={x + 5.5} y2={y - 5.5} />
        </g>
      ) : (
        <ellipse cx={x} cy={y} rx={6.5} ry={4.8} fill="#0f172a" />
      )}

      <line x1={x + 7} y1={y} x2={x + 7} y2={stemTop} stroke="#0f172a" strokeWidth="1.3" />

      {note.duration !== "quarter" ? (
        <path
          d={`M ${x + 7} ${stemTop} C ${x + 18} ${stemTop + 1}, ${x + 20} ${stemTop + 8}, ${x + 8} ${stemTop + 11}`}
          stroke="#0f172a"
          strokeWidth="1.3"
          fill="none"
        />
      ) : null}
    </g>
  );
}

function MeasureBlock({ measure, isFirstInSystem = false }: { measure: DrumMeasure; isFirstInSystem?: boolean }) {
  return (
    <g>
      {isFirstInSystem ? null : <line x1={0} y1={STAFF_TOP} x2={0} y2={STAFF_BOTTOM} stroke="#0f172a" strokeWidth="1.1" />}
      {measure.notes.map((note, index) => noteGlyph(note, index))}
    </g>
  );
}

function ScoreSystem({
  sectionName,
  timeSignature,
  measures,
  showSectionLabel,
}: {
  sectionName: string;
  timeSignature: string;
  measures: DrumMeasure[];
  showSectionLabel: boolean;
}) {
  const width = SYSTEM_LEFT_PAD + TIME_SIGNATURE_WIDTH + measures.length * MEASURE_WIDTH + 12;

  return (
    <div className="overflow-x-auto rounded-xl border border-stone-300 bg-[#fcfbf7] px-4 py-4 shadow-sm">
      <svg viewBox={`0 0 ${width} ${SYSTEM_HEIGHT}`} className="min-w-[860px] h-auto w-full">
        <rect x="0" y="0" width={width} height={SYSTEM_HEIGHT} fill="#fcfbf7" rx="12" />

        {showSectionLabel ? (
          <text x="0" y="16" fill="#0f172a" fontSize="12" fontWeight="700" fontFamily="ui-sans-serif, system-ui, sans-serif">
            {sectionName.toUpperCase()}
          </text>
        ) : null}

        {STAFF_LINES.map((lineY) => (
          <line
            key={lineY}
            x1={SYSTEM_LEFT_PAD}
            y1={lineY}
            x2={width - 12}
            y2={lineY}
            stroke="#334155"
            strokeWidth="1"
          />
        ))}

        <line x1={SYSTEM_LEFT_PAD} y1={STAFF_TOP} x2={SYSTEM_LEFT_PAD} y2={STAFF_BOTTOM} stroke="#0f172a" strokeWidth="1.4" />
        <line x1={SYSTEM_LEFT_PAD + 4} y1={STAFF_TOP} x2={SYSTEM_LEFT_PAD + 4} y2={STAFF_BOTTOM} stroke="#0f172a" strokeWidth="1.4" />

        <text x={SYSTEM_LEFT_PAD + 15} y={48} fill="#0f172a" fontSize="26" fontFamily="serif">
          𝄽
        </text>

        <g fill="#0f172a" fontSize="14" fontFamily="ui-sans-serif, system-ui, sans-serif" fontWeight="700">
          <text x={SYSTEM_LEFT_PAD + 41} y={42}>{timeSignature.split("/")[0]}</text>
          <text x={SYSTEM_LEFT_PAD + 41} y={61}>{timeSignature.split("/")[1]}</text>
        </g>

        {measures.map((measure, index) => {
          const measureX = SYSTEM_LEFT_PAD + TIME_SIGNATURE_WIDTH + index * MEASURE_WIDTH;
          return (
            <g key={`${sectionName}-${index}`} transform={`translate(${measureX}, 0)`}>
              <MeasureBlock measure={measure} isFirstInSystem={index === 0} />
              <line x1={MEASURE_WIDTH} y1={STAFF_TOP} x2={MEASURE_WIDTH} y2={STAFF_BOTTOM} stroke="#0f172a" strokeWidth="1.1" />
              <text
                x={MEASURE_WIDTH / 2}
                y={112}
                textAnchor="middle"
                fill="#64748b"
                fontSize="10"
                fontFamily="ui-sans-serif, system-ui, sans-serif"
              >
                {index + 1}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

export default function DrumSheetPreview({ result }: DrumSheetPreviewProps) {
  if (!result) return null;

  return (
    <div className="rounded-3xl border border-stone-300 bg-[#f5f1e8] p-6 text-slate-900 shadow-xl">
      <div className="border-b border-stone-300 pb-5">
        <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-stone-500">
              Experimental drum transcription preview
            </p>
            <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-900">{result.title}</h2>
          </div>

          <div className="flex flex-wrap gap-2 text-xs font-medium text-stone-700">
            <span className="rounded-full border border-stone-400 px-3 py-1 bg-white/70 capitalize">
              {result.difficulty}
            </span>
            <span className="rounded-full border border-stone-400 px-3 py-1 bg-white/70">
              Confidence {Math.round(result.confidence * 100)}%
            </span>
          </div>
        </div>

        <p className="mt-4 max-w-3xl text-sm leading-6 text-stone-700">{result.summary}</p>
      </div>

      <div className="mt-6 space-y-8">
        {result.notationSections.map((section) => {
          const systems = chunkMeasures(section.measures, MEASURES_PER_SYSTEM);
          return (
            <section key={section.name} className="space-y-3">
              {systems.map((systemMeasures, systemIndex) => (
                <ScoreSystem
                  key={`${section.name}-${systemIndex}`}
                  sectionName={section.name}
                  timeSignature={section.timeSignature}
                  measures={systemMeasures}
                  showSectionLabel={systemIndex === 0}
                />
              ))}
            </section>
          );
        })}
      </div>
    </div>
  );
}
