/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Backend origin for production (e.g. https://api.example.com). Empty in dev — the
   *  Vite proxy serves /api. The client appends the /api/v1 prefix itself. */
  readonly VITE_API_BASE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
