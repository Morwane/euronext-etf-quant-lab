from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data import ETF_UNIVERSE, load_prices, returns_from_prices
from src.optimization import vol_target_strategy
from src.simulation import block_bootstrap_paths, fee_revenue_sensitivity, scenario_table


ROOT = Path(__file__).resolve().parents[1]


def run() -> None:
    prices = load_prices(ETF_UNIVERSE)
    returns = returns_from_prices(prices).dropna(how="all")
    strategy, _ = vol_target_strategy(returns, target_vol=0.10)
    scenarios = scenario_table(returns, strategy)
    scenarios.to_csv(ROOT / "data" / "processed" / "scenario_stress_tests.csv")

    paths = block_bootstrap_paths(strategy, horizon_days=252, n_paths=1000)
    terminal = (1.0 + paths).prod(axis=0) - 1.0
    bootstrap = {
        "p05_one_year_return": terminal.quantile(0.05),
        "p50_one_year_return": terminal.quantile(0.50),
        "p95_one_year_return": terminal.quantile(0.95),
    }
    revenue = fee_revenue_sensitivity()
    revenue.to_csv(ROOT / "data" / "processed" / "fee_revenue_sensitivity.csv", index=False)

    report = [
        "# Simulation & Scenario Models",
        "",
        "Objective: stress-test ETF portfolio outcomes using Monte Carlo/block-bootstrap and cost/scenario sensitivity.",
        "",
        "## Portfolio scenario results",
        "",
        scenarios.to_markdown(floatfmt=".4f"),
        "",
        "## Block-bootstrap one-year distribution",
        "",
        "\n".join(f"- {k}: {v:.2%}" for k, v in bootstrap.items()),
        "",
        "## Fee/revenue sensitivity",
        "",
        revenue.head(10).to_markdown(index=False, floatfmt=".2f"),
        "",
        "## Interview defense",
        "",
        "This connects to ETF strategy work because exchanges care about volume, fees, listing revenue and how market regimes affect economics. The model is deliberately simple but auditable.",
    ]
    (ROOT / "reports" / "scenario_models_report.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    run()

