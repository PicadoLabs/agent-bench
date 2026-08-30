import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { LeaderboardEntry } from '../types';
import { formatTime, formatScore, formatCost } from '../lib/utils';
import {
  Trophy,
  Search
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

export const Leaderboard: React.FC = () => {
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState<'all' | 'local' | 'api'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    async function loadLeaderboard() {
      try {
        const data = await api.getLeaderboard();
        setEntries(data);
      } catch (err) {
        console.error('Failed to load leaderboard', err);
      } finally {
        setLoading(false);
      }
    }
    loadLeaderboard();
  }, []);

  const filtered = entries.filter((item) => {
    if (filterType === 'local' && !item.is_local) return false;
    if (filterType === 'api' && item.is_local) return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      return (
        item.agent_name.toLowerCase().includes(q) ||
        item.model_name.toLowerCase().includes(q) ||
        item.provider_name.toLowerCase().includes(q)
      );
    }
    return true;
  });

  const getRankBadge = (rank: number) => {
    const formatted = rank < 10 ? `0${rank}` : `${rank}`;
    if (rank === 1) {
      return (
        <span className="w-8 h-8 rounded-lg bg-brand-orange text-black font-black text-xs font-mono flex items-center justify-center shadow-md">
          {formatted}
        </span>
      );
    }
    return <span className="font-mono font-bold text-primary-muted text-sm pl-2">{formatted}</span>;
  };

  const chartData = filtered.slice(0, 8).map((e) => ({
    name: `${e.agent_name.replace('Agent', '')} / ${e.model_name}`,
    score: e.avg_score,
    success: e.success_rate,
  }));

  return (
    <div className="space-y-12 pb-20">
      {/* Hero Header */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6 pb-6 border-b border-border">
        <div>
          <span className="text-xs font-mono text-brand-orange font-bold tracking-widest uppercase">
            GLOBAL BENCHMARK LEADERBOARD
          </span>
          <h1 className="text-3xl lg:text-5xl font-extrabold text-primary-text tracking-tight uppercase mt-2 font-sans">
            WHO BUILDS THE <br />
            <span className="text-brand-orange text-glow-orange">BEST AGENT?</span>
          </h1>
          <p className="text-sm text-primary-secondary mt-2 max-w-2xl font-medium">
            Objective rankings based on test pass rates, correctness, code quality, speed, and cost efficiency.
          </p>
        </div>

        {/* Filter Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex rounded-lg bg-surface border border-border p-1 text-xs font-mono">
            <button
              onClick={() => setFilterType('all')}
              className={`px-3.5 py-1.5 rounded-md font-bold transition-all ${
                filterType === 'all' ? 'bg-brand-orange text-black shadow-sm' : 'text-primary-secondary hover:text-primary-text'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilterType('local')}
              className={`px-3.5 py-1.5 rounded-md font-bold transition-all ${
                filterType === 'local' ? 'bg-brand-orange text-black shadow-sm' : 'text-primary-secondary hover:text-primary-text'
              }`}
            >
              Local (Ollama)
            </button>
            <button
              onClick={() => setFilterType('api')}
              className={`px-3.5 py-1.5 rounded-md font-bold transition-all ${
                filterType === 'api' ? 'bg-brand-orange text-black shadow-sm' : 'text-primary-secondary hover:text-primary-text'
              }`}
            >
              Cloud API
            </button>
          </div>
        </div>
      </div>

      {/* Top Chart Section */}
      <div className="bg-surface-card p-6 rounded-card border border-border">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="font-mono font-bold text-sm text-primary-text uppercase">
              Average Score Comparison (Top Configurations)
            </h3>
            <p className="text-xs text-primary-muted font-mono mt-0.5">
              Normalized score 0–100 across evaluated runs
            </p>
          </div>
        </div>

        <div className="h-64 w-full">
          {chartData.length === 0 ? (
            <div className="h-full flex items-center justify-center text-xs text-primary-muted font-mono italic">
              No leaderboard entries to display.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1c1c1c" vertical={false} />
                <XAxis dataKey="name" stroke="#555" tick={{ fill: '#777', fontSize: 10 }} angle={-15} textAnchor="end" />
                <YAxis domain={[0, 100]} stroke="#555" tick={{ fill: '#777', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0D0D0D', borderColor: '#252525', borderRadius: '8px', color: '#fff' }}
                />
                <Bar dataKey="score" fill="#FF5A1F" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Leaderboard Table */}
      <div className="bg-surface-card rounded-card border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-surface text-primary-muted border-b border-border uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-4 px-6 text-center w-16">Rank</th>
                <th className="py-4 px-6">Agent Configuration</th>
                <th className="py-4 px-6">Model</th>
                <th className="py-4 px-6">Provider</th>
                <th className="py-4 px-6 text-right">Success Rate</th>
                <th className="py-4 px-6 text-right">Avg Score</th>
                <th className="py-4 px-6 text-right">Avg Duration</th>
                <th className="py-4 px-6 text-right">Avg Cost</th>
                <th className="py-4 px-6 text-center">Runs</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border text-primary-secondary">
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={9} className="py-12 text-center text-primary-muted italic">
                    No benchmark runs recorded yet. Run your first benchmark to populate the leaderboard.
                  </td>
                </tr>
              ) : (
                filtered.map((entry) => (
                  <tr key={`${entry.agent_name}-${entry.model_name}`} className="hover:bg-surface-hover transition-colors">
                    <td className="py-4 px-6 text-center">{getRankBadge(entry.rank)}</td>
                    <td className="py-4 px-6">
                      <div className="font-bold text-primary-text">{entry.agent_name}</div>
                    </td>
                    <td className="py-4 px-6 text-primary-muted">{entry.model_name}</td>
                    <td className="py-4 px-6">
                      <span
                        className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase border ${
                          entry.is_local
                            ? 'bg-brand-orange/10 text-brand-orange border-brand-orange/30'
                            : 'bg-surface text-primary-secondary border-border'
                        }`}
                      >
                        {entry.provider_name}
                      </span>
                    </td>
                    <td className="py-4 px-6 text-right font-bold text-status-success">
                      {entry.success_rate}%
                    </td>
                    <td className="py-4 px-6 text-right font-black text-sm text-brand-orange">
                      {entry.avg_score}
                    </td>
                    <td className="py-4 px-6 text-right">{formatTime(entry.avg_time)}</td>
                    <td className="py-4 px-6 text-right">{formatCost(entry.avg_cost)}</td>
                    <td className="py-4 px-6 text-center font-bold text-primary-text">
                      {entry.total_runs}
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
