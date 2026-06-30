from __future__ import annotations

import numpy as np
import pandas as pd

from .data import load_optional_fields
from .metrics import annualized_vol, beta_to_benchmark, max_drawdown, rolling_tracking_error


def quoted_spread_bps(optional_fields: pd.DataFrame) -> pd.Series:
    if {"BID", "ASK"}.issubset(optional_fields.columns):
        mid = (optional_fields["BID"] + optional_fields["ASK"]) / 2.0
        return (optional_fields["ASK"] - optional_fields["BID"]) / mid * 10_000.0
    return pd.Series(dtype=float)


def premium_discount_bps(price: pd.Series, optional_fields: pd.DataFrame) -> pd.Series:
    if "NAV" in optional_fields.columns:
        return (price - optional_fields["NAV"]) / optional_fields["NAV"] * 10_000.0
    return pd.Series(dtype=float)


def market_quality_snapshot(prices: pd.DataFrame, benchmark: str = "SPY") -> pd.DataFrame:
    returns = prices.pct_change(fill_method=None)
    benchmark_returns = returns[benchmark]
    rows = []
    for symbol in prices.columns:
        if symbol == benchmark:
            continue
        r = returns[symbol].dropna()
        if len(r) < 252:
            continue
        opt = load_optional_fields(symbol)
        spread = quoted_spread_bps(opt)
        premium = premium_discount_bps(prices[symbol], opt)
        te_63 = rolling_tracking_error(returns[symbol], benchmark_returns, 63).iloc[-1]
        vol_21 = annualized_vol(r.tail(21))
        vol_63 = annualized_vol(r.tail(63))
        beta = beta_to_benchmark(returns[symbol], benchmark_returns)
        corr = returns[[symbol, benchmark]].dropna().corr().iloc[0, 1]
        proxy_spread = r.abs().rolling(21).median().iloc[-1] * 10_000.0
        stress = np.nanmean(
            [
                _rank_safe(vol_21, returns.drop(columns=[benchmark]).tail(21).std() * np.sqrt(252)),
                _rank_safe(te_63, returns.drop(columns=[benchmark]).tail(63).std() * np.sqrt(252)),
                _rank_safe(abs(max_drawdown(r.tail(252))), returns.drop(columns=[benchmark]).tail(252).apply(max_drawdown).abs()),
            ]
        )
        rows.append(
            {
                "symbol": symbol,
                "latest_price": prices[symbol].dropna().iloc[-1],
                "ann_vol_21d": vol_21,
                "ann_vol_63d": vol_63,
                "tracking_error_63d_vs_spy": te_63,
                "beta_vs_spy": beta,
                "corr_vs_spy": corr,
                "max_drawdown_1y": max_drawdown(r.tail(252)),
                "quoted_spread_bps": spread.tail(20).median() if not spread.empty else np.nan,
                "premium_discount_bps": premium.tail(20).median() if not premium.empty else np.nan,
                "price_proxy_spread_bps": proxy_spread,
                "stress_rank_0_1": stress,
                "data_note": "true bid/ask/NAV" if not spread.empty or not premium.empty else "price-only LSEG cache; proxy metrics used",
            }
        )
    return pd.DataFrame(rows).sort_values("stress_rank_0_1", ascending=False)


def _rank_safe(value: float, cross_section: pd.Series) -> float:
    clean = pd.Series(cross_section).dropna()
    if clean.empty or pd.isna(value):
        return np.nan
    return float((clean <= value).mean())

