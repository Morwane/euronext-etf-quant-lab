# ETF Market-Quality & Fair-Value Analytics

Objective: measure ETF market quality across a tradable ETF universe using LSEG data.

The framework supports true BID/ASK/NAV fields when available. The current local LSEG cache is daily price-only, so quoted spread and NAV premium/discount are left blank and price-based liquidity proxies are reported.

## Top stress names

| symbol   |   ann_vol_21d |   tracking_error_63d_vs_spy |   beta_vs_spy |   price_proxy_spread_bps |   stress_rank_0_1 | data_note                                 |
|:---------|--------------:|----------------------------:|--------------:|-------------------------:|------------------:|:------------------------------------------|
| SLV      |        0.5681 |                      0.4520 |        0.4095 |                 196.9274 |            0.9753 | price-only LSEG cache; proxy metrics used |
| EWZ      |        0.2555 |                      0.2233 |        1.1272 |                 108.6394 |            0.8272 | price-only LSEG cache; proxy metrics used |
| XLE      |        0.2461 |                      0.3361 |        1.0514 |                 117.2004 |            0.7654 | price-only LSEG cache; proxy metrics used |
| GLD      |        0.1897 |                      0.2102 |        0.0603 |                  76.4228 |            0.7160 | price-only LSEG cache; proxy metrics used |
| XLK      |        0.3430 |                      0.1700 |        1.1736 |                 134.4576 |            0.7037 | price-only LSEG cache; proxy metrics used |
| EEM      |        0.3503 |                      0.2000 |        0.9738 |                 117.2769 |            0.6790 | price-only LSEG cache; proxy metrics used |
| FXI      |        0.2268 |                      0.1569 |        0.9131 |                  82.7389 |            0.6543 | price-only LSEG cache; proxy metrics used |
| EWG      |        0.2036 |                      0.1399 |        1.0472 |                  52.4559 |            0.5432 | price-only LSEG cache; proxy metrics used |
| XLY      |        0.1785 |                      0.1163 |        1.0717 |                  64.4395 |            0.4815 | price-only LSEG cache; proxy metrics used |
| XLU      |        0.1830 |                      0.2160 |        0.5921 |                  88.6525 |            0.4691 | price-only LSEG cache; proxy metrics used |

## Interview defense

This is relevant for Euronext because ETF issuers, exchanges and liquidity providers monitor spreads, premium/discount, tracking quality, volatility and liquidity stress. In production, the same module can be fed with intraday bid/ask and iNAV/NAV fields from LSEG Workspace.