import { ChartCard } from "@/components/ChartCard";
import { MetricCard } from "@/components/MetricCard";
import { QueryBoundary } from "@/components/QueryBoundary";
import { SectionHeader } from "@/components/SectionHeader";
import { BarSeriesChart } from "@/components/charts";
import { formatCurrency, formatNumber, formatRatioPct } from "@/lib/format";
import { useFinancial } from "@/services/hooks";
import { useUiStore } from "@/services/store";

export function FinancialPage() {
  const { scope, scopeLabel } = useUiStore();
  const financial = useFinancial(scope);

  return (
    <div>
      <SectionHeader title="Financial Analysis" description={scopeLabel} />
      <QueryBoundary query={financial} emptyMessage="Import sales data to compute financial metrics.">
        {({ metrics: m }) => (
          <div className="space-y-6">
            <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
              <MetricCard label="Revenue" value={formatCurrency(m.revenue)} />
              <MetricCard label="COGS" value={formatCurrency(m.cogs)} />
              <MetricCard
                label="Gross profit"
                value={formatCurrency(m.gross_profit)}
                tone={m.gross_profit >= 0 ? "positive" : "negative"}
              />
              <MetricCard
                label="Net profit"
                value={formatCurrency(m.net_profit)}
                tone={m.net_profit >= 0 ? "positive" : "negative"}
              />
              <MetricCard label="Gross margin" value={formatRatioPct(m.gross_margin)} />
              <MetricCard
                label="Contribution margin %"
                value={formatRatioPct(m.contribution_margin_ratio)}
              />
              <MetricCard label="Avg. selling price" value={formatCurrency(m.average_selling_price)} />
              <MetricCard label="Units sold" value={formatNumber(m.total_units, 0)} />
            </div>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <ChartCard title="Revenue, cost & profit">
                <BarSeriesChart
                  xKey="metric"
                  data={[
                    { metric: "Revenue", value: m.revenue },
                    { metric: "COGS", value: m.cogs },
                    { metric: "Gross profit", value: m.gross_profit },
                    { metric: "Net profit", value: m.net_profit },
                  ]}
                  series={[{ key: "value", name: "Amount" }]}
                />
              </ChartCard>
              <ChartCard title="Per-unit economics">
                <BarSeriesChart
                  xKey="metric"
                  data={[
                    { metric: "ASP", value: m.average_selling_price },
                    { metric: "Unit cost", value: m.unit_cost },
                    { metric: "Profit/unit", value: m.profit_per_unit },
                  ]}
                  series={[{ key: "value", name: "Per unit" }]}
                />
              </ChartCard>
            </div>
          </div>
        )}
      </QueryBoundary>
    </div>
  );
}
