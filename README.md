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
