import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import logoImg from '../assets/logo.png';
import {
  LayoutDashboard,
  Layers,
  PlayCircle,
  Activity,
  Trophy,
  AlertTriangle,
  Bot,
  Stethoscope,
  PlusCircle,
  GitCompare
} from 'lucide-react';

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ isOpen = true, onClose }) => {
  const navSections = [
    {
      title: 'OVERVIEW',
      items: [
        { label: 'Dashboard', path: '/', icon: LayoutDashboard },
        { label: 'Benchmarks', path: '/benchmarks', icon: Layers },
        { label: 'New Benchmark', path: '/benchmarks/create', icon: PlusCircle },
      ],
    },
    {
      title: 'EXECUTION',
      items: [
        { label: 'Run Benchmark', path: '/run', icon: PlayCircle },
        { label: 'Runs History', path: '/runs', icon: Activity },
        { label: 'Agents & Models', path: '/agents-models', icon: Bot },
      ],
    },
    {
      title: 'ANALYSIS',
      items: [
        { label: 'Leaderboard', path: '/leaderboard', icon: Trophy },
        { label: 'Failure Analysis', path: '/failures', icon: AlertTriangle },
        { label: 'Compare Runs', path: '/compare', icon: GitCompare },
      ],
    },
    {
      title: 'SYSTEM',
      items: [
        { label: 'Environment Doctor', path: '/doctor', icon: Stethoscope },
      ],
    },
  ];

  return (
    <aside
      className={`fixed inset-y-0 left-0 z-40 w-64 bg-surface border-r border-border flex flex-col justify-between transition-transform duration-200 lg:translate-x-0 ${
        isOpen ? 'translate-x-0' : '-translate-x-full'
      }`}
    >
      <div>
        {/* Brand Logo & Tagline */}
        <div className="p-5 border-b border-border">
          <Link to="/" className="flex items-center gap-3 group">
            <img
              src={logoImg}
              alt="AgentBench Logo"
              className="w-10 h-10 rounded-lg object-contain shadow-sm group-hover:scale-105 transition-transform"
            />
            <div>
              <div className="font-extrabold tracking-wider text-primary-text text-sm leading-none font-mono">
                AGENTBENCH
              </div>
              <div className="text-[10px] font-mono text-primary-muted tracking-tight mt-1">
                Evaluate. Compare. Improve.
              </div>
            </div>
          </Link>
        </div>

        {/* Navigation Links */}
        <nav className="p-4 space-y-6 overflow-y-auto max-h-[calc(100vh-170px)]">
          {navSections.map((section, idx) => (
            <div key={idx} className="space-y-1">
              <div className="px-3 text-[10px] font-mono font-bold tracking-widest text-primary-muted uppercase">
                {section.title}
              </div>
              {section.items.map((item, itemIdx) => {
                const Icon = item.icon;
                return (
                  <NavLink
                    key={itemIdx}
                    to={item.path}
                    onClick={onClose}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                        isActive
                          ? 'bg-surface-secondary text-primary-text font-semibold border-l-2 border-brand-orange pl-2.5'
                          : 'text-primary-secondary hover:text-primary-text hover:bg-surface-hover'
                      }`
                    }
                  >
                    {({ isActive }) => (
                      <>
                        <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-brand-orange' : 'text-primary-muted'}`} />
                        <span>{item.label}</span>
                      </>
                    )}
                  </NavLink>
                );
              })}
            </div>
          ))}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-4 border-t border-border bg-surface-secondary/40">
        <div className="flex items-center justify-between text-xs text-primary-muted font-mono">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-brand-orange animate-pulse"></span>
            v1.0.0 (Local-First)
          </span>
          <span className="text-[10px] bg-border px-1.5 py-0.5 rounded text-primary-secondary">
            OSS
          </span>
        </div>
      </div>
    </aside>
  );
};
