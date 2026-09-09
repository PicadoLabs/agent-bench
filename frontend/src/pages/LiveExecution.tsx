import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { api } from '../lib/api';
import { RunItem } from '../types';
import { Terminal } from '../components/Terminal';
import { StatusBadge } from '../components/StatusBadge';
import { formatTime } from '../lib/utils';
import {
  Activity,
  Clock,
  Wrench,
  RefreshCw,
  ArrowRight,
  Zap,
  Terminal as TermIcon
} from 'lucide-react';

export const LiveExecution: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [run, setRun] = useState<RunItem | null>(null);
  const [logs, setLogs] = useState<string[]>([]);
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [isFinished, setIsFinished] = useState(false);
  const timerRef = useRef<any>(null);

  // Poll or WebSocket stream
  useEffect(() => {
    if (!id) return;

    // Start local timer
    const startT = Date.now();
    timerRef.current = setInterval(() => {
      setElapsedSeconds(Math.floor((Date.now() - startT) / 1000));
    }, 500);

    // Setup WebSocket connection
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/runs/${id}`;
    let socket: WebSocket | null = null;

    try {
      socket = new WebSocket(wsUrl);
      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.message) {
            setLogs((prev) => [...prev, `${data.event_type.toUpperCase()} ➔ ${data.message}`]);
          }
          if (data.event_type === 'benchmark_completed' || data.event_type === 'benchmark_failed') {
            setIsFinished(true);
          }
        } catch (e) {
          console.error(e);
        }
      };
    } catch (e) {
      console.warn('WebSocket fallback to polling', e);
    }

    // Polling interval
    const pollInterval = setInterval(async () => {
      try {
        const runData = await api.getRun(id);
        setRun(runData);

        if (runData.events && runData.events.length > 0) {
          const eventMsgs = runData.events.map((e: any) => `${e.event_type.toUpperCase()} ➔ ${e.message}`);
          setLogs((prev) => (eventMsgs.length > prev.length ? eventMsgs : prev));
        }

        if (['SUCCEEDED', 'PARTIAL', 'FAILED', 'TIMEOUT', 'CRASHED'].includes(runData.status)) {
          setIsFinished(true);
          clearInterval(pollInterval);
          if (timerRef.current) clearInterval(timerRef.current);
        }
      } catch (err) {
        console.error('Polling error', err);
      }
    }, 1500);

    return () => {
      clearInterval(pollInterval);
      if (timerRef.current) clearInterval(timerRef.current);
      if (socket) socket.close();
    };
  }, [id]);

  const scoreDisplay = run ? run.total_score : 0;
  const statusDisplay = run ? run.status : 'RUNNING';
  const toolCallsDisplay = run ? run.tool_calls_count : logs.filter((l) => l.includes('TOOL')).length;
  const retriesDisplay = run ? run.retries_count : 0;

  return (
    <div className="space-y-10 pb-20">
      {/* Top Banner */}
      <div className="bg-surface-card rounded-card border border-border p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-brand-orange/10 border border-brand-orange/30 flex items-center justify-center text-brand-orange">
            <Activity className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono font-black text-xl text-primary-text">{id}</span>
              <StatusBadge status={statusDisplay} />
            </div>
            <p className="text-xs text-primary-secondary font-mono mt-1">
              Task: <strong className="text-primary-text">{run?.benchmark_name || run?.benchmark_id || 'Initializing...'}</strong>
            </p>
          </div>
        </div>

        {isFinished && (
          <button
            onClick={() => navigate(`/runs/${id}`)}
            className="flex items-center gap-2 px-6 py-3 bg-brand-orange hover:bg-brand-orange-hover text-black font-extrabold text-xs font-mono rounded-lg shadow-lg hover:orange-glow transition-all"
          >
            <span>INSPECT FULL RUN DETAILS</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Main Live Execution Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Terminal Output (2 Cols) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-mono font-bold text-primary-text uppercase">
              <TermIcon className="w-4 h-4 text-brand-orange" />
              <span>Live Execution Trace &amp; Event Stream</span>
            </div>
            <span className="text-[10px] font-mono text-primary-muted flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-brand-orange animate-ping"></span>
              Streaming telemetry
            </span>
          </div>

          <Terminal
            title={`Real-Time Telemetry — ${id}`}
            logs={logs.length > 0 ? logs : ['Waiting for runner to initialize sandbox and begin agent execution...']}
            maxHeight="max-h-[520px]"
            autoScroll={true}
          />
        </div>

        {/* Live Metrics Telemetry Sidebar (1 Col) */}
        <div className="space-y-4 font-mono text-xs">
          <div className="text-xs font-bold text-primary-text uppercase flex items-center gap-2">
            <Zap className="w-4 h-4 text-brand-orange" />
            <span>Telemetry Status</span>
          </div>

          <div className="bg-surface-card p-6 rounded-card border border-border space-y-6">
            {/* Live Score */}
            <div>
              <span className="text-primary-muted text-[10px] uppercase font-bold tracking-wider">
                CURRENT EVALUATION SCORE
              </span>
              <div className="text-4xl font-black text-brand-orange mt-1 font-mono">
                {scoreDisplay}
                <span className="text-base text-primary-muted font-normal"> / 100</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
              {/* Duration */}
              <div>
                <span className="text-primary-muted text-[10px] uppercase font-bold tracking-wider">
                  ELAPSED TIME
                </span>
                <div className="text-xl font-bold text-primary-text mt-1 flex items-center gap-1.5">
                  <Clock className="w-4 h-4 text-primary-muted" />
                  <span>{formatTime(run?.duration_seconds || elapsedSeconds)}</span>
                </div>
              </div>

              {/* Status */}
              <div>
                <span className="text-primary-muted text-[10px] uppercase font-bold tracking-wider">
                  EXECUTION STATUS
                </span>
                <div className="mt-1">
                  <StatusBadge status={statusDisplay} size="sm" />
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-border">
              {/* Tool Calls */}
              <div>
                <span className="text-primary-muted text-[10px] uppercase font-bold tracking-wider">
                  TOOL CALLS
                </span>
                <div className="text-xl font-bold text-primary-text mt-1 flex items-center gap-1.5">
                  <Wrench className="w-4 h-4 text-brand-orange" />
                  <span>{toolCallsDisplay}</span>
                </div>
              </div>

              {/* Retries */}
              <div>
                <span className="text-primary-muted text-[10px] uppercase font-bold tracking-wider">
                  REPAIR RETRIES
                </span>
                <div className="text-xl font-bold text-primary-text mt-1 flex items-center gap-1.5">
                  <RefreshCw className="w-4 h-4 text-status-warning" />
                  <span>{retriesDisplay}</span>
                </div>
              </div>
            </div>

            {/* Agent / Model info */}
            <div className="pt-4 border-t border-border space-y-2 text-[11px] text-primary-secondary">
              <div className="flex justify-between">
                <span className="text-primary-muted">Agent:</span>
                <span className="text-primary-text font-bold">{run?.agent_name || 'IterativeCodingAgent'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-primary-muted">Model:</span>
                <span className="text-primary-text font-bold">{run?.model_name || 'qwen2.5-coder'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-primary-muted">Provider:</span>
                <span className="text-brand-orange uppercase font-bold">{run?.provider_name || 'Ollama (Local)'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
