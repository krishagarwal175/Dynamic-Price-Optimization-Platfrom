import { useState } from "react";

import { QueryBoundary } from "@/components/QueryBoundary";
import { ReportViewer } from "@/components/ReportViewer";
import { SectionHeader } from "@/components/SectionHeader";
import { useReport } from "@/services/hooks";
import { useUiStore } from "@/services/store";
import type { Objective, ReportFormat } from "@/services/types";

export function ReportsPage() {
  const { scope, scopeLabel } = useUiStore();
  const [format, setFormat] = useState<ReportFormat>("markdown");
  const objective: Objective = "maximize_gross_profit";
  const report = useReport(scope, format, objective);

  return (
    <div>
      <SectionHeader
        title="Pricing Report"
        description={`Full analysis for ${scopeLabel}. Switch format, then copy or download.`}
      />
      <QueryBoundary
        query={report}
        emptyMessage="Not enough data to generate a report for this scope."
      >
        {(data) => <ReportViewer data={data} format={format} onFormatChange={setFormat} />}
      </QueryBoundary>
    </div>
  );
}
