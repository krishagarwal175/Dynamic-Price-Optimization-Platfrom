import { useProducts } from "@/services/hooks";
import { useUiStore } from "@/services/store";

export function Topbar({ onMenuClick }: { onMenuClick: () => void }) {
  const scope = useUiStore((s) => s.scope);
  const scopeLabel = useUiStore((s) => s.scopeLabel);
  const setScope = useUiStore((s) => s.setScope);
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

  return (
    <header className="flex h-14 shrink-0 items-center justify-between gap-3 border-b border-line bg-ink-0/80 px-4 backdrop-blur sm:px-6">
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={onMenuClick}
          className="btn-ghost lg:hidden"
          aria-label="Open navigation menu"
        >
          ☰
        </button>
        <label htmlFor="scope" className="eyebrow hidden sm:block">
          Scope
        </label>
        <select
          id="scope"
          className="input max-w-[280px] font-mono text-xs"
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

      <div className="flex items-center gap-2">
        <span className="hidden font-mono text-[11px] uppercase tracking-wider text-neutral-500 md:inline">
          {scopeLabel}
        </span>
        <span className="pl-live inline-block h-1.5 w-1.5 rounded-full bg-accent" aria-hidden="true" />
      </div>
    </header>
  );
}
