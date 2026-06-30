import numpy as np
import pandas as pd

from src.metrics import max_drawdown, sharpe
from src.toolkit import black_scholes_price, crr_binomial_price


def test_sharpe_positive_for_positive_returns():
    returns = pd.Series([0.001] * 252)
    assert sharpe(returns) > 0


def test_max_drawdown_is_negative_or_zero():
    returns = pd.Series([0.10, -0.20, 0.05])
    assert max_drawdown(returns) <= 0


def test_crr_converges_near_black_scholes():
    bs = black_scholes_price(100, 100, 1.0, 0.03, 0.20, "call")
    crr = crr_binomial_price(100, 100, 1.0, 0.03, 0.20, 300, "call")
    assert np.isclose(bs, crr, atol=0.15)

