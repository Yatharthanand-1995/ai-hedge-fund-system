import React, { useState } from 'react';
import { cn, isValidStockSymbol } from '../../utils';

interface StockSearchFormProps {
  onSearch: (symbol: string) => void;
  isLoading?: boolean;
  className?: string;
}

export const StockSearchForm: React.FC<StockSearchFormProps> = ({
  onSearch,
  isLoading = false,
  className,
}) => {
  const [symbol, setSymbol] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const trimmedSymbol = symbol.trim().toUpperCase();

    if (!trimmedSymbol) {
      setError('Please enter a stock symbol');
      return;
    }

    if (!isValidStockSymbol(trimmedSymbol)) {
      setError('Please enter a valid stock symbol (1-5 letters)');
      return;
    }

    setError('');
    onSearch(trimmedSymbol);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value.toUpperCase();
    setSymbol(value);
    if (error) setError('');
  };

  return (
    <div className={cn('w-full max-w-md', className)}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="stock-symbol" className="block text-sm font-medium text-foreground mb-2">
            Stock Symbol
          </label>
          <div className="relative">
            <input
              id="stock-symbol"
              type="text"
              value={symbol}
              onChange={handleInputChange}
              placeholder="e.g., AAPL"
              className={cn(
                'w-full px-4 py-3 rounded-lg border-2 transition-colors',
                'bg-background text-foreground placeholder-muted-foreground',
                'focus:outline-none focus:ring-0',
                error
                  ? 'border-red-500 focus:border-red-500'
                  : 'border-gray-600 focus:border-accent'
              )}
              disabled={isLoading}
              maxLength={5}
            />
            {isLoading && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-accent"></div>
              </div>
            )}
          </div>
          {error && (
            <p className="mt-2 text-sm text-red-400">{error}</p>
          )}
        </div>

        <button
          type="submit"
          disabled={isLoading || !symbol.trim()}
          className={cn(
            'w-full py-3 px-4 rounded-lg font-medium transition-all',
            'bg-accent text-accent-foreground hover:bg-accent/90',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'focus:outline-none focus:ring-2 focus:ring-accent focus:ring-offset-2 focus:ring-offset-background'
          )}
        >
          {isLoading ? 'Analyzing...' : 'Analyze Stock'}
        </button>
      </form>
    </div>
  );
};