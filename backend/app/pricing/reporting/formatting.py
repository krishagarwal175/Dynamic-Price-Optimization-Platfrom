"""Formatters: render a :class:`PricingReport` as a dict (JSON), Markdown, or plain text.

The engine is formatter-agnostic — it returns a structured report and these pure functions
render it. A future PDF exporter can be added here without touching business composition.
"""

from __future__ import annotations

from dataclasses import asdict
from enum import Enum
from typing import Any

from app.pricing.reporting.errors import FormattingError
from app.pricing.reporting.models import PricingReport


class ReportFormat(str, Enum):
    JSON = "json"
    MARKDOWN = "markdown"
    TEXT = "text"


def to_dict(report: PricingReport) -> dict[str, Any]:
    """JSON-serializable dict (all leaves are primitives)."""
    return asdict(report)


def render(report: PricingReport, fmt: ReportFormat) -> str:
    if fmt is ReportFormat.MARKDOWN:
        return to_markdown(report)
    if fmt is ReportFormat.TEXT:
        return to_text(report)
    raise FormattingError(f"'{fmt}' is not a text-renderable format; use to_dict for JSON.")


def to_markdown(report: PricingReport) -> str:
    m = report.metadata
    lines: list[str] = [
        f"# {m.title}",
        "",
        f"**Subject:** {m.subject}  ",
        f"**Objective:** {m.objective}",
    ]
    if m.generated_at:
        lines.append(f"**Generated:** {m.generated_at}")
    lines += ["", "## Executive Summary", ""]
    ex = report.executive_summary
    lines += [
        f"- {ex.overall_recommendation}",
        f"- Current price: {ex.current_price} → recommended: {ex.recommended_price}",
        f"- Expected demand: {ex.expected_demand}, revenue: {ex.expected_revenue}, "
        f"net profit: {ex.expected_net_profit}",
        f"- Expected improvement: {ex.expected_improvement}",
        f"- {ex.key_conclusion}",
    ]

    fin = report.financial
    lines += ["", "## Financial Summary", ""]
    lines += [
        f"- Revenue: {fin.revenue}",
        f"- Gross profit: {fin.gross_profit}",
        f"- Contribution margin: {fin.contribution_margin}",
        f"- Net profit: {fin.net_profit}",
        f"- Gross margin: {fin.gross_margin}",
    ]
    lines += [f"- {n}" for n in fin.notes]

    ela = report.elasticity
    lines += ["", "## Elasticity Analysis", ""]
    lines += [
        f"- Elasticity: {ela.elasticity_coefficient} ({ela.classification})",
        f"- R²: {ela.r_squared}",
        f"- {ela.interpretation}",
    ]
    lines += [f"- {n}" for n in ela.business_implications]

    fc = report.forecast
    lines += ["", "## Forecast Summary", ""]
    lines += [
        f"- Strategy: {fc.selected_strategy} (horizon {fc.horizon})",
        f"- Forecast: {list(fc.forecast_values)}",
        f"- {fc.interpretation}",
    ]
    lines += [f"- {n}" for n in fc.confidence_notes]

    opt = report.optimization
    lines += ["", "## Optimization Summary", ""]
    lines += [
        f"- Objective: {opt.objective}",
        f"- Optimal price: {opt.optimal_price} (value {opt.objective_value})",
        f"- Improvement: {opt.improvement}",
        f"- Search range: {opt.search_range[0]}–{opt.search_range[1]} "
        f"({opt.iterations} evaluations)",
        f"- Binding constraints: {', '.join(opt.binding_constraints) or 'none'}",
    ]

    sc = report.scenario
    lines += [
        "",
        "## Scenario Summary",
        "",
        "| Scenario | Price | Demand | Revenue | Net Profit | Rank |",
        "|---|---|---|---|---|---|",
    ]
    lines += [
        f"| {r.label} | {r.price} | {r.demand} | {r.revenue} | {r.net_profit} | {r.rank} |"
        for r in sc.rows
    ]
    lines += ["", f"- Best: {sc.best_scenario}; Worst: {sc.worst_scenario}"]
    lines += [f"- {o}" for o in sc.observations]

    rec = report.recommendations
    lines += ["", "## Recommendations", "", f"**Action:** {rec.pricing_action}", ""]
    lines += [f"- {r}" for r in rec.recommendations]
    lines += ["", "**Risks:**"] + [f"- {r}" for r in rec.risks]
    lines += ["", "**Monitoring:**"] + [f"- {r}" for r in rec.monitoring]
    lines += ["", "**Implementation:**"] + [f"- {r}" for r in rec.implementation_notes]

    lines += ["", "## Assumptions", ""] + [f"- {a}" for a in report.assumptions.assumptions]
    lines += ["", "## Limitations", ""] + [f"- {limit}" for limit in report.limitations.limitations]
    return "\n".join(lines)


def to_text(report: PricingReport) -> str:
    """Plain text: the Markdown rendering with heading markers stripped."""
    stripped: list[str] = []
    for line in to_markdown(report).splitlines():
        cleaned = line.lstrip("#").strip() if line.startswith("#") else line
        cleaned = cleaned.replace("**", "")
        stripped.append(cleaned)
    return "\n".join(stripped)
