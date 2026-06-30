from __future__ import annotations

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.data import ETF_UNIVERSE, load_prices
from src.market_quality import market_quality_snapshot


ROOT = Path(__file__).resolve().parents[1]


def run() -> None:
    prices = load_prices(ETF_UNIVERSE)
    snapshot = market_quality_snapshot(prices)
    out_csv = ROOT / "data" / "processed" / "market_quality_snapshot.csv"
    snapshot.to_csv(out_csv, index=False)

    top = snapshot.head(10)
    report = [
        "# ETF Market-Quality & Fair-Value Analytics",
        "",
        "Objective: measure ETF market quality across a tradable ETF universe using LSEG data.",
        "",
        "The framework supports true BID/ASK/NAV fields when available. The current local LSEG cache is daily price-only, so quoted spread and NAV premium/discount are left blank and price-based liquidity proxies are reported.",
        "",
        "## Top stress names",
        "",
        top[
            [
                "symbol",
                "ann_vol_21d",
                "tracking_error_63d_vs_spy",
                "beta_vs_spy",
                "price_proxy_spread_bps",
                "stress_rank_0_1",
                "data_note",
            ]
        ].to_markdown(index=False, floatfmt=".4f"),
        "",
        "## Interview defense",
        "",
        "This is relevant for Euronext because ETF issuers, exchanges and liquidity providers monitor spreads, premium/discount, tracking quality, volatility and liquidity stress. In production, the same module can be fed with intraday bid/ask and iNAV/NAV fields from LSEG Workspace.",
    ]
    (ROOT / "reports" / "market_quality_report.md").write_text("\n".join(report), encoding="utf-8")


if __name__ == "__main__":
    run()

