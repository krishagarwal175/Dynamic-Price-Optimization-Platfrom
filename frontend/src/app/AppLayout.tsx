import { useState } from "react";
import { Outlet } from "react-router-dom";

import { MobileNav, Sidebar } from "@/app/Sidebar";
import { Topbar } from "@/app/Topbar";

export function AppLayout() {
  const [menuOpen, setMenuOpen] = useState(false);
  return (
    <div className="flex h-full">
      <Sidebar />
      <MobileNav open={menuOpen} onClose={() => setMenuOpen(false)} />
      <div className="flex min-w-0 flex-1 flex-col">
        <Topbar onMenuClick={() => setMenuOpen(true)} />
        <main className="flex-1 overflow-y-auto px-4 py-6 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-6xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
