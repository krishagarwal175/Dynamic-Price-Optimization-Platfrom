/** TypeScript shapes for the backend `data` payloads (read-only). */

export type Scope = number | "dataset";

// ---- catalog ----
export interface ProductSummary {
  id: number;
  sku: string;
  name: string;
  base_price: number;
}

export interface ProductRead extends ProductSummary {
  category_id: number;
  description: string | null;
  unit_cost: number;
  currency: string;
  is_active: boolean;
}

export interface ProductListResponse {
  items: ProductSummary[];
  total: number;
  limit: number;
  offset: number;
}

export interface CategorySummary {
  id: number;
  name: string;
}

export interface CategoryListResponse {
  items: CategorySummary[];
  total: number;
}

// ---- financial ----
export interface FinancialMetrics {
  total_units: number;
  revenue: number;
  gross_revenue: number;
  cogs: number;
  total_variable_cost: number;
  total_fixed_cost: number;
  gross_profit: number;
  net_profit: number;
  contribution_margin: number;
  gross_margin: number | null;
  contribution_margin_ratio: number | null;
  average_selling_price: number | null;
  unit_cost: number | null;
  profit_per_unit: number | null;
  breakeven_units: number | null;
  breakeven_revenue: number | null;
}

export interface FinancialResponse {
  scope?: string;
  product_id?: number;
  sku?: string;
  name?: string;
  category_id?: number;
  metrics: FinancialMetrics;
}

// ---- elasticity ----
export interface CurvePoint {
  price: number;
  value: number;
}

export interface ElasticityAnalysis {
  method: string;
  elasticity_coefficient: number;
  classification: string;
  arc_elasticity: number | null;
  point_elasticity: number | null;
  diagnostics: {
    slope: number;
    intercept: number;
    r_squared: number | null;
    residual_std: number;
    sample_size: number;
    distinct_prices: number;
    assumptions: string[];
    notes: string[];
  };
  demand_curve: CurvePoint[];
  revenue_curve: CurvePoint[];
  profit_curve: CurvePoint[] | null;
}

export interface ElasticityResponse {
  scope?: string;
  sku?: string;
  name?: string;
  analysis: ElasticityAnalysis;
}

// ---- forecast ----
export interface ForecastResult {
  horizon: number;
  selected_strategy: string;
  forecast: { step: number; predicted: number; lower: number; upper: number }[];
  history: { period: string; demand: number }[];
  diagnostics: {
    selected_strategy: string;
    mae: number;
    mape: number | null;
    rmse: number;
    mean_error: number;
    residuals: { count: number; mean: number; std: number; minimum: number; maximum: number };
    sample_size: number;
    distinct_periods: number;
    assumptions: string[];
    notes: string[];
  };
  alternatives: {
    method: string;
    usable: boolean;
    mae: number | null;
    mape: number | null;
    rmse: number | null;
  }[];
}

export interface ForecastResponse {
  scope?: string;
  sku?: string;
  name?: string;
  forecast: ForecastResult;
}

// ---- optimization ----
export interface OptimizationResult {
  objective: string;
  recommended_price: number;
  expected_demand: number;
  expected_revenue: number;
  expected_gross_profit: number;
  expected_net_profit: number;
  objective_value: number;
  baseline_price: number;
  baseline_objective_value: number;
  improvement: number;
  search_lower: number;
  search_upper: number;
  iterations: number;
  active_constraints: string[];
  assumptions: string[];
  notes: string[];
}

export interface OptimizationResponse {
  scope?: string;
  sku?: string;
  name?: string;
  optimization: OptimizationResult;
}

// ---- simulation ----
export interface DeltaSet {
  demand_abs: number;
  demand_pct: number | null;
  revenue_abs: number;
  revenue_pct: number | null;
  gross_profit_abs: number;
  gross_profit_pct: number | null;
  net_profit_abs: number;
  net_profit_pct: number | null;
  margin_points: number;
}

export interface ScenarioResult {
  label: string;
  scenario_type: string;
  price: number;
  demand: number;
  revenue: number;
  gross_profit: number;
  contribution_margin: number;
  net_profit: number;
  margin_pct: number;
  objective_value: number;
  vs_baseline: DeltaSet;
  vs_recommended: DeltaSet | null;
  rank: number;
  diagnostics: {
    price_change_pct: number | null;
    demand_change_pct: number | null;
    revenue_improved: boolean;
    profit_improved: boolean;
    margin_improved: boolean;
    is_recommended: boolean;
    notes: string[];
  };
}

export interface SimulationResult {
  objective: string;
  baseline_label: string;
  scenarios: ScenarioResult[];
  ranking_by_objective: string[];
  ranking_by_revenue: string[];
  ranking_by_net_profit: string[];
  best_scenario: string;
  notes: string[];
}

export interface SimulationResponse {
  scope?: string;
  sku?: string;
  name?: string;
  simulation: SimulationResult;
}

// ---- report ----
export type ReportFormat = "json" | "markdown" | "text";

export interface ReportResponse {
  scope?: string;
  sku?: string;
  name?: string;
  format: ReportFormat;
  report: Record<string, unknown> | null;
  content: string | null;
}

export type Objective =
  | "maximize_revenue"
  | "maximize_gross_profit"
  | "maximize_contribution_margin"
  | "maximize_net_profit";
