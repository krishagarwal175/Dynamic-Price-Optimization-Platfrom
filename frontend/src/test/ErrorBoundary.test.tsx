import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { ErrorBoundary } from "@/app/ErrorBoundary";

function Boom(): never {
  throw new Error("kaboom");
}

describe("ErrorBoundary", () => {
  it("renders children when there is no error", () => {
    render(
      <ErrorBoundary>
        <p>all good</p>
      </ErrorBoundary>,
    );
    expect(screen.getByText("all good")).toBeInTheDocument();
  });

  it("renders a fallback when a child throws", () => {
    // Silence the expected React error log for this render.
    const spy = vi.spyOn(console, "error").mockImplementation(() => {});
    render(
      <ErrorBoundary>
        <Boom />
      </ErrorBoundary>,
    );
    expect(screen.getByText("This view failed to render")).toBeInTheDocument();
    spy.mockRestore();
  });
});
