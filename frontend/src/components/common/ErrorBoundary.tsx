import React, { Component, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  onReset?: () => void;
  componentName?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

/**
 * ErrorBoundary Component
 *
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of crashing.
 *
 * Usage:
 * <ErrorBoundary componentName="Dashboard Panel">
 *   <YourComponent />
 * </ErrorBoundary>
 */
export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): Partial<ErrorBoundaryState> {
    // Update state so the next render will show the fallback UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    // Log error details for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);

    this.setState({
      error,
      errorInfo
    });

    // You can also log the error to an error reporting service here
    // Example: logErrorToService(error, errorInfo);
  }

  handleReset = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });

    // Call custom reset handler if provided
    if (this.props.onReset) {
      this.props.onReset();
    }
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="professional-card p-6 border-2 border-red-500/20 bg-red-500/5">
          <div className="flex items-start space-x-4">
            <div className="flex-shrink-0">
              <AlertTriangle className="h-8 w-8 text-red-500" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-red-500 mb-2">
                {this.props.componentName
                  ? `${this.props.componentName} Error`
                  : 'Something went wrong'}
              </h3>
              <p className="text-sm text-muted-foreground mb-4">
                {this.state.error?.message || 'An unexpected error occurred in this component.'}
              </p>

              {/* Show error details in development */}
              {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                <details className="mb-4 text-xs">
                  <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                    Technical Details
                  </summary>
                  <pre className="mt-2 p-3 bg-muted rounded text-xs overflow-auto max-h-40">
                    {this.state.error?.stack}
                    {'\n\n'}
                    {this.state.errorInfo.componentStack}
                  </pre>
                </details>
              )}

              <button
                onClick={this.handleReset}
                className="inline-flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium text-sm transition-colors"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Try Again</span>
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

/**
 * withErrorBoundary HOC
 *
 * Higher-Order Component to wrap any component with an ErrorBoundary
 *
 * Usage:
 * export default withErrorBoundary(MyComponent, 'My Component');
 */
export function withErrorBoundary<P extends object>(
  Component: React.ComponentType<P>,
  componentName?: string
): React.ComponentType<P> {
  return function WithErrorBoundaryWrapper(props: P) {
    return (
      <ErrorBoundary componentName={componentName}>
        <Component {...props} />
      </ErrorBoundary>
    );
  };
}
