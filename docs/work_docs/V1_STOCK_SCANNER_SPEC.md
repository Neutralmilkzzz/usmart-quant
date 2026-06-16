# V1 选股引擎实现规范

> 修订说明：V1 策略口径已在 `docs/work_docs/V1_MVP_STRATEGY.md` 中更新。
>
> 当前 V1 不做复杂多因子、不做 beta、不做回测。本文中若有“因子打分”相关旧表述，以 `V1_MVP_STRATEGY.md` 和 `PRD_V1_US_STOCK_ALERT_BOT.md` 的最新口径为准。

## 文档目的

本文件用于冻结第一版美股选股 Bot 的实现口径，避免后续 coding 过程中反复漂移。

当前阶段不是完整 PRD，而是直接指导程序框架与策略层实现的工作规范。

---

## V1 核心结论

### 扫描频率

- 自动扫描：**每小时执行一次**
- 手动扫描：用户可在 **Discord** 或 **Telegram** 中通过命令立即触发一次扫描

### 输出逻辑

- 先过滤
- 再按实时 `day_change_pct` 简单排序
- 取 **Top 10** 作为本轮候选结果

### 股票池范围

- 第一版只跑 **P0 + P1**
- 暂不跑 **P2**

---

## 关于 P0 / P1 / P2 的定义

### P0

最高优先级观察标的。

特征：

- 市场最核心
- 流动性最高
- 成交最活跃
- 用户最可能重点关注
- 应优先纳入扫描和提醒

典型例子：

- QQQ
- SPY
- AAPL
- MSFT
- NVDA
- AMZN
- GOOGL
- META
- AVGO
- AMD

### P1

中高优先级观察标的。

特征：

- 行业代表性强
- 热度高
- 流动性通常足够
- 适合纳入第一版扩展池

典型例子：

- ORCL
- CRM
- MU
- TSM
- ASML
- PANW
- CRWD
- MELI
- ABNB
- LLY

### P2

较低优先级或波动更高的观察标的。

特征：

- 主题性更强
- 噪音更大
- 波动高
- 数据和信号稳定性相对较弱
- 更适合第二阶段再纳入

典型例子：

- RKLB
- ASTS
- HOOD
- RBLX
- CAVA
- XBI

### 为什么 V1 只做 P0 + P1

原因：

1. 降低噪音
2. 提高提醒质量
3. 先验证框架是否稳定
4. 降低第一版误报率

---

## V1 输入定义

### 股票池

来源：

- `docs/立花宗茂/美股核心观察池100清单.md`

执行口径：

- 读取全部 100 只
- 仅保留 `watch_priority in {P0, P1}` 的标的进入 V1 扫描

### 数据源

当前以 Finnhub 为唯一 feed。

已确认可用接口：

- `stock/symbol?exchange=US`
- `quote`
- `stock/profile2`
- `stock/market-status`
- `stock/metric?metric=all`

暂不可用：

- `stock/candle`

因此 V1 不依赖历史 K 线技术指标。

---

## V1 因子框架

### 1. 过滤层

先做硬过滤，筛掉不适合进入候选池的标的。

建议过滤项：

- 优先级必须属于 `P0` 或 `P1`
- 市值达到最低门槛
- 交易活跃度达到最低门槛
- 市场状态允许扫描

当前建议使用字段：

- `marketCapitalization`
- `10DayAverageTradingVolume`
- `3MonthAverageTradingVolume`
- `isOpen`

### 2. 打分层

在过滤后的股票池上做多因子打分。

#### 动量组

- `13WeekPriceReturnDaily`
- `26WeekPriceReturnDaily`
- `52WeekPriceReturnDaily`

#### 质量组

- `roeTTM`
- `grossMarginTTM`
- `operatingMarginTTM`

#### 估值组

- `peTTM`
- `pb`
- `psTTM`

#### 风险 / 约束组

- `beta`
- `3MonthADReturnStd`

### 3. 排名层

建议流程：

1. 对原始字段做清洗
2. 对各因子做方向统一
3. 做标准化
4. 组合成总分
5. 按总分降序排列
6. 取 Top 10

---

## V1 输出定义

每轮扫描输出候选池 Top 10。

建议输出字段：

- `symbol`
- `name`
- `price`
- `day_change_pct`
- `market_cap`
- `momentum_score`
- `quality_score`
- `value_score`
- `composite_score`
- `selected_reason`
- `timestamp`

---

## V1 触发方式

### 自动触发

- Linux / AWS 环境下每小时跑一次

### 手动触发

Telegram：

- 命令触发立即扫描

Discord：

- Slash command 触发立即扫描

建议统一命令名：

- `/scan`

---

## 程序结构建议

### 1. `universe`

职责：

- 读取股票池
- 过滤出 P0 / P1

### 2. `feed`

职责：

- 调用 Finnhub API
- 拉取 quote / profile / metric / market status

### 3. `factor`

职责：

- 将原始字段转换为可比较的因子值

### 4. `selector`

职责：

- 执行过滤
- 执行标准化与打分
- 生成 Top 10

### 5. `notifier`

职责：

- 推送结果到 Telegram / Discord

### 6. `scheduler`

职责：

- 每小时定时执行
- 提供统一调度入口

---

## V1 暂不实现内容

以下内容延后：

- 复杂状态机
- K 线技术指标
- 分钟级 / tick 级因子
- order book / microstructure 因子
- 24 小时全时段复杂事件处理

---

## 当前阶段的下一步

1. 将 P0 / P1 股票池整理为程序可读格式
2. 固定 Finnhub 字段抓取 schema
3. 搭建 `feed / factor / selector / notifier / scheduler` 五层骨架
4. 先做命令触发扫描
5. 再做每小时定时扫描
