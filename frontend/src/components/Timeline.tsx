import React from 'react';
import { ExecutionEventItem } from '../types';
import {
  PlayCircle,
  Box,
  Wrench,
  Activity,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Terminal as TermIcon,
  Sparkles
} from 'lucide-react';

interface TimelineProps {
  events: ExecutionEventItem[];
}

export const Timeline: React.FC<TimelineProps> = ({ events }) => {
  const getIcon = (eventType: string) => {
    if (eventType.includes('benchmark_started')) return <PlayCircle className="w-4 h-4 text-brand-orange" />;
    if (eventType.includes('sandbox')) return <Box className="w-4 h-4 text-primary-text" />;
    if (eventType.includes('tool')) return <Wrench className="w-4 h-4 text-brand-orange" />;
    if (eventType.includes('test')) return <Activity className="w-4 h-4 text-primary-text" />;
    if (eventType.includes('retry')) return <RefreshCw className="w-4 h-4 text-status-warning" />;
    if (eventType.includes('evaluation')) return <Sparkles className="w-4 h-4 text-brand-orange" />;
    if (eventType.includes('completed') || eventType.includes('success')) return <CheckCircle2 className="w-4 h-4 text-status-success" />;
    if (eventType.includes('failed') || eventType.includes('crashed')) return <XCircle className="w-4 h-4 text-status-error" />;
    return <TermIcon className="w-4 h-4 text-primary-muted" />;
  };

  return (
    <div className="relative pl-6 space-y-6 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-border">
      {events.map((event, idx) => (
        <div key={idx} className="relative group">
          {/* Dot / Icon */}
          <div className="absolute -left-6 top-0.5 w-5 h-5 rounded-full bg-surface border border-border flex items-center justify-center group-hover:border-brand-orange transition-colors">
            {getIcon(event.event_type)}
          </div>

          {/* Event Content */}
          <div className="bg-surface-card p-4 rounded-card border border-border hover:border-border-light transition-all">
            <div className="flex items-center justify-between gap-4">
              <span className="font-mono font-semibold text-xs text-primary-text">
                {event.message}
              </span>
              <span className="text-[10px] font-mono text-primary-muted shrink-0">
                {event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : `Step ${event.step}`}
              </span>
            </div>

            {event.details && Object.keys(event.details).length > 0 && (
              <div className="mt-2.5 text-[11px] font-mono bg-surface p-3 rounded-lg border border-border/50 text-primary-secondary overflow-x-auto">
                <pre>{JSON.stringify(event.details, null, 2)}</pre>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};
