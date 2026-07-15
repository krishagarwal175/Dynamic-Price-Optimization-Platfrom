import { useProducts } from "@/services/hooks";
import { applyTheme, useUiStore } from "@/services/store";

export function Topbar() {
  const { scope, scopeLabel, setScope, theme, toggleTheme } = useUiStore();
  const products = useProducts({ limit: 200 });

  const onScopeChange = (value: string) => {
    if (value === "dataset") {
      setScope("dataset", "Aggregate dataset");
      return;
    }
    const id = Number(value);
    const product = products.data?.items.find((p) => p.id === id);
    setScope(id, product ? `${product.sku} — ${product.name}` : `Product ${id}`);
  };

  const onToggleTheme = () => {
    toggleTheme();
    applyTheme(theme === "light" ? "dark" : "light");
  };

  return (
    <header className="flex h-14 shrink-0 items-center justify-between gap-3 border-b border-neutral-200 bg-white/80 px-4 backdrop-blur dark:border-neutral-800 dark:bg-neutral-900/80 sm:px-6">
      <div className="flex items-center gap-2">
        <label htmlFor="scope" className="text-xs font-medium text-neutral-500 dark:text-neutral-400">
          Scope
        </label>
        <select
          id="scope"
          className="input max-w-[280px]"
          value={scope === "dataset" ? "dataset" : String(scope)}
          onChange={(e) => onScopeChange(e.target.value)}
        >
          <option value="dataset">Aggregate dataset</option>
          {products.data?.items.map((p) => (
            <option key={p.id} value={p.id}>
              {p.sku} — {p.name}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center gap-3">
        <span className="hidden text-xs text-neutral-400 sm:inline">{scopeLabel}</span>
        <button
          type="button"
          onClick={onToggleTheme}
          className="btn-ghost"
          aria-label="Toggle color theme"
        >
          {theme === "light" ? "Dark" : "Light"}
        </button>
      </div>
    </header>
  );
}
