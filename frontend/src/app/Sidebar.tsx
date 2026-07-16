import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useState } from "react";

import { DUR, EASE } from "@/lib/motion";

import { NavList } from "@/app/NavList";

function Brand() {
  return (
    <div className="flex h-14 items-center gap-2.5 border-b border-line px-5">
      <div className="flex h-7 w-7 items-center justify-center bg-accent font-display text-sm text-accent-fg">
        P
      </div>
      <div className="leading-none">
        <p className="font-display text-base uppercase tracking-tight text-white">PricingLab</p>
        <p className="mt-0.5 font-mono text-[9px] uppercase tracking-[0.18em] text-neutral-500">
          Console OS
        </p>
      </div>
    </div>
  );
}

function pad(n: number) {
  return String(n).padStart(2, "0");
}

/** Live system-status footer: a running clock signals the console is connected and current,
 *  reinforcing the "operational platform" feel without adding any product surface. */
function SystemStatus() {
  const [time, setTime] = useState("--:--:--");
  useEffect(() => {
    const tick = () => {
      const d = new Date();
      setTime(`${pad(d.getUTCHours())}:${pad(d.getUTCMinutes())}:${pad(d.getUTCSeconds())}`);
    };
    tick();
    const id = window.setInterval(tick, 1000);
    return () => window.clearInterval(id);
  }, []);
  return (
    <div className="border-t border-line p-4">
      <div className="flex items-center justify-between font-mono text-[10.5px] uppercase tracking-[0.12em] text-neutral-500">
        <span className="flex items-center gap-2">
          <span className="pl-live inline-block h-1.5 w-1.5 rounded-full bg-accent" />
          System online
        </span>
        <span className="tabular-nums text-neutral-400">{time} UTC</span>
      </div>
      <p className="mt-1.5 font-mono text-[10px] uppercase tracking-[0.1em] text-neutral-600">
        Deterministic · read-only
      </p>
    </div>
  );
}

export function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-line bg-ink-0 lg:flex">
      <Brand />
      <NavList idPrefix="sidebar" />
      <SystemStatus />
    </aside>
  );
}

/** Off-canvas navigation for viewports below `lg` (the sidebar is hidden there). Slides in
 *  from the edge and fades its scrim; exits reverse so dismissal feels physical. */
export function MobileNav({ open, onClose }: { open: boolean; onClose: () => void }) {
  return (
    <AnimatePresence>
      {open ? (
        <div className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true" aria-label="Menu">
          <motion.button
            type="button"
            aria-label="Close menu"
            className="absolute inset-0 bg-black/60 backdrop-blur-[1px]"
            onClick={onClose}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: DUR.fast }}
          />
          <motion.div
            className="absolute left-0 top-0 flex h-full w-64 flex-col border-r border-line bg-ink-0"
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            transition={{ duration: DUR.base, ease: EASE }}
          >
            <Brand />
            <NavList idPrefix="mobile" onNavigate={onClose} />
          </motion.div>
        </div>
      ) : null}
    </AnimatePresence>
  );
}
