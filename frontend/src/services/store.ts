/** Lightweight client-side UI state (Zustand) — theme + selected product scope. */

import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { Scope } from "@/services/types";

type Theme = "light" | "dark";

interface UiState {
  theme: Theme;
  scope: Scope;
  scopeLabel: string;
  toggleTheme: () => void;
  setScope: (scope: Scope, label: string) => void;
}

export const useUiStore = create<UiState>()(
  persist(
    (set) => ({
      theme: "light",
      scope: "dataset",
      scopeLabel: "Aggregate dataset",
      toggleTheme: () =>
        set((state) => ({ theme: state.theme === "light" ? "dark" : "light" })),
      setScope: (scope, label) => set({ scope, scopeLabel: label }),
    }),
    { name: "dpop-ui" },
  ),
);

/** Apply the persisted theme to <html> (called once at startup and on change). */
export function applyTheme(theme: Theme): void {
  const root = document.documentElement;
  root.classList.toggle("dark", theme === "dark");
}
