# Simulation & Scenario Models

Objective: stress-test ETF portfolio outcomes using Monte Carlo/block-bootstrap and cost/scenario sensitivity.

## Portfolio scenario results

| scenario                |   annualized_mean |   annualized_vol |   sharpe |   max_drawdown |
|:------------------------|------------------:|-----------------:|---------:|---------------:|
| base_history            |            0.0388 |           0.1021 |   0.3802 |        -0.1962 |
| covid_style_left_tail   |           -0.1506 |           0.1364 |  -1.1044 |        -0.9285 |
| cost_plus_10bps_monthly |            0.0268 |           0.1021 |   0.2627 |        -0.2068 |
| high_vol_deleveraging   |            0.0394 |           0.0991 |   0.3978 |        -0.2003 |

## Block-bootstrap one-year distribution

- p05_one_year_return: -12.76%
- p50_one_year_return: 4.59%
- p95_one_year_return: 19.82%

## Fee/revenue sensitivity

|   aum_shock |   fee_bps |   annual_revenue_eur |
|------------:|----------:|---------------------:|
|       -0.25 |      7.00 |            131250.00 |
|       -0.25 |      9.00 |            168750.00 |
|       -0.25 |     11.00 |            206250.00 |
|       -0.10 |      7.00 |            157500.00 |
|       -0.10 |      9.00 |            202500.00 |
|       -0.10 |     11.00 |            247500.00 |
|        0.00 |      7.00 |            175000.00 |
|        0.00 |      9.00 |            225000.00 |
|        0.00 |     11.00 |            275000.00 |
|        0.10 |      7.00 |            192500.00 |

## Interview defense

This connects to ETF strategy work because exchanges care about volume, fees, listing revenue and how market regimes affect economics. The model is deliberately simple but auditable.