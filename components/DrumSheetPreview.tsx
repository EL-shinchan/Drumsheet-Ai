"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { DebugHit, GenerationResult } from "@/lib/types";

type DrumSheetPreviewProps = {
  result: GenerationResult | null;
};

function symbolForKind(kind: string) {
  if (kind === "bd") return "B";
  if (kind === "sn") return "S";
  if (kind === "hh" || kind === "oh") return "H";
  if (kind === "cr") return "C";
  return ".";
}

function buildRow(hits: DebugHit[], predicate: (kind: string) => boolean) {
  const row = Array.from({ length: 64 }, () => ".");
  for (const hit of hits) {
    if (predicate(hit.kind)) {
      row[hit.step] = symbolForKind(hit.kind);
    }
  }
  return row;
}

function GridRow({ label, values }: { label: string; values: string[] }) {
  return (
    <div className="grid grid-cols-[40px_1fr] items-center gap-3 font-mono text-xs text-stone-700">
      <span className="font-semibold text-stone-500">{label}</span>
      <div className="grid grid-cols-16 gap-1 md:grid-cols-32">
        {values.map((value, index) => (
          <span
            key={`${label}-${index}`}
            className={`rounded border px-1 py-0.5 text-center ${
              value === "." ? "border-stone-200 bg-white/70 text-stone-300" : "border-stone-400 bg-stone-100 text-slate-900"
            }`}
          >
            {value}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function DrumSheetPreview({ result }: DrumSheetPreviewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [renderError, setRenderError] = useState<string | null>(null);
  const xml = useMemo(() => result?.musicXml ?? "", [result]);

  useEffect(() => {
    let cancelled = false;

    async function renderScore() {
      if (!result || !containerRef.current) return;

      containerRef.current.innerHTML = "";
      setRenderError(null);

      try {
        const { OpenSheetMusicDisplay } = await import("opensheetmusicdisplay");
        const osmd = new OpenSheetMusicDisplay(containerRef.current, {
          autoResize: true,
          backend: "svg",
          drawTitle: true,
          drawSubtitle: false,
          drawComposer: false,
          drawPartNames: false,
          pageFormat: "Endless",
          pageBackgroundColor: "#fcfbf7",
          defaultFontFamily: "Times New Roman",
        });

        await osmd.load(xml);
        osmd.render();

        if (!cancelled) {
          const svg = containerRef.current.querySelector("svg");
          if (svg) {
            svg.setAttribute("style", "width: 100%; height: auto;");
          }
        }
      } catch (error) {
        if (!cancelled) {
          setRenderError(error instanceof Error ? error.message : "Failed to render score preview.");
        }
      }
    }

    void renderScore();

    return () => {
      cancelled = true;
    };
  }, [result, xml]);

  if (!result) return null;

  const debug = result.debug;
  const acceptedHits = debug?.acceptedHits ?? [];
  const quantizedHits = debug?.quantizedHits ?? [];
  const beatRow = debug?.grid ?? Array.from({ length: 64 }, () => ".");
  const kickRow = buildRow(acceptedHits, (kind) => kind === "bd");
  const snareRow = buildRow(acceptedHits, (kind) => kind === "sn");
  const hatRow = buildRow(acceptedHits, (kind) => kind === "hh" || kind === "oh");

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
            <span className="rounded-full border border-stone-400 bg-white/70 px-3 py-1 capitalize">
              {result.difficulty}
            </span>
            <span className="rounded-full border border-stone-400 bg-white/70 px-3 py-1">
              Confidence {Math.round(result.confidence * 100)}%
            </span>
            {debug ? (
              <span className="rounded-full border border-stone-400 bg-white/70 px-3 py-1">
                {Math.round(debug.bpm)} BPM
              </span>
            ) : null}
          </div>
        </div>

        <p className="mt-4 max-w-3xl text-sm leading-6 text-stone-700">{result.summary}</p>
      </div>

      <div className="mt-6 rounded-2xl border border-stone-300 bg-[#fcfbf7] p-4 shadow-sm">
        {renderError ? (
          <div className="rounded-xl border border-red-300 bg-red-50 p-4 text-sm text-red-700">
            Couldn&apos;t render the MusicXML preview yet: {renderError}
          </div>
        ) : null}
        <div ref={containerRef} className="musicxml-score overflow-x-auto" />
      </div>

      {debug ? (
        <div className="mt-6 rounded-2xl border border-stone-300 bg-white/60 p-4 shadow-sm">
          <div className="mb-4 flex flex-wrap gap-2 text-xs text-stone-700">
            <span className="rounded-full border border-stone-300 px-3 py-1">Window {debug.windowStart.toFixed(2)}s → {debug.windowEnd.toFixed(2)}s</span>
            <span className="rounded-full border border-stone-300 px-3 py-1">Raw hits {debug.rawDetectedCount}</span>
            <span className="rounded-full border border-stone-300 px-3 py-1">Quantized {debug.quantizedDetectedCount}</span>
            <span className="rounded-full border border-stone-300 px-3 py-1">Accepted {debug.acceptedCount}</span>
          </div>

          <div className="space-y-2">
            <GridRow label="Beat" values={beatRow} />
            <GridRow label="Hat" values={hatRow} />
            <GridRow label="Snr" values={snareRow} />
            <GridRow label="Kick" values={kickRow} />
          </div>

          <details className="mt-5 rounded-xl border border-stone-200 bg-stone-50 p-3">
            <summary className="cursor-pointer text-sm font-semibold text-stone-700">Advanced debug</summary>
            <div className="mt-3 space-y-4 text-xs text-stone-700">
              <div>
                <p className="mb-2 font-semibold">Accepted hits</p>
                <pre className="overflow-x-auto rounded-lg bg-white p-3">{JSON.stringify(acceptedHits, null, 2)}</pre>
              </div>
              <div>
                <p className="mb-2 font-semibold">Quantized hits</p>
                <pre className="overflow-x-auto rounded-lg bg-white p-3">{JSON.stringify(quantizedHits, null, 2)}</pre>
              </div>
            </div>
          </details>
        </div>
      ) : null}
    </div>
  );
}
