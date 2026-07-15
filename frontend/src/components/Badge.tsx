import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

type Tone = "neutral" | "positive" | "negative" | "accent" | "warning";

const TONES: Record<Tone, string> = {
  neutral:
    "bg-neutral-100 text-neutral-600 dark:bg-neutral-800 dark:text-neutral-300",
  positive:
    "bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300",
  negative: "bg-red-50 text-red-700 dark:bg-red-950 dark:text-red-300",
  accent: "bg-accent-muted text-accent dark:bg-indigo-950 dark:text-indigo-300",
  warning: "bg-amber-50 text-amber-700 dark:bg-amber-950 dark:text-amber-300",
};

export function Badge({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium",
        TONES[tone],
      )}
    >
      {children}
    </span>
  );
}
