import type { ReactNode } from "react";

export function ChartCard({
  title,
  description,
  children,
  height = 280,
}: {
  title: string;
  description?: string;
  children: ReactNode;
  height?: number;
}) {
  return (
    <div className="surface p-5">
      <div className="mb-3">
        <h3 className="text-sm font-semibold text-neutral-800 dark:text-neutral-100">{title}</h3>
        {description ? (
          <p className="text-xs text-neutral-500 dark:text-neutral-400">{description}</p>
        ) : null}
      </div>
      <div style={{ height }}>{children}</div>
    </div>
  );
}
