import { cn } from "@/lib/cn";

import { AnimatedNumber } from "@/components/AnimatedNumber";
import { LoadingSkeleton } from "@/components/states";

interface Props {
  label: string;
  value: string;
  /** When provided, the value counts up to `numeric.value` (formatted) instead of the
   *  static string — use for headline figures the eye should land on. */
  numeric?: { value: number; format: (n: number) => string; from?: number };
  sublabel?: string;
  tone?: "default" | "positive" | "negative";
  loading?: boolean;
}

const TONE: Record<NonNullable<Props["tone"]>, string> = {
  default: "text-white",
  positive: "text-accent",
  negative: "text-signal",
};

export function MetricCard({ label, value, numeric, sublabel, tone = "default", loading }: Props) {
  return (
    <div className="surface p-4">
      <p className="eyebrow">{label}</p>
      {loading ? (
        <LoadingSkeleton className="mt-2 h-8 w-24" />
      ) : (
        <p className={cn("mt-1.5 font-display text-3xl tracking-tightest tabular-nums", TONE[tone])}>
          {numeric ? (
            <AnimatedNumber value={numeric.value} format={numeric.format} from={numeric.from} />
          ) : (
            value
          )}
        </p>
      )}
      {sublabel && !loading ? (
        <p className="mt-1 font-mono text-[11px] uppercase tracking-wider text-neutral-500">
          {sublabel}
        </p>
      ) : null}
    </div>
  );
}
