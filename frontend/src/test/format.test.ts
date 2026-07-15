import { describe, expect, it } from "vitest";

import { formatCurrency, formatPct, formatRatioPct, titleCase } from "@/lib/format";

describe("format helpers", () => {
  it("formats currency", () => {
    expect(formatCurrency(1234.5)).toBe("$1,234.50");
    expect(formatCurrency(null)).toBe("—");
  });

  it("formats a ratio as a percentage", () => {
    expect(formatRatioPct(0.625)).toBe("62.5%");
    expect(formatRatioPct(null)).toBe("—");
  });

  it("formats a signed percentage", () => {
    expect(formatPct(8)).toBe("+8.0%");
    expect(formatPct(-3.5)).toBe("-3.5%");
  });

  it("title-cases snake_case", () => {
    expect(titleCase("highly_elastic")).toBe("Highly Elastic");
  });
});
