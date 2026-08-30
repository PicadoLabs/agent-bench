import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { DoctorReport } from '../types';
import {
  Stethoscope,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Terminal as TermIcon,
  Copy,
  Check,
  ExternalLink,
  Cpu
} from 'lucide-react';

export const DoctorDocs: React.FC = () => {
  const [report, setReport] = useState<DoctorReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [copiedCmd, setCopiedCmd] = useState<string | null>(null);

  useEffect(() => {
    async function loadDoctor() {
      try {
        const data = await api.getDoctorReport();
        setReport(data);
      } catch (err) {
        console.error('Failed to load doctor diagnostics', err);
      } finally {
        setLoading(false);
      }
    }
    loadDoctor();
  }, []);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCmd(text);
    setTimeout(() => setCopiedCmd(null), 2000);
  };

  const cliCommands = [
    { title: 'Run Health Check', cmd: 'python agentbench.py doctor' },
    { title: 'List All Benchmark Tasks', cmd: 'python agentbench.py list' },
    { title: 'Execute Benchmark with Ollama', cmd: 'python agentbench.py run --benchmark fix-rate-limiter --provider ollama --model qwen2.5-coder:1.5b' },
    { title: 'Run FastPatchAgent', cmd: 'python agentbench.py run --benchmark fix-sql-builder --agent FastPatchAgent --provider ollama' },
    { title: 'Inspect Run and Git Diff', cmd: 'python agentbench.py inspect RUN-0003' },
    { title: 'View Global Leaderboard', cmd: 'python agentbench.py leaderboard' },
    { title: 'Compare Two Runs', cmd: 'python agentbench.py compare RUN-0002 RUN-0003' },
    { title: 'Start Web Dashboard & API', cmd: 'python agentbench.py serve --port 8000' },
  ];

  return (
    <div className="space-y-12 pb-20 font-mono">
      {/* Header */}
      <div className="pb-6 border-b border-border">
        <span className="text-xs text-brand-orange font-bold tracking-widest uppercase">
          SYSTEM DIAGNOSTICS &amp; DEVELOPER REFERENCE
        </span>
        <h1 className="text-3xl lg:text-5xl font-extrabold text-primary-text uppercase mt-1 font-sans">
          DOCTOR &amp; CLI DOCS
        </h1>
        <p className="text-sm text-primary-secondary mt-1 max-w-2xl font-medium font-sans">
          Inspect execution environments, local LLM daemons, sandbox runtimes, and CLI command references.
        </p>
      </div>

      {/* Doctor Status Banner */}
      <div className="bg-surface-card p-6 rounded-card border border-border space-y-6">
        <div className="flex items-center justify-between border-b border-border pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-brand-orange/10 border border-brand-orange/30 flex items-center justify-center text-brand-orange">
              <Stethoscope className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-sm text-primary-text uppercase">System Environment Diagnostic</h3>
              <p className="text-xs text-primary-muted font-sans">Host runtime and dependency health status</p>
            </div>
          </div>

          <span className="px-3 py-1 bg-status-success/10 border border-status-success/30 text-status-success text-xs font-bold rounded">
            {report?.status === 'ok' ? 'HEALTHY' : 'OPERATIONAL'}
          </span>
        </div>

        {/* Checks Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
          {/* Python */}
          <div className="bg-surface p-4 rounded-lg border border-border space-y-2 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="font-bold text-primary-text uppercase text-[11px]">Python Runtime</span>
              <CheckCircle2 className="w-4 h-4 text-status-success" />
            </div>
            <div className="text-[11px] text-primary-muted">Version {report?.python_version || '3.12+'}</div>
            <div className="text-[10px] text-brand-orange font-bold uppercase">Operational</div>
          </div>

          {/* Ollama */}
          <div className="bg-surface p-4 rounded-lg border border-border space-y-2 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="font-bold text-primary-text uppercase text-[11px]">Ollama Local Daemon</span>
              {report?.ollama_available ? (
                <CheckCircle2 className="w-4 h-4 text-status-success" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-status-warning" />
              )}
            </div>
            <div className="text-[11px] text-primary-muted">
              {report?.ollama_available
                ? `Active (${report.ollama_models?.length || 0} models detected)`
                : 'Offline (Optional for local LLMs)'}
            </div>
            <div className="text-[10px] text-brand-orange font-bold uppercase">
              {report?.ollama_available ? 'Connected' : 'Notice'}
            </div>
          </div>

          {/* Docker */}
          <div className="bg-surface p-4 rounded-lg border border-border space-y-2 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="font-bold text-primary-text uppercase text-[11px]">Docker Sandbox Layer</span>
              {report?.docker_available ? (
                <CheckCircle2 className="w-4 h-4 text-status-success" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-status-warning" />
              )}
            </div>
            <div className="text-[11px] text-primary-muted">
              {report?.docker_available ? 'Docker daemon running' : 'Using LocalProcessSandbox isolation'}
            </div>
            <div className="text-[10px] text-brand-orange font-bold uppercase">
              {report?.docker_available ? 'Available' : 'Local Fallback Active'}
            </div>
          </div>

          {/* Database */}
          <div className="bg-surface p-4 rounded-lg border border-border space-y-2 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="font-bold text-primary-text uppercase text-[11px]">SQLite Persistence</span>
              <CheckCircle2 className="w-4 h-4 text-status-success" />
            </div>
            <div className="text-[11px] text-primary-muted truncate">{report?.database_url || 'sqlite:///./agentbench.db'}</div>
            <div className="text-[10px] text-brand-orange font-bold uppercase">Connected</div>
          </div>

          {/* Default Model */}
          <div className="bg-surface p-4 rounded-lg border border-border space-y-2 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="font-bold text-primary-text uppercase text-[11px]">Default Model Provider</span>
              <CheckCircle2 className="w-4 h-4 text-brand-orange" />
            </div>
            <div className="text-[11px] text-primary-muted">
              {report?.default_provider} / {report?.default_model}
            </div>
            <div className="text-[10px] text-brand-orange font-bold uppercase">Active</div>
          </div>

          {/* Cloud Keys */}
          <div className="bg-surface p-4 rounded-lg border border-border space-y-2 flex flex-col justify-between">
            <div className="flex items-center justify-between">
              <span className="font-bold text-primary-text uppercase text-[11px]">API Key Status</span>
              <CheckCircle2 className="w-4 h-4 text-primary-muted" />
            </div>
            <div className="text-[11px] text-primary-muted">
              OpenAI: {report?.configured_api_keys?.openai ? '✓' : '—'} | Anthropic: {report?.configured_api_keys?.anthropic ? '✓' : '—'} | Gemini: {report?.configured_api_keys?.gemini ? '✓' : '—'}
            </div>
            <div className="text-[10px] text-primary-muted font-bold uppercase">Optional</div>
          </div>
        </div>
      </div>

      {/* CLI Reference & Quick Commands */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 font-bold text-sm text-primary-text uppercase">
            <TermIcon className="w-4 h-4 text-brand-orange" />
            <span>CLI Command Reference</span>
          </div>

          <a
            href="/docs"
            target="_blank"
            rel="noreferrer"
            className="text-xs text-brand-orange hover:text-brand-orange-hover flex items-center gap-1 font-bold"
          >
            <span>Interactive OpenAPI Swagger</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {cliCommands.map((item, idx) => (
            <div
              key={idx}
              className="bg-surface-card p-4 rounded-card border border-border space-y-2 flex flex-col justify-between hover:border-border-light transition-all"
            >
              <div className="text-[11px] font-bold text-primary-muted uppercase">{item.title}</div>
              <div className="bg-surface p-3 rounded-lg border border-border flex items-center justify-between gap-2">
                <code className="text-xs text-primary-text select-all break-all">{item.cmd}</code>
                <button
                  onClick={() => handleCopy(item.cmd)}
                  className="p-1.5 rounded hover:bg-surface-secondary text-primary-muted hover:text-primary-text shrink-0"
                  title="Copy command"
                >
                  {copiedCmd === item.cmd ? <Check className="w-3.5 h-3.5 text-brand-orange" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
