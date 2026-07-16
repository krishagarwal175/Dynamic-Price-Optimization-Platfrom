import { cn } from "@/lib/cn";
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
    <div className="surface border-l-2 border-l-accent p-5">
      <div className="flex items-center justify-between">
        <p className="eyebrow">Recommended action</p>
        <Badge tone={improved ? "positive" : "neutral"}>
          {improved ? "Uplift available" : "Already optimal"}
        </Badge>
      </div>
      <p className="mt-2 font-display text-2xl uppercase tracking-tight text-white">{action}</p>
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
      <p className="font-mono text-[10px] uppercase tracking-wider text-neutral-500">{label}</p>
      <p className={cn("mt-0.5 font-semibold tabular-nums", tone === "pos" ? "text-accent" : "text-white")}>
        {value}
      </p>
    </div>
  );
}
