# Benchmark Task Specification Format

Benchmark tasks in AgentBench are defined in clean YAML files placed in `benchmarks/tasks/`.

## Example YAML Task Definition

```yaml
id: fix-auth-jwt
name: Fix JWT Authentication & Token Security
description: Fix signature verification, algorithm confusion (alg:none), and expiration validation.
category: Bug Fixing
difficulty: Medium

repository:
  type: local
  path: benchmarks/repos/auth-jwt-service
  commit: HEAD

task:
  prompt: |
    In auth_service.py, the `verify_token` method has severe security vulnerabilities:
    1. It fails to reject tokens with algorithm "none".
    2. It does not compute or compare the HMAC-SHA256 signature using `self.secret_key`.
    3. It ignores the expiration timestamp (`exp`) in the payload.

    Investigate `auth_service.py` and fix `verify_token`.
    Do not modify test_auth.py.

  constraints: |
    - Use Python standard libraries (hmac, hashlib, json, base64, time).
    - Do not modify test files.

evaluation:
  command: pytest test_auth.py
  timeout: 60

scoring:
  correctness: 50
  test_pass_rate: 25
  code_quality: 10
  efficiency: 10
  reliability: 5
```

## Schema Fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique task slug identifier. |
| `name` | string | Human-readable task title. |
| `description` | string | Brief summary of the problem. |
| `category` | string | One of `Bug Fixing`, `Feature Implementation`, `Refactoring`, `Testing`, `Debugging`. |
| `difficulty` | string | `Easy`, `Medium`, or `Hard`. |
| `repository.path` | string | Relative or absolute path to the target repository. |
| `repository.commit` | string | Pinned git commit or `HEAD` for reproducibility. |
| `task.prompt` | string | The full task prompt given to the AI coding agent. |
| `task.constraints` | string | Optional technical constraints or guidelines. |
| `evaluation.command` | string | Shell test command executed inside the sandbox (e.g. `pytest`). |
| `evaluation.timeout` | int | Maximum execution timeout in seconds. |
| `scoring` | object | Percentage weights for score normalization (sum = 100). |

