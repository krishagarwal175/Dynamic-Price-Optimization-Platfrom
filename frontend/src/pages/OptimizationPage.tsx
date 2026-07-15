import { useState } from "react";

import { ChartCard } from "@/components/ChartCard";
import { MetricCard } from "@/components/MetricCard";
import { QueryBoundary } from "@/components/QueryBoundary";
import { RecommendationCard } from "@/components/RecommendationCard";
import { SectionHeader } from "@/components/SectionHeader";
import { Badge } from "@/components/Badge";
import { BarSeriesChart } from "@/components/charts";
import { formatCurrency, formatNumber } from "@/lib/format";
import { useOptimization } from "@/services/hooks";
import { useUiStore } from "@/services/store";
import type { Objective } from "@/services/types";

const OBJECTIVES: { value: Objective; label: string }[] = [
  { value: "maximize_gross_profit", label: "Maximize gross profit" },
  { value: "maximize_net_profit", label: "Maximize net profit" },
  { value: "maximize_revenue", label: "Maximize revenue" },
  { value: "maximize_contribution_margin", label: "Maximize contribution margin" },
];

export function OptimizationPage() {
  const scope = useUiStore((s) => s.scope);
  const scopeLabel = useUiStore((s) => s.scopeLabel);
  const [objective, setObjective] = useState<Objective>("maximize_gross_profit");
  const optimization = useOptimization(scope, objective);

  return (
    <div>
      <SectionHeader
        title="Pricing Optimization"
        description={scopeLabel}
        actions={
          <select
            className="input max-w-[240px]"
            value={objective}
            onChange={(e) => setObjective(e.target.value as Objective)}
            aria-label="Optimization objective"
          >
            {OBJECTIVES.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
        }
      />

      <QueryBoundary
        query={optimization}
        emptyMessage="Not enough price variation and history to recommend a price."
      >
        {({ optimization: o }) => (
          <div className="space-y-6">
            <RecommendationCard result={o} />

            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <MetricCard label="Objective value" value={formatNumber(o.objective_value)} />
              <MetricCard label="Expected revenue" value={formatCurrency(o.expected_revenue)} />
              <MetricCard label="Expected net profit" value={formatCurrency(o.expected_net_profit)} />
              <MetricCard label="Search evaluations" value={formatNumber(o.iterations, 0)} />
            </div>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <ChartCard title="Objective: current vs recommended">
                <BarSeriesChart
                  xKey="label"
                  data={[
                    { label: "Current", value: o.baseline_objective_value },
                    { label: "Recommended", value: o.objective_value },
                  ]}
                  series={[{ key: "value", name: "Objective value", color: "#4f46e5" }]}
                />
              </ChartCard>

              <div className="space-y-4">
                <div className="surface p-5">
                  <p className="mb-2 text-sm font-semibold text-neutral-800 dark:text-neutral-100">
                    Constraints & search
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {o.active_constraints.length === 0 ? (
                      <Badge tone="neutral">No binding constraints</Badge>
                    ) : (
                      o.active_constraints.map((c) => (
                        <Badge key={c} tone="warning">
                          {c}
                        </Badge>
                      ))
                    )}
                  </div>
                  <p className="mt-3 text-sm text-neutral-500 dark:text-neutral-400">
                    Searched {formatCurrency(o.search_lower)}–{formatCurrency(o.search_upper)} in{" "}
                    {o.iterations} evaluations.
                  </p>
                </div>
                <div className="surface p-5">
                  <p className="mb-2 text-sm font-semibold text-neutral-800 dark:text-neutral-100">
                    Explanation
                  </p>
                  <ul className="space-y-1.5 text-sm text-neutral-600 dark:text-neutral-300">
                    {o.notes.map((note, i) => (
                      <li key={i} className="flex gap-2">
                        <span className="text-accent">•</span>
                        {note}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </QueryBoundary>
    </div>
  );
}
