import {
  type ColumnDef,
  type SortingState,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { useState } from "react";

import { cn } from "@/lib/cn";

interface Props<T> {
  columns: ColumnDef<T, unknown>[];
  data: T[];
  onRowClick?: (row: T) => void;
}

/** A headless-table wrapper with column sorting and optional row selection. */
export function DataTable<T>({ columns, data, onRowClick }: Props<T>) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const table = useReactTable({
    data,
    columns,
    state: { sorting },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
  });

  return (
    <div className="surface overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="border-b border-neutral-200 bg-neutral-50/60 dark:border-neutral-800 dark:bg-neutral-900">
          {table.getHeaderGroups().map((group) => (
            <tr key={group.id}>
              {group.headers.map((header) => {
                const sortable = header.column.getCanSort();
                const dir = header.column.getIsSorted();
                const label = flexRender(header.column.columnDef.header, header.getContext());
                const indicator = dir ? (
                  <span aria-hidden="true">{dir === "asc" ? "↑" : "↓"}</span>
                ) : null;
                return (
                  <th
                    key={header.id}
                    className="px-4 py-2.5 text-left text-xs font-semibold uppercase tracking-wide text-neutral-500 dark:text-neutral-400"
                    aria-sort={dir === "asc" ? "ascending" : dir === "desc" ? "descending" : "none"}
                  >
                    {sortable ? (
                      <button
                        type="button"
                        className="inline-flex select-none items-center gap-1 uppercase tracking-wide"
                        onClick={header.column.getToggleSortingHandler()}
                      >
                        {label}
                        {indicator}
                      </button>
                    ) : (
                      <span className="inline-flex items-center gap-1">
                        {label}
                        {indicator}
                      </span>
                    )}
                  </th>
                );
              })}
            </tr>
          ))}
        </thead>
        <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800">
          {table.getRowModel().rows.map((row) => (
            <tr
              key={row.id}
              className={cn(
                "transition-colors",
                onRowClick && "cursor-pointer hover:bg-neutral-50 dark:hover:bg-neutral-800/50",
              )}
              onClick={onRowClick ? () => onRowClick(row.original) : undefined}
            >
              {row.getVisibleCells().map((cell) => (
                <td key={cell.id} className="px-4 py-2.5 text-neutral-700 dark:text-neutral-200">
                  {flexRender(cell.column.columnDef.cell, cell.getContext())}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
