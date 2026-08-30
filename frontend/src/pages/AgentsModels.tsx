import React, { useEffect, useState } from 'react';
import { api } from '../lib/api';
import { AgentItem, ModelItem } from '../types';
import { Bot, Cpu } from 'lucide-react';

export const AgentsModels: React.FC = () => {
  const [agents, setAgents] = useState<AgentItem[]>([]);
  const [models, setModels] = useState<ModelItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [agentsData, modelsData] = await Promise.all([api.getAgents(), api.getModels()]);
        setAgents(agentsData);
        setModels(modelsData);
      } catch (err) {
        console.error('Failed to load agents/models', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-12 pb-20">
      {/* Header */}
      <div className="pb-6 border-b border-border">
        <span className="text-xs font-mono text-brand-orange font-bold tracking-widest uppercase">
          AGENT &amp; MODEL INFRASTRUCTURE
        </span>
        <h1 className="text-3xl lg:text-5xl font-extrabold text-primary-text tracking-tight uppercase mt-1 font-sans">
          AGENTS &amp; MODELS
        </h1>
        <p className="text-sm text-primary-secondary mt-1 max-w-2xl font-medium">
          Manage evaluated coding agent architectures, local Ollama LLMs, and cloud API providers.
        </p>
      </div>

      {/* Agents Section */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 font-mono font-bold text-sm text-primary-text uppercase">
            <Bot className="w-4 h-4 text-brand-orange" />
            <span>Registered Agent Architectures</span>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 font-mono text-xs">
          {agents.map((agent) => (
            <div key={agent.id} className="bg-surface-card p-6 rounded-card border border-border space-y-4 flex flex-col justify-between hover:border-border-light transition-all">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-base font-black text-primary-text">{agent.name}</span>
                  <span className="px-2.5 py-0.5 bg-brand-orange/10 border border-brand-orange/30 text-brand-orange text-[10px] font-bold rounded">
                    v{agent.version}
                  </span>
                </div>

                <div className="text-primary-muted font-medium text-[11px]">{agent.agent_type}</div>
                <p className="text-primary-secondary text-xs leading-relaxed font-sans">{agent.description}</p>
              </div>

              <div className="pt-4 border-t border-border grid grid-cols-3 gap-2 text-center text-[10px]">
                <div className="bg-surface p-2.5 rounded">
                  <span className="text-primary-muted uppercase block">Runs</span>
                  <strong className="text-primary-text text-xs mt-0.5 block">{agent.total_runs}</strong>
                </div>
                <div className="bg-surface p-2.5 rounded">
                  <span className="text-primary-muted uppercase block">Success</span>
                  <strong className="text-status-success text-xs mt-0.5 block">{agent.success_rate}%</strong>
                </div>
                <div className="bg-surface p-2.5 rounded">
                  <span className="text-primary-muted uppercase block">Avg Score</span>
                  <strong className="text-brand-orange text-xs mt-0.5 block">{agent.avg_score}</strong>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Models Section */}
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 font-mono font-bold text-sm text-primary-text uppercase">
            <Cpu className="w-4 h-4 text-brand-orange" />
            <span>Supported LLM Models &amp; Pricing</span>
          </div>
        </div>

        <div className="bg-surface-card rounded-card border border-border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-surface text-primary-muted border-b border-border uppercase tracking-wider text-[10px]">
                <tr>
                  <th className="py-4 px-6">Model</th>
                  <th className="py-4 px-6">Provider</th>
                  <th className="py-4 px-6">Deployment</th>
                  <th className="py-4 px-6">Context Window</th>
                  <th className="py-4 px-6">Input / Output Cost</th>
                  <th className="py-4 px-6 text-right">Avg Score</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border text-primary-secondary">
                {models.map((m) => (
                  <tr key={m.id} className="hover:bg-surface-hover transition-colors">
                    <td className="py-4 px-6 font-bold text-primary-text">{m.name}</td>
                    <td className="py-4 px-6 uppercase font-bold text-xs">{m.provider}</td>
                    <td className="py-4 px-6">
                      <span
                        className={`px-2.5 py-0.5 rounded text-[10px] font-bold uppercase border ${
                          m.is_local
                            ? 'bg-brand-orange/10 text-brand-orange border-brand-orange/30'
                            : 'bg-surface text-primary-secondary border-border'
                        }`}
                      >
                        {m.is_local ? 'Free Local (Ollama)' : 'Cloud API'}
                      </span>
                    </td>
                    <td className="py-4 px-6">{m.context_window?.toLocaleString()} tokens</td>
                    <td className="py-4 px-6">
                      {m.is_local
                        ? '$0.00 / $0.00 (Local-First)'
                        : `$${m.pricing?.input ?? 0} / $${m.pricing?.output ?? 0} per 1M`}
                    </td>
                    <td className="py-4 px-6 text-right font-bold text-brand-orange">
                      {m.avg_score ? m.avg_score : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
