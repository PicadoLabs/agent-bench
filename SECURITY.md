# Security Policy

PicadoLabs takes the security of AgentBench and its users seriously. We appreciate the responsible disclosure of any potential vulnerabilities.

---

## Supported Versions

Only the latest stable release line receives security patches and vulnerability updates:

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | Yes |
| < 1.0   | No  |

---

## Reporting a Vulnerability

**Please DO NOT report security vulnerabilities through public GitHub issues, discussions, or pull requests.**

If you discover a security vulnerability in AgentBench (such as sandbox escape, path traversal, credential exposure, or remote execution vulnerabilities), please report it privately:

1. **Email**: Send your findings directly to [picadolabs@gmail.com](mailto:picadolabs@gmail.com).
2. **Subject Line**: Prefix the subject with `[SECURITY VULNERABILITY] AgentBench - <Brief Summary>`.
3. **Details to Include**:
   * A detailed description of the vulnerability and its potential impact.
   * Step-by-step instructions or a minimal Proof of Concept (PoC) to reproduce the issue.
   * Affected component (e.g. `LocalProcessSandbox`, `DockerSandbox`, CLI runner, API server, or ingestion parser).
   * Your operating system, Python version, and dependency versions.
   * Any suggested remediation or patch (if available).

---

## Response & Disclosure Process

* **Acknowledgment**: We aim to acknowledge receipt of your vulnerability report within **48 hours**.
* **Assessment & Fix**: We will assess the severity, validate the reproduction steps, and work on a security patch in a private branch.
* **Coordination**: We will coordinate with you regarding the fix verification and timeline.
* **Public Release & Credit**: Once the patch is released in a new version, we will publicly credit you in the release notes (unless you prefer to remain anonymous).

Thank you for helping keep AgentBench and the open-source community safe and secure!

