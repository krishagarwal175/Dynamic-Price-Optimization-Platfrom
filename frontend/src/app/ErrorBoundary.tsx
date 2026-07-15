import { Component, type ErrorInfo, type ReactNode } from "react";

import { ErrorState } from "@/components/states";

interface Props {
  children: ReactNode;
}

interface State {
  error: Error | null;
}

/** Catches render-time exceptions so a single thrown error shows a fallback instead of
 *  unmounting the whole app to a blank screen. Query errors are handled by QueryBoundary;
 *  this is the backstop for everything else. */
export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("Unhandled UI error:", error, info.componentStack);
  }

  private reset = () => this.setState({ error: null });

  render(): ReactNode {
    if (this.state.error) {
      return (
        <ErrorState
          title="This view failed to render"
          message="An unexpected error occurred. You can retry, or navigate to another page."
          onRetry={this.reset}
        />
      );
    }
    return this.props.children;
  }
}
