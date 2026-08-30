export interface Benchmark {
  id: string;
  name: string;
  description: string;
  category: string;
  difficulty: string;
  repo_type: string;
  repo_path: string;
  repo_commit: string;
  evaluation_command: string;
  evaluation_timeout: number;
  scoring_weights: {
    correctness: number;
    test_pass_rate: number;
    code_quality: number;
    efficiency: number;
    reliability: number;
  };
  prompt: string;
  constraints: string;
  total_runs: number;
}

export interface ScoreBreakdown {
  correctness: number;
  test_pass_rate: number;
  code_quality: number;
  efficiency: number;
  reliability: number;
  overall_score: number;
  breakdown: Record<string, any>;
  ai_judge_evaluation?: {
    is_ai_assisted: boolean;
    correctness_rating: number;
    code_quality_rating: number;
    task_completion_rating: number;
    reasoning: string;
  };
}

export interface FailureAnalysis {
  primary_failure: string;
  root_cause: string;
  failed_tests_count: number;
  attempts_count: number;
  resolution_hints: string;
  details: Record<string, any>;
}

export interface ToolCallItem {
  step: number;
  tool: string;
  input: Record<string, any>;
  output: any;
  duration: number;
  error?: string;
  timestamp: string;
}

export interface ExecutionEventItem {
  event_type: string;
  step: number;
  message: string;
  details: Record<string, any>;
  timestamp: string;
}

export interface TestResultItem {
  command: string;
  exit_code: number;
  duration: number;
  passed: number;
  failed: number;
  skipped: number;
  total: number;
  stdout: string;
  stderr: string;
  details: Record<string, any>;
}

export interface RunItem {
  id: string;
  benchmark_id: string;
  benchmark_name: string;
  agent_name: string;
  model_name: string;
  provider_name: string;
  status: string; // QUEUED, PREPARING, RUNNING, TESTING, EVALUATING, SUCCEEDED, PARTIAL, FAILED, TIMEOUT, CRASHED
  start_time: string;
  end_time?: string;
  duration_seconds: number;
  total_score: number;
  test_pass_rate: number;
  passed_tests: number;
  failed_tests: number;
  total_tests: number;
  tool_calls_count: number;
  commands_count: number;
  retries_count: number;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  estimated_cost: number;
  git_diff?: string;
  logs?: string;
  score_breakdown?: ScoreBreakdown;
  failure_analysis?: FailureAnalysis;
  tool_calls?: ToolCallItem[];
  events?: ExecutionEventItem[];
  test_results?: TestResultItem[];
}

export interface LeaderboardEntry {
  rank: number;
  agent_name: string;
  model_name: string;
  provider_name: string;
  total_runs: number;
  success_rate: number;
  avg_score: number;
  avg_time: number;
  avg_cost: number;
  avg_tool_calls: number;
  is_local: boolean;
}

export interface FailureStats {
  category_counts: Record<string, number>;
  total_failures: number;
  recent_failures: Array<{
    run_id: string;
    primary_failure: string;
    root_cause: string;
    failed_tests_count: number;
    attempts_count: number;
    resolution_hints: string;
    timestamp: string;
  }>;
}

export interface AgentItem {
  id: string;
  name: string;
  agent_type: string;
  description: string;
  version: string;
  is_active: boolean;
  total_runs: number;
  success_rate: number;
  avg_score: number;
}

export interface ModelItem {
  id: string;
  name: string;
  provider: string;
  is_local: boolean;
  context_window: number;
  pricing: {
    input: number;
    output: number;
  };
  total_runs: number;
  avg_score: number;
  avg_cost: number;
}

export interface DoctorReport {
  status: string;
  python_version: string;
  docker_available: boolean;
  ollama_available: boolean;
  ollama_models: string[];
  default_provider: string;
  default_model: string;
  sandbox_runtime: string;
  configured_api_keys: {
    openai: boolean;
    anthropic: boolean;
    gemini: boolean;
    custom: boolean;
  };
  database_url: string;
}
