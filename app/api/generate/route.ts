import { spawn } from "child_process";
import fs from "fs/promises";
import path from "path";
import { NextRequest, NextResponse } from "next/server";
import type { Difficulty, GenerationResult } from "@/lib/types";

export const runtime = "nodejs";

const VALID_DIFFICULTIES: Difficulty[] = ["beginner", "intermediate", "pro"];
const MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024;

function isDifficulty(value: string): value is Difficulty {
  return VALID_DIFFICULTIES.includes(value as Difficulty);
}

function sanitizeFilename(filename: string) {
  return filename.replace(/[^a-zA-Z0-9._-]+/g, "-");
}

function runPythonScript(filePath: string, difficulty: Difficulty): Promise<string> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(process.cwd(), "engine", "process_song.py");
    const child = spawn("python3", [scriptPath, filePath, difficulty]);

    let stdout = "";
    let stderr = "";

    child.stdout.on("data", (data) => {
      stdout += data.toString();
    });

    child.stderr.on("data", (data) => {
      stderr += data.toString();
    });

    child.on("error", (error) => {
      reject(error);
    });

    child.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(stderr.trim() || `Python process exited with code ${code}`));
        return;
      }

      resolve(stdout.trim());
    });
  });
}

export async function POST(request: NextRequest) {
  let savedPath: string | null = null;

  try {
    const formData = await request.formData();
    const file = formData.get("audio");
    const difficultyValue = formData.get("difficulty");

    if (!(file instanceof File)) {
      return NextResponse.json({ error: "No audio file uploaded." }, { status: 400 });
    }

    if (typeof difficultyValue !== "string" || !isDifficulty(difficultyValue)) {
      return NextResponse.json({ error: "Please choose a valid difficulty." }, { status: 400 });
    }

    if (file.size === 0) {
      return NextResponse.json({ error: "Uploaded file is empty." }, { status: 400 });
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      return NextResponse.json(
        { error: "File is too large. Please upload something under 25MB for now." },
        { status: 400 },
      );
    }

    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    const uploadsDir = path.join(process.cwd(), "uploads");
    await fs.mkdir(uploadsDir, { recursive: true });

    const safeFilename = `${Date.now()}-${sanitizeFilename(file.name || "upload-audio")}`;
    savedPath = path.join(uploadsDir, safeFilename);
    await fs.writeFile(savedPath, buffer);

    const output = await runPythonScript(savedPath, difficultyValue);
    const parsed = JSON.parse(output) as GenerationResult | { error: string };

    if ("error" in parsed) {
      return NextResponse.json({ error: parsed.error }, { status: 400 });
    }

    return NextResponse.json(parsed);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unexpected server error.";
    return NextResponse.json({ error: message }, { status: 500 });
  } finally {
    if (savedPath) {
      await fs.unlink(savedPath).catch(() => undefined);
    }
  }
}
