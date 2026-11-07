"""Rich Terminal CLI for SiteSense RFI Agent.
Perfect for live demo recordings, hackathon presentations, and instant terminal checks.
"""
import sys
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt

from src.agent import SiteSenseRFIAgent
from src.models import WorkerQueryRequest, HazardLevel

console = Console()


def print_banner():
    banner = Text(
        r"""
  ____  _ _        ____                        ____  _____ ___ 
 / ___|(_) |_ ___ / ___|  ___ _ __  ___  ___  |  _ \|  ___|_ _|
 \___ \| | __/ _ \\___ \ / _ \ '_ \/ __|/ _ \ | |_) | |_   | | 
  ___) | | ||  __/ ___) |  __/ | | \__ \  __/ |  _ <|  _|  | | 
 |____/|_|\__\___||____/ \___|_| |_|___/\___| |_| \_\_|   |___|
        Zero-Rework Construction Agent • Powered by Vectorize Hindsight
        """,
        style="bold cyan"
    )
    console.print(banner)


def show_hazard_panel(resp):
    if resp.status == HazardLevel.CRITICAL_STOP_WORK:
        border_style = "bold red"
        title = "🚨 [CRITICAL HAZARD - STOP WORK IMMEDIATELY]"
    elif resp.status == HazardLevel.CAUTION_VERIFY:
        border_style = "bold yellow"
        title = "⚠️ [CAUTION - VERIFICATION & RESTRICTIONS REQUIRED]"
    else:
        border_style = "bold green"
        title = "✅ [SAFE TO PROCEED - STANDARD SPECIFICATIONS]"

    content = f"[bold]{resp.verdict}[/bold]\n\n"
    content += f"[bold underline]Hazard Details:[/bold underline]\n{resp.hazard_details}\n\n"
    
    if resp.recalled_rfis:
        content += "[bold underline]Recalled Hindsight RFIs:[/bold underline]\n"
        for r in resp.recalled_rfis:
            content += f"  • [yellow]{r['id']}[/yellow]: {r['title']} ({r['date']}) - Risk: [bold red]${r['risk_cost']:,.0f}[/bold red]\n"
        content += "\n"

    if resp.critical_directives:
        content += "[bold underline]Active Field Directives:[/bold underline]\n"
        for d in resp.critical_directives:
            content += f"  ⛔ {d}\n"
        content += "\n"

    content += f"[bold underline]Recommended Action / Safe Alternative:[/bold underline]\n[green]{resp.recommended_alternative}[/green]\n\n"
    content += f"[bold]Rework Cost Prevented:[/bold] [bold green]${resp.rework_cost_prevented:,.2f}[/bold green]"

    console.print(Panel(content, title=title, border_style=border_style, padding=(1, 2)))


def run_demo():
    print_banner()
    agent = SiteSenseRFIAgent()

    console.print("\n[bold yellow]═══ STEP 1: RETAINING HISTORICAL CONSTRUCTION RFIS IN HINDSIGHT ═══[/bold yellow]")
    with console.status("[cyan]Syncing memory bank 'omega_tower_construction_rfis' with Hindsight..."):
        time.sleep(1)
    
    table = Table(title="Hindsight Memory Bank Ingestion", show_lines=True)
    table.add_column("RFI ID", style="bold cyan")
    table.add_column("Date", style="magenta")
    table.add_column("Location", style="yellow")
    table.add_column("Discipline", style="blue")
    table.add_column("Hazard", style="red")
    table.add_column("Rework Risk", style="green")

    for rfi in agent.get_all_rfis():
        table.add_row(
            rfi.id,
            rfi.date_issued,
            f"{rfi.level}, {rfi.grid_location}",
            rfi.discipline.value,
            rfi.hazard_level.value,
            f"${rfi.rework_cost_risk:,.0f}"
        )
    console.print(table)

    console.print("\n[bold yellow]═══ STEP 2: SIMULATING CRITICAL FIELD SCENARIO ═══[/bold yellow]")
    worker_q = "Can I core-drill a 4-inch hole at Level 3, Grid B-4 to run a plumbing line?"
    console.print(f"[bold white]Worker asks on site radio:[/bold white] \"[italic]{worker_q}[/italic]\"\n")

    console.print("[dim]Querying Hindsight Memory Bank (temporal graph + entity recall)...[/dim]")
    time.sleep(1)

    req = WorkerQueryRequest(question=worker_q, level="Level 3", grid_location="Grid B-4", action_type="Core Drilling")
    resp = agent.evaluate_worker_query(req)

    show_hazard_panel(resp)

    console.print("\n[bold yellow]═══ STEP 3: STATELESS LLM VS HINDSIGHT MEMORY COMPARISON ═══[/bold yellow]")
    benchmarks = agent.get_benchmarks()
    b = benchmarks[0]

    comp_table = Table(title="Catastrophic Rework Prevention Benchmark", show_lines=True)
    comp_table.add_column("System", style="bold")
    comp_table.add_column("Advice Provided to Site Worker", style="white")
    comp_table.add_column("Real-World Consequence", style="bold red")

    comp_table.add_row(
        "[red]Stateless LLM / Blueprint RAG\n(Without Hindsight)[/red]",
        b.stateless_behavior["response"],
        b.stateless_behavior["disaster_outcome"]
    )
    comp_table.add_row(
        "[green]SiteSense Agent\n(With Hindsight Memory)[/green]",
        b.hindsight_behavior["response"],
        f"[green]{b.hindsight_behavior['disaster_outcome']}[/green]\n\n[bold green]Rework Saved: ${b.rework_cost_prevented:,.0f}[/bold green]"
    )
    console.print(comp_table)
    console.print(Panel(
        f"[bold green]SUMMARY:[/bold green] By recalling temporal change directives, Hindsight transformed a potential "
        f"[bold red]${b.rework_cost_prevented:,.0f} disaster[/bold red] into a zero-rework safe operation.",
        border_style="green"
    ))


def run_query(query_text: str):
    print_banner()
    agent = SiteSenseRFIAgent()
    req = WorkerQueryRequest(question=query_text)
    resp = agent.evaluate_worker_query(req)
    show_hazard_panel(resp)


def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "demo":
            run_demo()
            return
        elif cmd == "compare":
            agent = SiteSenseRFIAgent()
            for b in agent.get_benchmarks():
                console.print(f"\n[bold cyan]Scenario: {b.scenario_title}[/bold cyan]")
                console.print(f"[yellow]Worker Query:[/yellow] {b.worker_question}")
                console.print(f"[red]Without Memory:[/red] {b.stateless_behavior['disaster_outcome']}")
                console.print(f"[green]With Hindsight:[/green] {b.hindsight_behavior['disaster_outcome']}")
                console.print(f"[bold green]Cost Saved: ${b.rework_cost_prevented:,.0f}[/bold green]\n" + "-"*60)
            return
        elif cmd == "rfis":
            agent = SiteSenseRFIAgent()
            table = Table(title="Currently Retained Construction RFIs")
            table.add_column("ID", style="cyan")
            table.add_column("Date", style="magenta")
            table.add_column("Title", style="white")
            table.add_column("Location", style="yellow")
            table.add_column("Hazard", style="red")
            for r in agent.get_all_rfis():
                table.add_row(r.id, r.date_issued, r.title, f"{r.level}, {r.grid_location}", r.hazard_level.value)
            console.print(table)
            return
        elif cmd == "query":
            q = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else Prompt.ask("Enter worker question")
            run_query(q)
            return

    # Default: Run demo
    run_demo()


if __name__ == "__main__":
    main()
