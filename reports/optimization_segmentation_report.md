# Optimization & Segmentation

Objective: allocate across ETF clusters using inverse-vol risk parity, volatility targeting and simple turnover costs.

## Strategy performance

| symbol                 |   ann_return |   ann_vol |   sharpe |   max_drawdown |   observations |
|:-----------------------|-------------:|----------:|---------:|---------------:|---------------:|
| vol_target_risk_parity |       0.0342 |    0.1021 |   0.3802 |        -0.1962 |      4130.0000 |

## Latest non-zero weights

|     |   latest_weight |
|:----|----------------:|
| TIP |          0.1160 |
| AGG |          0.1055 |
| JNK |          0.0903 |
| HYG |          0.0883 |
| LQD |          0.0733 |
| XLP |          0.0353 |
| DIA |          0.0350 |
| XLF |          0.0349 |
| XLC |          0.0338 |
| SPY |          0.0338 |
| XLV |          0.0312 |
| XLU |          0.0286 |
| XLB |          0.0284 |
| EWU |          0.0255 |
| XLI |          0.0253 |
| XLY |          0.0241 |
| FXI |          0.0240 |
| EFA |          0.0239 |
| IWM |          0.0235 |
| VGK |          0.0229 |

## Cluster segmentation

| cluster       | members                                          |   n_members |   median_ann_vol |   avg_pairwise_corr |
|:--------------|:-------------------------------------------------|------------:|-----------------:|--------------------:|
| core_us       | SPY, DIA, IWM                                    |           3 |           0.1718 |              0.8965 |
| international | EFA, EEM, VGK, EWG, EWJ, EWU, EWZ, FXI           |           8 |           0.2121 |              0.7323 |
| sectors       | XLK, XLF, XLE, XLV, XLY, XLP, XLI, XLU, XLB, XLC |          10 |           0.2057 |              0.6458 |
| rates_credit  | LQD, HYG, JNK, AGG, TIP                          |           5 |           0.0768 |              0.4879 |
| commodities   | GLD, SLV                                         |           2 |           0.2407 |              0.7866 |

## Interview defense

The project shows portfolio construction, constraints, transaction-cost awareness and segmentation. For Euronext, it maps naturally to ETF baskets, liquidity clusters and client/product analytics.