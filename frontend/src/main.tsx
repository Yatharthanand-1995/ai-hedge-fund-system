import React, { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import * as Sentry from '@sentry/react'
import './index.css'
// Using full App with ErrorBoundary
import App from './App.tsx'

// Initialize Sentry error tracking (optional - gracefully degrades if not configured)
const SENTRY_DSN = import.meta.env.VITE_SENTRY_DSN
if (SENTRY_DSN) {
  Sentry.init({
    dsn: SENTRY_DSN,
    environment: import.meta.env.VITE_ENVIRONMENT || 'development',
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],
    // Performance Monitoring
    tracesSampleRate: 0.1, // 10% of transactions
    // Session Replay
    replaysSessionSampleRate: 0.1, // 10% of sessions
    replaysOnErrorSampleRate: 1.0, // 100% of sessions with errors
    // Filter out sensitive data
    beforeSend(event) {
      // Remove sensitive data from breadcrumbs and context
      if (event.request?.headers) {
        delete event.request.headers['Authorization']
        delete event.request.headers['Cookie']
      }
      return event
    },
  })
  console.log('✅ Sentry initialized')
} else {
  console.log('ℹ️  Sentry not configured (VITE_SENTRY_DSN not set)')
}

console.log('🌟 main.tsx loaded');
console.log('📦 React version:', React.version);

const rootElement = document.getElementById('root');
console.log('🎯 Root element:', rootElement);

if (!rootElement) {
  console.error('❌ Root element not found!');
  throw new Error('Root element not found');
}

console.log('🚀 Creating React root...');

// Remove loading fallback class
rootElement.classList.remove('loading-fallback');

createRoot(rootElement).render(
  <StrictMode>
    <Sentry.ErrorBoundary
      fallback={({ error, componentStack }) => (
        <div style={{
          padding: '2rem',
          maxWidth: '800px',
          margin: '0 auto',
          fontFamily: 'system-ui'
        }}>
          <h1 style={{ color: '#dc2626', marginBottom: '1rem' }}>
            🚨 Something went wrong
          </h1>
          <p style={{ marginBottom: '1rem' }}>
            The application encountered an unexpected error. Our team has been notified.
          </p>
          <details style={{
            background: '#f3f4f6',
            padding: '1rem',
            borderRadius: '0.5rem',
            marginBottom: '1rem'
          }}>
            <summary style={{ cursor: 'pointer', fontWeight: 'bold' }}>
              Error Details
            </summary>
            <pre style={{
              marginTop: '1rem',
              fontSize: '0.875rem',
              overflow: 'auto'
            }}>
              {error instanceof Error ? error.toString() : String(error)}
              {componentStack}
            </pre>
          </details>
          <button
            onClick={() => window.location.reload()}
            style={{
              background: '#3b82f6',
              color: 'white',
              padding: '0.75rem 1.5rem',
              borderRadius: '0.5rem',
              border: 'none',
              cursor: 'pointer',
              fontSize: '1rem'
            }}
          >
            Reload Page
          </button>
        </div>
      )}
      showDialog
    >
      <App />
    </Sentry.ErrorBoundary>
  </StrictMode>,
);

console.log('✅ React app mounted successfully');

// Check if Tailwind CSS loaded
setTimeout(() => {
  const bodyBg = window.getComputedStyle(document.body).backgroundColor;
  console.log('🎨 Body background color:', bodyBg);

  if (bodyBg === 'rgba(0, 0, 0, 0)' || bodyBg === 'rgb(255, 255, 255)' || bodyBg === 'transparent') {
    console.warn('⚠️ Tailwind CSS may not have loaded! Background is default white/transparent');
  } else {
    console.log('✅ Tailwind CSS loaded successfully');
  }
}, 100);
