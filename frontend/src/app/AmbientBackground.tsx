/**
 * A near-invisible engineering grid behind the app. It gives the surface a sense of a
 * coordinate system — depth and precision — without competing with content. It is fixed,
 * non-interactive, and drifts extremely slowly (disabled under reduced motion via CSS).
 */
export function AmbientBackground() {
  return <div className="ambient-grid" aria-hidden="true" />;
}
