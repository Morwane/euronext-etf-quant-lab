# Quantitative Market Research

Objective: test relative-value, volatility and correlation research ideas without look-ahead in a daily LSEG ETF universe.

## Relative-value mean-reversion test

| name      |   ann_return |   ann_vol |   sharpe |   max_drawdown |   hit_rate |
|:----------|-------------:|----------:|---------:|---------------:|-----------:|
| strategy  |       0.0190 |    0.1111 |   0.1710 |        -0.2566 |     0.4712 |
| benchmark |       0.1282 |    0.1712 |   0.7487 |        -0.3410 |     0.5459 |

## Latest cross-asset / volatility context

| Date                |    _VIX |   _VIX3M |   _COR1M |   _COR3M |   _DSPX |
|:--------------------|--------:|---------:|---------:|---------:|--------:|
| 2026-06-01 00:00:00 | 16.0500 |  19.4300 |   6.0200 |   8.2200 | 44.0700 |
| 2026-06-02 00:00:00 | 15.7700 |  19.4900 |   5.8600 |   8.1000 | 43.9900 |
| 2026-06-03 00:00:00 | 16.0600 |  19.7600 |   6.3200 |   8.3800 | 43.7000 |
| 2026-06-04 00:00:00 | 15.4000 |  19.2300 |   6.9100 |   8.8300 | 41.0100 |
| 2026-06-05 00:00:00 | 21.5100 |  21.8200 |  14.5200 |  12.2300 | 40.2700 |

## Latest sector dispersion

| Date                |   sector_dispersion |   dispersion_z |
|:--------------------|--------------------:|---------------:|
| 2026-06-01 00:00:00 |              0.0164 |         2.4383 |
| 2026-06-02 00:00:00 |              0.0117 |         1.0469 |
| 2026-06-03 00:00:00 |              0.0087 |         0.1762 |
| 2026-06-04 00:00:00 |              0.0135 |         1.5624 |
| 2026-06-05 00:00:00 |              0.0235 |         4.3261 |

## Interpretation

This is research infrastructure, not a production trading claim. It includes transaction costs and a benchmark comparison. A signal is CV-useful when it demonstrates rigorous process, even if it is not an institutional alpha.