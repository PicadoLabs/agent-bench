import os
import sys
import asyncio
from pathlib import Path
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import print as rprint

from app.config.settings import get_settings
from app.storage.database import init_db, SessionLocal
from app.storage.repository import BenchmarkRepository, RunRepository
from app.benchmarks.loader import BenchmarkLoader
from app.benchmarks.runner import BenchmarkRunner
from app.sandbox.factory import is_docker_available

# Safe cross-platform console
console = Console(safe_box=True, highlight=False)
cli_app = typer.Typer(help="AgentBench - AI Coding-Agent Benchmarking & Evaluation Platform")


@cli_app.command("init")
def init_cmd():
    """Initialize AgentBench database, workspace directories, and seed benchmarks."""
    console.print("[bold green]Initializing AgentBench...[/bold green]")
    init_db()
    db = SessionLocal()
    try:
        settings = get_settings()
        synced = BenchmarkLoader.sync_benchmarks_to_db(db, os.path.join(settings.benchmarks_dir, "tasks"))
        console.print(f"[bold green][OK][/bold green] Database initialized and {len(synced)} benchmarks registered.")
    finally:
        db.close()


@cli_app.command("doctor")
def doctor_cmd():
    """Diagnose system environment, Docker daemon, Ollama reachability, and configuration."""
    settings = get_settings()
    console.print(Panel.fit("[bold white]AGENTBENCH ENVIRONMENT DOCTOR[/bold white]", border_style="bright_blue"))

    # 1. Python
    console.print(f"[bold green][OK][/bold green] Python {sys.version.split()[0]}")

    # 2. Docker
    docker_ok = is_docker_available()
    if docker_ok:
        console.print("[bold green][OK][/bold green] Docker Daemon active and reachable")
    else:
        console.print("[bold yellow][!][/bold yellow] Docker Daemon unreachable (LocalProcessSandbox fallback enabled)")

    # 3. Ollama
    import httpx
    try:
        res = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=2.0)
        if res.status_code == 200:
            models = [m.get("name") for m in res.json().get("models", [])]
            console.print(f"[bold green][OK][/bold green] Ollama service connected ({len(models)} local models found: {', '.join(models[:3])})")
        else:
            console.print(f"[bold yellow][!][/bold yellow] Ollama responded with status {res.status_code}")
    except Exception:
        console.print(f"[bold yellow][!][/bold yellow] Ollama not running at {settings.ollama_base_url} (Free mode ready when Ollama started)")

    # 4. Database
    try:
        init_db()
        console.print(f"[bold green][OK][/bold green] SQLite persistence ready ({settings.database_url})")
    except Exception as e:
        console.print(f"[bold red][X][/bold red] Database error: {e}")

    # 5. API Keys
    if settings.openai_api_key:
        console.print("[bold green][OK][/bold green] OpenAI API key configured")
    else:
        console.print("[dim][-] OpenAI API key not set (optional)[/dim]")

    if settings.anthropic_api_key:
        console.print("[bold green][OK][/bold green] Anthropic API key configured")
    else:
        console.print("[dim][-] Anthropic API key not set (optional)[/dim]")

    if settings.gemini_api_key:
        console.print("[bold green][OK][/bold green] Gemini API key configured")
    else:
        console.print("[dim][-] Gemini API key not set (optional)[/dim]")


@cli_app.command("list")
def list_cmd():
    """List all registered benchmark tasks."""
    init_db()
    db = SessionLocal()
    try:
        repo = BenchmarkRepository(db)
        benchmarks = repo.get_all()
        if not benchmarks:
            settings = get_settings()
            BenchmarkLoader.sync_benchmarks_to_db(db, os.path.join(settings.benchmarks_dir, "tasks"))
            benchmarks = repo.get_all()

        table = Table(title="Available Benchmarks", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan", width=24)
        table.add_column("Name", style="white")
        table.add_column("Category", style="green")
        table.add_column("Difficulty", style="yellow")
        table.add_column("Command", style="dim")

        for b in benchmarks:
            cmd = b.tasks[0].evaluation_command if b.tasks else "pytest"
            table.add_row(b.id, b.name, b.category, b.difficulty, cmd)

        console.print(table)
    finally:
        db.close()


@cli_app.command("run")
def run_cmd(
    benchmark: str = typer.Option(..., "--benchmark", "-b", help="Benchmark ID to run"),
    agent: str = typer.Option("IterativeCodingAgent", "--agent", "-a", help="Agent name"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model name"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Provider name (ollama, mock, openai, etc.)"),
    runtime: Optional[str] = typer.Option(None, "--runtime", "-r", help="Sandbox runtime (docker or local)"),
    judge: bool = typer.Option(False, "--judge", help="Enable AI LLM Judge")
):
    """Execute a benchmark evaluation run."""
    init_db()
    db = SessionLocal()
    try:
        runner = BenchmarkRunner(db)
        console.print(f"[bold cyan]Starting benchmark evaluation run on '{benchmark}'...[/bold cyan]")

        async def console_event_listener(event: dict):
            ev_type = event.get("event_type")
            msg = event.get("message")
            if "started" in ev_type:
                console.print(f"[dim]{ev_type}[/dim] ➔ {msg}")
            elif "tool" in ev_type:
                console.print(f"  [yellow]→[/yellow] {msg}")
            elif "test" in ev_type:
                console.print(f"  [blue]⚡[/blue] {msg}")
            elif "completed" in ev_type:
                console.print(f"[bold green]✓ {msg}[/bold green]")
            elif "failed" in ev_type or "crashed" in ev_type:
                console.print(f"[bold red]✕ {msg}[/bold red]")

        result = asyncio.run(runner.execute_run(
            benchmark_id=benchmark,
            agent_name=agent,
            model_name=model,
            provider_name=provider,
            sandbox_runtime=runtime,
            enable_llm_judge=judge,
            broadcaster=console_event_listener
        ))

        # Pretty print summary panel
        status_color = "green" if result["status"] == "SUCCEEDED" else ("yellow" if result["status"] == "PARTIAL" else "red")
        summary = f"""[bold]Run ID:[/bold] {result['run_id']}
[bold]Status:[/bold] [{status_color}]{result['status']}[/{status_color}]
[bold]Score:[/bold] [bold {status_color}]{result['score']}/100[/bold {status_color}]
[bold]Tests Passed:[/bold] {result['passed_tests']}/{result['total_tests']}
[bold]Execution Time:[/bold] {result['metrics']['duration_seconds']}s
[bold]Tool Calls:[/bold] {result['metrics']['tool_calls_count']}
[bold]Estimated Cost:[/bold] ${result['metrics']['estimated_cost']:.4f}
"""
        console.print(Panel(summary, title=f"Benchmark Result — {benchmark}", border_style=status_color))

        if result.get("failure_analysis"):
            fa = result["failure_analysis"]
            fa_text = f"[bold red]Primary Failure:[/bold red] {fa['primary_failure']}\n[bold]Root Cause:[/bold] {fa['root_cause']}\n[bold]Hint:[/bold] {fa['resolution_hints']}"
            console.print(Panel(fa_text, title="Failure Analysis", border_style="red"))

    finally:
        db.close()


@cli_app.command("leaderboard")
def leaderboard_cmd():
    """Display the AgentBench leaderboard."""
    init_db()
    db = SessionLocal()
    try:
        repo = RunRepository(db)
        board = repo.get_leaderboard()

        if not board:
            console.print("[yellow]No completed benchmark runs found yet. Execute 'agentbench run' first.[/yellow]")
            return

        table = Table(title="AgentBench Global Leaderboard", show_header=True, header_style="bold green")
        table.add_column("Rank", justify="center", style="bold")
        table.add_column("Agent", style="white")
        table.add_column("Model", style="cyan")
        table.add_column("Provider", style="magenta")
        table.add_column("Success Rate", justify="right", style="green")
        table.add_column("Avg Score", justify="right", style="bold yellow")
        table.add_column("Avg Time", justify="right")
        table.add_column("Avg Cost", justify="right")
        table.add_column("Runs", justify="center")

        for row in board:
            table.add_row(
                str(row["rank"]),
                row["agent_name"],
                row["model_name"],
                row["provider_name"],
                f"{row['success_rate']}%",
                f"{row['avg_score']}/100",
                f"{row['avg_time']}s",
                f"${row['avg_cost']:.4f}",
                str(row["total_runs"])
            )

        console.print(table)
    finally:
        db.close()


@cli_app.command("results")
def results_cmd(limit: int = 20):
    """List recent benchmark run results."""
    init_db()
    db = SessionLocal()
    try:
        repo = RunRepository(db)
        runs = repo.list_runs(limit=limit)

        table = Table(title="Recent Benchmark Runs", show_header=True, header_style="bold blue")
        table.add_column("Run ID", style="cyan")
        table.add_column("Benchmark", style="white")
        table.add_column("Agent", style="dim")
        table.add_column("Model", style="dim")
        table.add_column("Status", justify="center")
        table.add_column("Score", justify="right", style="bold")
        table.add_column("Tests", justify="center")
        table.add_column("Time", justify="right")

        for r in runs:
            st_color = "green" if r.status == "SUCCEEDED" else ("yellow" if r.status == "PARTIAL" else "red")
            table.add_row(
                r.id,
                r.benchmark_name or r.benchmark_id,
                r.agent_name,
                r.model_name,
                f"[{st_color}]{r.status}[/{st_color}]",
                f"{r.total_score}",
                f"{r.passed_tests}/{r.total_tests}",
                f"{r.duration_seconds}s"
            )

        console.print(table)
    finally:
        db.close()


@cli_app.command("inspect")
def inspect_cmd(run_id: str = typer.Argument(..., help="Run ID to inspect")):
    """Inspect detailed trace, diff, and failure breakdown of a run."""
    init_db()
    db = SessionLocal()
    try:
        repo = RunRepository(db)
        r = repo.get_run(run_id)
        if not r:
            console.print(f"[red]Error: Run '{run_id}' not found.[/red]")
            return

        st_color = "green" if r.status == "SUCCEEDED" else "red"
        info = f"""[bold]Run ID:[/bold] {r.id}
[bold]Benchmark:[/bold] {r.benchmark_name} ({r.benchmark_id})
[bold]Agent / Model:[/bold] {r.agent_name} / {r.model_name} ({r.provider_name})
[bold]Status:[/bold] [{st_color}]{r.status}[/{st_color}]
[bold]Score:[/bold] {r.total_score}/100
[bold]Tests:[/bold] {r.passed_tests}/{r.total_tests} passed
[bold]Tool Calls:[/bold] {r.tool_calls_count}
[bold]Retries:[/bold] {r.retries_count}
[bold]Duration:[/bold] {r.duration_seconds}s
"""
        console.print(Panel(info, title=f"Run Inspection — {r.id}", border_style=st_color))

        if r.git_diff:
            console.print(Panel(r.git_diff, title="Git Diff", border_style="cyan"))

        if r.failure_analysis:
            fa = r.failure_analysis
            console.print(Panel(
                f"[bold red]Failure:[/bold red] {fa.primary_failure}\n[bold]Root Cause:[/bold] {fa.root_cause}\n[bold]Hints:[/bold] {fa.resolution_hints}",
                title="Failure Analysis",
                border_style="red"
            ))
    finally:
        db.close()


@cli_app.command("compare")
def compare_cmd(run_ids: List[str] = typer.Argument(..., help="List of run IDs to compare")):
    """Compare multiple benchmark runs side-by-side."""
    init_db()
    db = SessionLocal()
    try:
        repo = RunRepository(db)
        runs = [repo.get_run(rid) for rid in run_ids]
        runs = [r for r in runs if r is not None]

        if not runs:
            console.print("[red]No matching runs found.[/red]")
            return

        table = Table(title="Run Comparison Matrix", show_header=True, header_style="bold magenta")
        table.add_column("Metric", style="bold")
        for r in runs:
            table.add_column(f"{r.id}\n({r.agent_name})", justify="center")

        table.add_row("Status", *[r.status for r in runs])
        table.add_row("Score", *[f"{r.total_score}/100" for r in runs])
        table.add_row("Test Pass Rate", *[f"{r.test_pass_rate}%" for r in runs])
        table.add_row("Tests Passed", *[f"{r.passed_tests}/{r.total_tests}" for r in runs])
        table.add_row("Duration", *[f"{r.duration_seconds}s" for r in runs])
        table.add_row("Tool Calls", *[str(r.tool_calls_count) for r in runs])
        table.add_row("Retries", *[str(r.retries_count) for r in runs])
        table.add_row("Cost", *[f"${r.estimated_cost:.4f}" for r in runs])

        console.print(table)
    finally:
        db.close()


@cli_app.command("serve")
def serve_cmd(port: int = 8000, host: str = "127.0.0.1"):
    """Start the AgentBench FastAPI backend server."""
    import uvicorn
    console.print(f"[bold green]Starting AgentBench API server at http://{host}:{port}...[/bold green]")
    uvicorn.run("main:app", host=host, port=port, reload=False)


def main():
    cli_app()


if __name__ == "__main__":
    main()
