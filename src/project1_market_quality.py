from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .data import DEFAULT_RAW_DIR, load_prices
from .metrics import annualized_vol, beta_to_benchmark, max_drawdown, rolling_tracking_error


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BENCHMARK_MAP = PROJECT_ROOT / "config" / "project1_benchmarks.csv"
DEFAULT_BENCHMARK_HISTORY_DIR = PROJECT_ROOT / "data" / "raw_lseg_project1_benchmarks"


def load_project1_folder(folder: Path) -> dict[str, pd.DataFrame]:
    panels = {}
    for path in sorted(folder.glob("*.csv")):
        if path.name == "lseg_pull_log.csv":
            continue
        df = pd.read_csv(path, parse_dates=["Date"]).set_index("Date").sort_index()
        panels[path.stem] = df
    return panels


def load_benchmark_map(path: Path = DEFAULT_BENCHMARK_MAP) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame(columns=["etf", "benchmark", "benchmark_name", "benchmark_quality"])
    return pd.read_csv(path)


def _benchmark_lookup(benchmark_map: pd.DataFrame) -> dict[str, dict[str, str]]:
    if benchmark_map.empty:
        return {}
    return benchmark_map.set_index("etf").fillna("").to_dict(orient="index")


def _load_external_benchmarks(symbols: set[str]) -> pd.DataFrame:
    if not symbols:
        return pd.DataFrame()
    local_series = {}
    missing = set()
    for symbol in symbols:
        path = DEFAULT_BENCHMARK_HISTORY_DIR / f"{symbol}.csv"
        if path.exists():
            df = pd.read_csv(path, parse_dates=["Date"]).set_index("Date").sort_index()
            df = df[~df.index.duplicated(keep="last")]
            col = "price" if "price" in df.columns else df.select_dtypes(include="number").columns[0]
            local_series[symbol] = pd.to_numeric(df[col], errors="coerce")
        else:
            missing.add(symbol)
    frames = []
    if local_series:
        frames.append(pd.concat(local_series, axis=1))
    try:
        if missing:
            frames.append(load_prices(sorted(missing), DEFAULT_RAW_DIR))
    except Exception:
        pass
    return pd.concat(frames, axis=1).sort_index() if frames else pd.DataFrame()


def compute_project1_metrics(
    panels: dict[str, pd.DataFrame],
    benchmark: str = "SPY",
    benchmark_map_path: Path = DEFAULT_BENCHMARK_MAP,
) -> pd.DataFrame:
    prices = {}
    for ric, df in panels.items():
        if "price" in df.columns:
            prices[ric] = pd.to_numeric(df["price"], errors="coerce")
        elif "TRDPRC_1" in df.columns:
            prices[ric] = pd.to_numeric(df["TRDPRC_1"], errors="coerce")
    price_df = pd.concat(prices, axis=1).sort_index()
    benchmark_map = load_benchmark_map(benchmark_map_path)
    lookup = _benchmark_lookup(benchmark_map)
    mapped_benchmarks = {row.get("benchmark", "") for row in lookup.values()}
    missing_benchmarks = {b for b in mapped_benchmarks if b and b not in price_df.columns}
    external_benchmarks = _load_external_benchmarks(missing_benchmarks)
    if not external_benchmarks.empty:
        price_df = pd.concat([price_df, external_benchmarks], axis=1).sort_index()
    returns = price_df.pct_change(fill_method=None)

    rows = []
    for ric, df in panels.items():
        if ric not in returns:
            continue
        bench_info = lookup.get(
            ric,
            {
                "benchmark": benchmark,
                "benchmark_name": f"default {benchmark}",
                "benchmark_quality": "default_proxy",
            },
        )
        benchmark_symbol = bench_info.get("benchmark") or benchmark
        if benchmark_symbol not in returns.columns:
            benchmark_symbol = benchmark if benchmark in returns.columns else ric
            benchmark_quality = "fallback_benchmark_missing"
        else:
            benchmark_quality = bench_info.get("benchmark_quality", "")
        benchmark_returns = returns[benchmark_symbol]
        r = returns[ric].dropna()
        if len(r) < 60:
            continue
        spread_bps = np.nan
        premium_discount_bps = np.nan
        has_real_spread = False
        has_real_nav = False
        if {"bid", "ask"}.issubset(df.columns):
            mid = (df["bid"] + df["ask"]) / 2.0
            spread_series = ((df["ask"] - df["bid"]) / mid * 10_000.0).replace([np.inf, -np.inf], np.nan)
            spread_bps = spread_series.dropna().tail(20).median()
            has_real_spread = spread_series.notna().any()
        if {"price", "nav"}.issubset(df.columns):
            aligned_price_nav = df[["price", "nav"]].dropna()
            if not aligned_price_nav.empty:
                premium_series = (
                    (aligned_price_nav["price"] - aligned_price_nav["nav"])
                    / aligned_price_nav["nav"]
                    * 10_000.0
                ).replace([np.inf, -np.inf], np.nan)
                premium_discount_bps = premium_series.dropna().tail(20).median()
                has_real_nav = premium_series.notna().any()
        te_series = rolling_tracking_error(returns[ric], benchmark_returns, 63).dropna()
        te = te_series.iloc[-1] if not te_series.empty else np.nan
        rows.append(
            {
                "ric": ric,
                "latest_price": price_df[ric].dropna().iloc[-1],
                "quoted_spread_bps_20d_median": spread_bps,
                "premium_discount_bps_20d_median": premium_discount_bps,
                "benchmark": benchmark_symbol,
                "benchmark_name": bench_info.get("benchmark_name", ""),
                "benchmark_quality": benchmark_quality,
                "tracking_error_63d": te,
                "ann_vol_63d": annualized_vol(r.tail(63)),
                "beta_to_benchmark": beta_to_benchmark(returns[ric], benchmark_returns),
                "max_drawdown_1y": max_drawdown(r.tail(252)),
                "has_real_spread": bool(has_real_spread),
                "has_real_nav": bool(has_real_nav),
            }
        )
    out = pd.DataFrame(rows)
    if out.empty:
        return out
    score_parts = [
        out["tracking_error_63d"].rank(pct=True),
        out["ann_vol_63d"].rank(pct=True),
    ]
    spread = out["quoted_spread_bps_20d_median"]
    if spread.notna().any():
        score_parts.append(spread.rank(pct=True))
    premium = out["premium_discount_bps_20d_median"].abs()
    if premium.notna().any():
        score_parts.append(premium.rank(pct=True))
    out["quality_risk_score"] = pd.concat(score_parts, axis=1).mean(axis=1)
    return out.sort_values("quality_risk_score", ascending=False)
