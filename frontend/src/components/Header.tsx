import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Play, Menu, Stethoscope, ArrowRight } from 'lucide-react';

interface HeaderProps {
  onToggleSidebar?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onToggleSidebar }) => {
  const navigate = useNavigate();

  return (
    <header className="sticky top-0 z-30 h-16 bg-surface/90 backdrop-blur-md border-b border-border px-6 flex items-center justify-between">
      <div className="flex items-center gap-4">
        <button
          onClick={onToggleSidebar}
          className="lg:hidden p-2 rounded-lg hover:bg-surface-secondary text-primary-secondary hover:text-primary-text"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div className="hidden sm:flex items-center text-xs font-mono text-primary-secondary">
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
          <span>RUN BENCHMARK</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </header>
  );
};
