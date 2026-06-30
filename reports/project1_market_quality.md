# Project 1 - ETF Market-Quality & Fair-Value Analytics

Data source used: live/pulled LSEG market-quality fields.

## What the project measures

- bid-ask spread when BID/ASK are available
- premium/discount when NAV is available
- tracking error versus each ETF benchmark/proxy from config/project1_benchmarks.csv
- realized volatility
- beta to benchmark
- drawdown and market-quality stress ranking

## Latest result

| ric   |   latest_price |   quoted_spread_bps_20d_median |   premium_discount_bps_20d_median | benchmark     | benchmark_name              | benchmark_quality    |   tracking_error_63d |   ann_vol_63d |   beta_to_benchmark |   max_drawdown_1y | has_real_spread   | has_real_nav   |   quality_risk_score |
|:------|---------------:|-------------------------------:|----------------------------------:|:--------------|:----------------------------|:---------------------|---------------------:|--------------:|--------------------:|------------------:|:------------------|:---------------|---------------------:|
| EEM   |        67.4300 |                         1.4723 |                           -0.4158 | _MSCIEF       | MSCI Emerging Markets Index | exact_lseg_candidate |               0.3061 |        0.3283 |              0.5418 |           -0.1352 | True              | True           |               0.9167 |
| EFA   |       103.4500 |                         0.9706 |                            8.1248 | _MIEA00000PUS | MSCI EAFE Index             | exact_lseg_candidate |               0.1605 |        0.2026 |              0.6092 |           -0.1142 | True              | True           |               0.7500 |
| SPY   |       741.0000 |                         0.2693 |                            0.0835 | _SPX          | S&P 500 Index               | close_index_proxy    |               0.0188 |        0.1554 |              1.0207 |           -0.0928 | True              | True           |               0.3333 |

## How to explain it

An ETF should trade close to its fair value, with tight spreads, stable tracking versus its own benchmark and enough liquidity. This project creates a monitoring table that ranks ETFs where market quality is deteriorating.

## What LSEG adds

Daily prices are enough for tracking error, volatility and drawdown. LSEG BID/ASK/NAV fields are needed for the full market-microstructure version: true quoted spread and true premium/discount to NAV.