# Contributing to AgentBench

Thank you for your interest in contributing to **AgentBench**! We welcome contributions from developers of all backgrounds.

AgentBench is maintained under the **PicadoLabs** organization ([https://github.com/PicadoLabs](https://github.com/PicadoLabs)).

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Prerequisites](#prerequisites)
3. [Local Setup & Installation](#local-setup--installation)
4. [Development Workflow](#development-workflow)
5. [Adding a New Benchmark Task](#adding-a-new-benchmark-task)
6. [Testing & Quality Verification](#testing--quality-verification)
7. [Commit Conventions](#commit-conventions)
8. [Submitting Pull Requests](#submitting-pull-requests)
9. [Reporting Issues](#reporting-issues)

---

## Code of Conduct

All contributors and maintainers are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). Please report any unacceptable behavior to [picadolabs@gmail.com](mailto:picadolabs@gmail.com).

---

## Prerequisites

Ensure you have the following installed on your machine:

* **Python**: 3.10, 3.11, or 3.12 (`python --version`)
* **Node.js**: 18.x or 20.x (`node --version`) and npm (`npm --version`)
* **Git**: (`git --version`)
* *(Optional)* **Ollama**: For free local LLM execution ([ollama.com](https://ollama.com))
* *(Optional)* **Docker**: For containerized sandboxing (`docker --version`)

---

## Local Setup & Installation

### 1. Fork & Clone the Repository

```bash
git clone https://github.com/<your-username>/Agent-Bench.git
cd Agent-Bench
```

### 2. Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Linux/macOS:
source venv/bin/activate

# Activate on Windows (PowerShell):
.\venv\Scripts\Activate.ps1
```

### 3. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install -e ".[dev]"
```

### 4. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 5. Initialize the Database & Seed Benchmarks

```bash
python agentbench.py init
python agentbench.py doctor
```

### 6. Run the Development Server

```bash
# Terminal 1: Backend API + CLI
python agentbench.py serve --port 8000

# Terminal 2: Frontend Vite Dev Server (for hot module reloading)
cd frontend
npm run dev
```

The frontend dev server will be running on `http://localhost:5173` proxying to `http://127.0.0.1:8000`.

---

## Development Workflow

1. Create a descriptive feature branch from `main`:
   ```bash
   git checkout -b feat/my-new-feature
   # or
   git checkout -b fix/issue-description
   ```
2. Make your targeted code changes.
3. Verify formatting and linting.
4. Run all unit and integration tests before submitting.

---

## Adding a New Benchmark Task

To add a new benchmark task to AgentBench:

1. Create a repository folder under `benchmarks/repos/<task-slug>/` containing the starting codebase and test suite.
2. Create a YAML task definition under `benchmarks/tasks/<number>-<task-slug>.yaml`:
   ```yaml
   id: my-custom-task
   name: Implement Custom Feature
   description: Brief description of the task
   category: Feature Implementation # Bug Fixing | Refactoring | Debugging
   difficulty: Medium # Easy | Medium | Hard
   repo_path: ./benchmarks/repos/my-custom-task
   repo_commit: HEAD
   prompt: |
     Detailed prompt and instructions given to the agent.
   constraints: |
     Do not modify test files. Preserve existing API signatures.
   evaluation:
     command: pytest test_feature.py # or "node --test test_feature.js"
     timeout: 120
   scoring_weights:
     correctness: 50
     test_pass_rate: 25
     code_quality: 10
     efficiency: 10
     reliability: 5
   ```
3. Test your benchmark:
   ```bash
   python agentbench.py run --benchmark my-custom-task --provider mock --model mock-coder
   ```

---

## Testing & Quality Verification

Before opening a pull request, verify that all test suites pass:

### 1. Run Python Tests
```bash
python -m pytest -v
```

### 2. Run Polyglot Node.js Benchmark Tests
```bash
node --test benchmarks/repos/express-auth-middleware/test_auth.js
node --test benchmarks/repos/react-hook-leak/test_hook.js
```

### 3. Build & Typecheck Frontend
```bash
cd frontend
npm run build
cd ..
```

---

## Commit Conventions

We follow [Conventional Commits](https://www.conventionalcommits.org/):

* `feat:` A new feature (e.g. `feat: add docker sandbox memory limit`)
* `fix:` A bug fix (e.g. `fix: handle edge case in test output parser`)
* `docs:` Documentation updates (e.g. `docs: update quickstart guide`)
* `test:` Adding or updating tests (e.g. `test: add unit test for scoring engine`)
* `refactor:` Code refactoring without behavioral changes (e.g. `refactor: clean up sandbox process lifecycle`)
* `chore:` Maintenance tasks and dependencies (e.g. `chore: update pydantic version`)

---

## Submitting Pull Requests

1. Push your branch to your fork:
   ```bash
   git push origin feat/my-new-feature
   ```
2. Open a Pull Request against the `main` branch of [https://github.com/PicadoLabs/Agent-Bench](https://github.com/PicadoLabs/Agent-Bench).
3. Fill out the pull request template with a concise summary of changes and testing steps.
4. Ensure all automated CI checks pass.

---

## Reporting Issues

* **Bug Reports**: Open an issue using the [Bug Report Template](.github/ISSUE_TEMPLATE/bug_report.md).
* **Feature Requests**: Open an issue using the [Feature Request Template](.github/ISSUE_TEMPLATE/feature_request.md).
* **Security Issues**: Please read [SECURITY.md](SECURITY.md) and report privately to [picadolabs@gmail.com](mailto:picadolabs@gmail.com).

Thank you for contributing to AgentBench!

