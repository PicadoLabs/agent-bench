import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { api } from '../lib/api';
import { RunItem, Benchmark, LeaderboardEntry } from '../types';
import { MetricCard } from '../components/MetricCard';
import { StatusBadge } from '../components/StatusBadge';
import { CyberMascot } from '../components/CyberMascot';
import { formatTime, formatScore } from '../lib/utils';
import {
  Play,
  Layers,
  Activity,
  Trophy,
  CheckCircle2,
  TrendingUp,
  ArrowRight,
  Zap,
  Terminal as TermIcon,
  Code2
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ScatterChart,
  Scatter
} from 'recharts';

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [runs, setRuns] = useState<RunItem[]>([]);
  const [benchmarks, setBenchmarks] = useState<Benchmark[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [runsData, benchData, leaderData] = await Promise.all([
          api.getRuns(15),
          api.getBenchmarks(),
          api.getLeaderboard(),
        ]);
        setRuns(runsData);
        setBenchmarks(benchData);
        setLeaderboard(leaderData);
      } catch (err) {
        console.error('Error loading dashboard data', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const totalRuns = runs.length;
  const succRuns = runs.filter((r) => r.status === 'SUCCEEDED').length;
  const successRate = totalRuns > 0 ? ((succRuns / totalRuns) * 100).toFixed(1) : '0.0';
  const avgScore = totalRuns > 0 ? (runs.reduce((acc, r) => acc + r.total_score, 0) / totalRuns).toFixed(1) : '0.0';

  // Chart data
  const scoreTrends = runs.slice().reverse().map((r) => ({
    name: r.id,
    score: r.total_score,
    agent: r.agent_name,
    duration: r.duration_seconds,
  }));

  const scatterCostScore = runs.map((r) => ({
    x: r.estimated_cost,
    y: r.total_score,
    name: `${r.agent_name} (${r.model_name})`,
  }));

  return (
    <div className="space-y-16 pb-20">
      {/* Editorial Spacious Hero with Ambient Orange Glow */}
      <div className="relative pt-4 pb-2 overflow-hidden">
        {/* Subtle Ambient Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[350px] bg-brand-orange/10 rounded-full blur-[140px] pointer-events-none -z-10" />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 lg:gap-12 items-center">
          {/* Left Column: Hero Text & Actions (7 Cols) */}
          <div className="lg:col-span-7 space-y-6">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-surface border border-border flex items-center justify-center text-brand-orange shadow-md p-1">
                <Code2 className="w-5 h-5" />
              </div>
              <div className="inline-flex items-center text-xs font-mono">
                <span className="text-primary-text font-bold tracking-widest uppercase">BENCHMARK. EVALUATE. IMPROVE.</span>
              </div>
            </div>

            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-primary-text uppercase leading-[1.05] font-sans">
              TEST YOUR AI. <br />
              KNOW WHAT <br />
              <span className="text-brand-orange text-glow-orange">ACTUALLY WORKS.</span>
            </h1>

            <p className="text-sm sm:text-base text-primary-secondary font-normal leading-relaxed max-w-xl">
              Benchmark coding agents on real software-engineering tasks inside reproducible isolated environments. Evaluate test suites, inspect failure root causes, and measure quality vs cost.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <button
                onClick={() => navigate('/run')}
                className="flex items-center gap-2.5 px-7 py-3.5 bg-brand-orange hover:bg-brand-orange-hover text-black font-extrabold text-xs tracking-wider font-mono rounded-lg shadow-xl hover:orange-glow transition-all transform active:scale-95"
              >
                <span>RUN BENCHMARK</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <Link
                to="/benchmarks"
                className="flex items-center gap-2 px-6 py-3.5 bg-surface hover:bg-surface-secondary text-primary-text font-bold text-xs font-mono rounded-lg border border-border hover:border-border-light transition-colors"
              >
                <Layers className="w-4 h-4 text-primary-muted" />
                <span>EXPLORE TASKS ({benchmarks.length})</span>
              </Link>
            </div>
          </div>

          {/* Right Column: Cool & Simple Cyber Animal Mascot (5 Cols) */}
          <div className="lg:col-span-5 flex justify-center lg:justify-end">
            <CyberMascot />
          </div>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 lg:gap-6">
        <MetricCard
          label="SUCCESS RATE"
          value={`${successRate}%`}
          subValue={`(${succRuns}/${totalRuns} runs)`}
          icon={CheckCircle2}
          accentColor="text-brand-orange"
        />
        <MetricCard
          label="AVG SCORE"
          value={avgScore}
          subValue="/ 100"
          icon={TrendingUp}
          accentColor="text-brand-orange"
        />
        <MetricCard
          label="BENCHMARK TASKS"
          value={benchmarks.length}
          subValue="Active suites"
          icon={Layers}
          accentColor="text-primary-text"
        />
        <MetricCard
          label="TOTAL RUNS"
          value={totalRuns}
          subValue="Evaluations"
          icon={Activity}
          accentColor="text-brand-orange"
        />
      </div>

      {/* Performance Section Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Score Over Recent Runs */}
        <div className="bg-surface-card p-6 rounded-card border border-border">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-mono font-bold text-sm text-primary-text uppercase">
                Score History &amp; Trajectory
              </h3>
              <p className="text-xs text-primary-muted font-mono mt-0.5">
                Evaluation score per sequential run
              </p>
            </div>
            <span className="text-xs font-mono text-brand-orange bg-brand-orange/10 px-2.5 py-0.5 rounded border border-brand-orange/20 font-bold">
              0–100 scale
            </span>
          </div>

          <div className="h-64 w-full">
            {scoreTrends.length === 0 ? (
              <div className="h-full flex items-center justify-center text-xs text-primary-muted font-mono italic">
                No runs recorded yet. Start a benchmark to view score history.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={scoreTrends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1c1c1c" vertical={false} />
                  <XAxis dataKey="name" stroke="#555" tick={{ fill: '#777', fontSize: 11 }} />
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

        {/* Quality vs API Cost & Efficiency */}
        <div className="bg-surface-card p-6 rounded-card border border-border">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-mono font-bold text-sm text-primary-text uppercase">
                Quality vs API Cost
              </h3>
              <p className="text-xs text-primary-muted font-mono mt-0.5">
                Score vs dollar expenditure
              </p>
            </div>
            <span className="text-xs font-mono text-brand-orange bg-brand-orange/10 px-2.5 py-0.5 rounded border border-brand-orange/20 font-bold">
              {scatterCostScore.every(d => d.x === 0) ? 'Local-First ($0.00)' : 'Cost Efficiency'}
            </span>
          </div>

          <div className="h-64 w-full">
            {scatterCostScore.length === 0 ? (
              <div className="h-full flex items-center justify-center text-xs text-primary-muted font-mono italic">
                No cost metrics available yet.
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 20, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1c1c1c" />
                  <XAxis
                    type="number"
                    dataKey="x"
                    name="Cost"
                    unit="$"
                    stroke="#555"
                    domain={[0, (dataMax: number) => (dataMax === 0 ? 0.05 : Math.max(dataMax * 1.2, 0.05))]}
                    tickFormatter={(val: number) => `$${val.toFixed(2)}`}
                    tick={{ fill: '#777', fontSize: 11 }}
                  />
                  <YAxis type="number" dataKey="y" name="Score" domain={[0, 100]} stroke="#555" tick={{ fill: '#777', fontSize: 11 }} />
                  <Tooltip
                    cursor={{ strokeDasharray: '3 3' }}
                    contentStyle={{ backgroundColor: '#0D0D0D', borderColor: '#252525', borderRadius: '8px', color: '#fff', fontSize: '11px', fontFamily: 'monospace' }}
                    formatter={(value: any, name: string) => [
                      name === 'Cost' ? `$${Number(value).toFixed(4)}` : `${value}/100`,
                      name
                    ]}
                  />
                  <Scatter data={scatterCostScore} fill="#FF5A1F" />
                </ScatterChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>

      {/* Recent Runs Table */}
      <div className="bg-surface-card rounded-card border border-border overflow-hidden">
        <div className="p-6 border-b border-border flex items-center justify-between">
          <div>
            <h3 className="font-mono font-bold text-sm text-primary-text uppercase">
              Recent Benchmark Runs
            </h3>
            <p className="text-xs text-primary-muted font-mono mt-0.5">
              Live updates and historical execution evaluations
            </p>
          </div>
          <Link
            to="/runs"
            className="text-xs font-mono font-bold text-brand-orange hover:text-brand-orange-hover flex items-center gap-1 transition-colors"
          >
            <span>View All Runs</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-surface text-primary-muted border-b border-border uppercase tracking-wider text-[10px]">
              <tr>
                <th className="py-3.5 px-6">Run ID</th>
                <th className="py-3.5 px-6">Task</th>
                <th className="py-3.5 px-6">Agent</th>
                <th className="py-3.5 px-6">Model</th>
                <th className="py-3.5 px-6">Score</th>
                <th className="py-3.5 px-6">Tests</th>
                <th className="py-3.5 px-6">Duration</th>
                <th className="py-3.5 px-6 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border text-primary-secondary">
              {runs.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-10 text-center text-primary-muted italic">
                    No benchmark runs recorded yet. Click 'Run Benchmark' to start.
                  </td>
                </tr>
              ) : (
                runs.map((r) => (
                  <tr
                    key={r.id}
                    onClick={() => navigate(`/runs/${r.id}`)}
                    className="hover:bg-surface-hover cursor-pointer transition-colors"
                  >
                    <td className="py-4 px-6 font-bold text-brand-orange">{r.id}</td>
                    <td className="py-4 px-6 text-primary-text font-medium">{r.benchmark_name || r.benchmark_id}</td>
                    <td className="py-4 px-6">{r.agent_name}</td>
                    <td className="py-4 px-6 text-primary-muted">{r.model_name}</td>
                    <td className="py-4 px-6 font-bold text-primary-text">
                      {formatScore(r.total_score)}
                    </td>
                    <td className="py-4 px-6">
                      {r.passed_tests}/{r.total_tests}
                    </td>
                    <td className="py-4 px-6">{formatTime(r.duration_seconds)}</td>
                    <td className="py-4 px-6 text-right">
                      <StatusBadge status={r.status} size="sm" />
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
