import type { Difficulty } from "@/lib/types";
import { cn } from "@/lib/helpers";

type DifficultySelectorProps = {
  value: Difficulty | null;
  onChange: (difficulty: Difficulty) => void;
  disabled?: boolean;
};

const options: Difficulty[] = ["beginner", "intermediate", "pro"];

export default function DifficultySelector({
  value,
  onChange,
  disabled,
}: DifficultySelectorProps) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-900 p-5">
      <span className="mb-3 block text-sm font-semibold text-slate-200">Choose difficulty</span>

      <div className="flex flex-wrap gap-3">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            onClick={() => onChange(option)}
            disabled={disabled}
            className={cn(
              "rounded-full border px-4 py-2 text-sm font-medium capitalize transition",
              value === option
                ? "border-blue-500 bg-blue-600 text-white"
                : "border-slate-700 bg-slate-950 text-slate-200 hover:border-slate-500",
              disabled && "cursor-not-allowed opacity-60 hover:border-slate-700",
            )}
          >
            {option}
          </button>
        ))}
      </div>
    </div>
  );
}
