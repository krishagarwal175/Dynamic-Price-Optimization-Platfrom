import { ChartCard } from "@/components/ChartCard";
import { MetricCard } from "@/components/MetricCard";
import { QueryBoundary } from "@/components/QueryBoundary";
import { RecommendationCard } from "@/components/RecommendationCard";
import { Reveal, Stagger, StaggerItem } from "@/components/Reveal";
import { SectionHeader } from "@/components/SectionHeader";
import { BarSeriesChart } from "@/components/charts";
import { formatCurrency, formatNumber, formatRatioPct } from "@/lib/format";
import {
  useElasticity,
  useFinancial,
  useOptimization,
  useProducts,
} from "@/services/hooks";
import { useUiStore } from "@/services/store";

const OBJECTIVE = "maximize_gross_profit" as const;

export function DashboardPage() {
  const scope = useUiStore((s) => s.scope);
  const scopeLabel = useUiStore((s) => s.scopeLabel);
  const financial = useFinancial(scope);
  const optimization = useOptimization(scope, OBJECTIVE);
  const elasticity = useElasticity(scope);
  const products = useProducts({ limit: 1 });

  const m = financial.data?.metrics;
  const beta = elasticity.data?.analysis.elasticity_coefficient ?? null;
  const gain = optimization.data?.optimization.improvement ?? null;
  const grossMargin = m?.gross_margin ?? null;
  const asp = m?.average_selling_price ?? null;

  return (
    <div>
      <SectionHeader
        title="Dashboard"
        description={`Overview for ${scopeLabel}. All figures are computed by the backend analytics engines.`}
      />

      <Stagger className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StaggerItem>
          <MetricCard
            label="Products"
            value={formatNumber(products.data?.total, 0)}
            numeric={
              products.data ? { value: products.data.total, format: (n) => formatNumber(n, 0) } : undefined
            }
            loading={products.isPending}
          />
        </StaggerItem>
        <StaggerItem>
          <MetricCard
            label="Revenue"
            value={formatCurrency(m?.revenue)}
            numeric={m ? { value: m.revenue, format: (n) => formatCurrency(n) } : undefined}
            loading={financial.isPending}
          />
        </StaggerItem>
        <StaggerItem>
          <MetricCard
            label="Net profit"
            value={formatCurrency(m?.net_profit)}
            numeric={m ? { value: m.net_profit, format: (n) => formatCurrency(n) } : undefined}
            tone={m && m.net_profit >= 0 ? "positive" : "negative"}
            loading={financial.isPending}
          />
        </StaggerItem>
        <StaggerItem>
          <MetricCard
            label="Gross margin"
            value={formatRatioPct(m?.gross_margin)}
            numeric={grossMargin != null ? { value: grossMargin, format: (n) => formatRatioPct(n) } : undefined}
            loading={financial.isPending}
          />
        </StaggerItem>
        <StaggerItem>
          <MetricCard
            label="Avg. elasticity"
            value={formatNumber(elasticity.data?.analysis.elasticity_coefficient)}
            numeric={beta != null ? { value: beta, format: (n) => formatNumber(n) } : undefined}
            sublabel={elasticity.data?.analysis.classification.replace(/_/g, " ")}
            loading={elasticity.isPending}
          />
        </StaggerItem>
        <StaggerItem>
          <MetricCard
            label="Optimization gain"
            value={formatNumber(optimization.data?.optimization.improvement)}
            numeric={gain != null ? { value: gain, format: (n) => formatNumber(n) } : undefined}
            tone="positive"
            loading={optimization.isPending}
          />
        </StaggerItem>
        <StaggerItem>
          <MetricCard
            label="Avg. selling price"
            value={formatCurrency(m?.average_selling_price)}
            numeric={asp != null ? { value: asp, format: (n) => formatCurrency(n) } : undefined}
            loading={financial.isPending}
          />
        </StaggerItem>
        <StaggerItem>
          <MetricCard
            label="Contribution margin"
            value={formatCurrency(m?.contribution_margin)}
            numeric={m ? { value: m.contribution_margin, format: (n) => formatCurrency(n) } : undefined}
            loading={financial.isPending}
          />
        </StaggerItem>
      </Stagger>

      <Reveal surface className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-2">
        <ChartCard title="Profitability" description="Revenue vs profit for the current scope">
          <QueryBoundary query={financial} emptyMessage="Import sales data to see financials.">
            {(data) => (
              <BarSeriesChart
                xKey="metric"
                data={[
                  { metric: "Revenue", value: data.metrics.revenue },
                  { metric: "Gross profit", value: data.metrics.gross_profit },
                  { metric: "Net profit", value: data.metrics.net_profit },
                ]}
                series={[{ key: "value", name: "Amount" }]}
              />
            )}
          </QueryBoundary>
        </ChartCard>

        <div className="flex flex-col gap-4">
          <QueryBoundary
            query={optimization}
            emptyMessage="Not enough price variation to recommend a price."
            skeletonRows={2}
          >
            {(data) => <RecommendationCard result={data.optimization} />}
          </QueryBoundary>
          <QueryBoundary query={optimization} skeletonRows={1}>
            {(data) => (
              <div className="surface p-5">
                <p className="mb-2 text-sm font-semibold text-neutral-800 dark:text-neutral-100">
                  Notes
                </p>
                <ul className="space-y-1.5 text-sm text-neutral-600 dark:text-neutral-300">
                  {data.optimization.notes.slice(0, 4).map((note, i) => (
                    <li key={i} className="flex gap-2">
                      <span className="text-accent">•</span>
                      {note}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </QueryBoundary>
        </div>
      </Reveal>
    </div>
  );
}
