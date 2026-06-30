from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data import DEFAULT_RAW_DIR, ETF_UNIVERSE, load_prices
from src.market_quality import market_quality_snapshot
from src.project1_market_quality import DEFAULT_BENCHMARK_MAP, compute_project1_metrics, load_project1_folder


ROOT = Path(__file__).resolve().parents[1]


def run_from_lseg_folder(folder: Path, benchmark_map: Path):
    panels = load_project1_folder(folder)
    return compute_project1_metrics(panels, benchmark_map_path=benchmark_map)


def run_from_daily_cache():
    prices = load_prices(ETF_UNIVERSE, DEFAULT_RAW_DIR)
    return market_quality_snapshot(prices)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Project 1 ETF market-quality analytics.")
    parser.add_argument("--lseg-folder", default=str(ROOT / "data" / "raw_lseg_project1"))
    parser.add_argument("--use-daily-cache", action="store_true")
    parser.add_argument("--benchmark-map", default=str(DEFAULT_BENCHMARK_MAP))
    args = parser.parse_args()

    folder = Path(args.lseg_folder)
    if folder.exists() and list(folder.glob("*.csv")) and not args.use_daily_cache:
        result = run_from_lseg_folder(folder, Path(args.benchmark_map))
        source = "live/pulled LSEG market-quality fields"
    else:
        result = run_from_daily_cache()
        source = "existing daily LSEG cache; price-only fallback"

    out_csv = ROOT / "data" / "processed" / "project1_market_quality.csv"
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(out_csv, index=False)

    report = [
        "# Project 1 - ETF Market-Quality & Fair-Value Analytics",
        "",
        f"Data source used: {source}.",
        "",
        "## What the project measures",
        "",
        "- bid-ask spread when BID/ASK are available",
        "- premium/discount when NAV is available",
        "- tracking error versus each ETF benchmark/proxy from config/project1_benchmarks.csv",
        "- realized volatility",
        "- beta to benchmark",
        "- drawdown and market-quality stress ranking",
        "",
        "## Latest result",
        "",
        result.head(12).to_markdown(index=False, floatfmt=".4f") if not result.empty else "No result generated.",
        "",
        "## How to explain it",
        "",
        "An ETF should trade close to its fair value, with tight spreads, stable tracking versus its own benchmark and enough liquidity. This project creates a monitoring table that ranks ETFs where market quality is deteriorating.",
        "",
        "## What LSEG adds",
        "",
        "Daily prices are enough for tracking error, volatility and drawdown. LSEG BID/ASK/NAV fields are needed for the full market-microstructure version: true quoted spread and true premium/discount to NAV.",
    ]
    report_path = ROOT / "reports" / "project1_market_quality.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report), encoding="utf-8")
    print(f"Saved: {out_csv}")
    print(f"Saved: {report_path}")
    print(result.head(12).to_string(index=False))


if __name__ == "__main__":
    main()
