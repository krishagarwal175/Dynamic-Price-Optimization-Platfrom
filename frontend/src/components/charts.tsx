/** Thin, theme-consistent wrappers over Recharts. Charts stay simple (no animations).
 *  Recharts takes explicit color strings (not CSS classes), so colors are resolved from
 *  the active theme here to keep charts legible in both light and dark mode. */
import {
  Area,
  Bar,
  BarChart,
  CartesianGrid,
  ComposedChart,
  Line,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { useUiStore } from "@/services/store";

export const CHART_COLORS = ["#4f46e5", "#059669", "#d97706", "#6b7280", "#db2777"];

interface Series {
  key: string;
  name: string;
  color?: string;
}

interface ChartTheme {
  axis: { fontSize: number; fill: string };
  grid: string;
  /** Fills the area below the forecast band's lower bound; must match the card surface. */
  surface: string;
  tooltip: {
    fontSize: number;
    borderRadius: number;
    border: string;
    background: string;
    color: string;
  };
}

const LIGHT: ChartTheme = {
  axis: { fontSize: 11, fill: "#9ca3af" },
  grid: "#e5e7eb",
  surface: "#ffffff",
  tooltip: {
    fontSize: 12,
    borderRadius: 8,
    border: "1px solid #e5e7eb",
    background: "#ffffff",
    color: "#111827",
  },
};

const DARK: ChartTheme = {
  axis: { fontSize: 11, fill: "#9ca3af" },
  grid: "#374151",
  surface: "#171717", // neutral-900, matches the dark card surface
  tooltip: {
    fontSize: 12,
    borderRadius: 8,
    border: "1px solid #374151",
    background: "#171717",
    color: "#f5f5f5",
  },
};

function useChartTheme(): ChartTheme {
  return useUiStore((s) => s.theme) === "dark" ? DARK : LIGHT;
}

export function LineSeriesChart<T extends object>({
  data,
  xKey,
  series,
  band,
}: {
  data: T[];
  xKey: string;
  series: Series[];
  band?: { lower: string; upper: string; color?: string };
}) {
  const t = useChartTheme();
  return (
    <ResponsiveContainer width="100%" height="100%">
      <ComposedChart data={data} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
        <CartesianGrid stroke={t.grid} strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey={xKey} tick={t.axis} tickLine={false} axisLine={false} minTickGap={24} />
        <YAxis tick={t.axis} tickLine={false} axisLine={false} width={48} />
        <Tooltip contentStyle={t.tooltip} />
        {band ? (
          <Area
            type="monotone"
            dataKey={band.upper}
            stroke="none"
            fill={band.color ?? "#c7d2fe"}
            fillOpacity={0.25}
            isAnimationActive={false}
          />
        ) : null}
        {band ? (
          <Area
            type="monotone"
            dataKey={band.lower}
            stroke="none"
            fill={t.surface}
            fillOpacity={1}
            isAnimationActive={false}
          />
        ) : null}
        {series.map((s, i) => (
          <Line
            key={s.key}
            type="monotone"
            dataKey={s.key}
            name={s.name}
            stroke={s.color ?? CHART_COLORS[i % CHART_COLORS.length]}
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        ))}
      </ComposedChart>
    </ResponsiveContainer>
  );
}

export function BarSeriesChart<T extends object>({
  data,
  xKey,
  series,
}: {
  data: T[];
  xKey: string;
  series: Series[];
}) {
  const t = useChartTheme();
  return (
    <ResponsiveContainer width="100%" height="100%">
      <BarChart data={data} margin={{ top: 8, right: 12, bottom: 4, left: 4 }}>
        <CartesianGrid stroke={t.grid} strokeDasharray="3 3" vertical={false} />
        <XAxis dataKey={xKey} tick={t.axis} tickLine={false} axisLine={false} minTickGap={12} />
        <YAxis tick={t.axis} tickLine={false} axisLine={false} width={48} />
        <Tooltip contentStyle={t.tooltip} cursor={{ fill: "rgba(0,0,0,0.06)" }} />
        {series.map((s, i) => (
          <Bar
            key={s.key}
            dataKey={s.key}
            name={s.name}
            fill={s.color ?? CHART_COLORS[i % CHART_COLORS.length]}
            radius={[4, 4, 0, 0]}
            isAnimationActive={false}
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
