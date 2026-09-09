import { Benchmark, RunItem, LeaderboardEntry, FailureStats, AgentItem, ModelItem, DoctorReport } from '../types';

const API_BASE = '/api';

export const api = {
  // Benchmarks
  async getBenchmarks(): Promise<Benchmark[]> {
    const res = await fetch(`${API_BASE}/benchmarks`);
    if (!res.ok) throw new Error('Failed to fetch benchmarks');
    return res.json();
  },

  async getBenchmark(id: string): Promise<Benchmark> {
    const res = await fetch(`${API_BASE}/benchmarks/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch benchmark ${id}`);
    return res.json();
  },

  async createBenchmark(data: any): Promise<any> {
    const res = await fetch(`${API_BASE}/benchmarks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to create benchmark');
    return res.json();
  },

  // Runs
  async getRuns(limit = 50, offset = 0): Promise<RunItem[]> {
    const res = await fetch(`${API_BASE}/runs?limit=${limit}&offset=${offset}`);
    if (!res.ok) throw new Error('Failed to fetch runs');
    return res.json();
  },

  async getRun(id: string): Promise<RunItem> {
    const res = await fetch(`${API_BASE}/runs/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch run ${id}`);
    return res.json();
  },

  async startRun(data: {
    benchmark_id: string;
    agent_name: string;
    model_name?: string;
    provider_name?: string;
    sandbox_runtime?: string;
    enable_llm_judge?: boolean;
  }): Promise<{ run_id: string; status: string; message: string }> {
    const res = await fetch(`${API_BASE}/runs`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error('Failed to start run');
    return res.json();
  },

  async getRunDiff(id: string): Promise<{ run_id: string; git_diff: string }> {
    const res = await fetch(`${API_BASE}/runs/${id}/diff`);
    if (!res.ok) throw new Error(`Failed to fetch diff for run ${id}`);
    return res.json();
  },

  async getRunEvents(id: string): Promise<any[]> {
    const res = await fetch(`${API_BASE}/runs/${id}/events`);
    if (!res.ok) throw new Error(`Failed to fetch events for run ${id}`);
    return res.json();
  },

  // Leaderboard
  async getLeaderboard(): Promise<LeaderboardEntry[]> {
    const res = await fetch(`${API_BASE}/leaderboard`);
    if (!res.ok) throw new Error('Failed to fetch leaderboard');
    return res.json();
  },

  // Failure Analysis
  async getFailures(): Promise<FailureStats> {
    const res = await fetch(`${API_BASE}/failures`);
    if (!res.ok) throw new Error('Failed to fetch failure stats');
    return res.json();
  },

  // Agents & Models
  async getAgents(): Promise<AgentItem[]> {
    const res = await fetch(`${API_BASE}/agents`);
    if (!res.ok) throw new Error('Failed to fetch agents');
    return res.json();
  },

  async getModels(): Promise<ModelItem[]> {
    const res = await fetch(`${API_BASE}/models`);
    if (!res.ok) throw new Error('Failed to fetch models');
    return res.json();
  },

  // Compare
  async compareRuns(runIds: string[]): Promise<{ compared_runs: any[] }> {
    const res = await fetch(`${API_BASE}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ run_ids: runIds }),
    });
    if (!res.ok) throw new Error('Failed to compare runs');
    return res.json();
  },

  // System Doctor
  async getDoctorReport(): Promise<DoctorReport> {
    const res = await fetch(`${API_BASE}/doctor`);
    if (!res.ok) throw new Error('Failed to fetch doctor report');
    return res.json();
  },
};
