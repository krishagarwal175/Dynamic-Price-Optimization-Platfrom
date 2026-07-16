import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

type Tone = "neutral" | "positive" | "negative" | "accent" | "warning";

const TONES: Record<Tone, string> = {
  neutral: "border-line bg-ink-3 text-neutral-400",
  positive: "border-accent-soft bg-accent-muted text-accent",
  negative: "border-signal/40 bg-signal-muted text-signal",
  accent: "border-accent-soft bg-accent-muted text-accent",
  warning: "border-amber-500/40 bg-amber-500/10 text-amber-400",
};

export function Badge({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return (
    <span
      className={cn(
        "inline-flex items-center border px-2 py-0.5 font-mono text-[10px] uppercase tracking-wider",
        TONES[tone],
      )}
    >
      {children}
    </span>
  );
}
