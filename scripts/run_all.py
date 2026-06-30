from __future__ import annotations

from pathlib import Path

import pandas as pd

from run_market_quality import run as run_market_quality
from run_optimization import run as run_optimization
from run_research import run as run_research
from run_scenarios import run as run_scenarios


ROOT = Path(__file__).resolve().parents[1]


def run() -> None:
    for folder in [ROOT / "reports", ROOT / "data" / "processed"]:
        folder.mkdir(parents=True, exist_ok=True)
    run_market_quality()
    run_optimization()
    run_scenarios()
    run_research()
    market = pd.read_csv(ROOT / "data" / "processed" / "market_quality_snapshot.csv")
    opt = pd.read_csv(ROOT / "data" / "processed" / "optimization_performance.csv")
    research = pd.read_csv(ROOT / "data" / "processed" / "quant_research_summary.csv")
    scenarios = pd.read_csv(ROOT / "data" / "processed" / "scenario_stress_tests.csv")
    dashboard = pd.DataFrame(
        [
            {
                "project": "ETF Market-Quality & Fair-Value Analytics",
                "status": "implemented",
                "main_output": "market_quality_snapshot.csv",
                "headline": f"{len(market)} ETFs ranked; highest stress: {market.iloc[0]['symbol']}",
            },
            {
                "project": "Simulation & Scenario Models",
                "status": "implemented",
                "main_output": "scenario_stress_tests.csv",
                "headline": f"base Sharpe {scenarios.loc[scenarios['scenario'].eq('base_history'), 'sharpe'].iloc[0]:.2f}; stress scenarios included",
            },
            {
                "project": "Optimization & Segmentation",
                "status": "implemented",
                "main_output": "optimization_performance.csv",
                "headline": f"vol-target allocator Sharpe {opt.iloc[0]['sharpe']:.2f}, max DD {opt.iloc[0]['max_drawdown']:.1%}",
            },
            {
                "project": "Market-Data Analytics & Dashboards",
                "status": "implemented",
                "main_output": "dashboard_snapshot.csv",
                "headline": "single CSV snapshot plus markdown reports",
            },
            {
                "project": "Quantitative Market Research",
                "status": "implemented; signal rejected as weak alpha",
                "main_output": "quant_research_summary.csv",
                "headline": f"relative-value Sharpe {research.loc[research['name'].eq('strategy'), 'sharpe'].iloc[0]:.2f} vs benchmark {research.loc[research['name'].eq('benchmark'), 'sharpe'].iloc[0]:.2f}",
            },
            {
                "project": "Quantitative Toolkit",
                "status": "implemented",
                "main_output": "src/toolkit.py and tests/",
                "headline": "Black-Scholes, CRR and walk-forward utilities",
            },
        ]
    )
    dashboard.to_csv(ROOT / "data" / "processed" / "dashboard_snapshot.csv", index=False)
    defense = [
        "# Interview Defense Sheet",
        "",
        "## What this GitHub project proves",
        "",
        "- I can turn ETF market data into market-quality metrics: volatility, tracking error, liquidity proxies, beta and stress ranking.",
        "- I understand that real ETF quality also needs bid/ask and NAV/iNAV; the code supports these fields and documents when the local cache is price-only.",
        "- I can run scenario analysis, cost sensitivity and block-bootstrap simulations.",
        "- I can build constrained portfolio allocation with volatility targeting and transaction costs.",
        "- I can compare a research signal against a benchmark and avoid look-ahead by using shifted weights/signals.",
        "- I can package the work as a reproducible research repo with tests and generated reports.",
        "",
        "## Best 20-second interview pitch",
        "",
        "I built an ETF quant analytics lab using LSEG data. It computes ETF market-quality metrics, tracks relative value and dispersion signals, stress-tests scenarios, and runs a constrained vol-targeted allocation. I also made the data limitations explicit: the current cache is daily price-only, but the market-quality module is designed to consume bid/ask and NAV fields when available.",
        "",
        "## Honest limitation",
        "",
        "This project is an analytics and research framework, not proof that I discovered a proprietary alpha. Its strength for Euronext is market structure, ETF analytics, data handling and rigorous validation.",
    ]
    (ROOT / "reports" / "interview_defense_sheet.md").write_text("\n".join(defense), encoding="utf-8")


if __name__ == "__main__":
    run()
