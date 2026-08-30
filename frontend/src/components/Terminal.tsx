import React, { useRef, useEffect } from 'react';
import { Terminal as TermIcon, Copy, Check } from 'lucide-react';

interface TerminalProps {
  title?: string;
  logs: string | string[];
  autoScroll?: boolean;
  maxHeight?: string;
}

export const Terminal: React.FC<TerminalProps> = ({
  title = 'Console Output',
  logs,
  autoScroll = true,
  maxHeight = 'max-h-96',
}) => {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [copied, setCopied] = React.useState(false);

  const logLines = Array.isArray(logs) ? logs : logs.split('\n');
  const fullText = Array.isArray(logs) ? logs.join('\n') : logs;

  useEffect(() => {
    if (autoScroll && bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs, autoScroll]);

  const handleCopy = () => {
    navigator.clipboard.writeText(fullText);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-[#050505] rounded-card border border-border overflow-hidden font-mono text-xs shadow-2xl">
      {/* Terminal Titlebar */}
      <div className="bg-surface px-4 py-3 border-b border-border flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="flex gap-1.5">
            <span className="w-2.5 h-2.5 rounded-full bg-[#2E2E2E]"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-[#2E2E2E]"></span>
            <span className="w-2.5 h-2.5 rounded-full bg-[#2E2E2E]"></span>
          </div>
          <span className="text-primary-muted font-bold text-[11px] ml-2 flex items-center gap-1.5">
            <TermIcon className="w-3.5 h-3.5 text-brand-orange" />
            {title}
          </span>
        </div>

        <button
          onClick={handleCopy}
          className="text-primary-muted hover:text-primary-text flex items-center gap-1 text-[11px] hover:bg-surface-secondary px-2.5 py-1 rounded transition-colors"
          title="Copy output"
        >
          {copied ? <Check className="w-3 h-3 text-brand-orange" /> : <Copy className="w-3 h-3" />}
          <span>{copied ? 'Copied' : 'Copy'}</span>
        </button>
      </div>

      {/* Terminal Body */}
      <div className={`p-4 overflow-y-auto ${maxHeight} space-y-1 select-text leading-relaxed`}>
        {logLines.length === 0 || (logLines.length === 1 && !logLines[0]) ? (
          <div className="text-primary-muted italic py-4 text-center">
            No terminal output generated.
          </div>
        ) : (
          logLines.map((line, idx) => {
            let color = 'text-primary-secondary';
            if (line.includes('PASSED') || line.includes('passed') || line.includes('✓')) {
              color = 'text-status-success';
            } else if (line.includes('FAILED') || line.includes('failed') || line.includes('✕') || line.includes('Error')) {
              color = 'text-status-error';
            } else if (line.includes('WARNING') || line.includes('⚠') || line.includes('retry')) {
              color = 'text-status-warning';
            } else if (line.startsWith('→') || line.startsWith('Tool') || line.includes('AGENT_STEP') || line.includes('TOOL_CALL')) {
              color = 'text-brand-orange';
            }

            return (
              <div key={idx} className={`${color} break-all flex gap-3`}>
                <span className="text-primary-muted/40 select-none text-[10px] w-6 text-right shrink-0">
                  {idx + 1}
                </span>
                <span>{line}</span>
              </div>
            );
          })
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
};
