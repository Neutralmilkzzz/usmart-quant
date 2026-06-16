# Finnhub API Docs

官方文档：

- https://finnhub.io/docs/api

官方 GitHub：

- API / Issues: https://github.com/finnhubio/Finnhub-API
- Python SDK: https://github.com/Finnhub-Stock-API/finnhub-python

## 对当前美股 MVP 最相关的接口

### 1. Stock Symbols

用途：

- 拉取美股股票池
- 作为后续扫描 universe 的基础

Python SDK 示例：

```python
finnhub_client.stock_symbols("US")
```

### 2. Stock Candles

用途：

- 获取日线 / 分钟线
- 做最小版选股因子

Python SDK 示例：

```python
finnhub_client.stock_candles("AAPL", "D", 1590988249, 1591852249)
```

### 3. Quote

用途：

- 获取最新价格
- 用于盘中筛选和消息推送展示

Python SDK 示例：

```python
finnhub_client.quote("AAPL")
```

### 4. Company Profile

用途：

- 获取公司基础信息
- 生成推送里的标的信息

Python SDK 示例：

```python
finnhub_client.company_profile2(symbol="AAPL")
```

### 5. Company Basic Financials

用途：

- 做基础面过滤
- 给第一版因子提供补充字段

Python SDK 示例：

```python
finnhub_client.company_basic_financials("AAPL", "all")
```

### 6. Earnings Calendar

用途：

- 过滤财报日前后波动
- 作为事件驱动提醒的补充

Python SDK 示例：

```python
finnhub_client.earnings_calendar(
    _from="2020-06-10",
    to="2020-06-30",
    symbol="",
    international=False,
)
```

### 7. Market Status

用途：

- 判断美股是否开市
- 控制 bot 的运行时段

Python SDK 示例：

```python
finnhub_client.market_status(exchange="US")
```

## 当前建议

MVP 阶段先围绕以下最小组合做：

1. `stock_symbols("US")`
2. `stock_candles(...)`
3. `quote(...)`
4. `market_status(exchange="US")`

如果后面要加事件或基本面，再补：

5. `company_profile2(...)`
6. `company_basic_financials(...)`
7. `earnings_calendar(...)`
