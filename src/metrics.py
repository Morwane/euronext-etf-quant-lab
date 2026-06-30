from __future__ import annotations

import numpy as np
import pandas as pd


TRADING_DAYS = 252


def annualized_return(returns: pd.Series) -> float:
    clean = returns.dropna()
    if clean.empty:
        return np.nan
    return (1.0 + clean).prod() ** (TRADING_DAYS / len(clean)) - 1.0


def annualized_vol(returns: pd.Series) -> float:
    return returns.dropna().std(ddof=0) * np.sqrt(TRADING_DAYS)


def sharpe(returns: pd.Series, rf: float = 0.0) -> float:
    clean = returns.dropna() - rf / TRADING_DAYS
    vol = clean.std(ddof=0)
    if clean.empty or vol == 0 or np.isnan(vol):
        return np.nan
    return clean.mean() / vol * np.sqrt(TRADING_DAYS)


def max_drawdown(returns: pd.Series) -> float:
    clean = returns.dropna()
    if clean.empty:
        return np.nan
    equity = (1.0 + clean).cumprod()
    return (equity / equity.cummax() - 1.0).min()


def rolling_tracking_error(asset: pd.Series, benchmark: pd.Series, window: int = 63) -> pd.Series:
    aligned = pd.concat([asset, benchmark], axis=1).dropna()
    diff = aligned.iloc[:, 0] - aligned.iloc[:, 1]
    return diff.rolling(window).std(ddof=0) * np.sqrt(TRADING_DAYS)


def beta_to_benchmark(asset: pd.Series, benchmark: pd.Series) -> float:
    aligned = pd.concat([asset, benchmark], axis=1).dropna()
    if len(aligned) < 20:
        return np.nan
    var = aligned.iloc[:, 1].var(ddof=0)
    if var == 0:
        return np.nan
    return aligned.iloc[:, 0].cov(aligned.iloc[:, 1]) / var


def zscore(series: pd.Series, window: int = 252) -> pd.Series:
    mean = series.rolling(window).mean()
    std = series.rolling(window).std(ddof=0)
    return (series - mean) / std.replace(0, np.nan)


def performance_table(returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for col in returns.columns:
        r = returns[col].dropna()
        rows.append(
            {
                "symbol": col,
                "ann_return": annualized_return(r),
                "ann_vol": annualized_vol(r),
                "sharpe": sharpe(r),
                "max_drawdown": max_drawdown(r),
                "observations": int(r.count()),
            }
        )
    return pd.DataFrame(rows).set_index("symbol").sort_index()


def turnover(weights: pd.DataFrame) -> pd.Series:
    return weights.diff().abs().sum(axis=1).fillna(0.0)

