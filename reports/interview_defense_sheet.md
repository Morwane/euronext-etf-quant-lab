# Interview Defense Sheet

## What this GitHub project proves

- I can turn ETF market data into market-quality metrics: volatility, tracking error, liquidity proxies, beta and stress ranking.
- I understand that real ETF quality also needs bid/ask and NAV/iNAV; the code supports these fields and documents when the local cache is price-only.
- I can run scenario analysis, cost sensitivity and block-bootstrap simulations.
- I can build constrained portfolio allocation with volatility targeting and transaction costs.
- I can compare a research signal against a benchmark and avoid look-ahead by using shifted weights/signals.
- I can package the work as a reproducible research repo with tests and generated reports.

## Best 20-second interview pitch

I built an ETF quant analytics lab using LSEG data. It computes ETF market-quality metrics, tracks relative value and dispersion signals, stress-tests scenarios, and runs a constrained vol-targeted allocation. I also made the data limitations explicit: the current cache is daily price-only, but the market-quality module is designed to consume bid/ask and NAV fields when available.

## Honest limitation

This project is an analytics and research framework, not proof that I discovered a proprietary alpha. Its strength for Euronext is market structure, ETF analytics, data handling and rigorous validation.