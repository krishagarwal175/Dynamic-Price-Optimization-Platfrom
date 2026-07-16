/** Lightweight client-side UI state (Zustand) — the selected product/dataset scope.
 *  The console commits to a single tactical dark theme, so there is no theme state. */

import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { Scope } from "@/services/types";

interface UiState {
  scope: Scope;
  scopeLabel: string;
  setScope: (scope: Scope, label: string) => void;
}

export const useUiStore = create<UiState>()(
  persist(
    (set) => ({
      scope: "dataset",
      scopeLabel: "Aggregate dataset",
      setScope: (scope, label) => set({ scope, scopeLabel: label }),
    }),
    { name: "dpop-ui" },
  ),
);

/** Apply the committed dark theme to <html> (called once at startup). */
export function applyTheme(): void {
  document.documentElement.classList.add("dark");
}
