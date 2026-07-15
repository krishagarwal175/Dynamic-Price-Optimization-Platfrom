import { NavLink } from "react-router-dom";

import { cn } from "@/lib/cn";

import { NAV_ITEMS } from "@/app/nav";

/** The primary navigation links, shared by the desktop sidebar and the mobile drawer. */
export function NavList({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="flex-1 space-y-0.5 px-3 py-2" aria-label="Primary">
      {NAV_ITEMS.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === "/"}
          onClick={onNavigate}
          className={({ isActive }) =>
            cn(
              "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
              isActive
                ? "bg-accent-muted text-accent dark:bg-indigo-950/50 dark:text-indigo-300"
                : "text-neutral-600 hover:bg-neutral-100 dark:text-neutral-300 dark:hover:bg-neutral-800",
            )
          }
        >
          <span className="text-neutral-400">{item.icon}</span>
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}
