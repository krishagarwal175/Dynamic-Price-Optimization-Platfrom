import { QueryClientProvider } from "@tanstack/react-query";
import { Suspense, lazy, useEffect } from "react";
import { BrowserRouter, Navigate, Outlet, Route, Routes } from "react-router-dom";

import { LoadingSkeleton } from "@/components/states";
import { applyTheme, useUiStore } from "@/services/store";

import { AppLayout } from "@/app/AppLayout";
import { queryClient } from "@/app/providers";

// Route-level code-splitting keeps the initial bundle small (charts load on demand).
const DashboardPage = lazy(() =>
  import("@/pages/DashboardPage").then((m) => ({ default: m.DashboardPage })),
);
const CatalogPage = lazy(() =>
  import("@/pages/CatalogPage").then((m) => ({ default: m.CatalogPage })),
);
const FinancialPage = lazy(() =>
  import("@/pages/FinancialPage").then((m) => ({ default: m.FinancialPage })),
);
const ElasticityPage = lazy(() =>
  import("@/pages/ElasticityPage").then((m) => ({ default: m.ElasticityPage })),
);
const ForecastPage = lazy(() =>
  import("@/pages/ForecastPage").then((m) => ({ default: m.ForecastPage })),
);
const OptimizationPage = lazy(() =>
  import("@/pages/OptimizationPage").then((m) => ({ default: m.OptimizationPage })),
);
const SimulationPage = lazy(() =>
  import("@/pages/SimulationPage").then((m) => ({ default: m.SimulationPage })),
);
const ReportsPage = lazy(() =>
  import("@/pages/ReportsPage").then((m) => ({ default: m.ReportsPage })),
);
const SettingsPage = lazy(() =>
  import("@/pages/SettingsPage").then((m) => ({ default: m.SettingsPage })),
);

function PageFallback() {
  return (
    <div className="grid gap-3">
      <LoadingSkeleton className="h-8 w-48" />
      <LoadingSkeleton className="h-40" />
    </div>
  );
}

export function App() {
  const theme = useUiStore((s) => s.theme);
  useEffect(() => applyTheme(theme), [theme]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route element={<AppLayout />}>
            <Route
              element={
                <Suspense fallback={<PageFallback />}>
                  <Outlet />
                </Suspense>
              }
            >
              <Route index element={<DashboardPage />} />
              <Route path="catalog" element={<CatalogPage />} />
              <Route path="financial" element={<FinancialPage />} />
              <Route path="elasticity" element={<ElasticityPage />} />
              <Route path="forecast" element={<ForecastPage />} />
              <Route path="optimization" element={<OptimizationPage />} />
              <Route path="simulation" element={<SimulationPage />} />
              <Route path="reports" element={<ReportsPage />} />
              <Route path="settings" element={<SettingsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
