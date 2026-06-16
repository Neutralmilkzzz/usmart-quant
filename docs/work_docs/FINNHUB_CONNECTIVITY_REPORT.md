# Finnhub API 连通性报告

## 任务背景

根据 `TEAM_ASSIGNMENTS.md` 中丰臣秀吉的分工，当前任务为：

- 测试 Finnhub API 是否可用
- 抓取股票数据
- 先以纳指 / 美股股票池为目标
- 确认可获取的交易字段

## 测试环境

- 测试时间：2026-06-16
- 测试目录：`C:\Users\ZHAOKAI\usmart-quant`
- 使用配置：`.env/finnhub.env`
- 鉴权方式：`FINNHUB_API_KEY`
- 样例股票：`AAPL`
- 市场范围：`US`

## 连通性结论

Finnhub API 当前可连通，至少以下接口已经通过实际调用验证：

- `GET /stock/symbol?exchange=US`
- `GET /quote?symbol=AAPL`
- `GET /stock/profile2?symbol=AAPL`
- `GET /stock/metric?symbol=AAPL&metric=all`
- `GET /stock/market-status?exchange=US`

当前美股股票池接口 `GET /stock/symbol?exchange=US` 可正常返回，实测返回数量为：

- `30670` 条证券记录

## 当前不可用接口

以下接口在当前 API key 权限下调用失败：

- `GET /stock/candle?symbol=AAPL&resolution=D&from=...&to=...`

返回错误：

```json
{"error":"You don't have access to this resource."}
```

这说明当前 key 已具备部分市场数据访问能力，但不具备该 K 线接口所需权限。

## 实测可获取字段概览

### 1. 美股股票池 `stock/symbol`

用途：

- 拉取美股 / 纳指候选股票池
- 作为后续行情抓取和股票筛选的基础主数据表

实测字段：

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

### 2. 实时报价 `quote`

用途：

- 获取单只股票最新价格快照

实测字段：

- `c`
- `d`
- `dp`
- `h`
- `l`
- `o`
- `pc`
- `t`

### 3. 公司资料 `profile2`

用途：

- 获取股票基础画像和公司识别信息

实测字段：

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

### 4. 基础财务指标 `stock/metric`

顶层字段：

- `metric`
- `metricType`
- `series`
- `symbol`

其中 `metric` 为最核心字段容器，当前 key 实测可返回大量财务/估值/交易统计字段，详见：

- `docs/work_docs/FINNHUB_FIELD_CATALOG.md`

### 5. 市场状态 `stock/market-status`

用途：

- 判断美股市场是否开市、处于何种交易时段

实测字段：

- `exchange`
- `holiday`
- `isOpen`
- `session`
- `t`
- `timezone`

## 对“交易字段”的实际含义说明

如果按当前权限下“直接与交易和行情最相关”的字段理解，优先可用的是：

- 股票池主数据字段：`symbol`、`displaySymbol`、`description`、`type`、`mic`
- 实时报价字段：`c`、`d`、`dp`、`h`、`l`、`o`、`pc`、`t`
- 市场状态字段：`isOpen`、`session`、`timezone`
- 部分估值/交易统计字段：如 `10DayAverageTradingVolume`、`3MonthAverageTradingVolume`、`52WeekHigh`、`52WeekLow`、`marketCapitalization`、`beta`、`peTTM`、`pb` 等

## 建议的下一步

- 若目标是先搭建“纳指 / 美股股票池 + 最新报价”的最小可用数据流，当前权限已经足够启动
- 若目标包含日 K、历史 K 线、回测特征构建，需要补足 `stock/candle` 对应权限或切换更高等级 key
- 可先以 `mic = XNAS` 过滤股票池，构造更聚焦的纳指候选集
