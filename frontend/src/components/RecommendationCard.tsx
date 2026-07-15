import { formatCurrency, formatNumber } from "@/lib/format";

import { Badge } from "@/components/Badge";
import type { OptimizationResult } from "@/services/types";

/** Highlights the recommended pricing action from an optimization result. */
export function RecommendationCard({ result }: { result: OptimizationResult }) {
  const delta = result.recommended_price - result.baseline_price;
  const action =
    Math.abs(delta) < 0.005
      ? "Maintain current price"
      : `${delta > 0 ? "Increase" : "Reduce"} price to ${formatCurrency(result.recommended_price)}`;
  const improved = result.improvement > 0;

  return (
    <div className="surface border-l-4 border-l-accent p-5">
      <div className="flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wide text-neutral-500 dark:text-neutral-400">
          Recommended action
        </p>
        <Badge tone={improved ? "positive" : "neutral"}>
          {improved ? "Uplift available" : "Already optimal"}
        </Badge>
      </div>
      <p className="mt-2 text-xl font-semibold text-neutral-900 dark:text-neutral-50">{action}</p>
      <div className="mt-3 grid grid-cols-2 gap-3 text-sm sm:grid-cols-4">
        <Stat label="Current" value={formatCurrency(result.baseline_price)} />
        <Stat label="Recommended" value={formatCurrency(result.recommended_price)} />
        <Stat label="Expected demand" value={formatNumber(result.expected_demand)} />
        <Stat label="Improvement" value={formatNumber(result.improvement)} tone={improved ? "pos" : undefined} />
      </div>
    </div>
  );
}

function Stat({ label, value, tone }: { label: string; value: string; tone?: "pos" }) {
  return (
    <div>
      <p className="text-xs text-neutral-500 dark:text-neutral-400">{label}</p>
      <p
        className={
          tone === "pos"
            ? "font-semibold text-emerald-600 dark:text-emerald-400"
            : "font-semibold text-neutral-800 dark:text-neutral-100"
        }
      >
        {value}
      </p>
    </div>
  );
}
