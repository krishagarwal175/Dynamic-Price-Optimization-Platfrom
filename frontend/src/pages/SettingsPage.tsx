import { MetricCard } from "@/components/MetricCard";
import { SectionHeader } from "@/components/SectionHeader";
import { Badge } from "@/components/Badge";
import { useHealth } from "@/services/hooks";

export function SettingsPage() {
  const health = useHealth();

  return (
    <div>
      <SectionHeader title="Settings" description="Console configuration and backend status." />
      <div className="space-y-6">
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="surface p-5">
            <p className="eyebrow mb-2">Backend</p>
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

        <div className="surface p-5 font-mono text-xs leading-relaxed text-neutral-400">
          The console is presentation-only: all metrics, forecasts, recommendations, and reports
          are computed by the backend analytics engines. No calculations run in the browser.
          Interface theme is fixed to the tactical dark palette.
        </div>
      </div>
    </div>
  );
}
