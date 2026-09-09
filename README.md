# AgentBench

[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![Node Version](https://img.shields.io/badge/node-%3E%3D18.0.0-green)](https://nodejs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Organization](https://img.shields.io/badge/Maintained%20by-PicadoLabs-FF5A1F)](https://picadolabs.me)

> **AgentBench** is a provider-agnostic, local-first evaluation and benchmarking platform for autonomous AI coding agents. Run agents against real software-engineering tasks in isolated execution sandboxes, execute automated test suites, collect execution telemetry, perform objective multi-dimensional scoring, and analyze failure root causes.

---

## Overview

Traditional LLM evaluation benchmarks (e.g. HumanEval, MBPP) measure single-turn string generation (`pass@1`) on isolated toy functions. In contrast, real software engineering requires autonomous agents to:
1. Navigate and explore multi-file codebases.
2. Formulate diagnostic hypotheses and execute test suites.
3. Apply surgical file modifications across interdependent modules.
4. Interpret test tracebacks and autonomously self-repair regressions.

**AgentBench** bridges this gap by providing an isolated, reproducible testbed where coding agents interact with real repositories using standardized tools (`read_file`, `write_file`, `list_files`, `run_tests`).

---

## Key Features

* **Free & Local-First by Default**: Out-of-the-box support for local models (`qwen2.5-coder`, `deepseek-coder-v2`, `llama3.1`) via **Ollama**. Run comprehensive benchmark sweeps with **$0.00 in API costs**.
* **Provider-Agnostic Engine**: Pluggable LLM provider architecture supporting Ollama, OpenAI (`gpt-4o`, `gpt-4o-mini`), Anthropic (`claude-3-5-sonnet`), Google Gemini (`gemini-1.5-pro`), and custom OpenAI-compatible endpoints.
* **Dual Sandboxing Layer**: Run evaluations inside containerized Docker environments or fast local subprocess sandboxes with path traversal prevention, process tree timeouts, and host secret isolation.
* **12 Standardized Multi-Language Benchmarks**: Real-world tasks covering Bug Fixing, Feature Implementation, Refactoring, Debugging, and Security Patches across Python (`pytest`) and Node.js/TypeScript (`node --test`).
* **GitHub PR & Issue Ingestion Tool**: CLI and Web UI tools to convert any public GitHub Pull Request into an immutable benchmark task definition with problem statement extraction, pinned commits, and patch diffs.
* **Objective Composite Scoring Engine**: Multi-dimensional scoring formula balancing Correctness (50%), Test Pass Rate (25%), Code Quality (10%), Execution Efficiency (10%), and Repair Reliability (5%).
* **Automated Failure Mode Taxonomy**: Automatic categorization of non-passing runs into explicit root causes (`wrong_solution`, `test_failure`, `syntax_error`, `timeout`, `tool_misuse`, `incomplete_solution`, `dependency_issue`).
* **Developer-Grade Dashboard & CLI**: High-contrast dark React/Tailwind web dashboard with live WebSocket telemetry streaming and a feature-complete Typer/Rich terminal CLI.

---

## System Architecture

```text
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
            ┌──────────────────┴──────────────────┐
            │                                     │
   [ 12 Standard Benchmarks ]             [ GitHub PR Ingestion ]
            │                                     │
            └──────────────────┬──────────────────┘
                               │
                       [ Benchmark Task ]
                               │
                      [ Agent Runtime ]
             (IterativeCodingAgent / FastPatchAgent)
                               │
                    [ Sandboxed Workspace ]
                   (Docker / Safe Process)
                               │
                     [ Surgical Code Edits ]
                               │
                   [ Objective Test Runner ]
                 (Pytest / Node.js Test Harness)
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
              ┌────────────────┼────────────────┐
              │                │                │
        [ Typer CLI ]  [ React Dashboard ]  [ GitHub Action CI ]
```

---

## Supported Platforms & Prerequisites

### Supported Operating Systems
* **Linux**: Ubuntu 20.04+, Debian 11+, Fedora 38+, Arch Linux
* **macOS**: macOS 12 (Monterey) or later (Apple Silicon & Intel)
* **Windows**: Windows 10 / 11 (PowerShell & WSL2)

### Prerequisites
* **Python**: `3.10`, `3.11`, or `3.12`
* **Node.js**: `18.x` or `20.x` (for React frontend & polyglot benchmarks)
* **Git**: `2.30+`
* *(Optional)* **Ollama**: For free offline local LLM execution ([ollama.com](https://ollama.com))
* *(Optional)* **Docker**: For containerized execution sandboxes

---

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/PicadoLabs/Agent-Bench.git
cd Agent-Bench
```

### 2. Install Python & Frontend Dependencies

```bash
# Set up Python virtual environment
python -m venv venv

# Linux / macOS
source venv/bin/activate
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Install core dependencies
pip install -r requirements.txt
pip install -e .

# Install frontend dependencies
cd frontend
npm install
npm run build
cd ..
```

### 3. Verify Environment Health

```bash
python agentbench.py doctor
```

Output:
```text
┌───────────────────────────────┐
│ AGENTBENCH ENVIRONMENT DOCTOR │
└───────────────────────────────┘
[OK] Python 3.12.x
[OK] Local Process Sandboxing Ready (Docker optional)
[OK] SQLite persistence ready (sqlite:///./agentbench.db)
```

### 4. Initialize Database & Seed Tasks

```bash
python agentbench.py init
```

### 5. Run Your First Benchmark

```bash
# Run a quick smoke benchmark with mock provider
python agentbench.py run --benchmark feat-fastapi-pagination --provider mock --model mock-coder

# Run against local Ollama model (zero API cost)
python agentbench.py run --benchmark fix-rate-limiter --provider ollama --model qwen2.5-coder:1.5b

# Run a Node.js polyglot benchmark
python agentbench.py run --benchmark feat-express-auth --provider mock --model mock-coder
```

### 6. Launch the Web Dashboard

```bash
python agentbench.py serve --port 8000
```

Open **[http://localhost:8000](http://localhost:8000)** in your browser to inspect execution trajectories, live test outputs, git diff patches, and leaderboard rankings.

---

## Configuration

AgentBench reads configuration from environment variables or a local `.env` file. Copy `.env.example` to get started:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `MODEL_PROVIDER` | `ollama` | Default LLM provider (`ollama`, `openai`, `anthropic`, `gemini`, `mock`, `custom`). |
| `MODEL_NAME` | `qwen2.5-coder:1.5b` | Model identifier to pass to provider. |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama daemon API base endpoint. |
| `OPENAI_API_KEY` | *(None)* | OpenAI API secret key. |
| `ANTHROPIC_API_KEY` | *(None)* | Anthropic API secret key. |
| `GEMINI_API_KEY` | *(None)* | Google Gemini API key. |
| `CUSTOM_API_BASE` | *(None)* | Custom OpenAI-compatible endpoint URL (e.g. vLLM, LiteLLM, Ollama OpenAI wrapper). |
| `CUSTOM_API_KEY` | *(None)* | API key for custom endpoint if required. |
| `DATABASE_URL` | `sqlite:///./agentbench.db` | SQLAlchemy connection URI. |
| `SANDBOX_RUNTIME` | `local` | Sandbox execution backend: `local` (Process Sandbox) or `docker` (Containers). |
| `EXECUTION_TIMEOUT` | `120` | Max duration (seconds) allowed per benchmark evaluation. |
| `HOST` | `0.0.0.0` | Bind host address for FastAPI server. |
| `PORT` | `8000` | Port for FastAPI server & Web UI. |

---

## CLI Reference

| Command | Description |
|---|---|
| `python agentbench.py doctor` | Diagnose environment, Docker daemon, Ollama status, and API configurations. |
| `python agentbench.py init` | Initialize database schema, workspaces, and seed benchmark tasks. |
| `python agentbench.py list` | List all registered benchmark tasks, categories, and test commands. |
| `python agentbench.py run -b <id>` | Launch benchmark evaluation run on a specified task. |
| `python agentbench.py ingest <pr_url>` | Ingest a real GitHub PR / Issue into a reproducible benchmark task. |
| `python agentbench.py results` | List recent run outcomes, scores, and execution durations. |
| `python agentbench.py inspect <run_id>` | Deep-dive into a run's timeline, step events, git diff, and failure analysis. |
| `python agentbench.py leaderboard` | Display aggregated rankings and model performance comparisons. |
| `python agentbench.py compare <r1> <r2>` | Perform side-by-side run comparison of code patches and scores. |
| `python agentbench.py serve [--port 8000]` | Start FastAPI backend and unified React UI. |

---

## Benchmark Task Suite

AgentBench includes 12 standardized software-engineering benchmark tasks:

| ID | Task Name | Stack | Category | Difficulty | Evaluation Test Command |
|---|---|---|---|---|---|
| `fix-auth-jwt` | Fix JWT Authentication & Token Security | Python | Bug Fixing | Medium | `pytest test_auth.py` |
| `feat-fastapi-pagination` | Implement API Pagination & Bounds | Python | Feature | Easy | `pytest test_pagination.py` |
| `fix-rate-limiter` | Fix Sliding Window Rate Limiter Logic | Python | Bug Fixing | Easy | `pytest test_rate_limiter.py` |
| `fix-sql-builder` | Parameterized SQL Query Builder | Python | Bug Fixing | Easy | `pytest test_query_builder.py` |
| `fix-lru-ttl-cache` | LRU Cache with TTL Expiration | Python | Bug Fixing | Medium | `pytest test_cache.py` |
| `fix-csv-pipeline` | Data Pipeline Ingestion & Cleaners | Python | Bug Fixing | Medium | `pytest test_pipeline.py` |
| `refactor-tree-serializer` | Refactor Tree Serializer with Cycle Detection | Python | Refactoring | Medium | `pytest test_serializer.py` |
| `feat-config-loader` | Typed Configuration Loader & Env Overrides | Python | Feature | Easy | `pytest test_config.py` |
| `debug-async-queue` | Async Task Queue Worker & Heartbeats | Python | Debugging | Medium | `pytest test_task_queue.py` |
| `debug-markdown-parser` | Markdown Link & Image AST Parser | Python | Debugging | Easy | `pytest test_markdown.py` |
| `feat-express-auth` | Express API Auth & Token-Bucket Rate Limiter | Node.js | Feature | Medium | `node --test test_auth.js` |
| `fix-react-hook-leak` | Fix React Hook Event & Timer Memory Leak | React / Node | Bug Fixing | Medium | `node --test test_hook.js` |

---

## GitHub PR Ingestion Engine

Convert any public GitHub Pull Request into an automated benchmark task:

```bash
# Ingest via CLI
python agentbench.py ingest https://github.com/fastapi/fastapi/pull/1234 \
  --category "Bug Fixing" \
  --difficulty "Medium" \
  --test-cmd "pytest"
```

The ingestion tool:
1. Queries the GitHub REST API to extract issue problem statements and PR descriptions.
2. Identifies the base commit SHA and packages the raw unified patch diff.
3. Automatically generates an immutable task configuration (`benchmarks/tasks/gh-<repo>-<pr>.yaml`).
4. Registers the new task in the database for immediate execution via CLI or Web UI.

---

## CI/CD Pull Request Gatekeeper

AgentBench includes an automated GitHub Actions workflow (`.github/workflows/ci.yml` and `.github/workflows/agentbench-eval.yml`) that can gate Pull Requests:

1. Installs Python (`3.10`, `3.11`, `3.12`) and Node.js (`20.x`).
2. Runs all unit, integration, and E2E test suites.
3. Evaluates target agents against the standardized benchmark matrix.
4. Posts an automated evaluation and pass/fail summary.

---

## Development & Testing

### Running the Python Test Suite
```bash
python -m pytest -v
```

### Running Polyglot Node.js Benchmark Tests
```bash
node --test benchmarks/repos/express-auth-middleware/test_auth.js
node --test benchmarks/repos/react-hook-leak/test_hook.js
```

### Building & Typechecking the Frontend
```bash
cd frontend
npm run build
cd ..
```

---

## Project Structure

```text
Agent-Bench/
├── backend/                  # Python backend application
│   ├── app/
│   │   ├── agents/           # Agent implementations (IterativeCoding, FastPatch, Baseline)
│   │   ├── api/              # FastAPI REST endpoints & WebSocket broadcasters
│   │   ├── benchmarks/       # Benchmark runner, loaders, and GitHub ingestion engine
│   │   ├── cli/              # Typer/Rich CLI implementation
│   │   ├── config/           # Application settings & environment parsing
│   │   ├── evaluation/       # Test parsers, scoring engine, failure taxonomy, AI judge
│   │   ├── providers/        # LLM providers (Ollama, OpenAI, Anthropic, Gemini, Mock)
│   │   ├── sandbox/          # LocalProcessSandbox & DockerSandbox isolation layers
│   │   └── storage/          # SQLAlchemy models, SQLite persistence, and repository
│   ├── tests/                # Unit, integration, and E2E test suites
│   └── main.py               # FastAPI application entrypoint
├── benchmarks/               # Standardized benchmark task suite
│   ├── repos/                # Target repository codebases & unit test suites
│   └── tasks/                # Benchmark YAML task definitions
├── frontend/                 # React 18 + TypeScript + Tailwind SPA
│   ├── src/
│   │   ├── components/       # UI components, sidebar, header, telemetry views
│   │   ├── pages/            # Dashboard, Benchmarks, Run, Leaderboard, Failures, Doctor
│   │   └── lib/              # API client and WebSocket handlers
│   ├── package.json
│   └── vite.config.ts
├── .github/                  # GitHub Actions CI & issue/PR templates
│   ├── workflows/            # ci.yml, agentbench-eval.yml
│   ├── ISSUE_TEMPLATE/       # bug_report.md, feature_request.md
│   └── pull_request_template.md
├── agentbench.py             # Root CLI entrypoint script
├── pyproject.toml            # Standard Python packaging configuration
├── requirements.txt          # Python dependency specifications
├── Dockerfile                # Multi-stage production container build
├── docker-compose.yml        # Docker Compose configuration
├── CONTRIBUTING.md           # Contributor guide and development workflow
├── CODE_OF_CONDUCT.md        # Contributor Covenant Code of Conduct
├── SECURITY.md               # Security vulnerability disclosure policy
└── LICENSE                   # MIT License
```

---

## PicadoLabs

AgentBench is an open-source project maintained by **PicadoLabs**.

* **Organization**: [PicadoLabs on GitHub](https://github.com/PicadoLabs)
* **Website**: [https://picadolabs.me](https://picadolabs.me)
* **Contact**: [picadolabs@gmail.com](mailto:picadolabs@gmail.com)

---

## Contributing & Community

We welcome contributions from the community! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) guide for details on our development workflow, coding standards, and pull request submission process.

All community members are expected to follow our [Code of Conduct](CODE_OF_CONDUCT.md).

---

## Security

If you discover a security vulnerability, please review our [SECURITY.md](SECURITY.md) policy and report it privately via email to [picadolabs@gmail.com](mailto:picadolabs@gmail.com).

---

## License

AgentBench is licensed under the [MIT License](LICENSE).  
Copyright (c) 2026 PicadoLabs.
