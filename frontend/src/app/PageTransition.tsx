import { AnimatePresence, motion } from "framer-motion";
import { useLocation, useOutlet } from "react-router-dom";

import { pageVariants } from "@/lib/motion";

/**
 * Crossfades routed pages. `mode="wait"` keeps the two views from overlapping; the exit is
 * deliberately faster than the enter so navigation feels instant and confident rather than
 * drawn out. The initial page does not animate (the boot sequence covers first paint, and
 * each page staggers its own content in).
 */
export function PageTransition() {
  const location = useLocation();
  const outlet = useOutlet();
  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={location.pathname}
        variants={pageVariants}
        initial="initial"
        animate="enter"
        exit="exit"
        style={{ willChange: "opacity, transform" }}
      >
        {outlet}
      </motion.div>
    </AnimatePresence>
  );
}
