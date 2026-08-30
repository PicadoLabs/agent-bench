import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../lib/api';
import { FailureStats } from '../types';
import {
  AlertTriangle,
  XCircle,
  Clock,
  Wrench,
  FileCode,
  ShieldAlert,
  HelpCircle,
  ArrowRight
} from 'lucide-react';

export const FailureAnalysis: React.FC = () => {
  const navigate = useNavigate();
  const [stats, setStats] = useState<FailureStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  useEffect(() => {
    async function loadFailures() {
      try {
        const data = await api.getFailures();
        setStats(data);
      } catch (err) {
        console.error('Failed to load failure stats', err);
      } finally {
        setLoading(false);
      }
    }
    loadFailures();
  }, []);

  const categoriesConfig = [
    { key: 'test_failure', label: 'Test Failure', icon: XCircle, color: 'text-status-error' },
    { key: 'wrong_solution', label: 'Wrong Solution', icon: AlertTriangle, color: 'text-status-warning' },
    { key: 'incomplete_solution', label: 'Incomplete Solution', icon: FileCode, color: 'text-brand-orange' },
    { key: 'timeout', label: 'Timeout', icon: Clock, color: 'text-status-warning' },
    { key: 'syntax_error', label: 'Syntax Error', icon: FileCode, color: 'text-status-error' },
    { key: 'tool_misuse', label: 'Tool Misuse', icon: Wrench, color: 'text-primary-text' },
    { key: 'permission_error', label: 'Security Block', icon: ShieldAlert, color: 'text-status-error' },
    { key: 'dependency_issue', label: 'Dependency Issue', icon: HelpCircle, color: 'text-primary-muted' },
  ];

  const recentFailures = stats?.recent_failures || [];
  const filteredFailures = selectedCategory
    ? recentFailures.filter((f) => f.primary_failure === selectedCategory)
    : recentFailures;

  return (
    <div className="space-y-12 pb-20">
      {/* Hero Header */}
      <div className="pb-6 border-b border-border">
        <span className="text-xs font-mono text-brand-orange font-bold tracking-widest uppercase">
          ROOT-CAUSE DIAGNOSTICS &amp; TAXONOMY
        </span>
        <h1 className="text-3xl lg:text-5xl font-extrabold text-primary-text tracking-tight uppercase mt-2 font-sans">
          WHY DID <br />
          <span className="text-brand-orange text-glow-orange">THE AGENT FAIL?</span>
        </h1>
        <p className="text-sm text-primary-secondary mt-2 max-w-2xl font-medium">
          Comprehensive taxonomy of agent failure modes, assertion errors, execution timeouts, and path traversal restrictions.
        </p>
      </div>

      {/* Failure Category Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {categoriesConfig.map((cat) => {
          const count = stats?.category_counts?.[cat.key] || 0;
          const Icon = cat.icon;
          const isSelected = selectedCategory === cat.key;
          return (
            <button
              key={cat.key}
              onClick={() => setSelectedCategory(isSelected ? null : cat.key)}
              className={`p-6 bg-surface-card rounded-card border text-left transition-all ${
                isSelected
                  ? 'border-brand-orange bg-surface-secondary shadow-lg'
                  : 'border-border hover:border-border-light hover:-translate-y-0.5'
              }`}
            >
              <div className="flex items-center justify-between">
                <Icon className={`w-5 h-5 ${cat.color}`} />
                <span className="text-2xl font-black font-mono text-primary-text">{count}</span>
              </div>
              <div className="mt-3.5 font-mono font-bold text-xs text-primary-text">
                {cat.label}
              </div>
              <div className="text-[10px] font-mono text-primary-muted mt-0.5">
                {count === 1 ? '1 failure' : `${count} failures`}
              </div>
            </button>
          );
        })}
      </div>

      {/* Filter indicator */}
      {selectedCategory && (
        <div className="flex items-center justify-between p-3.5 bg-surface-card rounded-lg border border-border font-mono text-xs">
          <span>
            Filtering by category: <strong className="text-brand-orange uppercase">{selectedCategory}</strong>
          </span>
          <button
            onClick={() => setSelectedCategory(null)}
            className="text-primary-muted hover:text-primary-text underline font-bold"
          >
            Clear Filter
          </button>
        </div>
      )}

      {/* Failed Runs List */}
      <div className="bg-surface-card rounded-card border border-border overflow-hidden">
        <div className="p-6 border-b border-border flex items-center justify-between">
          <div>
            <h3 className="font-mono font-bold text-sm text-primary-text uppercase">
              Recent Failed Benchmark Executions
            </h3>
            <p className="text-xs text-primary-muted font-mono mt-0.5">
              Inspecting root causes, failed test cases, and suggested fixes
            </p>
          </div>
        </div>

        <div className="divide-y divide-border">
          {filteredFailures.length === 0 ? (
            <div className="p-12 text-center text-primary-muted font-mono text-xs italic">
              No failed benchmark runs recorded in this category.
            </div>
          ) : (
            filteredFailures.map((item, idx) => (
              <div key={idx} className="p-6 hover:bg-surface-hover transition-colors font-mono text-xs space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Link
                      to={`/runs/${item.run_id}`}
                      className="text-sm font-bold text-brand-orange hover:underline"
                    >
                      {item.run_id}
                    </Link>
                    <span className="px-2.5 py-0.5 bg-status-error/10 border border-status-error/30 text-status-error font-bold rounded uppercase text-[10px]">
                      {item.primary_failure}
                    </span>
                  </div>
                  <span className="text-primary-muted text-[10px]">
                    {item.timestamp ? new Date(item.timestamp).toLocaleString() : ''}
                  </span>
                </div>

                <div className="bg-surface p-4 rounded-lg border border-border text-primary-text font-medium leading-relaxed font-sans">
                  <span className="text-primary-muted text-[10px] uppercase font-bold font-mono block mb-1">Root Cause:</span>
                  {item.root_cause}
                </div>

                {item.resolution_hints && (
                  <div className="text-primary-secondary text-[11px] font-sans">
                    <span className="text-brand-orange font-bold font-mono">Remediation Hint: </span>
                    {item.resolution_hints}
                  </div>
                )}

                <div className="flex items-center justify-between pt-1 text-[11px] text-primary-muted">
                  <div className="flex gap-4">
                    <span>Failed Tests: <strong className="text-status-error">{item.failed_tests_count}</strong></span>
                    <span>Repair Attempts: <strong className="text-primary-text">{item.attempts_count}</strong></span>
                  </div>

                  <Link
                    to={`/runs/${item.run_id}`}
                    className="flex items-center gap-1 text-primary-text hover:text-brand-orange font-bold transition-colors"
                  >
                    <span>Inspect Run Trace</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </Link>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
