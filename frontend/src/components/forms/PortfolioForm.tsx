import React, { useState } from 'react';
import { cn, isValidStockSymbol } from '../../utils';

interface PortfolioStock {
  symbol: string;
  weight?: number;
}

interface PortfolioFormProps {
  onAnalyze: (symbols: string[], weights?: number[]) => void;
  isLoading?: boolean;
  className?: string;
}

export const PortfolioForm: React.FC<PortfolioFormProps> = ({
  onAnalyze,
  isLoading = false,
  className,
}) => {
  const [stocks, setStocks] = useState<PortfolioStock[]>([
    { symbol: '', weight: undefined },
    { symbol: '', weight: undefined },
  ]);
  const [useCustomWeights, setUseCustomWeights] = useState(false);
  const [error, setError] = useState('');

  const addStock = () => {
    if (stocks.length < 20) {
      setStocks([...stocks, { symbol: '', weight: undefined }]);
    }
  };

  const removeStock = (index: number) => {
    if (stocks.length > 2) {
      const newStocks = stocks.filter((_, i) => i !== index);
      setStocks(newStocks);
    }
  };

  const updateStock = (index: number, field: keyof PortfolioStock, value: string | number) => {
    const newStocks = [...stocks];
    if (field === 'symbol') {
      newStocks[index].symbol = (value as string).toUpperCase();
    } else if (field === 'weight') {
      newStocks[index].weight = value === '' ? undefined : Number(value);
    }
    setStocks(newStocks);
    if (error) setError('');
  };

  const validateForm = (): boolean => {
    const validStocks = stocks.filter(stock => stock.symbol.trim());

    if (validStocks.length < 2) {
      setError('Please enter at least 2 stock symbols');
      return false;
    }

    for (const stock of validStocks) {
      if (!isValidStockSymbol(stock.symbol)) {
        setError(`Invalid stock symbol: ${stock.symbol}`);
        return false;
      }
    }

    if (useCustomWeights) {
      const weights = validStocks.map(stock => stock.weight || 0);
      const totalWeight = weights.reduce((sum, weight) => sum + weight, 0);

      if (Math.abs(totalWeight - 100) > 0.1) {
        setError('Weights must sum to 100%');
        return false;
      }

      if (weights.some(weight => weight <= 0)) {
        setError('All weights must be greater than 0');
        return false;
      }
    }

    return true;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    const validStocks = stocks.filter(stock => stock.symbol.trim());
    const symbols = validStocks.map(stock => stock.symbol);
    const weights = useCustomWeights
      ? validStocks.map(stock => (stock.weight || 0) / 100)
      : undefined;

    setError('');
    onAnalyze(symbols, weights);
  };

  const remainingWeight = useCustomWeights
    ? 100 - stocks.reduce((sum, stock) => sum + (stock.weight || 0), 0)
    : 0;

  return (
    <div className={cn('w-full max-w-4xl', className)}>
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Header */}
        <div>
          <h2 className="text-xl font-semibold text-foreground mb-2">
            Portfolio Composition
          </h2>
          <p className="text-muted-foreground text-sm">
            Add 2-20 stocks to analyze your portfolio using our 5-agent system
          </p>
        </div>

        {/* Weight Toggle */}
        <div className="flex items-center space-x-3">
          <input
            type="checkbox"
            id="custom-weights"
            checked={useCustomWeights}
            onChange={(e) => setUseCustomWeights(e.target.checked)}
            className="rounded border-gray-600 focus:ring-accent"
          />
          <label htmlFor="custom-weights" className="text-sm text-foreground">
            Use custom weights (otherwise equal weighting will be applied)
          </label>
        </div>

        {/* Stocks List */}
        <div className="space-y-3">
          {stocks.map((stock, index) => (
            <div key={index} className="flex items-center space-x-3">
              <div className="flex-1">
                <input
                  type="text"
                  placeholder="e.g., AAPL"
                  value={stock.symbol}
                  onChange={(e) => updateStock(index, 'symbol', e.target.value)}
                  className={cn(
                    'w-full px-3 py-2 rounded-lg border transition-colors',
                    'bg-background text-foreground placeholder-muted-foreground',
                    'focus:outline-none focus:ring-2 focus:ring-accent',
                    'border-gray-600 focus:border-accent'
                  )}
                  maxLength={5}
                  disabled={isLoading}
                />
              </div>

              {useCustomWeights && (
                <div className="w-24">
                  <input
                    type="number"
                    placeholder="25"
                    min="0"
                    max="100"
                    step="0.1"
                    value={stock.weight || ''}
                    onChange={(e) => updateStock(index, 'weight', e.target.value)}
                    className={cn(
                      'w-full px-3 py-2 rounded-lg border transition-colors',
                      'bg-background text-foreground placeholder-muted-foreground',
                      'focus:outline-none focus:ring-2 focus:ring-accent',
                      'border-gray-600 focus:border-accent'
                    )}
                    disabled={isLoading}
                  />
                </div>
              )}

              {useCustomWeights && (
                <span className="text-muted-foreground text-sm w-6">%</span>
              )}

              <button
                type="button"
                onClick={() => removeStock(index)}
                disabled={stocks.length <= 2 || isLoading}
                className={cn(
                  'p-2 rounded-lg transition-colors',
                  stocks.length <= 2
                    ? 'text-muted-foreground cursor-not-allowed'
                    : 'text-red-400 hover:bg-red-400/10'
                )}
              >
                ✕
              </button>
            </div>
          ))}
        </div>

        {/* Add Stock Button */}
        <button
          type="button"
          onClick={addStock}
          disabled={stocks.length >= 20 || isLoading}
          className={cn(
            'w-full py-2 px-4 rounded-lg border-2 border-dashed transition-colors',
            'border-gray-600 hover:border-accent text-muted-foreground hover:text-foreground',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          + Add Stock ({stocks.length}/20)
        </button>

        {/* Weight Summary */}
        {useCustomWeights && (
          <div className="bg-muted/30 p-3 rounded-lg">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Total Weight:</span>
              <span className={cn(
                'font-medium',
                Math.abs(remainingWeight) < 0.1
                  ? 'text-green-400'
                  : 'text-yellow-400'
              )}>
                {(100 - remainingWeight).toFixed(1)}%
              </span>
            </div>
            {remainingWeight !== 0 && (
              <div className="flex justify-between text-sm mt-1">
                <span className="text-muted-foreground">Remaining:</span>
                <span className="text-muted-foreground">{remainingWeight.toFixed(1)}%</span>
              </div>
            )}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <p className="text-sm text-red-400">{error}</p>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className={cn(
            'w-full py-3 px-4 rounded-lg font-medium transition-all',
            'bg-accent text-accent-foreground hover:bg-accent/90',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-background'
          )}
        >
          {isLoading ? 'Analyzing Portfolio...' : 'Analyze Portfolio'}
        </button>
      </form>
    </div>
  );
};