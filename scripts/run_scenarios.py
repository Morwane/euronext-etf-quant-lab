from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data import ETF_UNIVERSE, load_prices, returns_from_prices
from src.metrics import turnover
from src.optimization import vol_target_strategy
from src.simulation import (
    block_bootstrap_paths,
    cost_sensitivity,
    distribution_summary,
    fee_revenue_sensitivity,
    parametric_monte_carlo_paths,
    regime_labels,
    regime_performance,
    scenario_table,
    terminal_distribution,
)


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "reports" / "figures" / "project2"


def _style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "white",
            "axes.facecolor": "white",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": True,
            "grid.alpha": 0.24,
            "font.size": 10.5,
            "axes.titleweight": "bold",
        }
    )


def _plot_terminal_distribution(mc_terminal: pd.Series, bootstrap_terminal: pd.Series) -> None:
    fig, ax = plt.subplots(figsize=(9, 5.4))
    ax.hist(mc_terminal, bins=45, alpha=0.55, label="Parametric Monte Carlo", color="#457b9d")
    ax.hist(bootstrap_terminal, bins=45, alpha=0.55, label="Block bootstrap", color="#e76f51")
    ax.axvline(mc_terminal.quantile(0.05), color="#457b9d", linestyle="--", linewidth=1.4)
    ax.axvline(bootstrap_terminal.quantile(0.05), color="#e76f51", linestyle="--", linewidth=1.4)
    ax.set_title("One-year simulated portfolio outcomes")
    ax.set_xlabel("One-year return")
    ax.set_ylabel("Number of paths")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(FIG_DIR / "terminal_distribution.png", dpi=180)
    plt.close(fig)


def _plot_scenarios(scenarios: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    sorted_s = scenarios.sort_values("sharpe")
    labels = [x.replace("_", " ").title() for x in sorted_s.index]
    axes[0].barh(labels, sorted_s["sharpe"], color="#457b9d")
    axes[0].axvline(0, color="#111111", linewidth=0.8)
    axes[0].set_title("Scenario Sharpe")
    axes[0].set_xlabel("Sharpe")
    axes[1].barh(labels, sorted_s["max_drawdown"], color="#e76f51")
    axes[1].axvline(0, color="#111111", linewidth=0.8)
    axes[1].set_title("Scenario max drawdown")
    axes[1].set_xlabel("Max drawdown")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "scenario_stress_summary.png", dpi=180)
    plt.close(fig)


def _plot_cost_sensitivity(costs: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(costs["cost_bps"], costs["sharpe"], marker="o", color="#2a9d8f", linewidth=2)
    ax.set_title("Transaction-cost sensitivity")
    ax.set_xlabel("Cost per turnover unit (bps)")
    ax.set_ylabel("Sharpe")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "cost_sensitivity.png", dpi=180)
    plt.close(fig)


def _plot_revenue_heatmap(revenue: pd.DataFrame) -> None:
    pivot = revenue.pivot_table(index="scenario", columns="fee_bps", values="total_revenue_proxy_eur")
    display_index = [x.replace("_", " ").title() for x in pivot.index]
    fig, ax = plt.subplots(figsize=(9.2, 5.2))
    image = ax.imshow(pivot.values / 1_000_000.0, aspect="auto", cmap="Blues")
    ax.set_title("Fee / revenue sensitivity proxy")
    ax.set_xlabel("Fee level (bps)")
    ax.set_ylabel("Market scenario")
    ax.set_xticks(range(len(pivot.columns)), [f"{x:.0f}" for x in pivot.columns])
    ax.set_yticks(range(len(pivot.index)), display_index)
    for i in range(pivot.shape[0]):
        for j in range(pivot.shape[1]):
            ax.text(j, i, f"{pivot.iloc[i, j] / 1_000_000:.2f}m", ha="center", va="center", fontsize=9)
    fig.colorbar(image, ax=ax, label="EUR millions")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "fee_revenue_heatmap.png", dpi=180)
    plt.close(fig)


def run() -> None:
    (ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    _style()

    prices = load_prices(ETF_UNIVERSE)
    returns = returns_from_prices(prices).dropna(how="all")
    gross_strategy, weights = vol_target_strategy(returns, target_vol=0.10, cost_bps=0.0)
    daily_turnover = turnover(weights).reindex(gross_strategy.index).fillna(0.0)
    net_strategy, _ = vol_target_strategy(returns, target_vol=0.10, cost_bps=2.0)
    net_strategy = net_strategy.reindex(gross_strategy.index).dropna()

    scenarios = scenario_table(returns, net_strategy)
    labels = regime_labels(returns["SPY"] if "SPY" in returns.columns else returns.mean(axis=1))
    regimes = regime_performance(net_strategy, labels)
    costs = cost_sensitivity(gross_strategy, daily_turnover)

    mc_paths = parametric_monte_carlo_paths(net_strategy, horizon_days=252, n_paths=2_000)
    bootstrap_paths = block_bootstrap_paths(net_strategy, horizon_days=252, n_paths=2_000)
    mc_terminal = terminal_distribution(mc_paths)
    bootstrap_terminal = terminal_distribution(bootstrap_paths)
    distribution = pd.DataFrame(
        [
            {**{"method": "parametric_monte_carlo"}, **distribution_summary(mc_terminal, "one_year")},
            {**{"method": "block_bootstrap"}, **distribution_summary(bootstrap_terminal, "one_year")},
        ]
    )

    revenue = fee_revenue_sensitivity()

    scenarios.to_csv(ROOT / "data" / "processed" / "scenario_stress_tests.csv")
    regimes.to_csv(ROOT / "data" / "processed" / "regime_performance.csv")
    costs.to_csv(ROOT / "data" / "processed" / "cost_sensitivity.csv", index=False)
    distribution.to_csv(ROOT / "data" / "processed" / "simulation_distribution_summary.csv", index=False)
    revenue.to_csv(ROOT / "data" / "processed" / "fee_revenue_sensitivity.csv", index=False)

    _plot_terminal_distribution(mc_terminal, bootstrap_terminal)
    _plot_scenarios(scenarios)
    _plot_cost_sensitivity(costs)
    _plot_revenue_heatmap(revenue)

    report = [
        "# Simulation & Scenario Models",
        "",
        "Objective: stress-test ETF portfolio outcomes using Monte Carlo simulation, block-bootstrap, transaction-cost sensitivity and regime scenarios.",
        "",
        "This is a scenario-analysis project, not a trading-alpha claim. It asks: how robust are outcomes if costs rise, volatility regimes change, or fee/revenue assumptions move?",
        "",
        "## Simulated one-year outcome distribution",
        "",
        distribution.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Portfolio scenario stress tests",
        "",
        scenarios.to_markdown(floatfmt=".4f"),
        "",
        "## Regime performance",
        "",
        regimes.to_markdown(floatfmt=".4f"),
        "",
        "## Cost sensitivity",
        "",
        costs.to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Fee / revenue sensitivity proxy",
        "",
        revenue.head(12).to_markdown(index=False, floatfmt=".2f"),
        "",
        "## Figures",
        "",
        "- `reports/figures/project2/terminal_distribution.png`",
        "- `reports/figures/project2/scenario_stress_summary.png`",
        "- `reports/figures/project2/cost_sensitivity.png`",
        "- `reports/figures/project2/fee_revenue_heatmap.png`",
        "",
        "## Interview defense",
        "",
        "This supports the CV line because it combines Monte Carlo, block-bootstrap, transaction-cost stress, regime analysis and a simple fee/revenue sensitivity model. The revenue block is a proxy model, not a claim about Euronext's exact fee schedule.",
    ]
    report_text = "\n".join(report)
    (ROOT / "reports" / "scenario_models_report.md").write_text(report_text, encoding="utf-8")
    (ROOT / "reports" / "project2_simulation_scenario_models.md").write_text(report_text, encoding="utf-8")


if __name__ == "__main__":
    run()
