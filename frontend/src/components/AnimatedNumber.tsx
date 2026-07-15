import { animate, useReducedMotion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

import { DUR, EASE } from "@/lib/motion";

interface Props {
  value: number;
  /** Format the interpolated value for display (e.g. currency, percent). */
  format?: (n: number) => string;
  /** Start value for the count-up (defaults to 0 on first mount). */
  from?: number;
  durationSeconds?: number;
  className?: string;
}

/**
 * Interpolates to `value` and renders the formatted result — a headline number counting
 * up draws the eye to the figure that matters and reads as "just computed". On reduced
 * motion it snaps to the final value immediately. Subsequent value changes animate from
 * the previously shown number, so scope switches feel continuous rather than jumpy.
 */
export function AnimatedNumber({
  value,
  format = (n) => String(Math.round(n)),
  from,
  durationSeconds = 1.1,
  className,
}: Props) {
  const reduce = useReducedMotion();
  const fmt = useRef(format);
  fmt.current = format;

  const start = from ?? 0;
  const [display, setDisplay] = useState(() => fmt.current(reduce ? value : start));
  const prev = useRef(reduce ? value : start);

  useEffect(() => {
    if (reduce) {
      setDisplay(fmt.current(value));
      prev.current = value;
      return;
    }
    const controls = animate(prev.current, value, {
      duration: Math.max(DUR.base, durationSeconds),
      ease: EASE,
      onUpdate: (v) => setDisplay(fmt.current(v)),
    });
    prev.current = value;
    return () => controls.stop();
    // format is read through a ref so it need not be a dependency
  }, [value, reduce, durationSeconds]);

  return (
    <span className={className} style={{ fontVariantNumeric: "tabular-nums" }}>
      {display}
    </span>
  );
}
