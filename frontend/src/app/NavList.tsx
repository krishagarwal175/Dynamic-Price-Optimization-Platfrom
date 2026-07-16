import { motion } from "framer-motion";
import { NavLink } from "react-router-dom";

import { EASE } from "@/lib/motion";
import { cn } from "@/lib/cn";

import { NAV_ITEMS } from "@/app/nav";

/** The primary navigation links, shared by the desktop sidebar and the mobile drawer.
 *  The active item is marked by a single pill that slides between links (shared layout),
 *  so the current location reads at a glance and route changes feel physically connected.
 *  `idPrefix` keeps the desktop and mobile instances from sharing one animation. */
export function NavList({ onNavigate, idPrefix = "nav" }: { onNavigate?: () => void; idPrefix?: string }) {
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
              "relative flex items-center gap-3 px-3 py-2 text-sm font-medium transition-colors",
              isActive ? "text-accent" : "text-neutral-400 hover:bg-ink-2 hover:text-white",
            )
          }
        >
          {({ isActive }) => (
            <>
              {isActive ? (
                <motion.span
                  layoutId={`${idPrefix}-active`}
                  className="absolute inset-0 -z-10 border-l-2 border-accent bg-accent-muted"
                  transition={{ duration: 0.28, ease: EASE }}
                />
              ) : null}
              <span className={cn("transition-colors", isActive ? "text-accent" : "text-neutral-500")}>
                {item.icon}
              </span>
              {item.label}
            </>
          )}
        </NavLink>
      ))}
    </nav>
  );
}
