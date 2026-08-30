import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../lib/api';
import { RunItem } from '../types';
import { StatusBadge } from '../components/StatusBadge';
import { Terminal } from '../components/Terminal';
import { Timeline } from '../components/Timeline';
import { DiffViewer } from '../components/DiffViewer';
import { MetricCard } from '../components/MetricCard';
import { formatTime, formatScore, formatCost } from '../lib/utils';
import {
  ArrowLeft,
  CheckCircle2,
  Clock,
  Wrench,
  RefreshCw,
  GitCommit,
  AlertTriangle,
  FileText,
  Activity,
  Layers,
  Sparkles,
  ChevronDown,
  ChevronRight
} from 'lucide-react';

export const RunDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [run, setRun] = useState<RunItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string>('overview');
  const [expandedToolIdx, setExpandedToolIdx] = useState<number | null>(null);

  useEffect(() => {
    async function loadRun() {
      if (!id) return;
      try {
        const data = await api.getRun(id);
        setRun(data);
      } catch (err) {
        console.error('Failed to load run details', err);
      } finally {
        setLoading(false);
      }
    }
    loadRun();
  }, [id]);

  if (loading || !run) {
    return (
      <div className="py-20 text-center text-primary-muted font-mono text-sm">
        Loading run evaluation details for {id}...
      </div>
    );
  }

  const score = run.score_breakdown;
  const failure = run.failure_analysis;

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Layers },
    { id: 'timeline', label: `Timeline (${run.events?.length || 0})`, icon: Activity },
    { id: 'tools', label: `Tool Calls (${run.tool_calls?.length || 0})`, icon: Wrench },
    { id: 'tests', label: `Tests (${run.passed_tests}/${run.total_tests})`, icon: CheckCircle2 },
    { id: 'diff', label: 'Git Diff', icon: GitCommit },
    { id: 'failure', label: 'Failure Analysis', icon: AlertTriangle },
    { id: 'logs', label: 'Raw Logs', icon: FileText },
  ];

  return (
    <div className="space-y-10 pb-20">
      {/* Back Link & Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-border">
        <div className="space-y-2">
          <Link
            to="/runs"
            className="text-xs font-mono text-primary-muted hover:text-primary-text flex items-center gap-1.5 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to All Runs</span>
          </Link>
          <div className="flex items-center gap-3">
            <h1 className="text-3xl font-black text-primary-text font-mono tracking-tight">
              {run.id}
            </h1>
            <StatusBadge status={run.status} />
            <span className="text-xs font-mono text-primary-muted">
              ({run.benchmark_name || run.benchmark_id})
            </span>
          </div>
        </div>

        {/* Big Score Header Badge */}
        <div className="flex items-center gap-4 bg-surface-card p-4 rounded-card border border-border">
          <div className="text-right font-mono">
            <div className="text-[10px] text-primary-muted uppercase font-bold">Overall Score</div>
            <div className="text-2xl font-black text-brand-orange">{formatScore(run.total_score)}</div>
          </div>
        </div>
      </div>

      {/* Summary KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricCard label="TESTS PASSED" value={`${run.passed_tests}/${run.total_tests}`} accentColor="text-status-success" />
        <MetricCard label="DURATION" value={formatTime(run.duration_seconds)} accentColor="text-primary-text" />
        <MetricCard label="TOOL CALLS" value={run.tool_calls_count} accentColor="text-brand-orange" />
        <MetricCard label="RETRIES" value={run.retries_count} accentColor="text-status-warning" />
        <MetricCard label="TOKENS" value={run.total_tokens.toLocaleString()} accentColor="text-primary-text" />
        <MetricCard label="EST. COST" value={formatCost(run.estimated_cost)} accentColor="text-brand-orange" />
      </div>

      {/* Tabs Navigation */}
      <div className="flex flex-wrap gap-2 border-b border-border pb-3">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-lg text-xs font-mono font-bold transition-all ${
                isActive
                  ? 'bg-brand-orange text-black shadow-md'
                  : 'bg-surface text-primary-secondary hover:text-primary-text hover:bg-surface-secondary border border-border'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="space-y-6">
        {/* Tab 1: Overview */}
        {activeTab === 'overview' && (
          <div className="space-y-6 font-mono text-xs">
            {/* Score Breakdown Radar/Grid */}
            <div className="bg-surface-card p-6 rounded-card border border-border space-y-4">
              <h3 className="font-bold text-sm text-primary-text uppercase">
                Weighted Scoring Breakdown (0–100)
              </h3>

              <div className="grid grid-cols-1 md:grid-cols-5 gap-4 pt-2">
                <div className="bg-surface p-4 rounded-lg border border-border space-y-1">
                  <div className="text-[10px] text-primary-muted uppercase">Correctness (50%)</div>
                  <div className="text-xl font-bold text-brand-orange">{score?.correctness || 0} pts</div>
                </div>
                <div className="bg-surface p-4 rounded-lg border border-border space-y-1">
                  <div className="text-[10px] text-primary-muted uppercase">Test Pass Rate (25%)</div>
                  <div className="text-xl font-bold text-status-success">{score?.test_pass_rate || 0} pts</div>
                </div>
                <div className="bg-surface p-4 rounded-lg border border-border space-y-1">
                  <div className="text-[10px] text-primary-muted uppercase">Code Quality (10%)</div>
                  <div className="text-xl font-bold text-primary-text">{score?.code_quality || 0} pts</div>
                </div>
                <div className="bg-surface p-4 rounded-lg border border-border space-y-1">
                  <div className="text-[10px] text-primary-muted uppercase">Efficiency (10%)</div>
                  <div className="text-xl font-bold text-primary-secondary">{score?.efficiency || 0} pts</div>
                </div>
                <div className="bg-surface p-4 rounded-lg border border-border space-y-1">
                  <div className="text-[10px] text-primary-muted uppercase">Reliability (5%)</div>
                  <div className="text-xl font-bold text-status-warning">{score?.reliability || 0} pts</div>
                </div>
              </div>
            </div>

            {/* AI Judge Evaluation (if available) */}
            {score?.ai_judge_evaluation && (
              <div className="bg-surface-card p-6 rounded-card border border-brand-orange/40 space-y-3">
                <div className="flex items-center gap-2 text-brand-orange font-bold text-sm uppercase">
                  <Sparkles className="w-4 h-4" />
                  <span>AI-Assisted Evaluation (LLM Judge)</span>
                </div>
                <p className="text-xs text-primary-secondary leading-relaxed bg-surface p-4 rounded-lg border border-border font-sans">
                  {score.ai_judge_evaluation.reasoning}
                </p>
                <div className="grid grid-cols-3 gap-4 pt-1 text-center">
                  <div className="bg-surface p-3 rounded border border-border">
                    <span className="text-[10px] text-primary-muted">Correctness Rating</span>
                    <div className="text-base font-bold text-primary-text">{score.ai_judge_evaluation.correctness_rating}/10</div>
                  </div>
                  <div className="bg-surface p-3 rounded border border-border">
                    <span className="text-[10px] text-primary-muted">Code Quality</span>
                    <div className="text-base font-bold text-primary-text">{score.ai_judge_evaluation.code_quality_rating}/10</div>
                  </div>
                  <div className="bg-surface p-3 rounded border border-border">
                    <span className="text-[10px] text-primary-muted">Task Completion</span>
                    <div className="text-base font-bold text-primary-text">{score.ai_judge_evaluation.task_completion_rating}/10</div>
                  </div>
                </div>
              </div>
            )}

            {/* Run Configuration Snapshot */}
            <div className="bg-surface-card p-6 rounded-card border border-border space-y-4">
              <h3 className="font-bold text-sm text-primary-text uppercase">Execution Metadata</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
                <div>
                  <span className="text-primary-muted">Agent Architecture:</span>
                  <div className="text-primary-text font-bold mt-0.5">{run.agent_name}</div>
                </div>
                <div>
                  <span className="text-primary-muted">Evaluated Model:</span>
                  <div className="text-primary-text font-bold mt-0.5">{run.model_name}</div>
                </div>
                <div>
                  <span className="text-primary-muted">Provider:</span>
                  <div className="text-brand-orange font-bold mt-0.5 uppercase">{run.provider_name}</div>
                </div>
                <div>
                  <span className="text-primary-muted">Start Time:</span>
                  <div className="text-primary-text font-bold mt-0.5">{new Date(run.start_time).toLocaleString()}</div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tab 2: Timeline */}
        {activeTab === 'timeline' && (
          <div className="bg-surface-card p-6 rounded-card border border-border">
            <Timeline events={run.events || []} />
          </div>
        )}

        {/* Tab 3: Tool Calls */}
        {activeTab === 'tools' && (
          <div className="space-y-3 font-mono text-xs">
            {!run.tool_calls || run.tool_calls.length === 0 ? (
              <div className="p-8 bg-surface-card rounded-card border border-border text-center text-primary-muted italic">
                No tool calls recorded during this execution.
              </div>
            ) : (
              run.tool_calls.map((tc, idx) => {
                const isExpanded = expandedToolIdx === idx;
                return (
                  <div key={idx} className="bg-surface-card rounded-card border border-border overflow-hidden">
                    <div
                      onClick={() => setExpandedToolIdx(isExpanded ? null : idx)}
                      className="p-4 flex items-center justify-between cursor-pointer hover:bg-surface-hover transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-primary-muted text-[11px] font-bold">#{tc.step || idx + 1}</span>
                        <span className="text-brand-orange font-bold text-sm">{tc.tool}</span>
                        <span className="text-[10px] text-primary-muted bg-surface px-2.5 py-0.5 rounded border border-border">
                          {tc.duration}s
                        </span>
                      </div>
                      {isExpanded ? <ChevronDown className="w-4 h-4 text-primary-muted" /> : <ChevronRight className="w-4 h-4 text-primary-muted" />}
                    </div>

                    {isExpanded && (
                      <div className="p-4 border-t border-border bg-[#050505] space-y-4">
                        <div>
                          <span className="text-primary-muted text-[10px] uppercase font-bold">Arguments Input</span>
                          <pre className="mt-1 p-3 bg-surface rounded border border-border text-primary-secondary overflow-x-auto">
                            {JSON.stringify(tc.input, null, 2)}
                          </pre>
                        </div>
                        <div>
                          <span className="text-primary-muted text-[10px] uppercase font-bold">Tool Output</span>
                          <pre className="mt-1 p-3 bg-surface rounded border border-border text-primary-secondary overflow-x-auto max-h-60 overflow-y-auto">
                            {typeof tc.output === 'string' ? tc.output : JSON.stringify(tc.output, null, 2)}
                          </pre>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })
            )}
          </div>
        )}

        {/* Tab 4: Tests */}
        {activeTab === 'tests' && (
          <div className="space-y-6 font-mono text-xs">
            <div className="bg-surface-card p-6 rounded-card border border-border flex items-center justify-between">
              <div>
                <span className="text-primary-muted uppercase text-[10px] font-bold">Evaluation Outcome</span>
                <div className="text-xl font-bold text-primary-text mt-1">
                  {run.passed_tests} Passed / {run.total_tests} Total Tests
                </div>
              </div>
              <StatusBadge status={run.status} />
            </div>

            {run.test_results && run.test_results.length > 0 ? (
              run.test_results.map((tr, idx) => (
                <div key={idx} className="space-y-3">
                  <div className="flex items-center justify-between text-xs text-primary-muted font-bold">
                    <span>Command: {tr.command}</span>
                    <span>Exit Code: {tr.exit_code}</span>
                  </div>
                  <Terminal title="Pytest Stdout / Stderr" logs={tr.stdout || tr.stderr} maxHeight="max-h-96" />
                </div>
              ))
            ) : (
              <Terminal title="Execution Test Logs" logs={run.logs || 'No test logs available.'} maxHeight="max-h-96" />
            )}
          </div>
        )}

        {/* Tab 5: Diff */}
        {activeTab === 'diff' && (
          <DiffViewer diff={run.git_diff || ''} />
        )}

        {/* Tab 6: Failure Analysis */}
        {activeTab === 'failure' && (
          <div className="space-y-6 font-mono text-xs">
            {failure ? (
              <div className="bg-surface-card p-6 rounded-card border border-status-error/40 space-y-6">
                <div className="flex items-center justify-between border-b border-border pb-4">
                  <div className="flex items-center gap-2 text-status-error font-bold text-sm uppercase">
                    <AlertTriangle className="w-5 h-5" />
                    <span>Failure Analysis Diagnostic</span>
                  </div>
                  <span className="px-3 py-1 bg-status-error/10 border border-status-error/30 text-status-error font-bold rounded">
                    {failure.primary_failure.toUpperCase()}
                  </span>
                </div>

                <div className="space-y-2">
                  <span className="text-primary-muted uppercase text-[10px] font-bold">Root Cause</span>
                  <div className="p-4 bg-surface rounded-lg border border-border text-primary-text font-bold">
                    {failure.root_cause}
                  </div>
                </div>

                <div className="space-y-2">
                  <span className="text-primary-muted uppercase text-[10px] font-bold">Remediation Hints</span>
                  <div className="p-4 bg-surface rounded-lg border border-border text-primary-secondary leading-relaxed">
                    {failure.resolution_hints}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4 pt-2">
                  <div className="bg-surface p-3.5 rounded-lg border border-border">
                    <span className="text-primary-muted text-[10px]">Failed Tests Count</span>
                    <div className="text-lg font-bold text-status-error mt-0.5">{failure.failed_tests_count}</div>
                  </div>
                  <div className="bg-surface p-3.5 rounded-lg border border-border">
                    <span className="text-primary-muted text-[10px]">Repair Attempts</span>
                    <div className="text-lg font-bold text-primary-text mt-0.5">{failure.attempts_count}</div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-surface-card p-8 rounded-card border border-border text-center text-status-success font-bold text-sm">
                <CheckCircle2 className="w-8 h-8 mx-auto mb-2 text-status-success" />
                This run succeeded completely without failure.
              </div>
            )}
          </div>
        )}

        {/* Tab 7: Raw Logs */}
        {activeTab === 'logs' && (
          <Terminal title="Full Execution Logs" logs={run.logs || 'No raw logs available.'} maxHeight="max-h-[600px]" />
        )}
      </div>
    </div>
  );
};
