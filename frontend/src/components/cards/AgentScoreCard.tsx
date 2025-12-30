import React from 'react';
import { cn, getScoreColorClass, getAgentColor, getAgentWeight, formatPercentage } from '../../utils';
import { type AgentType } from '../../types/api';

interface AgentScoreCardProps {
  agent: AgentType;
  score: number;
  confidence?: number;
  reasoning?: string;
  className?: string;
  showWeight?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

const agentLabels: Record<AgentType, string> = {
  fundamentals: 'Fundamentals',
  momentum: 'Momentum',
  quality: 'Quality',
  sentiment: 'Sentiment',
  institutional_flow: 'Institutional Flow',
};

const agentDescriptions: Record<AgentType, string> = {
  fundamentals: 'Financial health, profitability, growth, and valuation',
  momentum: 'Technical analysis and price trend evaluation',
  quality: 'Business characteristics and operational efficiency',
  sentiment: 'Market sentiment and analyst outlook analysis',
  institutional_flow: 'Smart money detection and institutional buying/selling patterns',
};

export const AgentScoreCard: React.FC<AgentScoreCardProps> = ({
  agent,
  score,
  confidence,
  reasoning,
  className,
  showWeight = true,
  size = 'md',
}) => {
  const weight = getAgentWeight(agent);
  const weightedScore = score * weight;
  const color = getAgentColor(agent);
  const scoreClass = getScoreColorClass(score);

  const sizeClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const scoreSizes = {
    sm: 'text-2xl',
    md: 'text-3xl',
    lg: 'text-4xl',
  };

  const radius = size === 'sm' ? 45 : size === 'md' ? 60 : 75;
  const strokeWidth = size === 'sm' ? 6 : size === 'md' ? 8 : 10;
  const normalizedRadius = radius - strokeWidth * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDasharray = `${(score / 100) * circumference} ${circumference}`;

  return (
    <div className={cn('professional-card', sizeClasses[size], className)}>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-foreground text-lg">
            {agentLabels[agent]}
          </h3>
          {showWeight && (
            <p className="text-sm text-muted-foreground">
              Weight: {formatPercentage(weight * 100, 0)}
            </p>
          )}
        </div>
        <div className="relative">
          <svg
            height={radius * 2}
            width={radius * 2}
            className="transform -rotate-90"
          >
            {/* Background circle */}
            <circle
              stroke="currentColor"
              fill="transparent"
              strokeWidth={strokeWidth}
              r={normalizedRadius}
              cx={radius}
              cy={radius}
              className="text-border"
            />
            {/* Progress circle */}
            <circle
              stroke={color}
              fill="transparent"
              strokeWidth={strokeWidth}
              strokeDasharray={strokeDasharray}
              strokeLinecap="round"
              r={normalizedRadius}
              cx={radius}
              cy={radius}
              className="transition-all duration-1000 ease-out"
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className={cn('font-bold', scoreSizes[size], scoreClass)}>
              {Math.round(score)}
            </span>
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <p className="text-sm text-muted-foreground">
          {agentDescriptions[agent]}
        </p>

        <div className="flex justify-between items-center text-sm">
          <span className="text-muted-foreground">Weighted Score:</span>
          <span className={cn('font-medium', scoreClass)}>
            {weightedScore.toFixed(1)}
          </span>
        </div>

        {confidence !== undefined && (
          <div className="flex justify-between items-center text-sm">
            <span className="text-muted-foreground">Confidence:</span>
            <span className="font-medium text-foreground">
              {formatPercentage(confidence * 100, 0)}
            </span>
          </div>
        )}

        {reasoning && (
          <div className="text-xs text-muted-foreground mt-2 p-2 bg-muted/20 rounded">
            <strong>Analysis:</strong> {reasoning}
          </div>
        )}
      </div>

      {/* Progress bar for weighted contribution */}
      {showWeight && (
        <div className="mt-4">
          <div className="flex justify-between text-xs text-muted-foreground mb-1">
            <span>Contribution to Overall Score</span>
            <span>{weightedScore.toFixed(1)}/100</span>
          </div>
          <div className="w-full bg-border rounded-full h-2">
            <div
              className="h-2 rounded-full transition-all duration-1000 ease-out"
              style={{
                width: `${(weightedScore / 100) * 100}%`,
                backgroundColor: color,
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};