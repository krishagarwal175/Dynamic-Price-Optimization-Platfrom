import { NavList } from "@/app/NavList";

function Brand() {
  return (
    <div className="flex h-14 items-center gap-2 px-5">
      <div className="flex h-7 w-7 items-center justify-center rounded-md bg-accent text-sm font-bold text-accent-fg">
        P
      </div>
      <div className="leading-tight">
        <p className="text-sm font-semibold text-neutral-900 dark:text-neutral-50">Pricing</p>
        <p className="text-[11px] text-neutral-500 dark:text-neutral-400">Console</p>
      </div>
    </div>
  );
}

export function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-neutral-200 bg-white dark:border-neutral-800 dark:bg-neutral-900 lg:flex">
      <Brand />
      <NavList />
      <div className="border-t border-neutral-200 p-4 text-[11px] text-neutral-400 dark:border-neutral-800">
        Deterministic analytics · read-only
      </div>
    </aside>
  );
}

/** Off-canvas navigation for viewports below `lg` (the sidebar is hidden there). */
export function MobileNav({ open, onClose }: { open: boolean; onClose: () => void }) {
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-40 lg:hidden" role="dialog" aria-modal="true" aria-label="Menu">
      <button
        type="button"
        aria-label="Close menu"
        className="absolute inset-0 bg-neutral-900/40"
        onClick={onClose}
      />
      <div className="absolute left-0 top-0 flex h-full w-64 flex-col border-r border-neutral-200 bg-white shadow-xl dark:border-neutral-800 dark:bg-neutral-900">
        <Brand />
        <NavList onNavigate={onClose} />
      </div>
    </div>
  );
}
