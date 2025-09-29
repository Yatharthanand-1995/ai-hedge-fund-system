import React, { useState, useEffect } from 'react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import { Brain, TrendingUp, TrendingDown, AlertCircle, CheckCircle, Users, Target } from 'lucide-react';
import { cn, formatPercentage } from '../../utils';

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
  const [viewMode, setViewMode] = useState<'consensus' | 'performance'>('consensus');

  useEffect(() => {
    // Simulate fetching consensus data
    const fetchConsensusData = async () => {
      try {
        const mockData: ConsensusData[] = [
          {
            symbol: 'AAPL',
            overallScore: 78.5,
            consensus: 'strong',
            agreement: 92,
            conflictAreas: [],
            topReason: 'Strong fundamentals with excellent momentum',
            agents: [
              {
                name: 'Fundamentals',
                score: 82,
                confidence: 0.95,
                weight: 40,
                accuracy: 87,
                reasoning: 'Excellent profitability metrics and strong balance sheet',
                status: 'healthy'
              },
              {
                name: 'Momentum',
                score: 75,
                confidence: 0.88,
                weight: 30,
                accuracy: 82,
                reasoning: 'Strong price momentum with bullish technical indicators',
                status: 'healthy'
              },
              {
                name: 'Quality',
                score: 85,
                confidence: 0.92,
                weight: 20,
                accuracy: 90,
                reasoning: 'High-quality business with strong competitive moat',
                status: 'healthy'
              },
              {
                name: 'Sentiment',
                score: 70,
                confidence: 0.85,
                weight: 10,
                accuracy: 78,
                reasoning: 'Mixed sentiment with analyst upgrades',
                status: 'healthy'
              }
            ]
          },
          {
            symbol: 'TSLA',
            overallScore: 65.2,
            consensus: 'weak',
            agreement: 65,
            conflictAreas: ['Valuation', 'Risk Assessment'],
            topReason: 'High growth potential but elevated valuation concerns',
            agents: [
              {
                name: 'Fundamentals',
                score: 45,
                confidence: 0.78,
                weight: 40,
                accuracy: 87,
                reasoning: 'High valuation multiples concern fundamental analysis',
                status: 'degraded'
              },
              {
                name: 'Momentum',
                score: 85,
                confidence: 0.91,
                weight: 30,
                accuracy: 82,
                reasoning: 'Very strong momentum with breakout patterns',
                status: 'healthy'
              },
              {
                name: 'Quality',
                score: 72,
                confidence: 0.86,
                weight: 20,
                accuracy: 90,
                reasoning: 'Innovative company but execution risks remain',
                status: 'healthy'
              },
              {
                name: 'Sentiment',
                score: 80,
                confidence: 0.89,
                weight: 10,
                accuracy: 78,
                reasoning: 'Very positive sentiment around EV adoption',
                status: 'healthy'
              }
            ]
          },
          {
            symbol: 'MSFT',
            overallScore: 81.3,
            consensus: 'strong',
            agreement: 94,
            conflictAreas: [],
            topReason: 'Excellent across all metrics with cloud growth',
            agents: [
              {
                name: 'Fundamentals',
                score: 85,
                confidence: 0.96,
                weight: 40,
                accuracy: 87,
                reasoning: 'Strong cloud revenue growth and margins',
                status: 'healthy'
              },
              {
                name: 'Momentum',
                score: 78,
                confidence: 0.90,
                weight: 30,
                accuracy: 82,
                reasoning: 'Steady uptrend with strong volume support',
                status: 'healthy'
              },
              {
                name: 'Quality',
                score: 88,
                confidence: 0.95,
                weight: 20,
                accuracy: 90,
                reasoning: 'Exceptional business quality and market position',
                status: 'healthy'
              },
              {
                name: 'Sentiment',
                score: 75,
                confidence: 0.87,
                weight: 10,
                accuracy: 78,
                reasoning: 'Positive sentiment on AI and cloud initiatives',
                status: 'healthy'
              }
            ]
          }
        ];

        setTimeout(() => {
          setConsensusData(mockData);
          setSelectedStock(mockData[0].symbol);
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Failed to fetch consensus data:', error);
        setLoading(false);
      }
    };

    fetchConsensusData();
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

  if (loading) {
    return (
      <div className={cn('professional-card p-6', className)}>
        <div className="flex items-center space-x-3 mb-6">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-accent"></div>
          <h2 className="text-xl font-semibold text-foreground">Loading Agent Consensus...</h2>
        </div>
      </div>
    );
  }

  const selectedData = consensusData.find(item => item.symbol === selectedStock);
  const agentPerformanceData = selectedData?.agents.map(agent => ({
    name: agent.name.slice(0, 4), // Shorten names for chart
    score: agent.score,
    accuracy: agent.accuracy,
    confidence: agent.confidence * 100
  })) || [];

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
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
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
            <button className="flex-1 bg-accent hover:bg-accent/80 text-accent-foreground px-4 py-2 rounded-lg font-medium text-sm transition-colors">
              View Full Analysis
            </button>
            <button className="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors">
              Compare Stocks
            </button>
            <button className="flex-1 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium text-sm transition-colors">
              Export Report
            </button>
          </div>
        </>
      )}
    </div>
  );
};