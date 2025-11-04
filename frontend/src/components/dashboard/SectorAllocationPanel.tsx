import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import { TrendingUp, TrendingDown, Activity, Target, AlertTriangle, RefreshCw } from 'lucide-react';
import { cn, formatPercentage } from '../../utils';
import { SkeletonLoader } from '../common/SkeletonLoader';

interface SectorData {
  name: string;
  allocation: number;
  target: number;
  performance: number;
  momentum: 'bullish' | 'bearish' | 'neutral';
  stocks: number;
  avgScore: number;
  riskLevel: 'low' | 'medium' | 'high';
}

interface SectorAllocationPanelProps {
  className?: string;
}

// Color mapping for all 7 sectors
const SECTOR_COLORS = {
  'Technology': '#0088FE',
  'Healthcare': '#00C49F',
  'Financial': '#FFBB28',
  'Consumer': '#FF8042',
  'Energy': '#8884d8',
  'Industrial': '#a855f7',  // Purple for Industrial
  'Communication': '#82ca9d'
};

export const SectorAllocationPanel: React.FC<SectorAllocationPanelProps> = ({ className }) => {
  const [sectorData, setSectorData] = useState<SectorData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'allocation' | 'performance'>('allocation');

  const fetchSectorData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch('http://localhost:8010/portfolio/sector-analysis');
      if (!response.ok) {
        throw new Error('Unable to fetch sector analysis. Please check your connection.');
      }

      const data = await response.json();
      const sectors = data.sectors || [];

      // Map API response to component data structure
      const mappedSectorData: SectorData[] = sectors.map((sector: any) => ({
        name: sector.name,
        allocation: sector.allocation,
        target: sector.target,
        performance: sector.performance,
        momentum: sector.momentum as 'bullish' | 'bearish' | 'neutral',
        stocks: sector.stocks,
        avgScore: sector.avgScore,
        riskLevel: sector.riskLevel as 'low' | 'medium' | 'high'
      }));

      setSectorData(mappedSectorData);
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load sector data. Please try again.';
      setError(errorMessage);
      console.error('Failed to fetch sector data:', err);
      setSectorData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSectorData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const getMomentumColor = (momentum: string) => {
    switch (momentum) {
      case 'bullish': return 'text-green-400';
      case 'bearish': return 'text-red-400';
      case 'neutral': return 'text-yellow-400';
      default: return 'text-gray-400';
    }
  };

  const getMomentumIcon = (momentum: string) => {
    switch (momentum) {
      case 'bullish': return <TrendingUp className="h-4 w-4" />;
      case 'bearish': return <TrendingDown className="h-4 w-4" />;
      case 'neutral': return <Activity className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'text-green-400';
      case 'medium': return 'text-yellow-400';
      case 'high': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 75) return 'text-green-400';
    if (score >= 65) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getPerformanceColor = (performance: number) => {
    return performance >= 0 ? 'text-green-400' : 'text-red-400';
  };

  const getAllocationDeviation = (current: number, target: number) => {
    return Math.abs(current - target);
  };

  if (loading) {
    return (
      <div className={cn('professional-card p-6', className)}>
        <div className="flex items-center justify-between mb-6">
          <SkeletonLoader variant="text" lines={1} height="24px" className="w-48" />
          <div className="flex space-x-2">
            <SkeletonLoader variant="button" height="40px" />
            <SkeletonLoader variant="button" height="40px" />
          </div>
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SkeletonLoader variant="chart" />
          <div className="space-y-4">
            <SkeletonLoader variant="card" />
            <SkeletonLoader variant="card" />
            <SkeletonLoader variant="card" />
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn('professional-card p-6 border-2 border-red-500/20 bg-red-500/5', className)}>
        <div className="flex items-start space-x-4">
          <AlertTriangle className="h-6 w-6 text-red-500 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-red-500 mb-2">Failed to Load Sector Analysis</h3>
            <p className="text-sm text-muted-foreground mb-4">{error}</p>
            <button
              onClick={fetchSectorData}
              className="inline-flex items-center space-x-2 px-4 py-2 bg-accent hover:bg-accent/80 text-accent-foreground rounded-lg font-medium text-sm transition-colors"
            >
              <RefreshCw className="h-4 w-4" />
              <span>Retry</span>
            </button>
          </div>
        </div>
      </div>
    );
  }

  const pieData = sectorData.map(sector => ({
    name: sector.name,
    value: sector.allocation,
    color: SECTOR_COLORS[sector.name as keyof typeof SECTOR_COLORS] || '#8884d8'
  }));

  const performanceData = sectorData.map(sector => ({
    name: sector.name,
    performance: sector.performance,
    avgScore: sector.avgScore
  }));

  return (
    <div className={cn('professional-card p-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-foreground">Sector Analysis</h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setViewMode('allocation')}
            className={cn('px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              viewMode === 'allocation'
                ? 'bg-accent text-accent-foreground'
                : 'text-muted-foreground hover:bg-muted/20'
            )}
          >
            Allocation
          </button>
          <button
            onClick={() => setViewMode('performance')}
            className={cn('px-3 py-2 rounded-lg text-sm font-medium transition-colors',
              viewMode === 'performance'
                ? 'bg-accent text-accent-foreground'
                : 'text-muted-foreground hover:bg-muted/20'
            )}
          >
            Performance
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart Section */}
        <div>
          {viewMode === 'allocation' ? (
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-4">Current Allocation</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}%`}
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => [`${value}%`, 'Allocation']} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          ) : (
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-4">Performance & Scores</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={performanceData}>
                    <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip
                      formatter={(value, name) => [
                        name === 'performance' ? `${value}%` : value,
                        name === 'performance' ? 'Performance' : 'Avg Score'
                      ]}
                    />
                    <Legend />
                    <Bar dataKey="performance" fill="#0088FE" name="Performance (%)" />
                    <Bar dataKey="avgScore" fill="#00C49F" name="Avg Score" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </div>

        {/* Sector Details */}
        <div>
          <h3 className="text-lg font-semibold text-foreground mb-4">Sector Details</h3>
          <div className="space-y-4 max-h-64 overflow-y-auto">
            {sectorData.map((sector) => (
              <div key={sector.name} className="professional-card p-4 bg-muted/20">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: SECTOR_COLORS[sector.name as keyof typeof SECTOR_COLORS] }}
                    />
                    <span className="font-medium text-foreground">{sector.name}</span>
                  </div>
                  <div className={cn('flex items-center space-x-1', getMomentumColor(sector.momentum))}>
                    {getMomentumIcon(sector.momentum)}
                    <span className="text-sm">{sector.momentum}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div>
                    <div className="text-muted-foreground">Allocation</div>
                    <div className="font-medium">
                      {formatPercentage(sector.allocation)}
                      {getAllocationDeviation(sector.allocation, sector.target) > 2 && (
                        <span className="text-yellow-400 ml-1">
                          <Target className="h-3 w-3 inline" />
                        </span>
                      )}
                    </div>
                    <div className="text-xs text-muted-foreground">
                      Target: {formatPercentage(sector.target)}
                    </div>
                  </div>

                  <div>
                    <div className="text-muted-foreground">Performance</div>
                    <div className={cn('font-medium', getPerformanceColor(sector.performance))}>
                      {sector.performance >= 0 ? '+' : ''}{formatPercentage(sector.performance)}
                    </div>
                  </div>

                  <div>
                    <div className="text-muted-foreground">Avg Score</div>
                    <div className={cn('font-medium', getScoreColor(sector.avgScore))}>
                      {sector.avgScore}
                    </div>
                  </div>

                  <div>
                    <div className="text-muted-foreground">Risk</div>
                    <div className={cn('font-medium capitalize', getRiskColor(sector.riskLevel))}>
                      {sector.riskLevel}
                    </div>
                  </div>
                </div>

                <div className="mt-2 text-xs text-muted-foreground">
                  {sector.stocks} stocks in sector
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Sector Alerts */}
      <div className="mt-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">Sector Alerts</h3>
        <div className="space-y-2">
          {sectorData
            .filter(sector => getAllocationDeviation(sector.allocation, sector.target) > 3)
            .map(sector => (
              <div key={sector.name} className="flex items-center space-x-2 text-sm bg-yellow-500/10 text-yellow-400 p-3 rounded-lg">
                <AlertTriangle className="h-4 w-4" />
                <span>
                  <strong>{sector.name}</strong> is {sector.allocation > sector.target ? 'overweight' : 'underweight'}
                  by {Math.abs(sector.allocation - sector.target).toFixed(1)}% - Consider rebalancing
                </span>
              </div>
            ))}
          {sectorData.filter(sector => getAllocationDeviation(sector.allocation, sector.target) > 3).length === 0 && (
            <div className="text-sm text-green-400 bg-green-500/10 p-3 rounded-lg">
              All sectors are within target allocation ranges
            </div>
          )}
        </div>
      </div>
    </div>
  );
};