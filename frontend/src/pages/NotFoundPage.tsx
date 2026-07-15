import { Link } from "react-router-dom";

import { EmptyState } from "@/components/states";

export function NotFoundPage() {
  return (
    <EmptyState
      title="Page not found"
      description="The page you’re looking for doesn’t exist."
      action={
        <Link to="/" className="btn-ghost">
          Back to dashboard
        </Link>
      }
    />
  );
}
