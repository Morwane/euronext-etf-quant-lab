import pandas as pd

from src.metrics import max_drawdown, rolling_tracking_error, sharpe


def test_sharpe_positive_for_positive_returns():
    returns = pd.Series([0.001] * 252)
    assert sharpe(returns) > 0


def test_max_drawdown_is_negative_or_zero():
    returns = pd.Series([0.10, -0.20, 0.05])
    assert max_drawdown(returns) <= 0


def test_tracking_error_is_zero_for_identical_returns():
    returns = pd.Series([0.001, -0.002, 0.003] * 40)
    te = rolling_tracking_error(returns, returns, window=20).dropna()
    assert te.iloc[-1] == 0
