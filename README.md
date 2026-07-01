# Euronext ETF Quant Lab

ETF market-data analytics project for market-structure, ETF strategy and quant research interviews.

This repository focuses only on **ETF market-quality analytics**. It uses LSEG / Refinitiv data when available, and can fall back to cached daily price data for metrics that do not require bid/ask or NAV.

This is not a PnL trading strategy. It is a monitoring and analytics dashboard designed to measure how efficiently ETFs trade.

## What This Project Measures

- **Bid-ask spread**: execution-cost proxy computed from `BID` and `ASK`.
- **Premium/discount to NAV**: fair-value alignment computed from ETF price and NAV.
- **Tracking error**: how closely the ETF follows its mapped benchmark.
- **Beta**: ETF sensitivity to the mapped benchmark.
- **Realized volatility**: recent realized risk.
- **Drawdown**: recent peak-to-trough loss.
- **Liquidity indicators**: volume and spread-based monitoring.
- **Market-quality risk score**: simple ranking of ETFs requiring attention.

## Why It Matters

ETF teams care about market quality because an ETF can be liquid, cheap to trade, and close to NAV, or it can show wider spreads, larger NAV gaps and higher tracking risk. This project turns those concepts into a reproducible Python workflow with LSEG data, benchmark mapping, reports and figures.

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run with live LSEG Workspace data:

```bash
python scripts/pull_project1_lseg.py --rics SPY,EFA,EEM --with-nav --out data/raw_lseg_project1_nav_core
python scripts/audit_project1_benchmarks_lseg.py --etfs SPY,EFA,EEM,DIA,IWM,XLK,XLF,XLE
python scripts/run_project1_market_quality.py --lseg-folder data/raw_lseg_project1_nav_core
python scripts/plot_project1_market_quality.py
pytest -q
```

Run in price-only fallback mode:

```bash
python scripts/run_project1_market_quality.py --use-daily-cache
python scripts/plot_project1_market_quality.py
pytest -q
```

## LSEG Data Modes

### Live Pull Mode

With LSEG Workspace open, `scripts/pull_project1_lseg.py` pulls:

- price;
- bid;
- ask;
- volume;
- NAV, when `--with-nav` is used.

This enables true spread and true premium/discount analytics.

### Price-Only Fallback Mode

If live LSEG fields are not available, the project can use cached daily prices. In that mode, spread and NAV analytics are not faked. The report explicitly says when proxy metrics are used.

Raw LSEG / Refinitiv data is not committed. See `DATA_LICENSE_NOTE.md`.

## Outputs

- `reports/project1_market_quality.md`
- `reports/project1_explanation_fr.md`
- `reports/market_quality_report.md`
- `reports/figures/project1/market_quality_dashboard.png`
- `reports/figures/project1/liquidity_vs_tracking.png`
- `reports/figures/project1/nav_alignment_detail.png`
- `reports/figures/project1/premium_discount_timeseries.png`
- `reports/figures/project1/spread_timeseries.png`
- `reports/figures/project1/normalized_price_vs_nav.png`

## Figures

![ETF market-quality dashboard](reports/figures/project1/market_quality_dashboard.png)

![Liquidity vs tracking](reports/figures/project1/liquidity_vs_tracking.png)

![ETF price vs NAV alignment](reports/figures/project1/nav_alignment_detail.png)

![Premium discount through time](reports/figures/project1/premium_discount_timeseries.png)

![Quoted spread through time](reports/figures/project1/spread_timeseries.png)

![Normalized ETF price vs NAV](reports/figures/project1/normalized_price_vs_nav.png)

## How To Explain This Project In An Interview

I built an ETF market-quality dashboard using LSEG Workspace data. It pulls ETF price, bid, ask, volume and NAV, maps ETFs to appropriate benchmarks such as S&P 500, MSCI EAFE and MSCI Emerging Markets, and computes spread, premium/discount to NAV, tracking error, beta, realized volatility and drawdown. The goal is not to generate PnL directly, but to monitor ETF trading quality and identify products that require attention.
