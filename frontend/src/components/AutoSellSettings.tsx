import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Shield, AlertTriangle, X } from 'lucide-react';
import { cn } from '../utils';
import { useToast } from './common/Toast';

interface AutoSellRules {
  enabled: boolean;
  stop_loss_percent: number;
  take_profit_percent: number;
  watch_ai_signals: boolean;
  max_position_age_days: number | null;
}

interface AutoSellSettingsProps {
  onClose: () => void;
}

const API_BASE = 'http://localhost:8010';

export const AutoSellSettings: React.FC<AutoSellSettingsProps> = ({ onClose }) => {
  const queryClient = useQueryClient();
  const toast = useToast();

  // Fetch current rules
  const { data: rulesData, isLoading } = useQuery({
    queryKey: ['autoSellRules'],
    queryFn: async () => {
      const response = await fetch(`${API_BASE}/portfolio/paper/auto-sell/rules`);
      if (!response.ok) throw new Error('Failed to fetch auto-sell rules');
      return response.json();
    },
  });

  const rules: AutoSellRules | undefined = rulesData?.rules;

  // Local state for form
  const [enabled, setEnabled] = useState(rules?.enabled ?? false);
  const [stopLoss, setStopLoss] = useState(rules?.stop_loss_percent?.toString() ?? '-10');
  const [takeProfit, setTakeProfit] = useState(rules?.take_profit_percent?.toString() ?? '20');
  const [watchAI, setWatchAI] = useState(rules?.watch_ai_signals ?? true);

  // Update rules on data load
  React.useEffect(() => {
    if (rules) {
      setEnabled(rules.enabled);
      setStopLoss(rules.stop_loss_percent.toString());
      setTakeProfit(rules.take_profit_percent.toString());
      setWatchAI(rules.watch_ai_signals);
    }
  }, [rules]);

  // Update rules mutation
  const updateRulesMutation = useMutation({
    mutationFn: async (params: Record<string, any>) => {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        queryParams.append(key, value.toString());
      });

      const response = await fetch(`${API_BASE}/portfolio/paper/auto-sell/rules?${queryParams}`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to update rules');
      return response.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['autoSellRules'] });
      toast.success('Auto-Sell Updated', 'Settings saved successfully');
    },
    onError: (error: Error) => {
      toast.error('Update Failed', error.message);
    },
  });

  // Scan mutation
  const scanMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`${API_BASE}/portfolio/paper/auto-sell/scan`);
      if (!response.ok) throw new Error('Failed to scan portfolio');
      return response.json();
    },
    onSuccess: (data) => {
      if (data.count === 0) {
        toast.info('No Triggers', 'No positions meet auto-sell criteria');
      } else {
        toast.warning('Positions to Sell', `${data.count} position(s) trigger auto-sell`);
      }
    },
  });

  // Execute auto-sells mutation
  const executeMutation = useMutation({
    mutationFn: async () => {
      const response = await fetch(`${API_BASE}/portfolio/paper/auto-sell/execute`, {
        method: 'POST',
      });
      if (!response.ok) throw new Error('Failed to execute auto-sells');
      return response.json();
    },
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['paperPortfolio'] });
      queryClient.invalidateQueries({ queryKey: ['paperTransactions'] });

      if (data.count === 0) {
        toast.info('No Sales', 'No positions met auto-sell criteria');
      } else {
        toast.success('Auto-Sell Executed', `Sold ${data.count} position(s)`);
      }
    },
    onError: (error: Error) => {
      toast.error('Auto-Sell Failed', error.message);
    },
  });

  const handleSave = () => {
    const params: Record<string, any> = {
      enabled,
      stop_loss_percent: parseFloat(stopLoss),
      take_profit_percent: parseFloat(takeProfit),
      watch_ai_signals: watchAI,
    };
    updateRulesMutation.mutate(params);
  };

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
        <div className="professional-card p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-accent mx-auto"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="professional-card p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-3">
            <Shield className="h-6 w-6 text-accent" />
            <h2 className="text-2xl font-bold">Auto-Sell Settings</h2>
          </div>
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground">
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Enable Toggle */}
        <div className="mb-6 p-4 bg-muted/10 rounded-lg">
          <label className="flex items-center justify-between cursor-pointer">
            <div>
              <div className="font-semibold">Enable Auto-Sell</div>
              <div className="text-sm text-muted-foreground">
                Automatically sell positions based on rules below
              </div>
            </div>
            <div className="relative">
              <input
                type="checkbox"
                checked={enabled}
                onChange={(e) => setEnabled(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-14 h-8 bg-muted rounded-full peer peer-checked:bg-accent transition-colors"></div>
              <div className="absolute left-1 top-1 w-6 h-6 bg-white rounded-full transition-transform peer-checked:translate-x-6"></div>
            </div>
          </label>
        </div>

        {/* Stop-Loss */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            Stop-Loss Threshold
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="number"
              value={stopLoss}
              onChange={(e) => setStopLoss(e.target.value)}
              step="0.5"
              className="professional-input flex-1"
              placeholder="-10"
              disabled={!enabled}
            />
            <span className="text-muted-foreground">%</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Sell if position drops below this percentage (e.g., -10 for -10%)
          </p>
        </div>

        {/* Take-Profit */}
        <div className="mb-4">
          <label className="block text-sm font-medium mb-2">
            Take-Profit Threshold
          </label>
          <div className="flex items-center space-x-2">
            <input
              type="number"
              value={takeProfit}
              onChange={(e) => setTakeProfit(e.target.value)}
              step="1"
              className="professional-input flex-1"
              placeholder="20"
              disabled={!enabled}
            />
            <span className="text-muted-foreground">%</span>
          </div>
          <p className="text-xs text-muted-foreground mt-1">
            Sell if position gains above this percentage (e.g., 20 for +20%)
          </p>
        </div>

        {/* AI Signals */}
        <div className="mb-6">
          <label className="flex items-center space-x-2 cursor-pointer">
            <input
              type="checkbox"
              checked={watchAI}
              onChange={(e) => setWatchAI(e.target.checked)}
              disabled={!enabled}
              className="w-4 h-4 rounded border-border bg-background checked:bg-accent"
            />
            <div>
              <div className="font-medium">Watch AI Signals</div>
              <div className="text-xs text-muted-foreground">
                Auto-sell when AI recommendation changes to SELL
              </div>
            </div>
          </label>
        </div>

        {/* Warning */}
        {enabled && (
          <div className="mb-6 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg flex items-start space-x-3">
            <AlertTriangle className="h-5 w-5 text-yellow-400 flex-shrink-0 mt-0.5" />
            <div className="text-sm text-yellow-200">
              Auto-sell is active. Positions will be automatically sold when they meet the criteria above.
              Use "Scan Portfolio" to preview which positions would be sold.
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-wrap gap-3">
          <button
            onClick={handleSave}
            disabled={updateRulesMutation.isPending}
            className="professional-button-primary flex-1"
          >
            {updateRulesMutation.isPending ? 'Saving...' : 'Save Settings'}
          </button>

          <button
            onClick={() => scanMutation.mutate()}
            disabled={!enabled || scanMutation.isPending}
            className="professional-button-secondary flex-1"
          >
            {scanMutation.isPending ? 'Scanning...' : 'Scan Portfolio'}
          </button>

          <button
            onClick={() => {
              if (confirm('Execute auto-sell for all triggered positions?')) {
                executeMutation.mutate();
              }
            }}
            disabled={!enabled || executeMutation.isPending}
            className="professional-button-secondary flex-1 border-red-500/20 text-red-400 hover:bg-red-500/10"
          >
            {executeMutation.isPending ? 'Executing...' : 'Execute Auto-Sells'}
          </button>
        </div>

        {/* Current Settings Summary */}
        {rules && (
          <div className="mt-6 pt-6 border-t border-border">
            <h3 className="font-semibold mb-3">Current Settings</h3>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <div className="text-muted-foreground">Status</div>
                <div className={cn('font-medium', rules.enabled ? 'text-green-400' : 'text-red-400')}>
                  {rules.enabled ? 'Enabled' : 'Disabled'}
                </div>
              </div>
              <div>
                <div className="text-muted-foreground">Stop-Loss</div>
                <div className="font-medium">{rules.stop_loss_percent}%</div>
              </div>
              <div>
                <div className="text-muted-foreground">Take-Profit</div>
                <div className="font-medium">+{rules.take_profit_percent}%</div>
              </div>
              <div>
                <div className="text-muted-foreground">AI Signals</div>
                <div className="font-medium">{rules.watch_ai_signals ? 'Watching' : 'Disabled'}</div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
