import type { ColumnDef } from "@tanstack/react-table";
import { useMemo, useState } from "react";

import { ChartCard } from "@/components/ChartCard";
import { DataTable } from "@/components/DataTable";
import { QueryBoundary } from "@/components/QueryBoundary";
import { SectionHeader } from "@/components/SectionHeader";
import { Badge } from "@/components/Badge";
import { BarSeriesChart } from "@/components/charts";
import { formatCurrency, formatNumber, formatPct } from "@/lib/format";
import { useSimulation, type ScenarioQuery } from "@/services/hooks";
import { useUiStore } from "@/services/store";
import type { Objective, ScenarioResult } from "@/services/types";

type Kind = "default" | "percentage_increase" | "percentage_decrease" | "fixed_price" | "recommended";

export function SimulationPage() {
  const { scope, scopeLabel } = useUiStore();
  const [objective] = useState<Objective>("maximize_gross_profit");
  const [kind, setKind] = useState<Kind>("default");
  const [percent, setPercent] = useState(10);
  const [price, setPrice] = useState(10);

  const query: ScenarioQuery = useMemo(() => {
    if (kind === "default") return { objective };
    if (kind === "recommended") return { objective, scenario: "recommended" };
    if (kind === "fixed_price") return { objective, scenario: "fixed_price", price };
    return { objective, scenario: kind, percentage_change: percent / 100 };
  }, [kind, objective, percent, price]);

  const simulation = useSimulation(scope, query);

  const columns = useMemo<ColumnDef<ScenarioResult, unknown>[]>(
    () => [
      { accessorKey: "label", header: "Scenario" },
      {
        accessorKey: "price",
        header: "Price",
        cell: (c) => <span className="tabular-nums">{formatCurrency(c.getValue<number>())}</span>,
      },
      {
        accessorKey: "demand",
        header: "Demand",
        cell: (c) => <span className="tabular-nums">{formatNumber(c.getValue<number>())}</span>,
      },
      {
        accessorKey: "revenue",
        header: "Revenue",
        cell: (c) => <span className="tabular-nums">{formatCurrency(c.getValue<number>())}</span>,
      },
      {
        accessorKey: "net_profit",
        header: "Net profit",
        cell: (c) => <span className="tabular-nums">{formatCurrency(c.getValue<number>())}</span>,
      },
      {
        id: "profit_change",
        header: "Δ Profit",
        accessorFn: (row) => row.vs_baseline.net_profit_pct ?? 0,
        cell: (c) => {
          const v = c.row.original.vs_baseline.net_profit_pct;
          return (
            <span
              className={
                v && v > 0
                  ? "text-emerald-600 dark:text-emerald-400"
                  : v && v < 0
                    ? "text-red-600 dark:text-red-400"
                    : "text-neutral-500"
              }
            >
              {formatPct(v)}
            </span>
          );
        },
      },
      { accessorKey: "rank", header: "Rank" },
    ],
    [],
  );

  return (
    <div>
      <SectionHeader title="Scenario Simulation" description={scopeLabel} />

      <div className="surface mb-5 flex flex-wrap items-end gap-3 p-4">
        <label className="text-sm">
          <span className="mb-1 block text-neutral-500 dark:text-neutral-400">Scenario</span>
          <select
            className="input max-w-[220px]"
            value={kind}
            onChange={(e) => setKind(e.target.value as Kind)}
          >
            <option value="default">Default comparison set</option>
            <option value="recommended">Recommended price</option>
            <option value="percentage_increase">Percentage increase</option>
            <option value="percentage_decrease">Percentage decrease</option>
            <option value="fixed_price">Custom fixed price</option>
          </select>
        </label>
        {(kind === "percentage_increase" || kind === "percentage_decrease") && (
          <label className="text-sm">
            <span className="mb-1 block text-neutral-500 dark:text-neutral-400">Change (%)</span>
            <input
              type="number"
              min={0}
              max={90}
              className="input max-w-[120px]"
              value={percent}
              onChange={(e) => setPercent(Number(e.target.value))}
            />
          </label>
        )}
        {kind === "fixed_price" && (
          <label className="text-sm">
            <span className="mb-1 block text-neutral-500 dark:text-neutral-400">Price</span>
            <input
              type="number"
              min={0.01}
              step={0.01}
              className="input max-w-[120px]"
              value={price}
              onChange={(e) => setPrice(Number(e.target.value))}
            />
          </label>
        )}
      </div>

      <QueryBoundary
        query={simulation}
        emptyMessage="Not enough data to simulate scenarios for this scope."
      >
        {({ simulation: s }) => (
          <div className="space-y-6">
            <div className="flex flex-wrap items-center gap-2 text-sm">
              <span className="text-neutral-500 dark:text-neutral-400">Best:</span>
              <Badge tone="positive">{s.best_scenario}</Badge>
              <span className="ml-2 text-neutral-500 dark:text-neutral-400">Ranked:</span>
              <span className="text-neutral-600 dark:text-neutral-300">
                {s.ranking_by_objective.join(" › ")}
              </span>
            </div>

            <DataTable columns={columns} data={s.scenarios} />

            <ChartCard title="Net profit by scenario">
              <BarSeriesChart
                xKey="label"
                data={s.scenarios.map((sc) => ({ label: sc.label, value: sc.net_profit }))}
                series={[{ key: "value", name: "Net profit", color: "#059669" }]}
              />
            </ChartCard>

            <div className="surface p-5">
              <p className="mb-2 text-sm font-semibold text-neutral-800 dark:text-neutral-100">
                Observations
              </p>
              <ul className="space-y-1.5 text-sm text-neutral-600 dark:text-neutral-300">
                {s.notes.map((note, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="text-accent">•</span>
                    {note}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </QueryBoundary>
    </div>
  );
}
