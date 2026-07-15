import { ChartCard } from "@/components/ChartCard";
import { MetricCard } from "@/components/MetricCard";
import { QueryBoundary } from "@/components/QueryBoundary";
import { SectionHeader } from "@/components/SectionHeader";
import { LineSeriesChart } from "@/components/charts";
import { formatNumber, titleCase } from "@/lib/format";
import { useForecast } from "@/services/hooks";
import { useUiStore } from "@/services/store";

export function ForecastPage() {
  const { scope, scopeLabel } = useUiStore();
  const forecast = useForecast(scope, 6);

  return (
    <div>
      <SectionHeader title="Demand Forecast" description={scopeLabel} />
      <QueryBoundary
        query={forecast}
        emptyMessage="At least two periods of sales history are required to forecast."
      >
        {({ forecast: f }) => {
          const rows = [
            ...f.history.map((h) => ({
              label: h.period,
              demand: h.demand,
              predicted: null,
              lower: null,
              upper: null,
            })),
            ...f.forecast.map((p) => ({
              label: `+${p.step}`,
              demand: null,
              predicted: p.predicted,
              lower: p.lower,
              upper: p.upper,
            })),
          ];
          return (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
                <MetricCard label="Strategy" value={titleCase(f.selected_strategy)} />
                <MetricCard label="Horizon" value={formatNumber(f.horizon, 0)} />
                <MetricCard label="RMSE" value={formatNumber(f.diagnostics.rmse)} />
                <MetricCard
                  label="Next-period demand"
                  value={formatNumber(f.forecast[0]?.predicted)}
                />
              </div>

              <ChartCard
                title="Historical & forecast demand"
                description="Shaded band shows the forecast interval"
                height={320}
              >
                <LineSeriesChart
                  xKey="label"
                  data={rows}
                  band={{ lower: "lower", upper: "upper" }}
                  series={[
                    { key: "demand", name: "History" },
                    { key: "predicted", name: "Forecast", color: "#059669" },
                  ]}
                />
              </ChartCard>

              <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
                <div className="surface p-5">
                  <p className="mb-2 text-sm font-semibold text-neutral-800 dark:text-neutral-100">
                    Confidence notes
                  </p>
                  <ul className="space-y-1.5 text-sm text-neutral-600 dark:text-neutral-300">
                    {f.diagnostics.notes.map((note, i) => (
                      <li key={i} className="flex gap-2">
                        <span className="text-accent">•</span>
                        {note}
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="surface p-5">
                  <p className="mb-2 text-sm font-semibold text-neutral-800 dark:text-neutral-100">
                    Assumptions
                  </p>
                  <ul className="space-y-1.5 text-sm text-neutral-500 dark:text-neutral-400">
                    {f.diagnostics.assumptions.map((item, i) => (
                      <li key={i}>— {item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          );
        }}
      </QueryBoundary>
    </div>
  );
}
