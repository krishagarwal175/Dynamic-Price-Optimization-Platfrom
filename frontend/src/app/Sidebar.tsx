import { NavLink } from "react-router-dom";

import { cn } from "@/lib/cn";

import { NAV_ITEMS } from "@/app/nav";

export function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-neutral-200 bg-white dark:border-neutral-800 dark:bg-neutral-900 lg:flex">
      <div className="flex h-14 items-center gap-2 px-5">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-accent text-sm font-bold text-accent-fg">
          P
        </div>
        <div className="leading-tight">
          <p className="text-sm font-semibold text-neutral-900 dark:text-neutral-50">Pricing</p>
          <p className="text-[11px] text-neutral-500 dark:text-neutral-400">Console</p>
        </div>
      </div>
      <nav className="flex-1 space-y-0.5 px-3 py-2" aria-label="Primary">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
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
      <div className="border-t border-neutral-200 p-4 text-[11px] text-neutral-400 dark:border-neutral-800">
        Deterministic analytics · read-only
      </div>
    </aside>
  );
}
