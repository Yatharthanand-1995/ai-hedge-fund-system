import React from 'react';
import { Search, Filter, ArrowUpDown, Download } from 'lucide-react';

export interface FilterState {
  searchTerm: string;
  recommendation: string;
  sector: string;
  riskLevel: string;
  scoreRange: string;
}

export interface SortConfig {
  field: string;
  direction: 'asc' | 'desc';
}

interface StockFilterBarProps {
  filters: FilterState;
  sortConfig: SortConfig;
  onFilterChange: (filters: FilterState) => void;
  onSortChange: (sort: SortConfig) => void;
  onExport: () => void;
  stockCount: number;
}

export const StockFilterBar: React.FC<StockFilterBarProps> = ({
  filters,
  sortConfig,
  onFilterChange,
  onSortChange,
  onExport,
  stockCount
}) => {
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onFilterChange({ ...filters, searchTerm: e.target.value });
  };

  const handleFilterChange = (key: keyof FilterState, value: string) => {
    onFilterChange({ ...filters, [key]: value });
  };

  const handleSortChange = (field: string) => {
    if (sortConfig.field === field) {
      onSortChange({ field, direction: sortConfig.direction === 'asc' ? 'desc' : 'asc' });
    } else {
      onSortChange({ field, direction: 'desc' });
    }
  };

  return (
    <div className="professional-card p-4 space-y-4">
      {/* Top Row - Search and Export */}
      <div className="flex items-center justify-between gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search stocks by symbol or name..."
            value={filters.searchTerm}
            onChange={handleSearchChange}
            className="w-full pl-10 pr-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-accent"
          />
        </div>

        <button
          onClick={onExport}
          className="flex items-center space-x-2 px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent/80 transition-colors"
        >
          <Download className="h-4 w-4" />
          <span>Export CSV</span>
        </button>
      </div>

      {/* Filters Row */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="flex items-center space-x-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">Filters:</span>
        </div>

        <select
          value={filters.recommendation}
          onChange={(e) => handleFilterChange('recommendation', e.target.value)}
          className="px-3 py-1.5 border border-border rounded-lg bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent"
        >
          <option value="">All Recommendations</option>
          <option value="STRONG BUY">STRONG BUY</option>
          <option value="BUY">BUY</option>
          <option value="WEAK BUY">WEAK BUY</option>
          <option value="HOLD">HOLD</option>
          <option value="WEAK SELL">WEAK SELL</option>
          <option value="SELL">SELL</option>
        </select>

        <select
          value={filters.sector}
          onChange={(e) => handleFilterChange('sector', e.target.value)}
          className="px-3 py-1.5 border border-border rounded-lg bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent"
        >
          <option value="">All Sectors</option>
          <option value="Technology">Technology</option>
          <option value="Healthcare">Healthcare</option>
          <option value="Finance">Finance</option>
          <option value="Consumer">Consumer</option>
          <option value="Energy">Energy</option>
          <option value="Industrial">Industrial</option>
        </select>

        <select
          value={filters.riskLevel}
          onChange={(e) => handleFilterChange('riskLevel', e.target.value)}
          className="px-3 py-1.5 border border-border rounded-lg bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent"
        >
          <option value="">All Risk Levels</option>
          <option value="low">Low Risk</option>
          <option value="medium">Medium Risk</option>
          <option value="high">High Risk</option>
        </select>

        <select
          value={filters.scoreRange}
          onChange={(e) => handleFilterChange('scoreRange', e.target.value)}
          className="px-3 py-1.5 border border-border rounded-lg bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent"
        >
          <option value="">All Scores</option>
          <option value="80-100">Excellent (80-100)</option>
          <option value="60-79">Good (60-79)</option>
          <option value="40-59">Fair (40-59)</option>
          <option value="0-39">Poor (0-39)</option>
        </select>

        {/* Sort Dropdown */}
        <div className="flex items-center space-x-2 ml-auto">
          <ArrowUpDown className="h-4 w-4 text-muted-foreground" />
          <select
            value={sortConfig.field}
            onChange={(e) => handleSortChange(e.target.value)}
            className="px-3 py-1.5 border border-border rounded-lg bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-accent"
          >
            <option value="overall_score">AI Score</option>
            <option value="market_data.price_change_percent">Price Change</option>
            <option value="recommendation">Recommendation</option>
            <option value="market_data.current_price">Price</option>
            <option value="weight">Portfolio Weight</option>
            <option value="symbol">Symbol</option>
          </select>
          <button
            onClick={() => onSortChange({ ...sortConfig, direction: sortConfig.direction === 'asc' ? 'desc' : 'asc' })}
            className="px-2 py-1.5 border border-border rounded-lg bg-background hover:bg-muted/20 transition-colors"
          >
            {sortConfig.direction === 'asc' ? '↑' : '↓'}
          </button>
        </div>
      </div>

      {/* Results Count */}
      <div className="text-sm text-muted-foreground">
        Showing <span className="font-semibold text-foreground">{stockCount}</span> stocks
      </div>
    </div>
  );
};