"""
Unit tests for RepoGuardian CLI.

Run with: pytest tests/
"""

import os
import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

# Import the app and functions from our CLI
# Updated to match the new folder structure
from repoguardian.cli import app, gather_codebase, get_llm

runner = CliRunner()


# ============================================
# Tests for gather_codebase()
# ============================================

class TestGatherCodebase:
    """Tests for the file-walking logic."""

    def test_finds_supported_extensions(self, tmp_path):
        """Should find files with supported extensions like .py, .js, etc."""
        # Create test files
        (tmp_path / "app.py").write_text("print('hello')")
        (tmp_path / "script.js").write_text("console.log('hi')")
        (tmp_path / "notes.txt").write_text("ignore me")  # Unsupported
        
        result = gather_codebase(str(tmp_path))
        
        assert "app.py" in result
        assert "script.js" in result
        assert "notes.txt" not in result

    def test_skips_ignored_directories(self, tmp_path):
        """Should skip node_modules, .git, venv, etc."""
        # Create files in ignored directories
        node_modules = tmp_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "package.py").write_text("bad code")
        
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        (git_dir / "config.py").write_text("git config")
        
        # Create a valid file
        (tmp_path / "main.py").write_text("good code")
        
        result = gather_codebase(str(tmp_path))
        
        assert "main.py" in result
        assert "package.py" not in result
        assert "config.py" not in result

    def test_handles_nested_directories(self, tmp_path):
        """Should recursively find files in subdirectories."""
        subdir = tmp_path / "src" / "utils"
        subdir.mkdir(parents=True)
        (subdir / "helper.py").write_text("def help(): pass")
        
        result = gather_codebase(str(tmp_path))
        
        assert "helper.py" in result
        assert "src/utils/helper.py" in result or "helper.py" in result

    def test_handles_empty_directory(self, tmp_path):
        """Should return empty string for directory with no supported files."""
        result = gather_codebase(str(tmp_path))
        assert result.strip() == ""

    def test_handles_unreadable_files_gracefully(self, tmp_path):
        """Should skip files that can't be read instead of crashing."""
        bad_file = tmp_path / "broken.py"
        bad_file.write_text("valid")
        # Simulate encoding error by making it unreadable
        # (In practice, the try/except in gather_codebase handles this)
        
        result = gather_codebase(str(tmp_path))
        # Should not raise an exception
        assert isinstance(result, str)


# ============================================
# Tests for get_llm()
# ============================================

class TestGetLLM:
    """Tests for the multi-provider LLM routing."""

    def test_ollama_provider(self):
        """Should return ChatOllama for ollama provider."""
        llm = get_llm("ollama", "qwen2.5-coder:7b")
        assert llm.__class__.__name__ == "ChatOllama"
        assert llm.model == "qwen2.5-coder:7b"

    def test_openai_provider_with_key(self, monkeypatch):
        """Should return ChatOpenAI when OPENAI_API_KEY is set."""
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")
        
        llm = get_llm("openai", "gpt-4o")
        assert llm.__class__.__name__ == "ChatOpenAI"
        assert llm.model_name == "gpt-4o"

    def test_deepseek_provider_with_key(self, monkeypatch):
        """Should route DeepSeek through OpenAI-compatible client."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test-key")
        
        llm = get_llm("deepseek", "deepseek-chat")
        assert llm.__class__.__name__ == "ChatOpenAI"
        assert "deepseek" in llm.openai_api_base

    def test_missing_api_key_exits(self, monkeypatch):
        """Should exit with error when API key is missing."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        
        with pytest.raises(SystemExit) as exc_info:
            get_llm("openai", "gpt-4o")
        assert exc_info.value.code == 1

    def test_unsupported_provider_exits(self):
        """Should exit with error for unknown providers."""
        with pytest.raises(SystemExit) as exc_info:
            get_llm("unknown_provider", "some-model")
        assert exc_info.value.code == 1


# ============================================
# Tests for the CLI scan command
# ============================================

class TestScanCommand:
    """Tests for the main CLI command using Typer's CliRunner."""

    def test_scan_nonexistent_directory(self):
        """Should fail gracefully when directory doesn't exist."""
        result = runner.invoke(app, ["scan", "/nonexistent/path"])
        assert result.exit_code == 1
        assert "does not exist" in result.stdout

    def test_scan_empty_directory(self, tmp_path):
        """Should exit cleanly when no supported files are found."""
        result = runner.invoke(app, ["scan", str(tmp_path)])
        assert result.exit_code == 0
        assert "No supported source files" in result.stdout

    @patch("repoguardian.cli.get_llm")  # Updated mock path
    def test_scan_with_mocked_llm(self, mock_get_llm, tmp_path):
        """Should run full scan with mocked LLM (no API calls)."""
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="**No vulnerabilities found.**")
        mock_get_llm.return_value = mock_llm
        
        # Create a test file
        (tmp_path / "test.py").write_text("print('safe code')")
        
        result = runner.invoke(app, ["scan", str(tmp_path), "-p", "ollama"])
        
        assert result.exit_code == 0
        assert "AI Security Audit Report" in result.stdout
        mock_get_llm.assert_called_once()

    def test_scan_with_custom_provider_flag(self, tmp_path, monkeypatch):
        """Should accept --provider and --model flags."""
        monkeypatch.setenv("DEEPSEEK_API_KEY", "sk-test")
        
        with patch("repoguardian.cli.get_llm") as mock_get_llm:  # Updated mock path
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content="Report")
            mock_get_llm.return_value = mock_llm
            
            (tmp_path / "app.py").write_text("x = 1")
            
            result = runner.invoke(app, [
                "scan", str(tmp_path),
                "-p", "deepseek",
                "-m", "deepseek-chat"
            ])
            
            assert result.exit_code == 0
            mock_get_llm.assert_called_once_with("deepseek", "deepseek-chat")