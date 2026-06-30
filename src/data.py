from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PROJECT_ROOT.parent
DEFAULT_RAW_DIR = WORKSPACE_ROOT / "data" / "capability_audit" / "raw_prices"

ETF_UNIVERSE = [
    "SPY", "DIA", "IWM", "EFA", "EEM", "VGK", "EWG", "EWJ", "EWU", "EWZ", "FXI",
    "XLK", "XLF", "XLE", "XLV", "XLY", "XLP", "XLI", "XLU", "XLB", "XLC",
    "GLD", "SLV", "LQD", "HYG", "JNK", "AGG", "TIP",
]

BENCHMARKS = ["SPY", "_SPX", "_VIX", "_VIX3M", "_COR1M", "_COR3M", "_DSPX"]


def available_symbols(raw_dir: Path = DEFAULT_RAW_DIR) -> list[str]:
    return sorted(path.stem for path in raw_dir.glob("*.csv"))


def _pick_price_column(df: pd.DataFrame) -> str:
    for col in ("TRDPRC_1", "Close", "PX_LAST", "LAST", "price"):
        if col in df.columns:
            return col
    numeric = [col for col in df.columns if col != "Date" and pd.api.types.is_numeric_dtype(df[col])]
    if not numeric:
        raise ValueError("No numeric price column found.")
    return numeric[0]


def load_symbol(symbol: str, raw_dir: Path = DEFAULT_RAW_DIR) -> pd.DataFrame:
    path = raw_dir / f"{symbol}.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing LSEG cache file: {path}")
    df = pd.read_csv(path)
    if "Date" not in df.columns:
        raise ValueError(f"{path} has no Date column.")
    price_col = _pick_price_column(df)
    out = df.copy()
    out["Date"] = pd.to_datetime(out["Date"])
    out = out.sort_values("Date").drop_duplicates("Date")
    out = out.set_index("Date")
    out["price"] = pd.to_numeric(out[price_col], errors="coerce")
    out = out[out["price"].gt(0)].copy()
    out["symbol"] = symbol
    return out


def load_prices(symbols: list[str], raw_dir: Path = DEFAULT_RAW_DIR) -> pd.DataFrame:
    series = {}
    for symbol in symbols:
        try:
            series[symbol] = load_symbol(symbol, raw_dir)["price"]
        except (FileNotFoundError, ValueError):
            continue
    if not series:
        raise ValueError("No symbols could be loaded.")
    prices = pd.concat(series, axis=1).sort_index()
    return prices.ffill().dropna(how="all")


def load_optional_fields(symbol: str, raw_dir: Path = DEFAULT_RAW_DIR) -> pd.DataFrame:
    """Return raw LSEG fields used when bid/ask/NAV are available."""
    df = load_symbol(symbol, raw_dir)
    fields = {}
    for name in ("BID", "ASK", "NAV", "ACVOL_UNS", "VOLUME"):
        if name in df.columns:
            fields[name] = pd.to_numeric(df[name], errors="coerce")
    return pd.DataFrame(fields, index=df.index)


def returns_from_prices(prices: pd.DataFrame) -> pd.DataFrame:
    rets = prices.pct_change(fill_method=None)
    rets = rets.replace([np.inf, -np.inf], np.nan)
    return rets.dropna(how="all")


def latest_common_window(prices: pd.DataFrame, min_obs: int = 252) -> pd.DataFrame:
    usable = prices.dropna(axis=1, thresh=min_obs)
    return usable.dropna(how="all")

