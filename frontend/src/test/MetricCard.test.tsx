import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { MetricCard } from "@/components/MetricCard";

describe("MetricCard", () => {
  it("renders label and value", () => {
    render(<MetricCard label="Revenue" value="$500.00" />);
    expect(screen.getByText("Revenue")).toBeInTheDocument();
    expect(screen.getByText("$500.00")).toBeInTheDocument();
  });

  it("shows a skeleton while loading", () => {
    const { container } = render(<MetricCard label="Revenue" value="$500.00" loading />);
    expect(screen.queryByText("$500.00")).not.toBeInTheDocument();
    expect(container.querySelector(".animate-pulse")).toBeTruthy();
  });
});
