from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data import ETF_UNIVERSE, BENCHMARKS, load_prices, returns_from_prices
from src.research import relative_value_zscores, research_summary, sector_dispersion_signal, simple_mean_reversion_backtest


ROOT = Path(__file__).resolve().parents[1]
SECTORS = ["XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLU", "XLB", "XLC"]


def run() -> None:
    prices = load_prices(ETF_UNIVERSE + BENCHMARKS)
    returns = returns_from_prices(prices).dropna(how="all")
    etf_prices = prices[[c for c in ETF_UNIVERSE if c in prices.columns]].dropna(how="all")
    etf_returns = returns[[c for c in ETF_UNIVERSE if c in returns.columns]].dropna(how="all")

    rv = relative_value_zscores(etf_prices, "SPY")
    strategy = simple_mean_reversion_backtest(rv, etf_returns, entry_z=1.5, cost_bps=2.0)
    benchmark = returns["SPY"].reindex(strategy.index)
    summary = research_summary(strategy, benchmark)
    dispersion = sector_dispersion_signal(returns, [c for c in SECTORS if c in returns.columns])

    rv.tail(250).to_csv(ROOT / "data" / "processed" / "relative_value_zscores.csv")
    dispersion.to_csv(ROOT / "data" / "processed" / "sector_dispersion.csv")
    summary.to_csv(ROOT / "data" / "processed" / "quant_research_summary.csv")

    context_cols = [c for c in ["_VIX", "_VIX3M", "_COR1M", "_COR3M", "_DSPX"] if c in prices.columns]
    context = prices[context_cols].tail(5) if context_cols else prices[["SPY"]].tail(5)

    report = [
        "# Quantitative Market Research",
        "",
        "Objective: test relative-value, volatility and correlation research ideas without look-ahead in a daily LSEG ETF universe.",
        "",
        "## Relative-value mean-reversion test",
        "",
        summary.to_markdown(floatfmt=".4f"),
        "",
        "## Latest cross-asset / volatility context",
        "",
        context.to_markdown(floatfmt=".4f"),
        "",
        "## Latest sector dispersion",
        "",
        dispersion.tail(5).to_markdown(floatfmt=".4f"),
        "",
        "## Interpretation",
        "",
        "This is research infrastructure, not a production trading claim. It includes transaction costs and a benchmark comparison. A signal is CV-useful when it demonstrates rigorous process, even if it is not an institutional alpha.",
    ]
    (ROOT / "reports" / "quant_market_research_report.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    run()

