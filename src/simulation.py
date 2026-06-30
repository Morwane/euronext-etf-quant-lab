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


def parametric_monte_carlo_paths(
    returns: pd.Series,
    horizon_days: int = 252,
    n_paths: int = 2_000,
    seed: int = 11,
) -> pd.DataFrame:
    clean = returns.dropna()
    if len(clean) < 60:
        raise ValueError("Not enough observations for Monte Carlo.")
    rng = np.random.default_rng(seed)
    paths = rng.normal(clean.mean(), clean.std(ddof=0), size=(horizon_days, n_paths))
    return pd.DataFrame(paths)


def terminal_distribution(paths: pd.DataFrame) -> pd.Series:
    return (1.0 + paths).prod(axis=0) - 1.0


def distribution_summary(terminal_returns: pd.Series, prefix: str) -> dict[str, float]:
    clean = terminal_returns.dropna()
    left_tail = clean[clean <= clean.quantile(0.05)]
    return {
        f"{prefix}_p01": clean.quantile(0.01),
        f"{prefix}_p05": clean.quantile(0.05),
        f"{prefix}_p50": clean.quantile(0.50),
        f"{prefix}_p95": clean.quantile(0.95),
        f"{prefix}_p99": clean.quantile(0.99),
        f"{prefix}_prob_loss": (clean < 0).mean(),
        f"{prefix}_expected_shortfall_5": left_tail.mean(),
    }


def regime_labels(market_returns: pd.Series, window: int = 21) -> pd.Series:
    realized_vol = market_returns.rolling(window).std(ddof=0) * np.sqrt(252)
    calm_cut = realized_vol.quantile(0.35)
    stress_cut = realized_vol.quantile(0.80)
    labels = pd.Series("normal", index=market_returns.index, dtype="object")
    labels[realized_vol <= calm_cut] = "calm"
    labels[realized_vol >= stress_cut] = "stress"
    return labels


def regime_performance(strategy_returns: pd.Series, labels: pd.Series) -> pd.DataFrame:
    aligned = pd.concat([strategy_returns.rename("strategy"), labels.rename("regime")], axis=1).dropna()
    rows = []
    for regime, sub in aligned.groupby("regime"):
        r = sub["strategy"]
        rows.append(
            {
                "regime": regime,
                "n_days": int(r.count()),
                "annualized_return": r.mean() * 252,
                "annualized_vol": r.std(ddof=0) * np.sqrt(252),
                "sharpe": sharpe(r),
                "max_drawdown": max_drawdown(r),
            }
        )
    return pd.DataFrame(rows).set_index("regime").sort_index()


def scenario_table(returns: pd.DataFrame, portfolio_returns: pd.Series) -> pd.DataFrame:
    market = returns.mean(axis=1)
    scenarios = {
        "base_history": portfolio_returns,
        "left_tail_shock": portfolio_returns - 0.015 * (market < market.quantile(0.05)),
        "cost_plus_10bps_monthly": portfolio_returns - 0.0010 / 21.0,
        "high_vol_deleveraging": portfolio_returns.where(
            market.rolling(21).std(ddof=0) < market.rolling(21).std(ddof=0).quantile(0.90),
            portfolio_returns * 0.5,
        ),
        "liquidity_fee_pressure": portfolio_returns - 0.0005 * (market < market.quantile(0.10)),
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


def cost_sensitivity(
    gross_returns: pd.Series,
    daily_turnover: pd.Series,
    cost_grid_bps: tuple[float, ...] = (0.0, 1.0, 2.0, 5.0, 10.0),
) -> pd.DataFrame:
    aligned = pd.concat([gross_returns.rename("gross"), daily_turnover.rename("turnover")], axis=1).dropna()
    rows = []
    for cost_bps in cost_grid_bps:
        net = aligned["gross"] - aligned["turnover"] * cost_bps / 10_000.0
        rows.append(
            {
                "cost_bps": cost_bps,
                "annualized_return": net.mean() * 252,
                "annualized_vol": net.std(ddof=0) * np.sqrt(252),
                "sharpe": sharpe(net),
                "max_drawdown": max_drawdown(net),
            }
        )
    return pd.DataFrame(rows)


def fee_revenue_sensitivity(
    aum_eur: float = 250_000_000,
    fee_bps: float = 9.0,
    adv_eur: float = 35_000_000,
    trading_fee_bps: float = 0.15,
) -> pd.DataFrame:
    rows = []
    scenarios = {
        "bear_outflows": {"aum_shock": -0.25, "adv_shock": 0.15},
        "base": {"aum_shock": 0.0, "adv_shock": 0.0},
        "growth_inflows": {"aum_shock": 0.25, "adv_shock": 0.10},
        "high_activity_stress": {"aum_shock": -0.10, "adv_shock": 0.45},
    }
    for scenario, shocks in scenarios.items():
        for fee_shock in [-3.0, -1.0, 0.0, 1.0, 3.0]:
            shocked_fee = max(fee_bps + fee_shock, 0.0)
            fee_cut = fee_bps - shocked_fee
            elasticity_aum_boost = max(fee_cut, 0.0) * 0.015
            shocked_aum = aum_eur * (1.0 + shocks["aum_shock"] + elasticity_aum_boost)
            shocked_adv = adv_eur * (1.0 + shocks["adv_shock"])
            management_revenue = shocked_aum * shocked_fee / 10_000.0
            trading_revenue = shocked_adv * 252 * trading_fee_bps / 10_000.0
            rows.append(
                {
                    "scenario": scenario,
                    "aum_shock": shocks["aum_shock"],
                    "adv_shock": shocks["adv_shock"],
                    "fee_bps": shocked_fee,
                    "aum_eur": shocked_aum,
                    "adv_eur": shocked_adv,
                    "management_fee_revenue_eur": management_revenue,
                    "trading_revenue_proxy_eur": trading_revenue,
                    "total_revenue_proxy_eur": management_revenue + trading_revenue,
                }
            )
    return pd.DataFrame(rows)
