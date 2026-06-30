from __future__ import annotations

import numpy as np
import pandas as pd

from .metrics import max_drawdown, sharpe, zscore


def sector_dispersion_signal(returns: pd.DataFrame, sector_cols: list[str]) -> pd.DataFrame:
    sector_returns = returns[sector_cols].dropna(how="all")
    dispersion = sector_returns.std(axis=1)
    signal = zscore(dispersion, 252)
    return pd.DataFrame({"sector_dispersion": dispersion, "dispersion_z": signal})


def relative_value_zscores(prices: pd.DataFrame, benchmark: str = "SPY", window: int = 252) -> pd.DataFrame:
    log_prices = np.log(prices.dropna(how="all"))
    rel = log_prices.sub(log_prices[benchmark], axis=0)
    signals = rel.apply(lambda s: zscore(s, window))
    return signals.drop(columns=[benchmark], errors="ignore")


def simple_mean_reversion_backtest(
    signals: pd.DataFrame,
    returns: pd.DataFrame,
    entry_z: float = 1.5,
    cost_bps: float = 2.0,
) -> pd.Series:
    raw = -np.sign(signals).where(signals.abs() > entry_z, 0.0)
    weights = raw.div(raw.abs().sum(axis=1).replace(0, np.nan), axis=0).fillna(0.0)
    strategy = (weights.shift(1) * returns[weights.columns]).sum(axis=1)
    costs = weights.diff().abs().sum(axis=1).fillna(0.0) * cost_bps / 10_000.0
    return (strategy - costs).dropna()


def research_summary(strategy: pd.Series, benchmark: pd.Series) -> pd.DataFrame:
    aligned = pd.concat([strategy.rename("strategy"), benchmark.rename("benchmark")], axis=1).dropna()
    rows = []
    for col in aligned.columns:
        r = aligned[col]
        rows.append(
            {
                "name": col,
                "ann_return": r.mean() * 252,
                "ann_vol": r.std(ddof=0) * np.sqrt(252),
                "sharpe": sharpe(r),
                "max_drawdown": max_drawdown(r),
                "hit_rate": (r > 0).mean(),
            }
        )
    return pd.DataFrame(rows).set_index("name")

