# AgentBench Architecture & Design Guide

AgentBench is an open-source, provider-agnostic evaluation platform for AI coding agents.

```
┌─────────────────────────────────────────────────────────────┐
│                       AGENTBENCH                            │
│           Evaluate. Compare. Improve.                       │
└─────────────────────────────────────────────────────────────┘
                               │
               ┌───────────────┴───────────────┐
               │                               │
        FREE LOCAL MODE                 API CLOUD MODE
        (Ollama / Local)              (OpenAI/Anthropic/Gemini)
               │                               │
               └───────────────┬───────────────┘
                               │
                       [ Benchmark Task ]
                               │
                      [ Agent Runtime ]
                               │
                    [ Sandboxed Workspace ]
                   (Docker / Safe Process)
                               │
                     [ Surgical Code Edits ]
                               │
                   [ Objective Test Runner ]
                          (Pytest)
                               │
              ┌────────────────┴────────────────┐
              │                                 │
     [ Scoring Engine ]               [ Failure Taxonomy ]
   (Correctness, Pass Rate,          (Root Cause, Misuse,
    Quality, Efficiency, Rel)         Timeouts, Syntactic)
              │                                 │
              └────────────────┬────────────────┘
                               │
                       [ SQLite Storage ]
                               │
              ┌────────────────┴────────────────┐
              │                                 │
        [ Typer CLI ]                 [ React Dashboard ]
```

## System Components

### 1. Model Provider Abstraction (`backend/app/providers/`)
- Base interface: `BaseModelProvider`
- `OllamaProvider`: Default local-first zero-cost provider for open models (Qwen 2.5 Coder, DeepSeek Coder, Llama 3.1).
- `OpenAIProvider`, `AnthropicProvider`, `GeminiProvider`: Cloud providers using standard REST / tool-calling endpoints.
- `MockProvider`: Deterministic scripted provider for offline testing and CI/CD pipelines.

### 2. Sandboxing Layer (`backend/app/sandbox/`)
- `DockerSandbox`: Isolated Linux container with volume mount, restricted network, memory/CPU quotas, and automatic cleanup.
- `LocalProcessSandbox`: Secure subprocess-based execution with strict path traversal blocking, sanitized environment variables, and process tree timeouts.

### 3. Agent Runtime (`backend/app/agents/`)
- `IterativeCodingAgent`: Multi-turn ReAct coding agent that inspects repository files, applies surgical patches via `write_file`, executes test suites, inspects failure tracebacks, and performs iterative repairs.
- `FastPatchAgent`: Single-pass rapid patching agent.
- `BaselineAgent`: Zero-shot baseline for difficulty calibration.

### 4. Tool Registry (`backend/app/agents/tools.py`)
- `read_file`, `write_file`, `list_files`, `search_files`, `run_command`, `run_tests`, `git_diff`, `git_status`.

### 5. Evaluation & Scoring Engine (`backend/app/evaluation/`, `backend/app/scoring/`)
- Objective test output parser for pytest pass/fail counts and error messages.
- Normalized 0–100 score:
  - Correctness (50%)
  - Test Pass Rate (25%)
  - Code Quality (10%)
  - Efficiency (10%)
  - Reliability (5%)
- Optional AI Judge (`LLMJudge`) for complementary qualitative review.

### 6. Failure Taxonomy (`backend/app/failure_analysis/`)
Classifies failure modes into:
- `wrong_solution`
- `incomplete_solution`
- `test_failure`
- `syntax_error`
- `timeout`
- `command_failure`
- `tool_misuse`
- `permission_error`
- `dependency_issue`
- `unknown`

