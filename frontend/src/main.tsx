import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

// Self-hosted type system (bundled by Vite — no external CDN, works offline / on Vercel):
// Inter for body/data, JetBrains Mono for the technical layer, Anton for condensed display.
import "@fontsource-variable/inter";
import "@fontsource/jetbrains-mono/400.css";
import "@fontsource/jetbrains-mono/500.css";
import "@fontsource/anton/400.css";

import { App } from "@/app/App";
import "@/styles/index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
