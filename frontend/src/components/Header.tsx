import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Play, Menu, Stethoscope, ArrowRight, Search } from 'lucide-react';

interface HeaderProps {
  onToggleSidebar?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  const navigate = useNavigate();

  useEffect(() => {
    const handleOpenPalette = () => window.dispatchEvent(new CustomEvent('agentbench:open-command-palette'));
    const button = document.getElementById('agentbench-command-trigger');
    button?.addEventListener('click', handleOpenPalette);
    return () => button?.removeEventListener('click', handleOpenPalette);
  }, []);

  return (
    <header className="sticky top-0 z-30 h-16 bg-surface/90 backdrop-blur-md border-b border-border px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-2 rounded-lg hover:bg-surface-secondary text-primary-secondary hover:text-primary-text"
          aria-label="Open navigation"
        >
          <Menu className="w-5 h-5" />
        </button>

        <button
          id="agentbench-command-trigger"
          type="button"
          aria-label="Open command palette"
          className="hidden sm:flex items-center gap-3 w-72 px-3 py-2 bg-surface-secondary hover:bg-surface-tertiary border border-border rounded-lg text-primary-muted transition-colors text-left"
        >
          <Search className="w-4 h-4 shrink-0" />
          <span className="text-xs font-mono flex-1">Search commands...</span>
          <kbd className="text-[10px] border border-border-light rounded px-1.5 py-0.5 text-primary-secondary">⌘K</kbd>
        </button>

        <div className="hidden xl:flex items-center text-xs font-mono text-primary-secondary">
          <span>Free local-first AI evaluation platform</span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Link
          to="/doctor"
          className="hidden md:flex items-center gap-1.5 px-3.5 py-2 text-xs font-mono text-primary-secondary hover:text-primary-text bg-surface-secondary hover:bg-surface-tertiary rounded-lg border border-border transition-colors"
        >
          <Stethoscope className="w-3.5 h-3.5 text-brand-orange" />
          <span>Doctor</span>
        </Link>

        <button
          onClick={() => navigate('/run')}
          className="flex items-center gap-2 px-5 py-2 bg-brand-orange hover:bg-brand-orange-hover text-black font-extrabold text-xs font-mono rounded-lg shadow-sm transition-all transform active:scale-95"
        >
          <Play className="w-3.5 h-3.5" />
          <span>RUN BENCHMARK</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </header>
  );
};
