import { Component, ReactNode } from "react";
import { AlertCircle } from "lucide-react";

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(_: Error): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, errorInfo: { componentStack: string }) {
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }
      return (
        <div className="bg-slate-800 rounded-xl p-6 border border-red-500/50">
          <div className="flex items-center gap-3 text-red-400">
            <AlertCircle size={20} />
            <span className="font-medium">Something went wrong</span>
          </div>
          <p className="text-gray-400 text-sm mt-2">
            Failed to load this section. Please try refreshing the page.
          </p>
        </div>
      );
    }

    return this.props.children;
  }
}
