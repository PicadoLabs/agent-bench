# Contributing to Agent Bench

Thank you for your interest in contributing to **Agent Bench**! Agent Bench provides a unified platform to evaluate AI coding agents securely against diverse real-world GitHub issues.

Agent Bench is maintained under the **PicadoLabs** organization ([https://github.com/PicadoLabs](https://github.com/PicadoLabs)).

---

## Table of Contents
1. [Code of Conduct](#code-of-conduct)
2. [Prerequisites](#prerequisites)
3. [Local Setup & Installation](#local-setup--installation)
4. [Testing & Quality Verification](#testing--quality-verification)
5. [Submitting Pull Requests](#submitting-pull-requests)

---

## 1. Code of Conduct
All contributors and maintainers are expected to adhere to the [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior to [picadolabs@gmail.com](mailto:picadolabs@gmail.com).

## 2. Prerequisites
- Python 3.10+
- Node.js 18+
- Docker (for sandbox testing)

## 3. Local Setup & Installation
1. Clone the repo.
2. `cd Agent Bench`
3. `pip install -e .[dev,test]`
4. `cd frontend && npm install && cd ..`

## 4. Testing & Quality Verification
Before submitting a pull request, ensure all tests pass:
`pytest tests/ -v`
For frontend: `cd frontend && npm test` (if applicable).

## 5. Submitting Pull Requests
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-new-feature`).
3. Commit your changes (`git commit -am 'Add some feature'`).
4. Push to the branch (`git push origin feature/my-new-feature`).
5. Create a new Pull Request.
