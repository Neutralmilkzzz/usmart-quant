# Finnhub 可获取字段总表

## 说明

本文件只整理当前 API key 实测“确实可返回”的字段，不包含仅存在于官方文档但当前未验证、或当前权限不可访问的字段。

测试时间：2026-06-16

## 1. `GET /stock/symbol?exchange=US`

字段列表：

- `currency`
- `description`
- `displaySymbol`
- `figi`
- `figiComposite`
- `isin`
- `mic`
- `shareClassFIGI`
- `symbol`
- `symbol2`
- `type`

样例记录字段含义直观说明：

- `symbol`：交易代码
- `displaySymbol`：展示用代码
- `description`：证券名称
- `mic`：市场标识
- `type`：证券类型
- `currency`：计价货币

## 2. `GET /quote?symbol=AAPL`

字段列表：

- `c`
- `d`
- `dp`
- `h`
- `l`
- `o`
- `pc`
- `t`

字段解释：

- `c`：当前价
- `d`：涨跌额
- `dp`：涨跌幅百分比
- `h`：当日最高价
- `l`：当日最低价
- `o`：当日开盘价
- `pc`：前收盘价
- `t`：时间戳

## 3. `GET /stock/profile2?symbol=AAPL`

字段列表：

- `ticker`
- `name`
- `country`
- `currency`
- `estimateCurrency`
- `exchange`
- `ipo`
- `marketCapitalization`
- `logo`
- `shareOutstanding`
- `finnhubIndustry`
- `phone`
- `weburl`
- `floatingShare`

## 4. `GET /stock/market-status?exchange=US`

字段列表：

- `exchange`
- `holiday`
- `isOpen`
- `session`
- `t`
- `timezone`

## 5. `GET /stock/metric?symbol=AAPL&metric=all`

### 顶层字段

- `metric`
- `metricType`
- `series`
- `symbol`

### `metric` 对象内字段

- `10DayAverageTradingVolume`
- `13WeekPriceReturnDaily`
- `26WeekPriceReturnDaily`
- `3MonthADReturnStd`
- `3MonthAverageTradingVolume`
- `52WeekHigh`
- `52WeekHighDate`
- `52WeekLow`
- `52WeekLowDate`
- `52WeekPriceReturnDaily`
- `5DayPriceReturnDaily`
- `assetTurnoverAnnual`
- `assetTurnoverTTM`
- `beta`
- `bookValuePerShareAnnual`
- `bookValuePerShareQuarterly`
- `bookValueShareGrowth5Y`
- `capexCagr5Y`
- `cashFlowPerShareAnnual`
- `cashFlowPerShareQuarterly`
- `cashFlowPerShareTTM`
- `cashPerSharePerShareAnnual`
- `cashPerSharePerShareQuarterly`
- `currentDividendYieldTTM`
- `currentEv/freeCashFlowAnnual`
- `currentEv/freeCashFlowTTM`
- `currentRatioAnnual`
- `currentRatioQuarterly`
- `dividendGrowthRate5Y`
- `dividendIndicatedAnnual`
- `dividendPerShareAnnual`
- `dividendPerShareTTM`
- `dividendYieldIndicatedAnnual`
- `ebitdaCagr5Y`
- `ebitdaInterimCagr5Y`
- `ebitdPerShareAnnual`
- `ebitdPerShareTTM`
- `enterpriseValue`
- `epsAnnual`
- `epsBasicExclExtraItemsAnnual`
- `epsBasicExclExtraItemsTTM`
- `epsExclExtraItemsAnnual`
- `epsExclExtraItemsTTM`
- `epsGrowth3Y`
- `epsGrowth5Y`
- `epsGrowthQuarterlyYoy`
- `epsGrowthTTMYoy`
- `epsInclExtraItemsAnnual`
- `epsInclExtraItemsTTM`
- `epsNormalizedAnnual`
- `epsTTM`
- `evEbitdaTTM`
- `evRevenueTTM`
- `focfCagr5Y`
- `forwardPE`
- `forwardPEG`
- `grossMargin5Y`
- `grossMarginAnnual`
- `grossMarginTTM`
- `inventoryTurnoverAnnual`
- `inventoryTurnoverTTM`
- `longTermDebt/equityAnnual`
- `longTermDebt/equityQuarterly`
- `marketCapitalization`
- `monthToDatePriceReturnDaily`
- `netIncomeEmployeeAnnual`
- `netIncomeEmployeeTTM`
- `netInterestCoverageAnnual`
- `netInterestCoverageTTM`
- `netMarginGrowth5Y`
- `netProfitMargin5Y`
- `netProfitMarginAnnual`
- `netProfitMarginTTM`
- `operatingMargin5Y`
- `operatingMarginAnnual`
- `operatingMarginTTM`
- `payoutRatioAnnual`
- `payoutRatioTTM`
- `pb`
- `pbAnnual`
- `pbQuarterly`
- `pcfShareAnnual`
- `pcfShareTTM`
- `peAnnual`
- `peBasicExclExtraTTM`
- `peExclExtraAnnual`
- `peExclExtraTTM`
- `pegTTM`
- `peInclExtraTTM`
- `peNormalizedAnnual`
- `peTTM`
- `pfcfShareAnnual`
- `pfcfShareTTM`
- `pretaxMargin5Y`
- `pretaxMarginAnnual`
- `pretaxMarginTTM`
- `priceRelativeToS&P50013Week`
- `priceRelativeToS&P50026Week`
- `priceRelativeToS&P5004Week`
- `priceRelativeToS&P50052Week`
- `priceRelativeToS&P500Ytd`
- `psAnnual`
- `psTTM`
- `ptbvAnnual`
- `ptbvQuarterly`
- `quickRatioAnnual`
- `quickRatioQuarterly`
- `receivablesTurnoverAnnual`
- `receivablesTurnoverTTM`
- `revenueEmployeeAnnual`
- `revenueEmployeeTTM`
- `revenueGrowth3Y`
- `revenueGrowth5Y`
- `revenueGrowthQuarterlyYoy`
- `revenueGrowthTTMYoy`
- `revenuePerShareAnnual`
- `revenuePerShareTTM`
- `revenueShareGrowth5Y`
- `roa5Y`
- `roaRfy`
- `roaTTM`
- `roe5Y`
- `roeRfy`
- `roeTTM`
- `roi5Y`
- `roiAnnual`
- `roiTTM`
- `tangibleBookValuePerShareAnnual`
- `tangibleBookValuePerShareQuarterly`
- `tbvCagr5Y`
- `totalDebt/totalEquityAnnual`
- `totalDebt/totalEquityQuarterly`
- `yearToDatePriceReturnDaily`

## 6. 当前权限下不可获取字段组

已验证当前 key 对以下接口无权限，因此其字段暂不纳入“可获取字段总表”：

- `GET /stock/candle`

错误信息：

```json
{"error":"You don't have access to this resource."}
```
