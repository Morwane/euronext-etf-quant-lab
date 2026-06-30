from __future__ import annotations

import numpy as np
import pandas as pd

from .metrics import max_drawdown, sharpe


def block_bootstrap_paths(
    returns: pd.Series,
    horizon_days: int = 252,
    n_paths: int = 2_000,
    block_size: int = 21,
    seed: int = 7,
) -> pd.DataFrame:
    clean = returns.dropna().to_numpy()
    if len(clean) < block_size:
        raise ValueError("Not enough observations for block bootstrap.")
    rng = np.random.default_rng(seed)
    starts = np.arange(0, len(clean) - block_size + 1)
    paths = np.empty((horizon_days, n_paths))
    for i in range(n_paths):
        sampled = []
        while len(sampled) < horizon_days:
            start = rng.choice(starts)
            sampled.extend(clean[start : start + block_size])
        paths[:, i] = sampled[:horizon_days]
    return pd.DataFrame(paths)


def scenario_table(returns: pd.DataFrame, portfolio_returns: pd.Series) -> pd.DataFrame:
    scenarios = {
        "base_history": portfolio_returns,
        "covid_style_left_tail": portfolio_returns - 0.015 * (returns.mean(axis=1) < returns.mean(axis=1).quantile(0.05)),
        "cost_plus_10bps_monthly": portfolio_returns - 0.0010 / 21.0,
        "high_vol_deleveraging": portfolio_returns.where(returns.std(axis=1).rolling(21).mean() < returns.std(axis=1).quantile(0.9), portfolio_returns * 0.5),
    }
    rows = []
    for name, r in scenarios.items():
        rows.append(
            {
                "scenario": name,
                "annualized_mean": r.dropna().mean() * 252,
                "annualized_vol": r.dropna().std(ddof=0) * np.sqrt(252),
                "sharpe": sharpe(r),
                "max_drawdown": max_drawdown(r),
            }
        )
    return pd.DataFrame(rows).set_index("scenario")


def fee_revenue_sensitivity(aum_eur: float = 250_000_000, fee_bps: float = 9.0) -> pd.DataFrame:
    rows = []
    for aum_shock in [-0.25, -0.10, 0.0, 0.10, 0.25]:
        for fee_shock in [-2.0, 0.0, 2.0]:
            shocked_aum = aum_eur * (1.0 + aum_shock)
            shocked_fee = max(fee_bps + fee_shock, 0.0)
            rows.append(
                {
                    "aum_shock": aum_shock,
                    "fee_bps": shocked_fee,
                    "annual_revenue_eur": shocked_aum * shocked_fee / 10_000.0,
                }
            )
    return pd.DataFrame(rows)

