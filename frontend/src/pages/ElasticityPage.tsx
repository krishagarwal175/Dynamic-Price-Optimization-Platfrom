import { ChartCard } from "@/components/ChartCard";
import { MetricCard } from "@/components/MetricCard";
import { QueryBoundary } from "@/components/QueryBoundary";
import { SectionHeader } from "@/components/SectionHeader";
import { Badge } from "@/components/Badge";
import { LineSeriesChart } from "@/components/charts";
import { formatNumber, titleCase } from "@/lib/format";
import { useElasticity } from "@/services/hooks";
import { useUiStore } from "@/services/store";

export function ElasticityPage() {
  const scope = useUiStore((s) => s.scope);
  const scopeLabel = useUiStore((s) => s.scopeLabel);
  const elasticity = useElasticity(scope);

  return (
    <div>
      <SectionHeader title="Price Elasticity" description={scopeLabel} />
      <QueryBoundary
        query={elasticity}
        emptyMessage="At least two distinct prices are required to estimate elasticity."
      >
        {({ analysis: a }) => (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <MetricCard label="Elasticity (E)" value={formatNumber(a.elasticity_coefficient)} />
              <MetricCard
                label="R²"
                value={a.diagnostics.r_squared === null ? "—" : formatNumber(a.diagnostics.r_squared, 3)}
              />
              <MetricCard label="Method" value={titleCase(a.method)} />
              <MetricCard label="Sample size" value={formatNumber(a.diagnostics.sample_size, 0)} />
            </div>

            <div className="surface p-5">
              <div className="mb-2 flex items-center gap-2">
                <p className="text-sm font-semibold text-neutral-800 dark:text-neutral-100">
                  Interpretation
                </p>
                <Badge tone="accent">{titleCase(a.classification)}</Badge>
              </div>
              <ul className="space-y-1.5 text-sm text-neutral-600 dark:text-neutral-300">
                {a.diagnostics.notes.map((note, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-accent">•</span>
                    {note}
                  </li>
                ))}
              </ul>
            </div>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <ChartCard title="Demand curve" description="Modelled quantity across price">
                <LineSeriesChart
                  xKey="price"
                  data={a.demand_curve}
                  series={[{ key: "value", name: "Quantity" }]}
                />
              </ChartCard>
              <ChartCard title="Revenue curve" description="Modelled revenue across price">
                <LineSeriesChart
                  xKey="price"
                  data={a.revenue_curve}
                  series={[{ key: "value", name: "Revenue", color: "#059669" }]}
                />
              </ChartCard>
            </div>

            <div className="surface p-5">
              <p className="mb-2 text-sm font-semibold text-neutral-800 dark:text-neutral-100">
                Assumptions
              </p>
              <ul className="grid gap-1.5 text-sm text-neutral-500 dark:text-neutral-400 sm:grid-cols-2">
                {a.diagnostics.assumptions.map((item, i) => (
                  <li key={i}>— {item}</li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </QueryBoundary>
    </div>
  );
}
