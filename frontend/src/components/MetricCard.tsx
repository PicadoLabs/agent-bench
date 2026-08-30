import React from 'react';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  icon?: LucideIcon;
  accentColor?: string;
  trend?: string;
  trendUp?: boolean;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subValue,
  icon: Icon,
  accentColor = 'text-brand-orange',
  trend,
  trendUp
}) => {
  return (
    <div className="bg-surface-card p-6 rounded-card border border-border hover:border-border-light transition-all flex flex-col justify-between group">
      <div className="flex items-center justify-between">
        <span className="text-[11px] font-mono font-semibold tracking-wider text-primary-muted uppercase">
          {label}
        </span>
        {Icon && <Icon className={`w-4 h-4 ${accentColor} opacity-90 group-hover:scale-110 transition-transform`} />}
      </div>

      <div className="mt-4 flex items-baseline gap-2">
        <span className="text-3xl lg:text-4xl font-extrabold tracking-tight text-primary-text font-mono">
          {value}
        </span>
        {subValue && (
          <span className="text-xs text-primary-muted font-mono">
            {subValue}
          </span>
        )}
      </div>

      {trend && (
        <div className="mt-3 text-[11px] font-mono">
          <span className={trendUp ? 'text-status-success' : 'text-status-error'}>
            {trend}
          </span>
        </div>
      )}
    </div>
  );
};
