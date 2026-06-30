# Simulation & Scenario Models

Objective: stress-test ETF portfolio outcomes using Monte Carlo simulation, block-bootstrap, transaction-cost sensitivity and regime scenarios.

This is a scenario-analysis project, not a trading-alpha claim. It asks: how robust are outcomes if costs rise, volatility regimes change, or fee/revenue assumptions move?

## Simulated one-year outcome distribution

| method                 |   one_year_p01 |   one_year_p05 |   one_year_p50 |   one_year_p95 |   one_year_p99 |   one_year_prob_loss |   one_year_expected_shortfall_5 |
|:-----------------------|---------------:|---------------:|---------------:|---------------:|---------------:|---------------------:|--------------------------------:|
| parametric_monte_carlo |        -0.2006 |        -0.1308 |         0.0326 |         0.2358 |         0.3347 |               0.3755 |                         -0.1695 |
| block_bootstrap        |        -0.2003 |        -0.1245 |         0.0409 |         0.1949 |         0.2657 |               0.3430 |                         -0.1710 |

## Portfolio scenario stress tests

| scenario                |   annualized_mean |   annualized_vol |   sharpe |   max_drawdown |
|:------------------------|------------------:|-----------------:|---------:|---------------:|
| base_history            |            0.0388 |           0.1021 |   0.3802 |        -0.1962 |
| left_tail_shock         |           -0.1506 |           0.1364 |  -1.1044 |        -0.9285 |
| cost_plus_10bps_monthly |            0.0268 |           0.1021 |   0.2627 |        -0.2068 |
| high_vol_deleveraging   |            0.0390 |           0.0948 |   0.4121 |        -0.1920 |
| liquidity_fee_pressure  |            0.0262 |           0.1035 |   0.2532 |        -0.2150 |

## Regime performance

| regime   |    n_days |   annualized_return |   annualized_vol |   sharpe |   max_drawdown |
|:---------|----------:|--------------------:|-----------------:|---------:|---------------:|
| calm     | 1439.0000 |              0.0446 |           0.0775 |   0.5751 |        -0.2094 |
| normal   | 1869.0000 |              0.0447 |           0.1048 |   0.4266 |        -0.1803 |
| stress   |  822.0000 |              0.0154 |           0.1299 |   0.1183 |        -0.1841 |

## Cost sensitivity

|   cost_bps |   annualized_return |   annualized_vol |   sharpe |   max_drawdown |
|-----------:|--------------------:|-----------------:|---------:|---------------:|
|     0.0000 |              0.0397 |           0.1021 |   0.3892 |        -0.1956 |
|     1.0000 |              0.0393 |           0.1021 |   0.3847 |        -0.1959 |
|     2.0000 |              0.0388 |           0.1021 |   0.3802 |        -0.1962 |
|     5.0000 |              0.0374 |           0.1021 |   0.3667 |        -0.1969 |
|    10.0000 |              0.0352 |           0.1022 |   0.3443 |        -0.1982 |

## Fee / revenue sensitivity proxy

| scenario       |   aum_shock |   adv_shock |   fee_bps |      aum_eur |     adv_eur |   management_fee_revenue_eur |   trading_revenue_proxy_eur |   total_revenue_proxy_eur |
|:---------------|------------:|------------:|----------:|-------------:|------------:|-----------------------------:|----------------------------:|--------------------------:|
| bear_outflows  |       -0.25 |        0.15 |      6.00 | 198750000.00 | 40250000.00 |                    119250.00 |                   152145.00 |                 271395.00 |
| bear_outflows  |       -0.25 |        0.15 |      8.00 | 191250000.00 | 40250000.00 |                    153000.00 |                   152145.00 |                 305145.00 |
| bear_outflows  |       -0.25 |        0.15 |      9.00 | 187500000.00 | 40250000.00 |                    168750.00 |                   152145.00 |                 320895.00 |
| bear_outflows  |       -0.25 |        0.15 |     10.00 | 187500000.00 | 40250000.00 |                    187500.00 |                   152145.00 |                 339645.00 |
| bear_outflows  |       -0.25 |        0.15 |     12.00 | 187500000.00 | 40250000.00 |                    225000.00 |                   152145.00 |                 377145.00 |
| base           |        0.00 |        0.00 |      6.00 | 261250000.00 | 35000000.00 |                    156750.00 |                   132300.00 |                 289050.00 |
| base           |        0.00 |        0.00 |      8.00 | 253750000.00 | 35000000.00 |                    203000.00 |                   132300.00 |                 335300.00 |
| base           |        0.00 |        0.00 |      9.00 | 250000000.00 | 35000000.00 |                    225000.00 |                   132300.00 |                 357300.00 |
| base           |        0.00 |        0.00 |     10.00 | 250000000.00 | 35000000.00 |                    250000.00 |                   132300.00 |                 382300.00 |
| base           |        0.00 |        0.00 |     12.00 | 250000000.00 | 35000000.00 |                    300000.00 |                   132300.00 |                 432300.00 |
| growth_inflows |        0.25 |        0.10 |      6.00 | 323750000.00 | 38500000.00 |                    194250.00 |                   145530.00 |                 339780.00 |
| growth_inflows |        0.25 |        0.10 |      8.00 | 316250000.00 | 38500000.00 |                    253000.00 |                   145530.00 |                 398530.00 |

## Figures

- `reports/figures/project2/terminal_distribution.png`
- `reports/figures/project2/scenario_stress_summary.png`
- `reports/figures/project2/cost_sensitivity.png`
- `reports/figures/project2/fee_revenue_heatmap.png`

## Interview defense

This supports the CV line because it combines Monte Carlo, block-bootstrap, transaction-cost stress, regime analysis and a simple fee/revenue sensitivity model. The revenue block is a proxy model, not a claim about Euronext's exact fee schedule.