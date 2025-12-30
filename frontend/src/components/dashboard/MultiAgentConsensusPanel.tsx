import React, { useState, useEffect } from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip } from 'recharts';
import { Brain, AlertCircle, CheckCircle, Users, Target, RefreshCw, AlertTriangle } from 'lucide-react';
import { cn, formatPercentage } from '../../utils';
import { SkeletonLoader } from '../common/SkeletonLoader';

interface AgentData {
  name: string;
  score: number;
  confidence: number;
  weight: number;
  accuracy: number;
  reasoning: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
}

interface ConsensusData {
  symbol: string;
  overallScore: number;
  consensus: 'strong' | 'moderate' | 'weak';
  agreement: number;
  conflictAreas: string[];
  topReason: string;
  agents: AgentData[];
}

interface MultiAgentConsensusPanelProps {
  className?: string;
}

export const MultiAgentConsensusPanel: React.FC<MultiAgentConsensusPanelProps> = ({ className }) => {
  const [consensusData, setConsensusData] = useState<ConsensusData[]>([]);
  const [selectedStock, setSelectedStock] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchConsensusData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch consensus data for top stocks
      const response = await fetch('http://localhost:8010/analyze/consensus?symbols=AAPL,MSFT,GOOGL,NVDA,TSLA');

      if (!response.ok) {
        throw new Error('Unable to fetch consensus data. Please check your connection.');
      }

      const data = await response.json();
      const consensusArray: ConsensusData[] = data.consensus || [];

      setConsensusData(consensusArray);
      if (consensusArray.length > 0) {
        setSelectedStock(consensusArray[0].symbol);
      }
      setError(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load consensus data. Please try again.';
      setError(errorMessage);
      console.error('Failed to fetch consensus data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConsensusData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const getConsensusColor = (consensus: string) => {
    switch (consensus) {
      case 'strong': return 'text-green-400';
      case 'moderate': return 'text-yellow-400';
      case 'weak': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getConsensusIcon = (consensus: string) => {
    switch (consensus) {
      case 'strong': return <CheckCircle className="h-5 w-5" />;
      case 'moderate': return <AlertCircle className="h-5 w-5" />;
      case 'weak': return <AlertCircle className="h-5 w-5" />;
      default: return <Users className="h-5 w-5" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-400';
      case 'degraded': return 'text-yellow-400';
      case 'unhealthy': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-400';
    if (score >= 60) return 'text-yellow-400';
    return 'text-red-400';
  };

  const handleViewFullAnalysis = () => {
    console.log('View Full Analysis clicked for', selectedStock);
    alert(`View Full Analysis - ${selectedStock}\n\nIn a real app, this would:\n• Navigate to detailed stock analysis page\n• Show comprehensive agent breakdowns\n• Display historical scoring trends\n• Include full investment thesis`);
  };

  const handleCompareStocks = () => {
    console.log('Compare Stocks clicked');
    alert('Compare Stocks\n\nIn a real app, this would:\n• Show side-by-side stock comparison\n• Compare all agent scores\n• Highlight key differences\n• Recommend best pick');
  };

  const handleExportReport = () => {
    if (!selectedData) return;
    const dataStr = JSON.stringify(selectedData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `consensus-analysis-${selectedStock}.json`;
    link.click();
    URL.revokeObjectURL(url);
    console.log('Exported consensus report for', selectedStock);
  };

  if (loading) {
    return (
      <div className={cn('professional-card p-6', className)}>
        <div className="flex items-center justify-between mb-6">
          <SkeletonLoader variant="text" lines={1} height="24px" className="w-48" />
          <SkeletonLoader variant="button" height="40px" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
          {[1, 2, 3, 4, 5].map(i => (
            <div key={i} className="text-center">
              <SkeletonLoader variant="text" lines={2} />
            </div>
          ))}
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <SkeletonLoader variant="chart" />
          <div className="space-y-3">
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
            <h3 className="text-lg font-semibold text-red-500 mb-2">Failed to Load AI Consensus</h3>
            <p className="text-sm text-muted-foreground mb-4">{error}</p>
            <button
              onClick={fetchConsensusData}
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

  const selectedData = consensusData.find(item => item.symbol === selectedStock);

  const radarData = selectedData?.agents.map(agent => ({
    agent: agent.name,
    score: agent.score,
    confidence: agent.confidence * 100,
    accuracy: agent.accuracy
  })) || [];

  return (
    <div className={cn('professional-card p-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-foreground flex items-center space-x-2">
          <Brain className="h-6 w-6 text-accent" />
          <span>AI Agent Consensus</span>
        </h2>
        <div className="flex space-x-2">
          <select
            value={selectedStock}
            onChange={(e) => setSelectedStock(e.target.value)}
            className="bg-muted border border-border rounded-lg px-3 py-2 text-sm text-foreground"
          >
            {consensusData.map(item => (
              <option key={item.symbol} value={item.symbol}>{item.symbol}</option>
            ))}
          </select>
        </div>
      </div>

      {selectedData && (
        <>
          {/* Consensus Overview */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
            <div className="text-center">
              <div className="text-sm text-muted-foreground mb-1">Overall Score</div>
              <div className={cn('text-2xl font-bold', getScoreColor(selectedData.overallScore))}>
                {selectedData.overallScore.toFixed(1)}
              </div>
            </div>

            <div className="text-center">
              <div className="text-sm text-muted-foreground mb-1">Consensus</div>
              <div className={cn('text-lg font-bold flex items-center justify-center space-x-1',
                getConsensusColor(selectedData.consensus))}>
                {getConsensusIcon(selectedData.consensus)}
                <span className="capitalize">{selectedData.consensus}</span>
              </div>
            </div>

            <div className="text-center">
              <div className="text-sm text-muted-foreground mb-1">Agreement</div>
              <div className={cn('text-2xl font-bold',
                selectedData.agreement >= 90 ? 'text-green-400' :
                selectedData.agreement >= 75 ? 'text-yellow-400' : 'text-red-400')}>
                {selectedData.agreement}%
              </div>
            </div>

            <div className="text-center">
              <div className="text-sm text-muted-foreground mb-1">Conflicts</div>
              <div className={cn('text-2xl font-bold',
                selectedData.conflictAreas.length === 0 ? 'text-green-400' : 'text-red-400')}>
                {selectedData.conflictAreas.length}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Radar Chart */}
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-4">Agent Performance Radar</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={radarData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="agent" tick={{ fontSize: 12 }} />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} tick={{ fontSize: 10 }} />
                    <Radar
                      name="Score"
                      dataKey="score"
                      stroke="#0088FE"
                      fill="#0088FE"
                      fillOpacity={0.3}
                    />
                    <Radar
                      name="Confidence"
                      dataKey="confidence"
                      stroke="#00C49F"
                      fill="#00C49F"
                      fillOpacity={0.2}
                    />
                    <Tooltip formatter={(value, name) => [`${value}${name === 'score' ? '' : '%'}`, name]} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Agent Details */}
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-4">Individual Agent Analysis</h3>
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {selectedData.agents.map((agent) => (
                  <div key={agent.name} className="professional-card p-4 bg-muted/20">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="font-medium text-foreground">{agent.name}</span>
                        <span className="text-xs text-muted-foreground">({agent.weight}%)</span>
                      </div>
                      <div className={cn('text-sm', getStatusColor(agent.status))}>
                        {agent.status}
                      </div>
                    </div>

                    <div className="grid grid-cols-3 gap-2 mb-2 text-sm">
                      <div>
                        <div className="text-muted-foreground">Score</div>
                        <div className={cn('font-medium', getScoreColor(agent.score))}>
                          {agent.score}
                        </div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Confidence</div>
                        <div className="font-medium">
                          {formatPercentage(agent.confidence * 100)}
                        </div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Accuracy</div>
                        <div className="font-medium">
                          {formatPercentage(agent.accuracy)}
                        </div>
                      </div>
                    </div>

                    <div className="text-xs text-muted-foreground">
                      {agent.reasoning}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Key Insights */}
          <div className="professional-card p-4 bg-muted/20">
            <h3 className="text-lg font-semibold text-foreground mb-3">Key Consensus Insights</h3>
            <div className="space-y-3">
              <div className="flex items-start space-x-2">
                <Target className="h-4 w-4 text-accent mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-foreground">Primary Reasoning</div>
                  <div className="text-sm text-muted-foreground">{selectedData.topReason}</div>
                </div>
              </div>

              {selectedData.conflictAreas.length > 0 && (
                <div className="flex items-start space-x-2">
                  <AlertCircle className="h-4 w-4 text-red-400 mt-0.5" />
                  <div>
                    <div className="text-sm font-medium text-foreground">Conflict Areas</div>
                    <div className="text-sm text-muted-foreground">
                      {selectedData.conflictAreas.join(', ')} - Agents disagree on these aspects
                    </div>
                  </div>
                </div>
              )}

              <div className="flex items-start space-x-2">
                <Users className="h-4 w-4 text-blue-400 mt-0.5" />
                <div>
                  <div className="text-sm font-medium text-foreground">Strongest Agreement</div>
                  <div className="text-sm text-muted-foreground">
                    {selectedData.agents
                      .sort((a, b) => b.score - a.score)[0].name} agent shows highest confidence
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Action Recommendations */}
          <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-3">
            <button
              onClick={handleViewFullAnalysis}
              className="flex-1 bg-accent hover:bg-accent/80 text-accent-foreground px-4 py-2 rounded-lg font-medium text-sm transition-colors"
            >
              View Full Analysis
            </button>
            <button
              onClick={handleCompareStocks}
              className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors"
            >
              Compare Stocks
            </button>
            <button
              onClick={handleExportReport}
              className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors"
            >
              Export Report
            </button>
          </div>
        </>
      )}
    </div>
  );
};