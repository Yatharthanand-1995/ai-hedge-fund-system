import React, { useState } from 'react';
import { Filter, X, ChevronDown, SortAsc, SortDesc, Search } from 'lucide-react';
import { cn } from '../../utils';
import type { FilterOptions, SortOption } from '../../types/filters';

interface SmartFilterBarProps {
  onFilterChange: (filters: FilterOptions) => void;
  onSortChange: (sort: SortOption) => void;
  totalCount: number;
  filteredCount: number;
  className?: string;
}

export const SmartFilterBar: React.FC<SmartFilterBarProps> = ({
  onFilterChange,
  onSortChange,
  totalCount,
  filteredCount,
  className
}) => {
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<FilterOptions>({
    sector: [],
    scoreRange: 'all',
    riskLevel: [],
    consensus: [],
    priceRange: 'all',
    searchQuery: ''
  });
  const [sortBy, setSortBy] = useState<SortOption>('score-desc');

  const sectors = ['Technology', 'Healthcare', 'Finance', 'Consumer', 'Energy', 'Industrial'];
  const scoreRanges = [
    { value: 'all', label: 'All Scores' },
    { value: 'strong-buy', label: 'Strong Buy (80+)' },
    { value: 'buy', label: 'Buy (65-79)' },
    { value: 'hold', label: 'Hold (45-64)' },
    { value: 'sell', label: 'Sell (<45)' }
  ];
  const riskLevels = ['Low', 'Medium', 'High'];
  const consensusOptions = ['Strong', 'Moderate', 'Weak'];
  const priceRanges = [
    { value: 'all', label: 'All Prices' },
    { value: '0-50', label: '$0-50' },
    { value: '50-200', label: '$50-200' },
    { value: '200-500', label: '$200-500' },
    { value: '500+', label: '$500+' }
  ];

  const sortOptions: { value: SortOption; label: string }[] = [
    { value: 'score-desc', label: 'Score: High → Low' },
    { value: 'score-asc', label: 'Score: Low → High' },
    { value: 'price-desc', label: 'Price: High → Low' },
    { value: 'price-asc', label: 'Price: Low → High' },
    { value: 'momentum-desc', label: 'Momentum: Best → Worst' },
    { value: 'alpha-asc', label: 'Alphabetical: A → Z' },
    { value: 'alpha-desc', label: 'Alphabetical: Z → A' }
  ];

  const handleFilterChange = (key: keyof FilterOptions, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const toggleArrayFilter = (key: 'sector' | 'riskLevel' | 'consensus', value: string) => {
    const currentArray = filters[key];
    const newArray = currentArray.includes(value)
      ? currentArray.filter(v => v !== value)
      : [...currentArray, value];
    handleFilterChange(key, newArray);
  };

  const handleSortChange = (value: SortOption) => {
    setSortBy(value);
    onSortChange(value);
  };

  const clearAllFilters = () => {
    const emptyFilters: FilterOptions = {
      sector: [],
      scoreRange: 'all',
      riskLevel: [],
      consensus: [],
      priceRange: 'all',
      searchQuery: ''
    };
    setFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  const hasActiveFilters =
    filters.sector.length > 0 ||
    filters.scoreRange !== 'all' ||
    filters.riskLevel.length > 0 ||
    filters.consensus.length > 0 ||
    filters.priceRange !== 'all' ||
    filters.searchQuery.length > 0;

  const activeFilterCount =
    filters.sector.length +
    filters.riskLevel.length +
    filters.consensus.length +
    (filters.scoreRange !== 'all' ? 1 : 0) +
    (filters.priceRange !== 'all' ? 1 : 0) +
    (filters.searchQuery ? 1 : 0);

  return (
    <div className={cn('space-y-4', className)}>
      {/* Filter Bar Header */}
      <div className="flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search stocks..."
            value={filters.searchQuery}
            onChange={(e) => handleFilterChange('searchQuery', e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-muted border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent"
          />
        </div>

        {/* Sort */}
        <div className="relative">
          <select
            value={sortBy}
            onChange={(e) => handleSortChange(e.target.value as SortOption)}
            className="appearance-none bg-muted border border-border rounded-lg px-4 py-2 pr-10 text-foreground focus:outline-none focus:ring-2 focus:ring-accent cursor-pointer"
          >
            {sortOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
        </div>

        {/* Filter Button */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className={cn(
            'flex items-center space-x-2 px-4 py-2 rounded-lg border transition-all',
            showFilters
              ? 'bg-accent text-accent-foreground border-accent'
              : 'bg-muted text-foreground border-border hover:border-accent'
          )}
        >
          <Filter className="h-4 w-4" />
          <span>Filters</span>
          {activeFilterCount > 0 && (
            <span className="bg-accent-foreground text-accent text-xs font-bold px-2 py-0.5 rounded-full">
              {activeFilterCount}
            </span>
          )}
        </button>

        {/* Clear Filters */}
        {hasActiveFilters && (
          <button
            onClick={clearAllFilters}
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            Clear All
          </button>
        )}

        {/* Results Count */}
        <div className="text-sm text-muted-foreground ml-auto">
          Showing {filteredCount} of {totalCount} stocks
        </div>
      </div>

      {/* Applied Filters Display */}
      {hasActiveFilters && (
        <div className="flex flex-wrap items-center gap-2">
          <span className="text-sm text-muted-foreground">Active filters:</span>
          {filters.sector.map(sector => (
            <span
              key={sector}
              className="inline-flex items-center space-x-1 bg-blue-500/20 text-blue-400 px-2 py-1 rounded text-xs"
            >
              <span>{sector}</span>
              <button onClick={() => toggleArrayFilter('sector', sector)}>
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
          {filters.scoreRange !== 'all' && (
            <span className="inline-flex items-center space-x-1 bg-green-500/20 text-green-400 px-2 py-1 rounded text-xs">
              <span>{scoreRanges.find(r => r.value === filters.scoreRange)?.label}</span>
              <button onClick={() => handleFilterChange('scoreRange', 'all')}>
                <X className="h-3 w-3" />
              </button>
            </span>
          )}
          {filters.riskLevel.map(risk => (
            <span
              key={risk}
              className="inline-flex items-center space-x-1 bg-orange-500/20 text-orange-400 px-2 py-1 rounded text-xs"
            >
              <span>Risk: {risk}</span>
              <button onClick={() => toggleArrayFilter('riskLevel', risk)}>
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
          {filters.consensus.map(cons => (
            <span
              key={cons}
              className="inline-flex items-center space-x-1 bg-purple-500/20 text-purple-400 px-2 py-1 rounded text-xs"
            >
              <span>Consensus: {cons}</span>
              <button onClick={() => toggleArrayFilter('consensus', cons)}>
                <X className="h-3 w-3" />
              </button>
            </span>
          ))}
          {filters.priceRange !== 'all' && (
            <span className="inline-flex items-center space-x-1 bg-yellow-500/20 text-yellow-400 px-2 py-1 rounded text-xs">
              <span>{priceRanges.find(r => r.value === filters.priceRange)?.label}</span>
              <button onClick={() => handleFilterChange('priceRange', 'all')}>
                <X className="h-3 w-3" />
              </button>
            </span>
          )}
        </div>
      )}

      {/* Filter Panel */}
      {showFilters && (
        <div className="professional-card p-6 space-y-6">
          {/* Sector Filter */}
          <div>
            <h4 className="text-sm font-semibold text-foreground mb-3">Sector</h4>
            <div className="flex flex-wrap gap-2">
              {sectors.map(sector => (
                <button
                  key={sector}
                  onClick={() => toggleArrayFilter('sector', sector)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm transition-all',
                    filters.sector.includes(sector)
                      ? 'bg-accent text-accent-foreground'
                      : 'bg-muted text-foreground hover:bg-muted/80'
                  )}
                >
                  {sector}
                </button>
              ))}
            </div>
          </div>

          {/* Score Range */}
          <div>
            <h4 className="text-sm font-semibold text-foreground mb-3">Score Range</h4>
            <div className="flex flex-wrap gap-2">
              {scoreRanges.map(range => (
                <button
                  key={range.value}
                  onClick={() => handleFilterChange('scoreRange', range.value)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm transition-all',
                    filters.scoreRange === range.value
                      ? 'bg-accent text-accent-foreground'
                      : 'bg-muted text-foreground hover:bg-muted/80'
                  )}
                >
                  {range.label}
                </button>
              ))}
            </div>
          </div>

          {/* Risk Level */}
          <div>
            <h4 className="text-sm font-semibold text-foreground mb-3">Risk Level</h4>
            <div className="flex flex-wrap gap-2">
              {riskLevels.map(risk => (
                <button
                  key={risk}
                  onClick={() => toggleArrayFilter('riskLevel', risk)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm transition-all',
                    filters.riskLevel.includes(risk)
                      ? 'bg-accent text-accent-foreground'
                      : 'bg-muted text-foreground hover:bg-muted/80'
                  )}
                >
                  {risk}
                </button>
              ))}
            </div>
          </div>

          {/* Agent Consensus */}
          <div>
            <h4 className="text-sm font-semibold text-foreground mb-3">Agent Consensus</h4>
            <div className="flex flex-wrap gap-2">
              {consensusOptions.map(cons => (
                <button
                  key={cons}
                  onClick={() => toggleArrayFilter('consensus', cons)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm transition-all',
                    filters.consensus.includes(cons)
                      ? 'bg-accent text-accent-foreground'
                      : 'bg-muted text-foreground hover:bg-muted/80'
                  )}
                >
                  {cons}
                </button>
              ))}
            </div>
          </div>

          {/* Price Range */}
          <div>
            <h4 className="text-sm font-semibold text-foreground mb-3">Price Range</h4>
            <div className="flex flex-wrap gap-2">
              {priceRanges.map(range => (
                <button
                  key={range.value}
                  onClick={() => handleFilterChange('priceRange', range.value)}
                  className={cn(
                    'px-3 py-1.5 rounded-lg text-sm transition-all',
                    filters.priceRange === range.value
                      ? 'bg-accent text-accent-foreground'
                      : 'bg-muted text-foreground hover:bg-muted/80'
                  )}
                >
                  {range.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
