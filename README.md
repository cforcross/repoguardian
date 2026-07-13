# 🛡️ RepoGuardian

**An open-source, AI-powered CLI tool that scans entire codebases for security vulnerabilities.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

RepoGuardian bridges the gap between traditional static analysis (which misses complex logic flaws) and raw LLM prompting (which fails on large codebases). It acts as an autonomous Application Security Engineer right in your terminal.

## ✨ Features

- 🧠 **AI-Driven Analysis:** Goes beyond regex-based linters to find complex logic flaws, broken access controls, and insecure data flows.
- 🔌 **Bring Your Own Key (BYOK):** Supports **Ollama** (100% local/private), **OpenAI**, **DeepSeek**, **Grok (xAI)**, and **Qwen**. No vendor lock-in.
- 💻 **CLI-First:** Built for developers. Integrates seamlessly into your local workflow and CI/CD pipelines.
- 🎨 **Beautiful Output:** Rich, color-coded terminal output with structured Markdown reports.
- 🚀 **Zero-Config Local Mode:** Run completely offline and private using local Ollama models.

## 🚀 Quick Start

### 1. Installation

Install directly from GitHub:
```bash
pip install git+https://github.com/YOUR_USERNAME/repoguardian.git
```
##  Configuration (For API Users)
```bash
cp .env.example .env
# Edit .env and add your API keys
```
(If you use local Ollama, you can skip this step!)

### 2. Scan Your Codebase
```bash
# Run locally with Ollama (Free & Private)
repoguardian scan ./my-project -p ollama -m qwen2.5-coder:7b

# Run with DeepSeek API (Fast & Cost-Effective)
repoguardian scan ./my-project -p deepseek -m deepseek-chat

# Run with OpenAI
repoguardian scan ./my-project -p openai -m gpt-4o
```
## 🏗️ Architecture & Roadmap

RepoGuardian is being built in phases to solve the "Context Window" problem in AI code auditing.

- [x] **Phase 1 (Current): The MVP.** Basic file-walking and direct LLM prompting. Perfect for small-to-medium repos.
- [ ] **Phase 2: The Parser Layer.** Integrating Tree-sitter for AST (Abstract Syntax Tree) generation to understand code structure.
- [ ] **Phase 3: The Memory Layer.** Implementing ChromaDB/Qdrant for semantic vector search, allowing the AI to trace data flows across massive enterprise codebases without hitting context limits.
- [ ] **Phase 4: Agentic Loop.** Implementing ReAct framework so the AI can autonomously use tools (`grep`, `view_file`, `run_linter`) to investigate complex bugs.

## 🤝 Contributing

We are building this in the open and would love your help! RepoGuardian is designed to be modular and easy to contribute to.

Check out our [Contributing Guide](CONTRIBUTING.md) and look for issues tagged with:

- 🟢 `good first issue` (Great for beginners)
- 🟡 `help wanted` (Core feature development)
- 🔴 `bug` (Squash some bugs)

**Ideas for first contributions:**
1. Add support for more file extensions (`.swift`, `.kt`, `.rs`).
2. Add a `--output` flag to save reports to a `.md` file.
3. Implement a `rich.progress` bar for the file indexing step.

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for more information.
