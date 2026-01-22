"""
Automated evaluation harness for the Market Sizing Estimator.
Run: python evals.py
"""
from __future__ import annotations
import os
from rich.console import Console
from rich.table import Table
from analyzer import generate_market_sizing
from schema import MarketInput, MarketSizingReport

console = Console()

TEST_CASES = [
    {
        "id": "test_01", "label": "SaaS PM Tool",
        "input": MarketInput(
            product_description="AI-powered OKR and product management platform for engineering teams",
            industry_vertical="SaaS / B2B Software",
            geographies=["United States", "United Kingdom"],
            company_stage="Startup (Post-PMF)",
            target_persona="Product Managers at Series A-C tech companies",
            pricing_model="SaaS / Subscription (per user/month)",
            avg_price=49.0, price_unit="user/month"
        )
    },
    {
        "id": "test_02", "label": "HealthTech App",
        "input": MarketInput(
            product_description="AI diagnostic intake agent for telehealth platforms",
            industry_vertical="HealthTech / Digital Health",
            geographies=["United States", "India"],
            company_stage="Startup (Pre-PMF)",
            target_persona="Patients and healthcare providers using telemedicine",
            pricing_model="Transactional / Usage-based",
            avg_price=12.0, price_unit="consultation"
        )
    },
    {
        "id": "test_03", "label": "FinTech Global",
        "input": MarketInput(
            product_description="Retail investment management app for emerging market investors",
            industry_vertical="FinTech / Payments",
            geographies=["India", "Brazil", "Indonesia"],
            company_stage="SMB",
            target_persona="Retail investors aged 25-45 in emerging markets",
            pricing_model="Marketplace (% of GMV)",
            avg_price=0.5, price_unit="% of AUM annually"
        )
    },
]


def check_hierarchy(report: MarketSizingReport) -> bool:
    """TAM > SAM > SOM at every level."""
    for sc in [report.reconciled_tam, report.reconciled_sam, report.reconciled_som]:
        if sc.low > sc.mid or sc.mid > sc.high:
            return False
    return (report.reconciled_tam.mid > report.reconciled_sam.mid >
            report.reconciled_som.mid > 0)


def check_three_methodologies(report: MarketSizingReport) -> bool:
    return len(report.methodology_results) == 3


def check_assumptions_sourced(report: MarketSizingReport) -> bool:
    for mr in report.methodology_results:
        if not mr.key_assumptions:
            return False
        if any(not a.source for a in mr.key_assumptions):
            return False
    return True


def check_five_year_projection(report: MarketSizingReport) -> bool:
    return (len(report.five_year_projection) == 5 and
            all(p.cagr_applied > 0 for p in report.five_year_projection))


def check_sensitivity(report: MarketSizingReport) -> bool:
    return (len(report.sensitivity_axes) >= 2 and
            all(len(a.som_impacts) == len(a.values) for a in report.sensitivity_axes))


def check_investor_narrative(report: MarketSizingReport) -> bool:
    sentences = report.investor_narrative.count(".")
    return sentences >= 2 and len(report.investor_narrative) > 100


def run_eval():
    api_key = os.environ.get("ANTHROPIC_API_KEY","")
    if not api_key:
        console.print("[red]Set ANTHROPIC_API_KEY environment variable.[/red]")
        return

    table = Table(title="Market Sizing Estimator — Eval Benchmark", show_lines=True)
    table.add_column("ID",        style="cyan",  width=10)
    table.add_column("Label",     style="white", width=18)
    table.add_column("Hierarchy", justify="center", width=10)
    table.add_column("3 Methods", justify="center", width=10)
    table.add_column("Sourced",   justify="center", width=9)
    table.add_column("5-Year",    justify="center", width=8)
    table.add_column("Sensitivity",justify="center",width=12)
    table.add_column("Narrative", justify="center", width=11)
    table.add_column("Status",    style="bold",  width=10)

    results = []
    for tc in TEST_CASES:
        console.print(f"Running [cyan]{tc['id']}[/cyan] — {tc['label']}...")
        try:
            report = generate_market_sizing(tc["input"], api_key)
            h  = check_hierarchy(report)
            m3 = check_three_methodologies(report)
            sr = check_assumptions_sourced(report)
            fy = check_five_year_projection(report)
            sv = check_sensitivity(report)
            nv = check_investor_narrative(report)
            ok = all([h, m3, sr, fy, sv, nv])
            results.append(ok)
            table.add_row(tc["id"], tc["label"],
                "✅" if h  else "❌","✅" if m3 else "❌",
                "✅" if sr else "❌","✅" if fy else "❌",
                "✅" if sv else "❌","✅" if nv else "❌",
                "[green]PASS[/green]" if ok else "[yellow]REVIEW[/yellow]")
        except Exception as e:
            console.print(f"  [red]Error:[/red] {e}")
            table.add_row(tc["id"],tc["label"],"❌","❌","❌","❌","❌","❌","[red]FAIL[/red]")
            results.append(False)

    console.print(table)
    rate = sum(results)/len(results)*100 if results else 0
    console.print(f"\n[bold]Pass Rate:[/bold] {rate:.1f}%")


if __name__ == "__main__":
    run_eval()
