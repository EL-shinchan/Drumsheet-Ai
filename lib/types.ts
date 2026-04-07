export type Difficulty = "beginner" | "intermediate" | "pro";

export type GenerationResult = {
  title: string;
  difficulty: Difficulty;
  confidence: number;
  previewMode: "musicxml";
  summary: string;
  musicXml: string;
};
