import { AnimatePresence, animate, motion, useReducedMotion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

import { DUR, EASE } from "@/lib/motion";

const STEPS = [
  "Initializing decision engine",
  "Loading elasticity models",
  "Calibrating demand forecasts",
  "Establishing secure session",
  "Rendering console",
] as const;

/**
 * A brief system-initialization sequence shown once per session. It masks the app's first
 * data fetch (perceived performance) and sets the tone of a serious analytical platform —
 * not a decorative splash. Click / any key skips it, and reduced-motion callers never see it.
 */
export function BootSequence({ onDone }: { onDone: () => void }) {
  const reduce = useReducedMotion();
  const [pct, setPct] = useState(0);
  const done = useRef(false);

  const finish = () => {
    if (done.current) return;
    done.current = true;
    onDone();
  };

  useEffect(() => {
    if (reduce) {
      finish();
      return;
    }
    const controls = animate(0, 100, {
      duration: 1.5,
      ease: [0.4, 0, 0.1, 1],
      onUpdate: (v) => setPct(v),
      onComplete: () => setTimeout(finish, 220),
    });
    // Hard safety net: rAF-driven animation can be throttled when the tab is backgrounded,
    // which would trap the user behind the overlay. Force completion regardless.
    const fallback = window.setTimeout(finish, 2600);
    const onKey = () => {
      controls.stop();
      finish();
    };
    window.addEventListener("keydown", onKey);
    return () => {
      controls.stop();
      window.clearTimeout(fallback);
      window.removeEventListener("keydown", onKey);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reduce]);

  if (reduce) return null;

  const active = Math.min(STEPS.length - 1, Math.floor((pct / 100) * STEPS.length));

  return (
    <motion.div
      role="status"
      aria-label="Initializing PricingLab"
      onClick={finish}
      className="fixed inset-0 z-[100] flex items-center justify-center bg-ink-0"
      initial={{ opacity: 1 }}
      exit={{ opacity: 0, filter: "blur(6px)" }}
      transition={{ duration: DUR.base, ease: EASE }}
    >
      <div className="w-full max-w-sm px-8">
        <div className="flex items-center gap-3">
          <span className="grid h-8 w-8 place-items-center bg-accent font-display text-base text-accent-fg">
            P
          </span>
          <div className="leading-none">
            <p className="font-display text-lg uppercase tracking-tight text-white">PricingLab</p>
            <p className="mt-0.5 font-mono text-[10px] uppercase tracking-[0.16em] text-neutral-500">
              Revenue Intelligence OS
            </p>
          </div>
        </div>

        <div className="mt-8 flex items-baseline justify-between">
          <span className="font-mono text-[11px] uppercase tracking-[0.14em] text-neutral-500">
            Initializing
          </span>
          <span className="font-display text-lg tabular-nums text-accent">{Math.round(pct)}%</span>
        </div>

        <div className="mt-2 h-px w-full overflow-hidden bg-ink-3">
          <motion.div className="h-full bg-accent" style={{ width: `${pct}%` }} aria-hidden="true" />
        </div>

        <ul className="mt-6 space-y-1.5">
          {STEPS.map((step, i) => {
            const state = i < active ? "done" : i === active ? "run" : "wait";
            return (
              <li
                key={step}
                className="flex items-center justify-between font-mono text-[11px] tracking-wide"
              >
                <span className={state === "wait" ? "text-neutral-600" : "text-neutral-300"}>
                  {step}
                </span>
                <span
                  className={
                    state === "done"
                      ? "text-accent"
                      : state === "run"
                        ? "text-accent"
                        : "text-neutral-700"
                  }
                >
                  {state === "done" ? "OK" : state === "run" ? "···" : "—"}
                </span>
              </li>
            );
          })}
        </ul>
      </div>
    </motion.div>
  );
}

/** Wraps the boot overlay so it can animate out via <AnimatePresence>. */
export function Boot({ show, onDone }: { show: boolean; onDone: () => void }) {
  return <AnimatePresence>{show ? <BootSequence onDone={onDone} /> : null}</AnimatePresence>;
}
