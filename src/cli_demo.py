"""Rich Terminal Demonstration of WardSense ICU + Vectorize Hindsight retain/recall."""
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.agent import wardsense_agent
from src.database import init_db
from src.hindsight_memory import memory_engine

console = Console()


def run_terminal_demo() -> None:
    init_db()
    console.print(
        Panel.fit(
            "[bold cyan]WARDSENSE ICU • CLINICAL SHIFT-HANDOFF & CONTINUITY ENGINE[/bold cyan]\n"
            "[dim]Powered by Vectorize Hindsight Cloud (client.retain / client.recall) & Groq LPU[/dim]",
            border_style="cyan",
        )
    )

    # Step 1: Nurse retains a critical shift observation
    console.print("\n[bold emerald]Step 1: Outgoing Night Nurse Logs Bedside Event -> client.retain()[/bold emerald]")
    retained = memory_engine.retain_shift_observation(
        patient_id="ICU-BED-04",
        shift_number=21,
        author_name="Sister Priya Nair, RN",
        author_role="nurse",
        category="Adverse Drug Reaction",
        severity="CRITICAL",
        content=(
            "Night Shift #21 Note: Patient had 8-beat non-sustained VTach run when Serum K+ dipped to 3.3 mEq/L. "
            "Strict hold on bolus loop diuretics (Furosemide); use continuous Bumetanide only after K+ >= 4.2."
        ),
    )
    console.print(
        f"  [green]✓ client.retain() succeeded[/green] | Memory ID: [bold]{retained['memory_id']}[/bold] "
        f"| Bank: [cyan]{retained['bank_id']}[/cyan] | Latency: [yellow]{retained['latency_ms']}ms[/yellow]"
    )

    # Step 2: Doctor Order Verification (Stateless AI vs. Hindsight Memory)
    console.print(
        "\n[bold sky_blue1]Step 2: Incoming Morning Doctor Verifies Order -> client.recall()[/bold sky_blue1]"
    )
    order = "Administer IV Furosemide (Lasix) 80mg stat bolus for acute pulmonary congestion."
    result = wardsense_agent.verify_clinical_order(
        patient_id="ICU-BED-04", proposed_order=order
    )

    table = Table(title="Before vs. After: ICU Order Safety Verification (ICU-BED-04)", show_lines=True)
    table.add_column("Dimension", style="bold white", width=20)
    table.add_column("Without Memory (Stateless EHR AI)", style="red", width=42)
    table.add_column("With Vectorize Hindsight Memory", style="green", width=48)

    table.add_row(
        "Verdict",
        result["stateless_ai"]["verdict"],
        result["hindsight_agent"]["verdict"],
    )
    table.add_row(
        "Clinical Reasoning",
        result["stateless_ai"]["reasoning"],
        result["hindsight_agent"]["clinical_why"],
    )
    table.add_row(
        "Outcome / Action",
        result["stateless_ai"]["risk_missed"],
        result["hindsight_agent"]["safe_alternative"],
    )
    console.print(table)


if __name__ == "__main__":
    run_terminal_demo()
