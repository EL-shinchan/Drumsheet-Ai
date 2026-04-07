export type Difficulty = "beginner" | "intermediate" | "pro";

export type DrumPitch =
  | "closed-hihat"
  | "snare"
  | "kick"
  | "crash"
  | "ride"
  | "high-tom"
  | "floor-tom";

export type DrumNote = {
  beat: number;
  pitch: DrumPitch;
  duration?: "eighth" | "quarter";
  accent?: boolean;
};

export type DrumMeasure = {
  notes: DrumNote[];
};

export type NotationSection = {
  name: string;
  timeSignature: string;
  measures: DrumMeasure[];
};

export type GenerationResult = {
  title: string;
  difficulty: Difficulty;
  confidence: number;
  previewMode: "experimental-notation";
  summary: string;
  notationSections: NotationSection[];
};
