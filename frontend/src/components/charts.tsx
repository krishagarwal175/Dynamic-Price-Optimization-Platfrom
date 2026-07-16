/** Thin, theme-consistent wrappers over Recharts.
 *  Recharts takes explicit color strings (not CSS classes), so colors are resolved from
 *  the active theme here to keep charts legible in both light and dark mode. Series draw in
 *  once on mount (line sweep / bar grow) to signal "just computed"; the forecast band and
 *  everything under reduced motion render instantly so the data is never withheld. */
import { useReducedMotion } from "framer-motion";
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

// Tactical series palette: neon green leads, signal red for contrast, muted supports.
export const CHART_COLORS = ["#c8ff00", "#ff3b30", "#f5a623", "#8f8f8f", "#38bdf8"];

const DRAW_MS = 700;

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

// Single committed dark theme (matches the ink surfaces + hairline borders).
const THEME: ChartTheme = {
  axis: { fontSize: 11, fill: "#8f8f8f" },
  grid: "#262626",
  surface: "#080808", // ink-1, matches the card surface (forecast band mask)
  tooltip: {
    fontSize: 12,
    borderRadius: 0,
    border: "1px solid #2e2e2e",
    background: "#101010",
    color: "#f5f5f5",
  },
};

function useChartTheme(): ChartTheme {
  return THEME;
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
  const reduce = useReducedMotion();
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
            isAnimationActive={!reduce}
            animationDuration={DRAW_MS}
            animationEasing="ease-out"
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
  const reduce = useReducedMotion();
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
            isAnimationActive={!reduce}
            animationDuration={DRAW_MS}
            animationEasing="ease-out"
          />
        ))}
      </BarChart>
    </ResponsiveContainer>
  );
}
