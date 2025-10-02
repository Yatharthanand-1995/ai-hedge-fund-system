import React, { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
// Using full App with ErrorBoundary
import App from './App.tsx'

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
    <App />
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
