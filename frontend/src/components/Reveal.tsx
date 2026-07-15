import { motion } from "framer-motion";
import type { ReactNode } from "react";

import { fadeUp, staggerContainer, surfaceIn, viewportOnce } from "@/lib/motion";

type Div = React.ComponentProps<typeof motion.div>;

/** Reveal a block as it enters the viewport (once). Rise + fade. */
export function Reveal({
  children,
  className,
  surface,
  ...rest
}: { children: ReactNode; className?: string; surface?: boolean } & Div) {
  return (
    <motion.div
      className={className}
      variants={surface ? surfaceIn : fadeUp}
      initial="hidden"
      whileInView="show"
      viewport={viewportOnce}
      {...rest}
    >
      {children}
    </motion.div>
  );
}

/** Parent that reveals its <StaggerItem> children in sequence on mount. Use for a page's
 *  primary grid so structure reads top-to-bottom instead of appearing all at once. */
export function Stagger({
  children,
  className,
  stagger,
  delay,
  ...rest
}: { children: ReactNode; className?: string; stagger?: number; delay?: number } & Div) {
  return (
    <motion.div
      className={className}
      variants={staggerContainer(stagger, delay)}
      initial="hidden"
      animate="show"
      {...rest}
    >
      {children}
    </motion.div>
  );
}

/** A child of <Stagger>; inherits the reveal trigger from its parent. */
export function StaggerItem({
  children,
  className,
  ...rest
}: { children: ReactNode; className?: string } & Div) {
  return (
    <motion.div className={className} variants={fadeUp} {...rest}>
      {children}
    </motion.div>
  );
}
