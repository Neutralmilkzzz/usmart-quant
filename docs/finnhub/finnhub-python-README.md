# finnhub-python

- API documentation: `https://finnhub.io/docs/api`
- API version: `1.0.0`
- Package version: `2.4.25`

## Installation

```sh
pip install finnhub-python
```

## Minimal examples

```python
import finnhub
import pandas as pd

finnhub_client = finnhub.Client(api_key="YOUR API KEY")

# Stock candles
res = finnhub_client.stock_candles('AAPL', 'D', 1590988249, 1591852249)
print(pd.DataFrame(res))

# Quote
print(finnhub_client.quote('AAPL'))

# Company profile
print(finnhub_client.company_profile2(symbol='AAPL'))

# Basic financials
print(finnhub_client.company_basic_financials('AAPL', 'all'))

# Earnings calendar
print(finnhub_client.earnings_calendar(
    _from="2020-06-10",
    to="2020-06-30",
    symbol="",
    international=False,
))

# Stock symbols
print(finnhub_client.stock_symbols('US')[0:5])

# Market status
print(finnhub_client.market_status(exchange='US'))
```

## 对 MVP 最相关的接口

- `stock_symbols('US')`
- `stock_candles(...)`
- `quote(...)`
- `company_profile2(...)`
- `company_basic_financials(...)`
- `earnings_calendar(...)`
- `market_status(exchange='US')`
