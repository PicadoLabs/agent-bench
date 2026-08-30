import React from 'react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const s = status ? status.toUpperCase() : 'UNKNOWN';

  let bg = 'bg-surface-tertiary text-primary-secondary border-border';
  let dot = 'bg-primary-muted';

  if (s === 'SUCCEEDED' || s === 'PASSED') {
    bg = 'bg-status-success/10 text-status-success border-status-success/30';
    dot = 'bg-status-success';
  } else if (s === 'PARTIAL') {
    bg = 'bg-status-warning/10 text-status-warning border-status-warning/30';
    dot = 'bg-status-warning';
  } else if (s === 'FAILED' || s === 'CRASHED') {
    bg = 'bg-status-error/10 text-status-error border-status-error/30';
    dot = 'bg-status-error';
  } else if (s === 'TIMEOUT') {
    bg = 'bg-status-warning/10 text-status-warning border-status-warning/30';
    dot = 'bg-status-warning animate-pulse';
  } else if (s === 'RUNNING' || s === 'TESTING' || s === 'EVALUATING') {
    bg = 'bg-brand-orange/10 text-brand-orange border-brand-orange/30';
    dot = 'bg-brand-orange animate-ping';
  } else if (s === 'QUEUED' || s === 'PREPARING') {
    bg = 'bg-status-info/10 text-status-info border-status-info/30';
    dot = 'bg-status-info';
  }

  const px = size === 'sm' ? 'px-2.5 py-0.5 text-[10px]' : 'px-3 py-1 text-xs';

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-mono font-semibold tracking-wide rounded-md border ${bg} ${px}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dot}`}></span>
      <span>{s}</span>
    </span>
  );
};
