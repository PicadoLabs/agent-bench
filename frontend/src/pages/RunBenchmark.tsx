import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api } from '../lib/api';
import { Benchmark, AgentItem, ModelItem } from '../types';
import { Play, Bot, Cpu, Box, Sparkles, Shield, AlertCircle, ArrowRight } from 'lucide-react';

export const RunBenchmark: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const initialBenchId = searchParams.get('benchmark') || '';

  const [benchmarks, setBenchmarks] = useState<Benchmark[]>([]);
  const [agents, setAgents] = useState<AgentItem[]>([]);
  const [models, setModels] = useState<ModelItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [selectedBenchmarkId, setSelectedBenchmarkId] = useState<string>(initialBenchId);
  const [selectedAgent, setSelectedAgent] = useState<string>('IterativeCodingAgent');
  const [selectedModel, setSelectedModel] = useState<string>('qwen2.5-coder:1.5b');
  const [selectedProvider, setSelectedProvider] = useState<string>('ollama');
  const [selectedRuntime, setSelectedRuntime] = useState<string>('local');
  const [enableJudge, setEnableJudge] = useState<boolean>(false);

  useEffect(() => {
    async function loadConfig() {
      try {
        const [benchData, agentData, modelData] = await Promise.all([
          api.getBenchmarks(),
          api.getAgents(),
          api.getModels(),
        ]);
        setBenchmarks(benchData);
        setAgents(agentData);
        setModels(modelData);

        if (!selectedBenchmarkId && benchData.length > 0) {
          setSelectedBenchmarkId(benchData[0].id);
        }
      } catch (err) {
        console.error('Failed to load runner options', err);
      } finally {
        setLoading(false);
      }
    }
    loadConfig();
  }, []);

  const handleModelChange = (modelId: string) => {
    setSelectedModel(modelId);
    const m = models.find((item) => item.id === modelId);
    if (m) {
      setSelectedProvider(m.provider);
    }
  };

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBenchmarkId) {
      setError('Please select a benchmark task.');
      return;
    }

    setSubmitting(true);
    setError(null);
    try {
      const res = await api.startRun({
        benchmark_id: selectedBenchmarkId,
        agent_name: selectedAgent,
        model_name: selectedModel,
        provider_name: selectedProvider,
        sandbox_runtime: selectedRuntime,
        enable_llm_judge: enableJudge,
      });

      // Navigate to live telemetry execution screen
      navigate(`/runs/${res.run_id}/live`);
    } catch (err: any) {
      setError(err.message || 'Failed to trigger benchmark run');
      setSubmitting(false);
    }
  };

  const activeBenchmark = benchmarks.find((b) => b.id === selectedBenchmarkId);

  return (
    <div className="max-w-4xl mx-auto space-y-10 pb-20">
      {/* Header */}
      <div className="border-b border-border pb-6">
        <span className="text-xs font-mono text-brand-orange font-bold tracking-widest uppercase">
          BENCHMARK EXECUTION ENGINE
        </span>
        <h1 className="text-3xl lg:text-5xl font-black text-primary-text uppercase mt-1 font-sans">
          RUN BENCHMARK
        </h1>
        <p className="text-sm text-primary-secondary mt-1 font-medium">
          Select target task, evaluation agent, model provider, and execution sandbox.
        </p>
      </div>

      {error && (
        <div className="p-4 bg-status-error/10 border border-status-error/30 text-status-error text-xs font-mono rounded-lg flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleStart} className="space-y-8 text-xs font-mono">
        {/* Step 1: Select Benchmark */}
        <div className="bg-surface-card p-6 rounded-card border border-border space-y-4">
          <div className="flex items-center gap-2 text-primary-text font-bold text-sm uppercase pb-3 border-b border-border">
            <span className="text-brand-orange font-mono">01.</span>
            <span>Target Benchmark Task</span>
          </div>

          <div className="space-y-2">
            <label className="text-primary-muted text-[11px] font-semibold uppercase">
              Select Benchmark Repository
            </label>
            <select
              value={selectedBenchmarkId}
              onChange={(e) => setSelectedBenchmarkId(e.target.value)}
              className="w-full bg-surface border border-border rounded-lg px-4 py-3.5 text-primary-text font-bold text-sm focus:outline-none focus:border-brand-orange"
            >
              {benchmarks.map((b) => (
                <option key={b.id} value={b.id}>
                  [{b.category}] {b.name} ({b.difficulty})
                </option>
              ))}
            </select>
          </div>

          {activeBenchmark && (
            <div className="bg-surface p-4 rounded-lg border border-border/70 space-y-2">
              <div className="text-primary-text font-bold text-xs">{activeBenchmark.name}</div>
              <p className="text-primary-secondary text-[11px] leading-relaxed font-sans">
                {activeBenchmark.prompt}
              </p>
              <div className="flex gap-4 pt-1 text-[10px] text-primary-muted font-mono">
                <span>Command: <strong className="text-brand-orange">{activeBenchmark.evaluation_command}</strong></span>
                <span>Timeout: {activeBenchmark.evaluation_timeout}s</span>
              </div>
            </div>
          )}
        </div>

        {/* Step 2: Agent & Model Selection */}
        <div className="bg-surface-card p-6 rounded-card border border-border space-y-6">
          <div className="flex items-center gap-2 text-primary-text font-bold text-sm uppercase pb-3 border-b border-border">
            <span className="text-brand-orange font-mono">02.</span>
            <span>Agent &amp; LLM Configuration</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Agent */}
            <div className="space-y-2">
              <label className="text-primary-muted text-[11px] font-semibold uppercase flex items-center gap-1.5">
                <Bot className="w-3.5 h-3.5 text-primary-muted" />
                <span>Coding Agent Architecture</span>
              </label>
              <select
                value={selectedAgent}
                onChange={(e) => setSelectedAgent(e.target.value)}
                className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
              >
                <option value="IterativeCodingAgent">IterativeCodingAgent (ReAct + Self-Repair)</option>
                <option value="FastPatchAgent">FastPatchAgent (Single-pass rapid)</option>
                <option value="BaselineAgent">BaselineAgent (Zero-shot baseline)</option>
              </select>
            </div>

            {/* Model */}
            <div className="space-y-2">
              <label className="text-primary-muted text-[11px] font-semibold uppercase flex items-center gap-1.5">
                <Cpu className="w-3.5 h-3.5 text-primary-muted" />
                <span>Model / Provider</span>
              </label>
              <select
                value={selectedModel}
                onChange={(e) => handleModelChange(e.target.value)}
                className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
              >
                <optgroup label="Free Local Models (Ollama)">
                  <option value="qwen2.5-coder:1.5b">Qwen 2.5 Coder 1.5B (Local Ollama)</option>
                  <option value="deepseek-r1:1.5b">DeepSeek R1 1.5B (Local Ollama)</option>
                  <option value="qwen2.5-coder">Qwen 2.5 Coder Default (Ollama)</option>
                </optgroup>
                <optgroup label="Deterministic / Testing">
                  <option value="mock-coder">Mock Coder (Fast Mock Provider)</option>
                </optgroup>
                <optgroup label="API Cloud Models (Optional Key)">
                  <option value="gpt-4o">OpenAI GPT-4o</option>
                  <option value="gpt-4o-mini">OpenAI GPT-4o Mini</option>
                  <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
                  <option value="gemini-1.5-pro">Gemini 1.5 Pro</option>
                  <option value="gemini-1.5-flash">Gemini 1.5 Flash</option>
                </optgroup>
              </select>
            </div>
          </div>
        </div>

        {/* Step 3: Sandboxing & Advanced */}
        <div className="bg-surface-card p-6 rounded-card border border-border space-y-4">
          <div className="flex items-center gap-2 text-primary-text font-bold text-sm uppercase pb-3 border-b border-border">
            <span className="text-brand-orange font-mono">03.</span>
            <span>Sandbox &amp; AI Judge Settings</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-primary-muted text-[11px] font-semibold uppercase flex items-center gap-1.5">
                <Shield className="w-3.5 h-3.5 text-primary-muted" />
                <span>Sandbox Isolation Layer</span>
              </label>
              <select
                value={selectedRuntime}
                onChange={(e) => setSelectedRuntime(e.target.value)}
                className="w-full bg-surface border border-border rounded-lg px-3.5 py-3 text-primary-text focus:outline-none focus:border-brand-orange"
              >
                <option value="local">LocalProcessSandbox (Fast Process Isolation)</option>
                <option value="docker">DockerSandbox (Containerized Mount)</option>
              </select>
            </div>

            <div className="flex items-center justify-between p-4 bg-surface rounded-lg border border-border mt-auto">
              <div className="space-y-0.5">
                <div className="text-primary-text font-bold flex items-center gap-1.5">
                  <Sparkles className="w-3.5 h-3.5 text-brand-orange" />
                  <span>Enable AI Judge Evaluation</span>
                </div>
                <div className="text-primary-muted text-[10px]">
                  Complement objective pytest results with qualitative AI scoring
                </div>
              </div>
              <input
                type="checkbox"
                checked={enableJudge}
                onChange={(e) => setEnableJudge(e.target.checked)}
                className="w-4 h-4 accent-brand-orange rounded cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Big Start Button */}
        <div className="pt-2">
          <button
            type="submit"
            disabled={submitting}
            className="w-full py-4 bg-brand-orange hover:bg-brand-orange-hover text-black font-black text-base uppercase tracking-wider rounded-card shadow-2xl hover:orange-glow transition-all transform active:scale-95 flex items-center justify-center gap-3 disabled:opacity-50"
          >
            <span>{submitting ? 'INITIALIZING BENCHMARK...' : 'START BENCHMARK'}</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
};
