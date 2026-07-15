import type { Transition, Variants } from "framer-motion";

/**
 * Central motion vocabulary. Every animation in the app derives from these tokens so the
 * feel stays consistent and the definitions live in exactly one place.
 *
 * Motion is functional: it establishes hierarchy (content settles top-down), gives feedback
 * (state changes are visible), and improves perceived performance (staged reveals mask
 * fetches). Durations are short and confident — nothing lingers.
 *
 * Reduced motion is honored globally by wrapping the app in `<MotionConfig reducedMotion="user">`,
 * which collapses transforms to opacity-only for users who ask for it.
 */

/** Premium deceleration curve — a quick start that eases to a soft stop. */
export const EASE = [0.16, 1, 0.3, 1] as const;
export const EASE_OUT = [0.22, 1, 0.36, 1] as const;

export const DUR = {
  fast: 0.18,
  base: 0.42,
  slow: 0.6,
} as const;

const spring: Transition = { duration: DUR.base, ease: EASE };

/** Content settling into place: rise + fade. The workhorse reveal. */
export const fadeUp: Variants = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: spring },
};

/** A quieter variant for large surfaces (panels, charts) — less travel, slight scale. */
export const surfaceIn: Variants = {
  hidden: { opacity: 0, y: 10, scale: 0.995 },
  show: { opacity: 1, y: 0, scale: 1, transition: { duration: DUR.slow, ease: EASE } },
};

/** Stagger parent: children reveal in sequence so the eye reads structure, not a flash. */
export const staggerContainer = (stagger = 0.06, delay = 0): Variants => ({
  hidden: {},
  show: { transition: { staggerChildren: stagger, delayChildren: delay } },
});

/** Full-page route transition — fast crossfade with a hair of travel. Confident, not showy. */
export const pageVariants: Variants = {
  initial: { opacity: 0, y: 8 },
  enter: { opacity: 1, y: 0, transition: { duration: DUR.base, ease: EASE } },
  exit: { opacity: 0, y: -6, transition: { duration: DUR.fast, ease: "easeIn" } },
};

/** Shared viewport config: reveal once, a little before fully in view. */
export const viewportOnce = { once: true, margin: "0px 0px -12% 0px" } as const;
