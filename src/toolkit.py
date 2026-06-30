from __future__ import annotations

import math

import numpy as np
import pandas as pd
from scipy.stats import norm


def black_scholes_price(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    vol: float,
    option_type: str = "call",
) -> float:
    if maturity <= 0:
        intrinsic = max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)
        return intrinsic
    d1 = (math.log(spot / strike) + (rate + 0.5 * vol * vol) * maturity) / (vol * math.sqrt(maturity))
    d2 = d1 - vol * math.sqrt(maturity)
    if option_type == "call":
        return spot * norm.cdf(d1) - strike * math.exp(-rate * maturity) * norm.cdf(d2)
    return strike * math.exp(-rate * maturity) * norm.cdf(-d2) - spot * norm.cdf(-d1)


def crr_binomial_price(
    spot: float,
    strike: float,
    maturity: float,
    rate: float,
    vol: float,
    steps: int = 200,
    option_type: str = "call",
) -> float:
    dt = maturity / steps
    up = math.exp(vol * math.sqrt(dt))
    down = 1.0 / up
    disc = math.exp(-rate * dt)
    p = (math.exp(rate * dt) - down) / (up - down)
    nodes = np.array([spot * up ** j * down ** (steps - j) for j in range(steps + 1)])
    if option_type == "call":
        values = np.maximum(nodes - strike, 0.0)
    else:
        values = np.maximum(strike - nodes, 0.0)
    for _ in range(steps):
        values = disc * (p * values[1:] + (1 - p) * values[:-1])
    return float(values[0])


def walk_forward_split(index: pd.Index, train_years: int = 3, test_months: int = 6) -> list[tuple[pd.Index, pd.Index]]:
    dates = pd.Series(index).drop_duplicates().sort_values()
    start = dates.min()
    end = dates.max()
    splits = []
    train_delta = pd.DateOffset(years=train_years)
    test_delta = pd.DateOffset(months=test_months)
    cursor = start
    while cursor + train_delta + test_delta <= end:
        train_end = cursor + train_delta
        test_end = train_end + test_delta
        train_idx = dates[(dates >= cursor) & (dates < train_end)]
        test_idx = dates[(dates >= train_end) & (dates < test_end)]
        if len(train_idx) > 100 and len(test_idx) > 20:
            splits.append((pd.Index(train_idx), pd.Index(test_idx)))
        cursor = cursor + test_delta
    return splits

