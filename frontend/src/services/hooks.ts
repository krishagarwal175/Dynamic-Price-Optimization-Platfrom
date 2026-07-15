/** React Query hooks — the app's data-access surface. Server state lives here. */

import { useQuery, type UseQueryResult } from "@tanstack/react-query";

import { apiGet } from "@/services/client";
import type {
  CategoryListResponse,
  ElasticityResponse,
  FinancialResponse,
  ForecastResponse,
  Objective,
  OptimizationResponse,
  ProductListResponse,
  ProductRead,
  ReportFormat,
  ReportResponse,
  Scope,
  SimulationResponse,
} from "@/services/types";

const RETRY = 1;

function isDataset(scope: Scope): scope is "dataset" {
  return scope === "dataset";
}

/** Build the analytics path for a scope: dataset-level vs per-product. */
function analyticsPath(scope: Scope, suffix: string): string {
  return isDataset(scope)
    ? `/analytics/${suffix}`
    : `/analytics/products/${scope}/${suffix}`;
}

export function useHealth(): UseQueryResult<{ status: string; service: string }> {
  return useQuery({
    queryKey: ["health"],
    queryFn: () => apiGet<{ status: string; service: string }>("/health"),
  });
}

export function useProducts(params: {
  search?: string;
  categoryId?: number | null;
  limit?: number;
  offset?: number;
}): UseQueryResult<ProductListResponse> {
  const { search, categoryId, limit = 50, offset = 0 } = params;
  return useQuery({
    queryKey: ["products", search ?? "", categoryId ?? null, limit, offset],
    queryFn: () =>
      apiGet<ProductListResponse>("/products", {
        search,
        category_id: categoryId ?? undefined,
        limit,
        offset,
      }),
  });
}

export function useProduct(id: number | null): UseQueryResult<ProductRead> {
  return useQuery({
    queryKey: ["product", id],
    queryFn: () => apiGet<ProductRead>(`/products/${id}`),
    enabled: id !== null,
  });
}

export function useCategories(): UseQueryResult<CategoryListResponse> {
  return useQuery({
    queryKey: ["categories"],
    queryFn: () => apiGet<CategoryListResponse>("/categories"),
  });
}

export function useFinancial(scope: Scope): UseQueryResult<FinancialResponse> {
  const path = isDataset(scope) ? "/analytics/financial" : `/analytics/products/${scope}`;
  return useQuery({
    queryKey: ["financial", scope],
    queryFn: () => apiGet<FinancialResponse>(path),
    retry: RETRY,
  });
}

export function useElasticity(scope: Scope): UseQueryResult<ElasticityResponse> {
  return useQuery({
    queryKey: ["elasticity", scope],
    queryFn: () => apiGet<ElasticityResponse>(analyticsPath(scope, "elasticity")),
    retry: RETRY,
  });
}

export function useForecast(scope: Scope, horizon = 6): UseQueryResult<ForecastResponse> {
  return useQuery({
    queryKey: ["forecast", scope, horizon],
    queryFn: () => apiGet<ForecastResponse>(analyticsPath(scope, "forecast"), { horizon }),
    retry: RETRY,
  });
}

export function useOptimization(
  scope: Scope,
  objective: Objective,
): UseQueryResult<OptimizationResponse> {
  return useQuery({
    queryKey: ["optimization", scope, objective],
    queryFn: () => apiGet<OptimizationResponse>(analyticsPath(scope, "optimization"), { objective }),
    retry: RETRY,
  });
}

export interface ScenarioQuery {
  objective: Objective;
  scenario?: string;
  price?: number;
  percentage_change?: number;
}

export function useSimulation(
  scope: Scope,
  query: ScenarioQuery,
): UseQueryResult<SimulationResponse> {
  return useQuery({
    queryKey: ["simulation", scope, query],
    queryFn: () =>
      apiGet<SimulationResponse>(analyticsPath(scope, "simulation"), {
        objective: query.objective,
        scenario: query.scenario,
        price: query.price,
        percentage_change: query.percentage_change,
      }),
    retry: RETRY,
  });
}

export function useReport(
  scope: Scope,
  format: ReportFormat,
  objective: Objective,
): UseQueryResult<ReportResponse> {
  return useQuery({
    queryKey: ["report", scope, format, objective],
    queryFn: () =>
      apiGet<ReportResponse>(analyticsPath(scope, "report"), { format, objective }),
    retry: RETRY,
  });
}
