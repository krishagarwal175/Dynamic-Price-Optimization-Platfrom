import { useState } from "react";

import { Badge } from "@/components/Badge";
import type { ReportFormat, ReportResponse } from "@/services/types";

/** Renders a generated report and offers copy / download. */
export function ReportViewer({
  data,
  format,
  onFormatChange,
}: {
  data: ReportResponse;
  format: ReportFormat;
  onFormatChange: (fmt: ReportFormat) => void;
}) {
  const [copied, setCopied] = useState(false);

  const text =
    format === "json"
      ? JSON.stringify(data.report, null, 2)
      : (data.content ?? "");

  const copy = async () => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  };

  const download = () => {
    const ext = format === "json" ? "json" : format === "markdown" ? "md" : "txt";
    const blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `pricing-report.${ext}`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const formats: ReportFormat[] = ["json", "markdown", "text"];

  return (
    <div className="surface overflow-hidden">
      <div className="flex flex-wrap items-center justify-between gap-2 border-b border-neutral-200 p-3 dark:border-neutral-800">
        <div className="inline-flex rounded-lg border border-neutral-200 p-0.5 dark:border-neutral-700">
          {formats.map((f) => (
            <button
              key={f}
              type="button"
              onClick={() => onFormatChange(f)}
              className={
                f === format
                  ? "rounded-md bg-accent px-2.5 py-1 text-xs font-medium text-accent-fg"
                  : "rounded-md px-2.5 py-1 text-xs font-medium text-neutral-600 hover:bg-neutral-100 dark:text-neutral-300 dark:hover:bg-neutral-800"
              }
            >
              {f.toUpperCase()}
            </button>
          ))}
        </div>
        <div className="flex items-center gap-2">
          {copied ? <Badge tone="positive">Copied</Badge> : null}
          <button type="button" className="btn-ghost" onClick={copy}>
            Copy
          </button>
          <button type="button" className="btn-primary" onClick={download}>
            Download
          </button>
        </div>
      </div>
      <pre className="max-h-[560px] overflow-auto bg-neutral-50 p-4 text-xs leading-relaxed text-neutral-800 dark:bg-neutral-950 dark:text-neutral-200">
        {text}
      </pre>
    </div>
  );
}
