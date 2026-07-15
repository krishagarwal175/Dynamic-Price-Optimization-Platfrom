import type { UseQueryResult } from "@tanstack/react-query";
import type { ReactNode } from "react";

import { ApiError } from "@/services/client";

import { ErrorState, LoadingSkeleton } from "@/components/states";

interface Props<T> {
  query: UseQueryResult<T>;
  children: (data: T) => ReactNode;
  /** Treat a 422 (no analytics data) as an empty state rather than an error. */
  emptyMessage?: string;
  skeletonRows?: number;
}

/** Renders loading / error / empty around a query, then the data. */
export function QueryBoundary<T>({
  query,
  children,
  emptyMessage = "No data available yet.",
  skeletonRows = 3,
}: Props<T>) {
  if (query.isPending) {
    return (
      <div className="grid gap-3">
        {Array.from({ length: skeletonRows }).map((_, i) => (
          <LoadingSkeleton key={i} className="h-24" />
        ))}
      </div>
    );
  }

  if (query.isError) {
    const err = query.error;
    if (err instanceof ApiError && (err.status === 422 || err.status === 404)) {
      return <ErrorState title="Not enough data" message={emptyMessage} onRetry={() => query.refetch()} />;
    }
    const message = err instanceof Error ? err.message : "Unexpected error.";
    return <ErrorState message={message} onRetry={() => query.refetch()} />;
  }

  return <>{children(query.data)}</>;
}
