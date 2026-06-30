# Euronext ETF Quant Lab

ETF market-data analytics project built for market-structure, ETF strategy and quant research .

The main completed use case is an ETF market-quality monitor using LSEG Workspace data. It pulls ETF price, bid, ask, volume and NAV, maps ETFs to appropriate benchmarks, and produces reports/figures on:

- quoted bid-ask spreads;
- premium/discount to NAV;
- liquidity/volume;
- tracking error versus mapped benchmarks;
- beta, realized volatility and drawdown;
- ETF market-quality monitoring scores.

This is not a PnL trading strategy. It is an analytics and monitoring framework for ETF market quality, designed to support the CV themes: market-data dashboards, quantitative market research, scenario analysis and portfolio/risk tooling.

## Quick start

```bash
pip install -r requirements.txt
python scripts/run_all.py
pytest
```

Generated outputs are written to `reports/` and `data/processed/`.

Raw LSEG / Refinitiv data is not committed to this repository. See `DATA_LICENSE_NOTE.md`.

For the completed ETF market-quality workflow:

```bash
python scripts/pull_project1_lseg.py --rics SPY,EFA,EEM --with-nav --out data/raw_lseg_project1_nav_core
python scripts/audit_project1_benchmarks_lseg.py --etfs SPY,EFA,EEM,DIA,IWM,XLK,XLF,XLE
python scripts/run_project1_market_quality.py --lseg-folder data/raw_lseg_project1_nav_core
python scripts/plot_project1_market_quality.py
pytest -q
```

## Data

The loader reads LSEG cache files from:

```text
../data/capability_audit/raw_prices
```

The current local cache contains daily close-like fields (`TRDPRC_1`) for ETFs, indices, volatility indices and correlation indices. The market-quality module also supports true `BID`, `ASK`, `NAV` and volume fields when they are available from LSEG Workspace.

When those fields are absent, the report is explicit and uses price-based liquidity/stress proxies instead of pretending to have bid/ask or NAV data.

## Main Project

### ETF Market-Quality Analytics

`scripts/run_project1_market_quality.py` computes quoted bid-ask spread, premium/discount to NAV, tracking error versus mapped LSEG benchmarks, beta, realized volatility, drawdown and market-quality risk score.

Output:

- `reports/project1_market_quality.md`
- `reports/figures/project1/market_quality_dashboard.png`
- `reports/figures/project1/liquidity_vs_tracking.png`
- `reports/figures/project1/premium_discount_timeseries.png`
- `reports/figures/project1/spread_timeseries.png`
- `reports/figures/project1/nav_alignment_detail.png`
- `reports/figures/project1/normalized_price_vs_nav.png`
- `data/processed/project1_market_quality.csv`
- `config/project1_benchmarks.csv`

This is an ETF analytics and monitoring project, not a PnL trading strategy. The goal is to detect whether an ETF trades efficiently: tight spreads, small NAV gap, reasonable liquidity and stable benchmark tracking.

![ETF market-quality dashboard](reports/figures/project1/market_quality_dashboard.png)

![Liquidity vs tracking](reports/figures/project1/liquidity_vs_tracking.png)

![ETF price vs NAV alignment](reports/figures/project1/nav_alignment_detail.png)

![Premium discount through time](reports/figures/project1/premium_discount_timeseries.png)

## Link To My CV

This repository supports the following CV lines:

### Market-Data Analytics & Dashboards

The project ingests LSEG ETF data, computes market-quality indicators and generates automated reports and figures. The README figures are produced by `scripts/plot_project1_market_quality.py`.

### Quantitative Market Research

The research component studies ETF spreads, NAV alignment, benchmark tracking, realized volatility and cross-ETF market-quality differences. The benchmark mapping is explicit in `config/project1_benchmarks.csv`, and benchmark availability is audited through `scripts/audit_project1_benchmarks_lseg.py`.

### Simulation & Scenario Models

Supporting module: `scripts/run_scenarios.py` runs block-bootstrap, stress scenarios and fee/revenue sensitivity. This is useful interview material, but less central than the ETF market-quality project.

### Optimization & Segmentation

Supporting module: `scripts/run_optimization.py` builds a simple risk-parity / volatility-target allocation across ETF clusters with turnover costs. This demonstrates portfolio/risk tooling, not a production allocator.

### Quantitative Toolkit

Supporting module: `src/toolkit.py` contains Black-Scholes, CRR binomial pricing and walk-forward split utilities, with tests in `tests/test_metrics.py`.

## Interview Pitch

I built an ETF market-quality dashboard using LSEG Workspace data. It pulls ETF price, bid, ask, volume and NAV, maps ETFs to appropriate benchmarks such as S&P 500, MSCI EAFE and MSCI Emerging Markets, and computes spread, premium/discount to NAV, tracking error, beta, volatility and drawdown. The goal is not to generate PnL directly, but to monitor ETF trading quality and identify products that require attention.

## Validation

The repository is structured to be auditable rather than over-claiming alpha:

- clean LSEG data ingestion
- explicit data limitations
- benchmark availability audit
- mapped benchmark comparison
- ETF market-quality analytics and figures
- transaction costs
- scenario stress testing support module
- reproducible reports and tests

Run:

```bash
pytest -q
```
