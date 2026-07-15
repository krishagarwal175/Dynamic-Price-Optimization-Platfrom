import type { ColumnDef } from "@tanstack/react-table";
import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { DataTable } from "@/components/DataTable";
import { QueryBoundary } from "@/components/QueryBoundary";
import { SectionHeader } from "@/components/SectionHeader";
import { EmptyState } from "@/components/states";
import { formatCurrency } from "@/lib/format";
import { useCategories, useProducts } from "@/services/hooks";
import { useUiStore } from "@/services/store";
import type { ProductSummary } from "@/services/types";

const PAGE_SIZE = 20;

export function CatalogPage() {
  const navigate = useNavigate();
  const setScope = useUiStore((s) => s.setScope);
  const [search, setSearch] = useState("");
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [page, setPage] = useState(0);

  const categories = useCategories();
  const products = useProducts({
    search,
    categoryId,
    limit: PAGE_SIZE,
    offset: page * PAGE_SIZE,
  });

  const columns = useMemo<ColumnDef<ProductSummary, unknown>[]>(
    () => [
      { accessorKey: "sku", header: "SKU" },
      { accessorKey: "name", header: "Name" },
      {
        accessorKey: "base_price",
        header: "Base price",
        cell: (ctx) => (
          <span className="tabular-nums">{formatCurrency(ctx.getValue<number>())}</span>
        ),
      },
    ],
    [],
  );

  const openProduct = (product: ProductSummary) => {
    setScope(product.id, `${product.sku} — ${product.name}`);
    navigate("/financial");
  };

  const total = products.data?.total ?? 0;
  const maxPage = Math.max(0, Math.ceil(total / PAGE_SIZE) - 1);

  return (
    <div>
      <SectionHeader
        title="Catalog"
        description="Browse products. Select one to open its analytics workspace."
      />

      <div className="mb-4 flex flex-wrap items-center gap-2">
        <input
          className="input max-w-xs"
          placeholder="Search SKU or name…"
          value={search}
          onChange={(e) => {
            setSearch(e.target.value);
            setPage(0);
          }}
          aria-label="Search products"
        />
        <select
          className="input max-w-[200px]"
          value={categoryId ?? ""}
          onChange={(e) => {
            setCategoryId(e.target.value ? Number(e.target.value) : null);
            setPage(0);
          }}
          aria-label="Filter by category"
        >
          <option value="">All categories</option>
          {categories.data?.items.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <span className="ml-auto text-sm text-neutral-500 dark:text-neutral-400">
          {total} product{total === 1 ? "" : "s"}
        </span>
      </div>

      <QueryBoundary query={products} skeletonRows={5}>
        {(data) =>
          data.items.length === 0 ? (
            <EmptyState
              title="No products found"
              description="Try a different search, or import a product catalog via the ingestion API."
            />
          ) : (
            <>
              <DataTable columns={columns} data={data.items} onRowClick={openProduct} />
              <div className="mt-3 flex items-center justify-between text-sm">
                <span className="text-neutral-500 dark:text-neutral-400">
                  Page {page + 1} of {maxPage + 1}
                </span>
                <div className="flex gap-2">
                  <button
                    type="button"
                    className="btn-ghost"
                    disabled={page === 0}
                    onClick={() => setPage((p) => Math.max(0, p - 1))}
                  >
                    Previous
                  </button>
                  <button
                    type="button"
                    className="btn-ghost"
                    disabled={page >= maxPage}
                    onClick={() => setPage((p) => Math.min(maxPage, p + 1))}
                  >
                    Next
                  </button>
                </div>
              </div>
            </>
          )
        }
      </QueryBoundary>
    </div>
  );
}
