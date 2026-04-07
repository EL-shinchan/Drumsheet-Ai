"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import type { GenerationResult } from "@/lib/types";

type DrumSheetPreviewProps = {
  result: GenerationResult | null;
};

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
    </div>
  );
}
