import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ArrowRight, Command, Search } from 'lucide-react';

interface CommandItem {
  id: string;
  label: string;
  description: string;
  path: string;
  keywords: string[];
}

const COMMANDS: CommandItem[] = [
  { id: 'dashboard', label: 'Dashboard', description: 'Overview and system activity', path: '/', keywords: ['home', 'overview'] },
  { id: 'benchmarks', label: 'Benchmarks', description: 'Browse evaluation tasks', path: '/benchmarks', keywords: ['tasks', 'repository', 'library'] },
  { id: 'create-benchmark', label: 'Create Benchmark', description: 'Define a new evaluation task', path: '/benchmarks/create', keywords: ['new', 'task', 'benchmark'] },
  { id: 'run', label: 'Run Benchmark', description: 'Start an evaluation run', path: '/run', keywords: ['execute', 'start', 'agent'] },
  { id: 'runs', label: 'Runs History', description: 'Inspect previous executions', path: '/runs', keywords: ['history', 'executions', 'archive'] },
  { id: 'leaderboard', label: 'Leaderboard', description: 'Compare evaluated configurations', path: '/leaderboard', keywords: ['scores', 'ranking', 'models'] },
  { id: 'failures', label: 'Failure Analysis', description: 'Inspect agent failure modes', path: '/failures', keywords: ['errors', 'diagnostics', 'root cause'] },
  { id: 'agents', label: 'Agents & Models', description: 'Inspect available agents and providers', path: '/agents-models', keywords: ['llm', 'provider', 'models'] },
  { id: 'compare', label: 'Compare Runs', description: 'Compare execution results side by side', path: '/compare', keywords: ['diff', 'results', 'analysis'] },
  { id: 'doctor', label: 'Environment Doctor', description: 'Diagnose local dependencies and runtime health', path: '/doctor', keywords: ['health', 'diagnostics', 'docker', 'ollama'] },
];

function fuzzyScore(query: string, command: CommandItem): number {
  if (!query.trim()) return 0;
  const haystack = [command.label, command.description, ...command.keywords].join(' ').toLowerCase();
  const needle = query.trim().toLowerCase();
  if (haystack.includes(needle)) return 100 - haystack.indexOf(needle);
  let score = 0;
  let cursor = 0;
  for (const char of needle) {
    const index = haystack.indexOf(char, cursor);
    if (index === -1) return -1;
    score += index === cursor ? 4 : 1;
    cursor = index + 1;
  }
  return score;
}

export const CommandPalette: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [activeIndex, setActiveIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const results = useMemo(() => {
    return COMMANDS
      .map((command) => ({ command, score: fuzzyScore(query, command) }))
      .filter(({ score }) => score >= 0)
      .sort((a, b) => b.score - a.score)
      .map(({ command }) => command);
  }, [query]);

  const close = () => {
    setOpen(false);
    setQuery('');
    setActiveIndex(0);
  };

  const select = (command: CommandItem) => {
    close();
    navigate(command.path);
  };

  useEffect(() => {
    const openPalette = () => {
      setOpen(true);
      setQuery('');
      setActiveIndex(0);
    };

    const onKeyDown = (event: KeyboardEvent) => {
      const isShortcut = (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === 'k';
      if (isShortcut) {
        event.preventDefault();
        openPalette();
        return;
      }

      if (!open) return;
      if (event.key === 'Escape') {
        event.preventDefault();
        close();
      } else if (event.key === 'ArrowDown') {
        event.preventDefault();
        setActiveIndex((index) => Math.min(index + 1, Math.max(results.length - 1, 0)));
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        setActiveIndex((index) => Math.max(index - 1, 0));
      } else if (event.key === 'Enter') {
        event.preventDefault();
        const command = results[activeIndex];
        if (command) select(command);
      }
    };

    window.addEventListener('agentbench:open-command-palette', openPalette);
    window.addEventListener('keydown', onKeyDown);
    return () => {
      window.removeEventListener('agentbench:open-command-palette', openPalette);
      window.removeEventListener('keydown', onKeyDown);
    };
  }, [open, results, activeIndex]);

  useEffect(() => {
    if (open) {
      requestAnimationFrame(() => inputRef.current?.focus());
    }
  }, [open]);

  useEffect(() => {
    if (open) {
      setOpen(false);
      setQuery('');
      setActiveIndex(0);
    }
  }, [location.pathname]);

  useEffect(() => {
    setActiveIndex(0);
  }, [query]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-[100] flex items-start justify-center px-4 pt-[12vh] bg-black/70 backdrop-blur-sm"
      role="presentation"
      onMouseDown={(event) => {
        if (event.target === event.currentTarget) close();
      }}
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label="Command palette"
        className="w-full max-w-2xl overflow-hidden rounded-xl border border-border bg-surface-card shadow-2xl"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="flex items-center gap-3 border-b border-border px-4">
          <Search className="h-5 w-5 shrink-0 text-primary-muted" aria-hidden="true" />
          <input
            ref={inputRef}
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Search commands..."
            aria-label="Search commands"
            aria-controls="agentbench-command-list"
            className="h-14 flex-1 bg-transparent text-sm text-primary-text outline-none placeholder:text-primary-muted"
          />
          <kbd className="hidden sm:inline-flex items-center gap-1 rounded border border-border-light px-2 py-1 text-[10px] font-mono text-primary-muted">
            <Command className="h-3 w-3" aria-hidden="true" /> K
          </kbd>
        </div>

        <div id="agentbench-command-list" role="listbox" aria-label="Commands" className="max-h-[55vh] overflow-y-auto p-2">
          {results.length === 0 ? (
            <div className="px-4 py-10 text-center text-xs font-mono text-primary-muted">
              No commands match <span className="text-primary-text">"{query}"</span>.
            </div>
          ) : (
            results.map((command, index) => {
              const active = index === activeIndex;
              return (
                <button
                  key={command.id}
                  type="button"
                  role="option"
                  aria-selected={active}
                  onMouseEnter={() => setActiveIndex(index)}
                  onClick={() => select(command)}
                  className={`w-full flex items-center gap-3 rounded-lg px-3 py-3 text-left transition-colors ${active ? 'bg-surface-secondary text-primary-text' : 'text-primary-secondary hover:bg-surface-secondary/70'}`}
                >
                  <div className="min-w-0 flex-1">
                    <div className="font-mono text-sm font-bold">{command.label}</div>
                    <div className="mt-0.5 truncate text-[11px] text-primary-muted">{command.description}</div>
                  </div>
                  <ArrowRight className={`h-4 w-4 shrink-0 ${active ? 'text-brand-orange' : 'text-primary-muted'}`} aria-hidden="true" />
                </button>
              );
            })
          )}
        </div>

        <div className="flex items-center justify-between border-t border-border px-4 py-2 text-[10px] font-mono text-primary-muted">
          <span>↑↓ navigate · Enter select · Esc close</span>
          <span>{results.length} command{results.length === 1 ? '' : 's'}</span>
        </div>
      </div>
    </div>
  );
};
