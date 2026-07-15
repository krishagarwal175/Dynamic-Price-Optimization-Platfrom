import { MetricCard } from "@/components/MetricCard";
import { SectionHeader } from "@/components/SectionHeader";
import { Badge } from "@/components/Badge";
import { useHealth } from "@/services/hooks";
import { applyTheme, useUiStore } from "@/services/store";

export function SettingsPage() {
  const { theme, toggleTheme } = useUiStore();
  const health = useHealth();

  const onToggle = () => {
    toggleTheme();
    applyTheme(theme === "light" ? "dark" : "light");
  };

  return (
    <div>
      <SectionHeader title="Settings" description="Console preferences and backend status." />
      <div className="space-y-6">
        <div className="surface flex items-center justify-between p-5">
          <div>
            <p className="text-sm font-semibold text-neutral-800 dark:text-neutral-100">Theme</p>
            <p className="text-sm text-neutral-500 dark:text-neutral-400">
              Currently {theme}. The preference is saved locally.
            </p>
          </div>
          <button type="button" className="btn-ghost" onClick={onToggle}>
            Switch to {theme === "light" ? "dark" : "light"}
          </button>
        </div>

        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="surface p-5">
            <p className="mb-1 text-sm font-semibold text-neutral-800 dark:text-neutral-100">
              Backend
            </p>
            {health.isPending ? (
              <Badge tone="neutral">Checking…</Badge>
            ) : health.isError ? (
              <Badge tone="negative">Unreachable</Badge>
            ) : (
              <Badge tone="positive">{health.data.status}</Badge>
            )}
          </div>
          <MetricCard label="API version" value="v1" />
          <MetricCard label="Mode" value="Read-only" />
        </div>

        <div className="surface p-5 text-sm text-neutral-500 dark:text-neutral-400">
          The console is presentation-only: all metrics, forecasts, recommendations, and reports
          are computed by the backend analytics engines. No calculations run in the browser.
        </div>
      </div>
    </div>
  );
}
