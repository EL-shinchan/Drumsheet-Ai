export type Difficulty = "beginner" | "intermediate" | "pro";

export type DebugHit = {
  step: number;
  kind: string;
  strength: number;
  time: number;
  lowRatio: number;
  midRatio: number;
  highRatio: number;
  accepted: boolean;
  source: "detected" | "fallback" | "skeleton" | "override";
};

export type DebugInfo = {
  bpm: number;
  windowStart: number;
  windowEnd: number;
  rawDetectedCount: number;
  quantizedDetectedCount: number;
  acceptedCount: number;
  grid: string[];
  quantizedHits: DebugHit[];
  acceptedHits: DebugHit[];
};

export type GenerationResult = {
  title: string;
  difficulty: Difficulty;
  confidence: number;
  previewMode: "musicxml";
  summary: string;
  musicXml: string;
  debug?: DebugInfo;
};
