/** Loading / empty / error presentation primitives. */
import type { ReactNode } from "react";

import { cn } from "@/lib/cn";

export function Spinner({ className }: { className?: string }) {
  return (
    <svg
      className={cn("h-4 w-4 animate-spin text-neutral-400", className)}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 0 1 8-8v4a4 4 0 0 0-4 4H4z"
      />
    </svg>
  );
}

export function LoadingSkeleton({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-lg bg-neutral-200/70 dark:bg-neutral-800/70",
        className,
      )}
      aria-hidden="true"
    />
  );
}

export function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="surface flex flex-col items-center justify-center gap-2 p-10 text-center">
      <div className="h-9 w-9 rounded-full bg-neutral-100 dark:bg-neutral-800" aria-hidden="true" />
      <p className="text-sm font-medium text-neutral-700 dark:text-neutral-200">{title}</p>
      {description ? (
        <p className="max-w-sm text-sm text-neutral-500 dark:text-neutral-400">{description}</p>
      ) : null}
      {action}
    </div>
  );
}

export function ErrorState({
  title = "Something went wrong",
  message,
  onRetry,
}: {
  title?: string;
  message?: string;
  onRetry?: () => void;
}) {
  return (
    <div className="surface flex flex-col items-center justify-center gap-3 p-10 text-center">
      <p className="text-sm font-medium text-red-600 dark:text-red-400">{title}</p>
      {message ? (
        <p className="max-w-sm text-sm text-neutral-500 dark:text-neutral-400">{message}</p>
      ) : null}
      {onRetry ? (
        <button type="button" className="btn-ghost" onClick={onRetry}>
          Retry
        </button>
      ) : null}
    </div>
  );
}
