/**
 * Error Reporting Service
 *
 * Centralized error logging and reporting for the application.
 * In development, logs to console.
 * In production, can be extended to send to error tracking services (Sentry, etc.)
 */

export interface ErrorReport {
  error: Error;
  errorInfo?: React.ErrorInfo;
  componentName?: string;
  timestamp: string;
  userAgent: string;
  url: string;
  environment: 'development' | 'production';
}

class ErrorReportingService {
  private errorQueue: ErrorReport[] = [];
  private maxQueueSize = 50;

  /**
   * Log an error to the reporting service
   */
  logError(
    error: Error,
    errorInfo?: React.ErrorInfo,
    componentName?: string
  ): void {
    const report: ErrorReport = {
      error,
      errorInfo,
      componentName,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href,
      environment: import.meta.env.MODE as 'development' | 'production'
    };

    // Add to queue
    this.errorQueue.push(report);
    if (this.errorQueue.length > this.maxQueueSize) {
      this.errorQueue.shift(); // Remove oldest
    }

    // Log to console in development
    if (import.meta.env.DEV) {
      console.group(`🔴 Error Report [${componentName || 'Unknown Component'}]`);
      console.error('Error:', error);
      console.error('Component Stack:', errorInfo?.componentStack);
      console.log('Timestamp:', report.timestamp);
      console.log('URL:', report.url);
      console.groupEnd();
    }

    // Send to external service in production
    if (import.meta.env.PROD) {
      this.sendToExternalService(report);
    }
  }

  /**
   * Send error to external tracking service (e.g., Sentry, LogRocket)
   * This is a placeholder - implement based on your service
   */
  private sendToExternalService(report: ErrorReport): void {
    // Example: Send to Sentry
    // if (window.Sentry) {
    //   window.Sentry.captureException(report.error, {
    //     contexts: {
    //       component: {
    //         name: report.componentName,
    //         stack: report.errorInfo?.componentStack
    //       }
    //     },
    //     tags: {
    //       environment: report.environment
    //     }
    //   });
    // }

    // For now, just log a warning
    console.warn('Error reporting not configured for production');
  }

  /**
   * Get all errors in the queue (for debugging)
   */
  getErrorQueue(): ErrorReport[] {
    return [...this.errorQueue];
  }

  /**
   * Clear the error queue
   */
  clearQueue(): void {
    this.errorQueue = [];
  }

  /**
   * Get error statistics
   */
  getStats(): {
    totalErrors: number;
    errorsByComponent: Record<string, number>;
    recentErrors: ErrorReport[];
  } {
    const errorsByComponent: Record<string, number> = {};

    this.errorQueue.forEach(report => {
      const component = report.componentName || 'Unknown';
      errorsByComponent[component] = (errorsByComponent[component] || 0) + 1;
    });

    return {
      totalErrors: this.errorQueue.length,
      errorsByComponent,
      recentErrors: this.errorQueue.slice(-5) // Last 5 errors
    };
  }
}

// Export singleton instance
export const errorReportingService = new ErrorReportingService();

// Expose to window for debugging in dev mode
if (import.meta.env.DEV) {
  (window as any).__errorReportingService = errorReportingService;
}
