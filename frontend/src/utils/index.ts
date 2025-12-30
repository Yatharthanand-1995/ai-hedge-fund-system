import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { type RecommendationType, type ConfidenceLevel, type AgentType } from '../types/api';

// Utility function for combining Tailwind classes
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// Format numbers for display
export function formatNumber(value: number, decimals: number = 2): string {
  if (Math.abs(value) >= 1e9) {
    return (value / 1e9).toFixed(decimals) + 'B';
  }
  if (Math.abs(value) >= 1e6) {
    return (value / 1e6).toFixed(decimals) + 'M';
  }
  if (Math.abs(value) >= 1e3) {
    return (value / 1e3).toFixed(decimals) + 'K';
  }
  return value.toFixed(decimals);
}

// Format percentage
export function formatPercentage(value: number, decimals: number = 2): string {
  return `${value.toFixed(decimals)}%`;
}

// Format currency
export function formatCurrency(value: number, currency: string = 'USD'): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

// Get score color class based on score value
export function getScoreColorClass(score: number): string {
  if (score >= 80) return 'score-excellent';
  if (score >= 65) return 'score-good';
  if (score >= 45) return 'score-neutral';
  if (score >= 25) return 'score-poor';
  return 'score-bad';
}

// Get recommendation color class
export function getRecommendationColorClass(recommendation: RecommendationType): string {
  const classes: Record<RecommendationType, string> = {
    'STRONG BUY': 'recommendation-strong-buy',
    'BUY': 'recommendation-buy',
    'WEAK BUY': 'recommendation-weak-buy',
    'HOLD': 'recommendation-hold',
    'WEAK SELL': 'recommendation-weak-sell',
    'SELL': 'recommendation-sell',
  };
  return classes[recommendation] || 'recommendation-hold';
}

// Get confidence level color
export function getConfidenceColorClass(confidence: ConfidenceLevel): string {
  const classes: Record<ConfidenceLevel, string> = {
    'HIGH': 'text-green-400',
    'MEDIUM': 'text-yellow-400',
    'LOW': 'text-red-400',
  };
  return classes[confidence] || 'text-gray-400';
}

// Get agent color
export function getAgentColor(agent: AgentType): string {
  const colors: Record<AgentType, string> = {
    fundamentals: '#3b82f6', // blue-500
    momentum: '#10b981', // emerald-500
    quality: '#8b5cf6', // violet-500
    sentiment: '#f59e0b', // amber-500
    institutional_flow: '#ec4899', // pink-500
  };
  return colors[agent];
}

// Get agent weight
export function getAgentWeight(agent: AgentType): number {
  const weights: Record<AgentType, number> = {
    fundamentals: 0.36, // 36%
    momentum: 0.27, // 27%
    quality: 0.18, // 18%
    sentiment: 0.09, // 9%
    institutional_flow: 0.10, // 10%
  };
  return weights[agent];
}

// Calculate weighted score
export function calculateWeightedScore(scores: Record<AgentType, number>): number {
  const agents: AgentType[] = ['fundamentals', 'momentum', 'quality', 'sentiment', 'institutional_flow'];
  return agents.reduce((total, agent) => {
    return total + (scores[agent] * getAgentWeight(agent));
  }, 0);
}

// Format time ago
export function formatTimeAgo(timestamp: string): string {
  const now = new Date();
  const date = new Date(timestamp);
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);

  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
}

// Validate stock symbol
export function isValidStockSymbol(symbol: string): boolean {
  const trimmed = symbol.trim().toUpperCase();
  return /^[A-Z]{1,5}$/.test(trimmed);
}

// Debounce function
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;
  return (...args: Parameters<T>) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func.apply(null, args), delay);
  };
}

// Throttle function
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  return (...args: Parameters<T>) => {
    const now = new Date().getTime();
    if (now - lastCall < delay) return;
    lastCall = now;
    return func.apply(null, args);
  };
}

// Generate random ID
export function generateId(): string {
  return Math.random().toString(36).substr(2, 9);
}

// Copy to clipboard
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    return false;
  }
}

// Safe JSON parse
export function safeJSONParse<T>(json: string, fallback: T): T {
  try {
    return JSON.parse(json);
  } catch {
    return fallback;
  }
}