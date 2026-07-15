import type { ReactNode } from "react";

/** Minimal monochrome icons (16px) — kept simple to avoid visual clutter. */
function Icon({ children }: { children: ReactNode }) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.75"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="h-[18px] w-[18px]"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

export interface NavItem {
  to: string;
  label: string;
  icon: ReactNode;
}

export const NAV_ITEMS: NavItem[] = [
  { to: "/", label: "Dashboard", icon: <Icon><rect x="3" y="3" width="7" height="7" /><rect x="14" y="3" width="7" height="7" /><rect x="3" y="14" width="7" height="7" /><rect x="14" y="14" width="7" height="7" /></Icon> },
  { to: "/catalog", label: "Catalog", icon: <Icon><path d="M4 6h16M4 12h16M4 18h16" /></Icon> },
  { to: "/financial", label: "Financial", icon: <Icon><path d="M12 2v20M17 6H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6" /></Icon> },
  { to: "/elasticity", label: "Elasticity", icon: <Icon><path d="M4 20c8 0 8-14 16-14" /><path d="M4 4v16h16" /></Icon> },
  { to: "/forecast", label: "Forecasting", icon: <Icon><path d="M3 17l5-5 4 4 8-8" /><path d="M16 4h5v5" /></Icon> },
  { to: "/optimization", label: "Optimization", icon: <Icon><circle cx="12" cy="12" r="8" /><path d="M12 8v4l3 2" /></Icon> },
  { to: "/simulation", label: "Simulation", icon: <Icon><path d="M4 4v16M4 8h16M4 16h16" /><circle cx="9" cy="8" r="1.4" /><circle cx="15" cy="16" r="1.4" /></Icon> },
  { to: "/reports", label: "Reports", icon: <Icon><path d="M6 2h9l4 4v16H6z" /><path d="M9 12h7M9 16h7M9 8h3" /></Icon> },
  { to: "/settings", label: "Settings", icon: <Icon><circle cx="12" cy="12" r="3" /><path d="M12 2v3M12 19v3M5 5l2 2M17 17l2 2M2 12h3M19 12h3M5 19l2-2M17 7l2-2" /></Icon> },
];
