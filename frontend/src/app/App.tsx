import { QueryClientProvider } from "@tanstack/react-query";
import { MotionConfig } from "framer-motion";
import { Suspense, lazy, useEffect, useState } from "react";
import { BrowserRouter, Route, Routes } from "react-router-dom";

import { LoadingSkeleton } from "@/components/states";
import { EASE } from "@/lib/motion";
import { applyTheme, useUiStore } from "@/services/store";

import { AppLayout } from "@/app/AppLayout";
import { Boot } from "@/app/BootSequence";
import { ErrorBoundary } from "@/app/ErrorBoundary";
import { PageTransition } from "@/app/PageTransition";
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
const NotFoundPage = lazy(() =>
  import("@/pages/NotFoundPage").then((m) => ({ default: m.NotFoundPage })),
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

  // Boot sequence plays once per browser session; navigations and refetches don't replay it.
  const [booting, setBooting] = useState(() => {
    try {
      return sessionStorage.getItem("pl_booted") !== "1";
    } catch {
      return true;
    }
  });
  const finishBoot = () => {
    try {
      sessionStorage.setItem("pl_booted", "1");
    } catch {
      /* storage unavailable — boot simply won't be remembered */
    }
    setBooting(false);
  };

  return (
    <MotionConfig reducedMotion="user" transition={{ ease: EASE }}>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Routes>
            <Route element={<AppLayout />}>
              <Route
                element={
                  <ErrorBoundary>
                    <Suspense fallback={<PageFallback />}>
                      <PageTransition />
                    </Suspense>
                  </ErrorBoundary>
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
                <Route path="*" element={<NotFoundPage />} />
              </Route>
            </Route>
          </Routes>
        </BrowserRouter>
      </QueryClientProvider>
      <Boot show={booting} onDone={finishBoot} />
    </MotionConfig>
  );
}
