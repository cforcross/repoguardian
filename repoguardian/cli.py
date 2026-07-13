import os
import typer
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

# Load environment variables from .env file
load_dotenv()
console = Console()
app = typer.Typer(help="🛡️ RepoGuardian: AI-Powered Codebase Security Scanner")

# --- 1. Core Logic: File Gathering ---
def gather_codebase(directory: str) -> str:
    extensions = {'.py', '.js', '.ts', '.java', '.go', '.c', '.cpp', '.rb', '.php'}
    code_context = []
    
    with console.status("[bold green]Indexing codebase..."):
        for root, _, files in os.walk(directory):
            if any(skip in root for skip in ['node_modules', '.git', 'venv', '__pycache__', '.venv']):
                continue
            for file in files:
                if os.path.splitext(file)[1] in extensions:
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                            code_context.append(f"--- File: {filepath} ---\n{content}\n")
                    except Exception:
                        pass
    return "\n".join(code_context)

# --- 2. LLM Routing: Multi-Provider Support ---
def get_llm(provider: str, model: str):
    """Routes to the correct LLM based on user input."""
    provider = provider.lower()
    
    if provider == "ollama":
        console.print(f"[cyan]Using local Ollama model:[/cyan] {model}")
        return ChatOllama(model=model, temperature=0)
    
    # OpenAI-compatible providers (OpenAI, DeepSeek, Grok, Qwen, etc.)
    api_compatible_providers = {
        "openai": {"url": "https://api.openai.com/v1", "key_env": "OPENAI_API_KEY"},
        "deepseek": {"url": "https://api.deepseek.com/v1", "key_env": "DEEPSEEK_API_KEY"},
        "grok": {"url": "https://api.x.ai/v1", "key_env": "XAI_API_KEY"},
        "qwen": {"url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "key_env": "DASHSCOPE_API_KEY"},
    }
    
    if provider in api_compatible_providers:
        config = api_compatible_providers[provider]
        api_key = os.getenv(config["key_env"])
        if not api_key:
            console.print(f"[red]Error:[/red] {config['key_env']} not found in .env file.")
            raise typer.Exit(1)
            
        console.print(f"[cyan]Using {provider.capitalize()} API model:[/cyan] {model}")
        return ChatOpenAI(
            model=model, 
            api_key=api_key, 
            base_url=config["url"], 
            temperature=0
        )
        
    console.print(f"[red]Error:[/red] Provider '{provider}' not supported.")
    raise typer.Exit(1)

# --- 3. The CLI Command ---
@app.command()
def scan(
    path: str = typer.Argument(..., help="Path to the codebase directory to scan"),
    provider: str = typer.Option("ollama", "--provider", "-p", help="LLM Provider (ollama, openai, deepseek, grok, qwen)"),
    model: str = typer.Option("qwen2.5-coder:7b", "--model", "-m", help="Model name to use")
):
    """Scans a codebase directory for security vulnerabilities using AI."""
    
    if not os.path.isdir(path):
        console.print(f"[red]Error:[/red] Directory '{path}' does not exist.")
        raise typer.Exit(1)

    # 1. Gather Code
    codebase_text = gather_codebase(path)
    if not codebase.strip():
        console.print("[yellow]No supported source files found in the directory.[/yellow]")
        raise typer.Exit(0)
        
    console.print(f"[green]✓[/green] Indexed {len(codebase_text)} characters of code.")

    # 2. Initialize LLM
    llm = get_llm(provider, model)

    # 3. Define Prompt & Run Audit
    prompt = ChatPromptTemplate.from_template("""
    You are an expert Application Security Engineer. 
    Analyze the following codebase for security vulnerabilities (e.g., SQL Injection, XSS, Hardcoded Secrets, Insecure Deserialization, Path Traversal, Broken Access Control).
    
    Output a structured Markdown report with:
    1. **Vulnerability Name**
    2. **File & Line/Function**
    3. **Severity** (Critical, High, Medium, Low)
    4. **Explanation** (Why it's a vulnerability)
    5. **Suggested Fix** (Code snippet or explanation)
    
    If no vulnerabilities are found, state that the code appears secure.
    
    Codebase:
    {codebase}
    """)

    chain = prompt | llm
    
    with console.status("[bold magenta]🧠 AI is analyzing the codebase for vulnerabilities...[/bold magenta]"):
        response = chain.invoke({"codebase": codebase_text})

    # 4. Output Results
    console.print("\n")
    console.print(Panel(Markdown(response.content), title="🛡️ AI Security Audit Report", border_style="green"))

if __name__ == "__main__":
    app()