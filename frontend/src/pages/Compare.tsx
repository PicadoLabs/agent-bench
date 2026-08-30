import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { RunItem } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { DiffViewer } from '../components/DiffViewer';
import { formatTime, formatScore, formatCost } from '../lib/utils';
import { GitCompare, ArrowRight } from 'lucide-react';

export const Compare: React.FC = () => {
  const [runs, setRuns] = useState<RunItem[]>([]);
  const [runAId, setRunAId] = useState<string>('');
  const [runBId, setRunBId] = useState<string>('');
  const [runA, setRunA] = useState<RunItem | null>(null);
  const [runB, setRunB] = useState<RunItem | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    async function loadRuns() {
      try {
        const data = await api.getRuns(50);
        setRuns(data);
        if (data.length >= 2) {
          setRunAId(data[0].id);
          setRunBId(data[1].id);
        } else if (data.length === 1) {
          setRunAId(data[0].id);
        }
      } catch (err) {
        console.error('Failed to load runs', err);
      }
    }
    loadRuns();
  }, []);

  const handleCompare = async () => {
    if (!runAId || !runBId) return;
    setLoading(true);
    try {
      const [resA, resB] = await Promise.all([api.getRun(runAId), api.getRun(runBId)]);
      setRunA(resA);
      setRunB(resB);
    } catch (err) {
      console.error('Failed to fetch runs for comparison', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-12 pb-20">
      {/* Header */}
      <div className="pb-6 border-b border-border">
        <span className="text-xs font-mono text-brand-orange font-bold tracking-widest uppercase">
          COMPARATIVE EVALUATION MATRIX
        </span>
        <h1 className="text-3xl lg:text-5xl font-extrabold text-primary-text uppercase mt-1 font-sans">
          COMPARE RUNS
        </h1>
        <p className="text-sm text-primary-secondary mt-1 max-w-2xl font-medium">
          Side-by-side metric comparison, score differentials, and git diff analysis.
        </p>
      </div>

      {/* Selectors */}
      <div className="bg-surface-card p-6 rounded-card border border-border space-y-4 font-mono text-xs">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-primary-muted uppercase font-bold text-[11px]">Select Baseline Run A</label>
            <select
              value={runAId}
              onChange={(e) => setRunAId(e.target.value)}
              className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
            >
              {runs.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.id} — {r.benchmark_name || r.benchmark_id} ({r.agent_name} / {r.model_name}) [{formatScore(r.total_score)}]
                </option>
              ))}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-primary-muted uppercase font-bold text-[11px]">Select Comparison Run B</label>
            <select
              value={runBId}
              onChange={(e) => setRunBId(e.target.value)}
              className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
            >
              {runs.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.id} — {r.benchmark_name || r.benchmark_id} ({r.agent_name} / {r.model_name}) [{formatScore(r.total_score)}]
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="pt-2 flex justify-end">
          <button
            onClick={handleCompare}
            disabled={loading || !runAId || !runBId}
            className="flex items-center gap-2 px-6 py-3 bg-brand-orange hover:bg-brand-orange-hover text-black font-extrabold text-xs rounded-lg shadow-md transition-all disabled:opacity-50"
          >
            <GitCompare className="w-4 h-4" />
            <span>COMPARE SELECTED RUNS</span>
          </button>
        </div>
      </div>

      {/* Comparison Matrix Output */}
      {runA && runB && (
        <div className="space-y-8 font-mono text-xs">
          <div className="bg-surface-card rounded-card border border-border overflow-hidden">
            <div className="p-6 border-b border-border">
              <h3 className="font-bold text-sm text-primary-text uppercase">Metric Differential Matrix</h3>
            </div>

            <table className="w-full text-left">
              <thead className="bg-surface text-primary-muted border-b border-border uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-4 px-6 w-1/3">Evaluation Metric</th>
                  <th className="py-4 px-6 w-1/3 text-brand-orange font-bold">Run A ({runA.id})</th>
                  <th className="py-4 px-6 w-1/3 text-primary-text font-bold">Run B ({runB.id})</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border text-primary-secondary">
                <tr>
                  <td className="py-4 px-6 text-primary-muted">Benchmark Task</td>
                  <td className="py-4 px-6 font-bold text-primary-text">{runA.benchmark_name || runA.benchmark_id}</td>
                  <td className="py-4 px-6 font-bold text-primary-text">{runB.benchmark_name || runB.benchmark_id}</td>
                </tr>
                <tr>
                  <td className="py-4 px-6 text-primary-muted">Agent Architecture</td>
                  <td className="py-4 px-6">{runA.agent_name}</td>
                  <td className="py-4 px-6">{runB.agent_name}</td>
                </tr>
                <tr>
                  <td className="py-4 px-6 text-primary-muted">Model Provider</td>
                  <td className="py-4 px-6">{runA.model_name} ({runA.provider_name})</td>
                  <td className="py-4 px-6">{runB.model_name} ({runB.provider_name})</td>
                </tr>
                <tr>
                  <td className="py-4 px-6 text-primary-muted">Status</td>
                  <td className="py-4 px-6"><StatusBadge status={runA.status} size="sm" /></td>
                  <td className="py-4 px-6"><StatusBadge status={runB.status} size="sm" /></td>
                </tr>
                <tr>
                  <td className="py-4 px-6 text-primary-muted">Overall Score</td>
                  <td className="py-4 px-6 font-black text-base text-brand-orange">{formatScore(runA.total_score)}</td>
                  <td className="py-4 px-6 font-black text-base text-brand-orange">{formatScore(runB.total_score)}</td>
                </tr>
                <tr>
                  <td className="py-4 px-6 text-primary-muted">Tests Passed</td>
                  <td className="py-4 px-6">{runA.passed_tests} / {runA.total_tests}</td>
                  <td className="py-4 px-6">{runB.passed_tests} / {runB.total_tests}</td>
                </tr>
                <tr>
                  <td className="py-4 px-6 text-primary-muted">Execution Duration</td>
                  <td className="py-4 px-6">{formatTime(runA.duration_seconds)}</td>
                  <td className="py-4 px-6">{formatTime(runB.duration_seconds)}</td>
                </tr>
                <tr>
                  <td className="py-4 px-6 text-primary-muted">Tool Calls</td>
                  <td className="py-4 px-6">{runA.tool_calls_count}</td>
                  <td className="py-4 px-6">{runB.tool_calls_count}</td>
                </tr>
                <tr>
                  <td className="py-4 px-6 text-primary-muted">Estimated Cost</td>
                  <td className="py-4 px-6">{formatCost(runA.estimated_cost)}</td>
                  <td className="py-4 px-6">{formatCost(runB.estimated_cost)}</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Diffs */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <h4 className="font-bold text-xs text-brand-orange uppercase mb-2">Run A Git Patch</h4>
              <DiffViewer diff={runA.git_diff || ''} />
            </div>
            <div>
              <h4 className="font-bold text-xs text-primary-text uppercase mb-2">Run B Git Patch</h4>
              <DiffViewer diff={runB.git_diff || ''} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
