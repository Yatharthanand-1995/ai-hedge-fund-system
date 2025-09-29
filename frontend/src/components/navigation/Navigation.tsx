import React from 'react';
import { cn } from '../../utils';

interface NavigationProps {
  currentPage: 'dashboard' | 'analysis' | 'portfolio';
  onPageChange: (page: 'dashboard' | 'analysis' | 'portfolio') => void;
}

export const Navigation: React.FC<NavigationProps> = ({
  currentPage,
  onPageChange,
}) => {
  const navItems = [
    { id: 'dashboard' as const, label: 'System Overview', icon: '🏦' },
    { id: 'analysis' as const, label: 'Stock Analysis', icon: '📊' },
    { id: 'portfolio' as const, label: 'Portfolio Manager', icon: '📈' },
  ];

  return (
    <nav className="professional-card p-4 mb-8">
      <div className="flex flex-wrap gap-2">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onPageChange(item.id)}
            className={cn(
              'flex items-center space-x-2 px-4 py-2 rounded-lg transition-all',
              'font-medium text-sm',
              currentPage === item.id
                ? 'bg-accent text-accent-foreground'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted'
            )}
          >
            <span>{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
};