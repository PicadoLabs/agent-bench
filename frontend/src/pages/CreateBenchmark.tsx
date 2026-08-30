import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { PlusCircle, ArrowLeft, Layers, Terminal as TermIcon, Sliders } from 'lucide-react';

export const CreateBenchmark: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    id: '',
    name: '',
    description: '',
    category: 'Bug Fixing',
    difficulty: 'Medium',
    repo_path: './benchmarks/repos/custom-task',
    repo_commit: 'HEAD',
    prompt: '',
    constraints: '',
    evaluation_command: 'pytest',
    evaluation_timeout: 120,
    scoring_weights: {
      correctness: 50,
      test_pass_rate: 25,
      code_quality: 10,
      efficiency: 10,
      reliability: 5,
    },
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.id || !formData.name || !formData.prompt) {
      setError('Please fill in ID, Name, and Task Prompt.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      await api.createBenchmark(formData);
      navigate('/benchmarks');
    } catch (err: any) {
      setError(err.message || 'Failed to create benchmark');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-10 pb-20">
      {/* Top Header */}
      <div className="flex items-center gap-4 border-b border-border pb-6">
        <button
          onClick={() => navigate('/benchmarks')}
          className="p-2.5 bg-surface hover:bg-surface-secondary rounded-lg border border-border text-primary-muted hover:text-primary-text transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>
        <div>
          <span className="text-xs font-mono text-brand-orange font-bold tracking-widest uppercase">
            BENCHMARK CREATOR
          </span>
          <h1 className="text-2xl lg:text-3xl font-black text-primary-text uppercase mt-1 font-mono">
            CREATE BENCHMARK TASK
          </h1>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-status-error/10 border border-status-error/30 text-status-error text-xs font-mono rounded-lg">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8 text-xs font-mono">
        {/* Section 1: Basic Information */}
        <div className="bg-surface-card p-6 rounded-card border border-border space-y-5">
          <div className="flex items-center gap-2 text-primary-text font-bold text-sm uppercase pb-3 border-b border-border">
            <Layers className="w-4 h-4 text-brand-orange" />
            <span>Basic Information</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-primary-muted text-[11px] font-semibold uppercase">
                Task Identifier (Slug) *
              </label>
              <input
                type="text"
                placeholder="e.g. fix-auth-middleware"
                value={formData.id}
                onChange={(e) => setFormData({ ...formData, id: e.target.value })}
                className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-primary-muted text-[11px] font-semibold uppercase">
                Display Name *
              </label>
              <input
                type="text"
                placeholder="e.g. Fix Authentication Middleware"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
                required
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-primary-muted text-[11px] font-semibold uppercase">
              Short Description
            </label>
            <input
              type="text"
              placeholder="Brief summary of the issue or feature"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-primary-muted text-[11px] font-semibold uppercase">
                Category
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
              >
                <option value="Bug Fixing">Bug Fixing</option>
                <option value="Feature Implementation">Feature Implementation</option>
                <option value="Refactoring">Refactoring</option>
                <option value="Testing">Testing</option>
                <option value="Debugging">Debugging</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-primary-muted text-[11px] font-semibold uppercase">
                Difficulty
              </label>
              <select
                value={formData.difficulty}
                onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
              >
                <option value="Easy">Easy</option>
                <option value="Medium">Medium</option>
                <option value="Hard">Hard</option>
              </select>
            </div>
          </div>
        </div>

        {/* Section 2: Repository & Task Description */}
        <div className="bg-surface-card p-6 rounded-card border border-border space-y-5">
          <div className="flex items-center gap-2 text-primary-text font-bold text-sm uppercase pb-3 border-b border-border">
            <TermIcon className="w-4 h-4 text-brand-orange" />
            <span>Repository &amp; Task Definition</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-primary-muted text-[11px] font-semibold uppercase">
                Repository Path (Local or Cloned)
              </label>
              <input
                type="text"
                value={formData.repo_path}
                onChange={(e) => setFormData({ ...formData, repo_path: e.target.value })}
                className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-primary-muted text-[11px] font-semibold uppercase">
                Pinned Commit / Ref
              </label>
              <input
                type="text"
                value={formData.repo_commit}
                onChange={(e) => setFormData({ ...formData, repo_commit: e.target.value })}
                className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-primary-muted text-[11px] font-semibold uppercase">
              Agent Task Prompt *
            </label>
            <textarea
              rows={4}
              placeholder="Instructions given to the AI coding agent..."
              value={formData.prompt}
              onChange={(e) => setFormData({ ...formData, prompt: e.target.value })}
              className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange leading-relaxed"
              required
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-primary-muted text-[11px] font-semibold uppercase">
              Constraints
            </label>
            <textarea
              rows={2}
              placeholder="e.g. Do not modify test files, preserve API signatures."
              value={formData.constraints}
              onChange={(e) => setFormData({ ...formData, constraints: e.target.value })}
              className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange leading-relaxed"
            />
          </div>
        </div>

        {/* Section 3: Evaluation & Scoring */}
        <div className="bg-surface-card p-6 rounded-card border border-border space-y-5">
          <div className="flex items-center gap-2 text-primary-text font-bold text-sm uppercase pb-3 border-b border-border">
            <Sliders className="w-4 h-4 text-brand-orange" />
            <span>Evaluation &amp; Scoring Configuration</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-primary-muted text-[11px] font-semibold uppercase">
                Test Evaluation Command
              </label>
              <input
                type="text"
                value={formData.evaluation_command}
                onChange={(e) => setFormData({ ...formData, evaluation_command: e.target.value })}
                className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-primary-muted text-[11px] font-semibold uppercase">
                Timeout (Seconds)
              </label>
              <input
                type="number"
                value={formData.evaluation_timeout}
                onChange={(e) => setFormData({ ...formData, evaluation_timeout: parseInt(e.target.value) || 120 })}
                className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
              />
            </div>
          </div>
        </div>

        {/* Submit Button */}
        <div className="flex justify-end gap-4 pt-4">
          <button
            type="button"
            onClick={() => navigate('/benchmarks')}
            className="px-6 py-3.5 bg-surface hover:bg-surface-secondary rounded-lg border border-border font-bold text-primary-secondary transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="px-8 py-3.5 bg-brand-orange hover:bg-brand-orange-hover text-black font-extrabold rounded-lg shadow-xl transition-all transform active:scale-95 disabled:opacity-50"
          >
            {loading ? 'CREATING...' : 'CREATE BENCHMARK'}
          </button>
        </div>
      </form>
    </div>
  );
};
