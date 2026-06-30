from __future__ import annotations

import numpy as np
import pandas as pd

from .metrics import turnover


CLUSTERS = {
    "core_us": ["SPY", "DIA", "IWM"],
    "international": ["EFA", "EEM", "VGK", "EWG", "EWJ", "EWU", "EWZ", "FXI"],
    "sectors": ["XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLU", "XLB", "XLC"],
    "rates_credit": ["LQD", "HYG", "JNK", "AGG", "TIP"],
    "commodities": ["GLD", "SLV"],
}


def inverse_vol_weights(returns: pd.DataFrame, lookback: int = 63, max_weight: float = 0.20) -> pd.DataFrame:
    vol = returns.rolling(lookback).std(ddof=0) * np.sqrt(252)
    raw = 1.0 / vol.replace(0, np.nan)
    weights = raw.div(raw.sum(axis=1), axis=0).clip(upper=max_weight)
    weights = weights.div(weights.sum(axis=1), axis=0)
    return weights.fillna(0.0)


def vol_target_strategy(
    returns: pd.DataFrame,
    target_vol: float = 0.10,
    lookback: int = 63,
    max_leverage: float = 1.5,
    cost_bps: float = 2.0,
) -> tuple[pd.Series, pd.DataFrame]:
    weights = inverse_vol_weights(returns, lookback=lookback)
    gross_returns = (weights.shift(1) * returns).sum(axis=1)
    realized_vol = gross_returns.rolling(lookback).std(ddof=0) * np.sqrt(252)
    leverage = (target_vol / realized_vol).clip(upper=max_leverage).fillna(0.0)
    scaled_weights = weights.mul(leverage, axis=0)
    daily_turnover = turnover(scaled_weights)
    net_returns = (scaled_weights.shift(1) * returns).sum(axis=1) - daily_turnover * cost_bps / 10_000.0
    return net_returns.dropna(), scaled_weights


def cluster_summary(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for cluster, symbols in CLUSTERS.items():
        cols = [symbol for symbol in symbols if symbol in returns.columns]
        if not cols:
            continue
        sub = returns[cols].dropna(how="all")
        corr = sub.corr().where(~np.eye(len(cols), dtype=bool)).stack()
        rows.append(
            {
                "cluster": cluster,
                "members": ", ".join(cols),
                "n_members": len(cols),
                "median_ann_vol": sub.std(ddof=0).median() * np.sqrt(252),
                "avg_pairwise_corr": corr.mean() if not corr.empty else np.nan,
            }
        )
    return pd.DataFrame(rows).set_index("cluster")

