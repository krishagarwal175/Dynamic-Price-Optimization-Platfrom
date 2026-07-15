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
  default: "text-neutral-900 dark:text-neutral-50",
  positive: "text-emerald-600 dark:text-emerald-400",
  negative: "text-red-600 dark:text-red-400",
};

export function MetricCard({ label, value, numeric, sublabel, tone = "default", loading }: Props) {
  return (
    <div className="surface p-4">
      <p className="text-xs font-medium uppercase tracking-wide text-neutral-500 dark:text-neutral-400">
        {label}
      </p>
      {loading ? (
        <LoadingSkeleton className="mt-2 h-7 w-24" />
      ) : (
        <p className={cn("mt-1 text-2xl font-semibold tabular-nums", TONE[tone])}>
          {numeric ? (
            <AnimatedNumber value={numeric.value} format={numeric.format} from={numeric.from} />
          ) : (
            value
          )}
        </p>
      )}
      {sublabel && !loading ? (
        <p className="mt-1 text-xs text-neutral-500 dark:text-neutral-400">{sublabel}</p>
      ) : null}
    </div>
  );
}
