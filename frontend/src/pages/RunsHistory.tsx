import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../lib/api';
import { RunItem } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { formatTime, formatScore } from '../lib/utils';
import { ArrowRight, Play, Search } from 'lucide-react';

export const RunsHistory: React.FC = () => {
  const navigate = useNavigate();
  const [runs, setRuns] = useState<RunItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  useEffect(() => {
    async function loadRuns() {
      try {
        const data = await api.getRuns(100);
        setRuns(data);
      } catch (err) {
        console.error('Failed to load runs', err);
      } finally {
        setLoading(false);
      }
    }
    loadRuns();
  }, []);

  const filtered = runs.filter((r) => {
    if (statusFilter !== 'ALL' && r.status !== statusFilter) return false;
    if (search) {
      const q = search.toLowerCase();
      return (
        r.id.toLowerCase().includes(q) ||
        (r.benchmark_name && r.benchmark_name.toLowerCase().includes(q)) ||
        r.agent_name.toLowerCase().includes(q) ||
        r.model_name.toLowerCase().includes(q)
      );
    }
    return true;
  });

  return (
    <div className="space-y-10 pb-20">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6 border-b border-border">
        <div>
          <span className="text-xs font-mono text-brand-orange font-bold tracking-widest uppercase">
            EXECUTION ARCHIVE
          </span>
          <h1 className="text-3xl lg:text-5xl font-extrabold text-primary-text uppercase mt-1 font-sans">
            BENCHMARK RUNS HISTORY
          </h1>
          <p className="text-sm text-primary-secondary mt-1 font-medium">
            Inspect all historical evaluation traces, test pass rates, and diff patches.
          </p>
        </div>

        <button
          onClick={() => navigate('/run')}
          className="flex items-center gap-2 px-5 py-3 bg-brand-orange hover:bg-brand-orange-hover text-black font-extrabold text-xs font-mono rounded-lg transition-all shadow-md"
        >
          <Play className="w-4 h-4 fill-black" />
          <span>NEW RUN</span>
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center justify-between font-mono text-xs">
        <div className="flex items-center gap-2 bg-surface-card px-3.5 py-2.5 rounded-lg border border-border w-full max-w-xs">
          <Search className="w-4 h-4 text-primary-muted" />
          <input
            type="text"
            placeholder="Search run ID, benchmark, model..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-transparent text-primary-text focus:outline-none w-full"
          />
        </div>

        <div className="flex items-center gap-2">
          {['ALL', 'SUCCEEDED', 'PARTIAL', 'FAILED'].map((st) => (
            <button
              key={st}
              onClick={() => setStatusFilter(st)}
              className={`px-3.5 py-2 rounded-md font-bold transition-all ${
                statusFilter === st
                  ? 'bg-brand-orange text-black shadow-sm'
                  : 'bg-surface text-primary-secondary hover:text-primary-text border border-border'
              }`}
            >
              {st}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="bg-surface-card rounded-card border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-surface text-primary-muted border-b border-border uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-4 px-6">Run ID</th>
                <th className="py-4 px-6">Benchmark Task</th>
                <th className="py-4 px-6">Agent</th>
                <th className="py-4 px-6">Model</th>
                <th className="py-4 px-6">Status</th>
                <th className="py-4 px-6">Score</th>
                <th className="py-4 px-6">Tests</th>
                <th className="py-4 px-6">Tools</th>
                <th className="py-4 px-6">Time</th>
                <th className="py-4 px-6 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border text-primary-secondary">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={10} className="py-12 text-center text-primary-muted italic">
                    No benchmark runs matching query.
                  </td>
                </tr>
              ) : (
                filtered.map((r) => (
                  <tr key={r.id} className="hover:bg-surface-hover transition-colors">
                    <td className="py-4 px-6 font-bold text-brand-orange">{r.id}</td>
                    <td className="py-4 px-6 font-medium text-primary-text">{r.benchmark_name || r.benchmark_id}</td>
                    <td className="py-4 px-6">{r.agent_name}</td>
                    <td className="py-4 px-6 text-primary-muted">{r.model_name}</td>
                    <td className="py-4 px-6">
                      <StatusBadge status={r.status} size="sm" />
                    </td>
                    <td className="py-4 px-6 font-bold text-primary-text">{formatScore(r.total_score)}</td>
                    <td className="py-4 px-6">{r.passed_tests}/{r.total_tests}</td>
                    <td className="py-4 px-6">{r.tool_calls_count}</td>
                    <td className="py-4 px-6">{formatTime(r.duration_seconds)}</td>
                    <td className="py-4 px-6 text-right">
                      <Link
                        to={`/runs/${r.id}`}
                        className="inline-flex items-center gap-1 text-primary-text hover:text-brand-orange font-bold transition-colors"
                      >
                        <span>Details</span>
                        <ArrowRight className="w-3.5 h-3.5" />
                      </Link>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
