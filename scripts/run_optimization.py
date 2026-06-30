from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data import ETF_UNIVERSE, load_prices, returns_from_prices
from src.metrics import performance_table
from src.optimization import cluster_summary, vol_target_strategy


ROOT = Path(__file__).resolve().parents[1]


def run() -> None:
    prices = load_prices(ETF_UNIVERSE)
    returns = returns_from_prices(prices).dropna(how="all")
    strategy, weights = vol_target_strategy(returns, target_vol=0.10, cost_bps=2.0)
    weights.to_csv(ROOT / "data" / "processed" / "vol_target_weights.csv")

    perf = performance_table(strategy.to_frame("vol_target_risk_parity"))
    clusters = cluster_summary(returns)
    perf.to_csv(ROOT / "data" / "processed" / "optimization_performance.csv")
    clusters.to_csv(ROOT / "data" / "processed" / "cluster_segmentation.csv")

    latest_weights = weights.tail(1).T
    latest_weights.columns = ["latest_weight"]
    latest_weights = latest_weights[latest_weights["latest_weight"].abs() > 0.001].sort_values("latest_weight", ascending=False)

    report = [
        "# Optimization & Segmentation",
        "",
        "Objective: allocate across ETF clusters using inverse-vol risk parity, volatility targeting and simple turnover costs.",
        "",
        "## Strategy performance",
        "",
        perf.to_markdown(floatfmt=".4f"),
        "",
        "## Latest non-zero weights",
        "",
        latest_weights.head(20).to_markdown(floatfmt=".4f"),
        "",
        "## Cluster segmentation",
        "",
        clusters.to_markdown(floatfmt=".4f"),
        "",
        "## Interview defense",
        "",
        "The project shows portfolio construction, constraints, transaction-cost awareness and segmentation. For Euronext, it maps naturally to ETF baskets, liquidity clusters and client/product analytics.",
    ]
    (ROOT / "reports" / "optimization_segmentation_report.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    run()

