import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../lib/api';
import { Benchmark } from '../types';
import { Modal } from '../components/Modal';
import {
  Layers,
  Play,
  Plus,
  Clock,
  FolderGit2,
  Terminal as TermIcon,
  ArrowRight
} from 'lucide-react';

export const Benchmarks: React.FC = () => {
  const navigate = useNavigate();
  const [benchmarks, setBenchmarks] = useState<Benchmark[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedBenchmark, setSelectedBenchmark] = useState<Benchmark | null>(null);

  useEffect(() => {
    async function fetchBenchmarks() {
      try {
        const data = await api.getBenchmarks();
        setBenchmarks(data);
      } catch (err) {
        console.error('Failed to load benchmarks', err);
      } finally {
        setLoading(false);
      }
    }
    fetchBenchmarks();
  }, []);

  const categories = ['All', 'Bug Fixing', 'Feature Implementation', 'Refactoring', 'Debugging'];

  const filtered = selectedCategory === 'All'
    ? benchmarks
    : benchmarks.filter((b) => b.category.toLowerCase().includes(selectedCategory.toLowerCase()));

  const getDifficultyColor = (diff: string) => {
    const d = diff.toLowerCase();
    if (d === 'easy') return 'text-status-success bg-status-success/10 border-status-success/30';
    if (d === 'hard') return 'text-status-error bg-status-error/10 border-status-error/30';
    return 'text-status-warning bg-status-warning/10 border-status-warning/30';
  };

  return (
    <div className="space-y-12 pb-20">
      {/* Hero Header */}
      <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6 pb-6 border-b border-border">
        <div>
          <span className="text-xs font-mono text-brand-orange font-bold tracking-widest uppercase">
            BENCHMARK REPOSITORY LIBRARY
          </span>
          <h1 className="text-3xl lg:text-5xl font-extrabold text-primary-text tracking-tight uppercase mt-2 font-sans">
            REAL TASKS. <br />
            <span className="text-brand-orange text-glow-orange">REAL REPOSITORIES.</span> <br />
            REAL RESULTS.
          </h1>
          <p className="text-sm text-primary-secondary mt-2 max-w-2xl font-medium">
            Explore original, standardized coding benchmarks across bug fixing, features, refactoring, and debugging.
          </p>
        </div>

        <Link
          to="/benchmarks/create"
          className="flex items-center gap-2 px-5 py-3 bg-brand-orange hover:bg-brand-orange-hover text-black font-extrabold text-xs font-mono rounded-lg transition-all transform active:scale-95 shrink-0 shadow-lg"
        >
          <Plus className="w-4 h-4" />
          <span>NEW BENCHMARK</span>
        </Link>
      </div>

      {/* Filter Tabs */}
      <div className="flex flex-wrap gap-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-lg text-xs font-mono font-bold transition-all ${
              selectedCategory === cat
                ? 'bg-brand-orange text-black shadow-md'
                : 'bg-surface text-primary-secondary hover:text-primary-text hover:bg-surface-secondary border border-border'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Benchmarks Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filtered.map((b) => (
          <div
            key={b.id}
            className="bg-surface-card rounded-card border border-border hover:border-brand-orange/40 hover:-translate-y-1 transition-all flex flex-col justify-between p-6 group relative overflow-hidden"
          >
            {/* Subtle top indicator on hover */}
            <div className="absolute top-0 left-0 right-0 h-1 bg-brand-orange opacity-0 group-hover:opacity-100 transition-opacity" />

            <div className="space-y-4">
              {/* Category & Difficulty Badges */}
              <div className="flex items-center justify-between">
                <span className="text-[11px] font-mono text-primary-muted bg-surface px-2.5 py-0.5 rounded border border-border font-medium">
                  {b.category}
                </span>
                <span
                  className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded border ${getDifficultyColor(
                    b.difficulty
                  )}`}
                >
                  {b.difficulty}
                </span>
              </div>

              {/* Title & Description */}
              <div>
                <h3 className="font-mono font-black text-base text-primary-text group-hover:text-brand-orange transition-colors">
                  {b.name}
                </h3>
                <p className="text-xs text-primary-secondary mt-2 line-clamp-2 leading-relaxed font-sans">
                  {b.description || b.prompt}
                </p>
              </div>

              {/* Specs Box */}
              <div className="bg-surface p-3.5 rounded-lg border border-border/70 space-y-2 text-[11px] font-mono text-primary-muted">
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <TermIcon className="w-3.5 h-3.5 text-brand-orange" />
                    <span>Command:</span>
                  </span>
                  <span className="text-primary-text truncate max-w-[140px]">
                    {b.evaluation_command}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <Clock className="w-3.5 h-3.5 text-primary-muted" />
                    <span>Timeout:</span>
                  </span>
                  <span className="text-primary-text">{b.evaluation_timeout}s</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="flex items-center gap-1.5">
                    <FolderGit2 className="w-3.5 h-3.5 text-primary-muted" />
                    <span>Commit:</span>
                  </span>
                  <span className="text-primary-text">{b.repo_commit}</span>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="mt-6 pt-4 border-t border-border flex items-center justify-between gap-3">
              <button
                onClick={() => setSelectedBenchmark(b)}
                className="text-xs font-mono font-semibold text-primary-muted hover:text-primary-text transition-colors"
              >
                Inspect Task
              </button>

              <button
                onClick={() => navigate(`/run?benchmark=${b.id}`)}
                className="flex items-center gap-1.5 px-3.5 py-1.5 bg-brand-orange hover:bg-brand-orange-hover text-black font-mono font-bold text-xs rounded-lg transition-all shadow-sm"
              >
                <Play className="w-3 h-3 fill-current" />
                <span>Run</span>
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Benchmark Detail Modal */}
      {selectedBenchmark && (
        <Modal
          isOpen={Boolean(selectedBenchmark)}
          onClose={() => setSelectedBenchmark(null)}
          title={`Benchmark: ${selectedBenchmark.name}`}
        >
          <div className="space-y-6 text-xs font-mono">
            <div>
              <span className="text-primary-muted uppercase text-[10px] font-bold">
                Task Prompt
              </span>
              <div className="mt-1.5 p-4 bg-surface rounded-lg border border-border text-primary-text leading-relaxed whitespace-pre-wrap font-sans">
                {selectedBenchmark.prompt}
              </div>
            </div>

            {selectedBenchmark.constraints && (
              <div>
                <span className="text-primary-muted uppercase text-[10px] font-bold">
                  Constraints
                </span>
                <div className="mt-1.5 p-4 bg-surface rounded-lg border border-border text-status-warning leading-relaxed whitespace-pre-wrap font-sans">
                  {selectedBenchmark.constraints}
                </div>
              </div>
            )}

            <div>
              <span className="text-primary-muted uppercase text-[10px] font-bold">
                Scoring Weights Breakdown
              </span>
              <div className="mt-1.5 grid grid-cols-5 gap-2 text-center">
                {Object.entries(selectedBenchmark.scoring_weights || {}).map(([key, weight]) => (
                  <div key={key} className="bg-surface p-2.5 rounded-lg border border-border">
                    <div className="text-[10px] text-primary-muted uppercase truncate">{key}</div>
                    <div className="text-sm font-bold text-brand-orange mt-0.5">{weight}%</div>
                  </div>
                ))}
              </div>
            </div>

            <div className="pt-4 flex justify-end gap-3">
              <button
                onClick={() => setSelectedBenchmark(null)}
                className="px-4 py-2 bg-surface hover:bg-surface-secondary rounded-lg text-primary-secondary transition-colors"
              >
                Close
              </button>
              <button
                onClick={() => navigate(`/run?benchmark=${selectedBenchmark.id}`)}
                className="px-5 py-2 bg-brand-orange hover:bg-brand-orange-hover text-black font-bold rounded-lg transition-colors flex items-center gap-1.5 shadow-md"
              >
                <Play className="w-3.5 h-3.5 fill-black" />
                <span>Start Benchmark</span>
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
