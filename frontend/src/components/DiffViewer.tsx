import React from 'react';
import { GitCommit, Copy, Check } from 'lucide-react';

interface DiffViewerProps {
  diff: string;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ diff }) => {
  const [copied, setCopied] = React.useState(false);

  if (!diff || !diff.trim()) {
    return (
      <div className="bg-surface-card p-8 rounded-card border border-border text-center text-primary-muted font-mono text-xs">
        <GitCommit className="w-8 h-8 mx-auto mb-2 opacity-40 text-primary-muted" />
        No Git diff detected for this run.
      </div>
    );
  }

  const lines = diff.split('\n');

  const handleCopy = () => {
    navigator.clipboard.writeText(diff);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-[#050505] rounded-card border border-border overflow-hidden font-mono text-xs shadow-xl">
      {/* Titlebar */}
      <div className="bg-surface px-4 py-3 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2 text-primary-muted font-bold text-[11px]">
          <GitCommit className="w-3.5 h-3.5 text-brand-orange" />
          <span>Git Diff Patch</span>
        </div>

        <button
          onClick={handleCopy}
          className="text-primary-muted hover:text-primary-text flex items-center gap-1 text-[11px] hover:bg-surface-secondary px-2.5 py-1 rounded transition-colors"
        >
          {copied ? <Check className="w-3 h-3 text-brand-orange" /> : <Copy className="w-3 h-3" />}
          <span>{copied ? 'Copied Diff' : 'Copy Diff'}</span>
        </button>
      </div>

      {/* Diff Content */}
      <div className="p-4 overflow-x-auto max-h-[500px] overflow-y-auto leading-relaxed select-text space-y-0.5">
        {lines.map((line, idx) => {
          let bg = 'bg-transparent text-primary-secondary';
          if (line.startsWith('+') && !line.startsWith('+++')) {
            bg = 'bg-status-success/10 text-status-success';
          } else if (line.startsWith('-') && !line.startsWith('---')) {
            bg = 'bg-status-error/10 text-status-error';
          } else if (line.startsWith('@@')) {
            bg = 'bg-brand-orange/15 text-brand-orange font-semibold';
          } else if (line.startsWith('diff --git') || line.startsWith('index ')) {
            bg = 'text-primary-muted font-bold';
          }

          return (
            <div key={idx} className={`px-2 py-0.5 rounded font-mono ${bg} whitespace-pre`}>
              {line}
            </div>
          );
        })}
      </div>
    </div>
  );
};
