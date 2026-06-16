# PRD：V2 因子层与策略层解耦重构

## 1. 文档信息

文档版本：`V2.0`

创建日期：`2026-06-16`

项目目录：`C:\Users\ZHAOKAI\usmart-quant`

产品负责人：织田信长

项目统筹：服部半藏

V2 重构负责人：立花宗茂

重构前检查点 commit：

- `48bac02` `Checkpoint V1 localized bot snapshot`
- `ed0b961` `Checkpoint localization tests before V2 refactor`

相关文档：

- `docs/work_docs/PRD_V1_US_STOCK_ALERT_BOT.md`
- `docs/work_docs/V1_MVP_STRATEGY.md`
- `docs/work_docs/PRODUCT_ROADMAP_MVP_TO_V5.md`
- `docs/work_docs/FINNHUB_FIELD_CATALOG.md`
- `doc/丰臣秀吉/芬虎字段因子实现清单.md`

---

## 2. V2 背景

V1 已经跑通基础 QD 链路：

`股票池 -> Finnhub feed -> 实时 quote -> 简单排序 -> Bot 推送`

当前问题是：代码虽然能跑，但研究扩展能力不够。

现有主流程中，`scanner` 直接串起股票池、feed、selector、状态写入和结果输出；`selector/ranker.py` 同时承担候选构造、过滤原因、排序规则。这样短期可用，但长期会导致两个问题：

1. 每新增一个因子，都容易改到主扫描流程。
2. 每试一个策略，都容易改到排序和候选构造细节。

V2 的目标不是立即做复杂 alpha，也不是开始回测，而是先把研究扩展的接口拆出来。

---

## 3. V2 产品目标

V2 要把系统明确拆成五层：

1. `Universe Layer`：决定扫谁
2. `Feed Layer`：决定拿什么原始数据
3. `Factor Layer`：决定从原始数据中计算哪些信号
4. `Strategy Layer`：决定如何过滤、打分、排序、选 Top N
5. `Delivery Layer`：决定如何通过 Telegram / Discord 发出结果

V2 成功后，后续新增研究逻辑时，应该主要新增 factor 或 strategy，而不是改 `scanner.py`。

---

## 4. V2 非目标

V2 不做：

- 自动交易
- 回测系统
- 历史数据库
- 复杂多因子 alpha
- 机器学习模型
- Web UI
- 多用户权限系统
- 高并发服务化
- 券商下单接口

V2 仍然是实时扫描提醒系统，只是内部结构要为后续研究预留干净接口。

---

## 5. 现有代码问题诊断

### 5.1 Scanner 职责偏重

当前 `src/stock_alert_bot/scanner.py` 负责：

- 读取股票池
- 调用 feed
- 收集 snapshot
- 调用 selector
- 判断 scan 状态
- 写入 last scan
- 更新状态机

这些职责可以保留在编排层，但策略逻辑不应该继续向 scanner 聚集。

### 5.2 Selector 与策略没有清晰边界

当前 `src/stock_alert_bot/selector/ranker.py` 负责：

- 判断 snapshot 能否入选
- 构造 `CandidateRecord`
- 写入 selected reasons
- 排序
- 截取 Top N

这些逻辑应拆成：

- 因子计算
- 过滤规则
- 策略排序
- 候选结果构造

### 5.3 Factor 概念尚未独立

当前系统已经有一些字段可以作为因子来源：

- `day_change_pct`
- `market_cap`
- `avg_volume_10d`
- `avg_volume_3m`
- `watch_priority`
- `asset_type`
- `industry`
- `metrics`

但这些字段只是散落在 snapshot 和 ranker 中，没有形成可注册、可测试、可组合的因子层。

### 5.4 Strategy 概念仍是硬编码

当前策略实际是：

1. 过滤无价格和无涨跌幅的股票
2. 按 `day_change_pct` 降序
3. 同分 P0 优先
4. 再同分市值高优先
5. 取 Top 10

这条规则应该成为一个明确的策略实现，例如：

`DayChangeTopNStrategy`

而不是藏在通用 ranker 里。

---

## 6. 目标架构

### 6.1 目标目录结构

建议 V2 目录结构：

```text
src/stock_alert_bot/
  universe/
    loader.py
  feed/
    base.py
    finnhub_client.py
  factors/
    base.py
    registry.py
    quote_factors.py
    profile_factors.py
    universe_factors.py
  strategies/
    base.py
    day_change_topn.py
    registry.py
  scanner/
    engine.py
    pipeline.py
  selector/
    filters.py
  notifier/
    formatter.py
    telegram_bot.py
    discord_bot.py
```

说明：

- `feed` 只负责取数和生成 snapshot。
- `factors` 只负责把 snapshot 转成 factor values。
- `strategies` 只负责基于 factor values 做筛选、打分和排序。
- `scanner` 只负责流程编排，不写具体策略。
- `notifier` 只负责消息输出，不关心因子怎么来的。

### 6.2 V2 数据流

V2 标准数据流：

```text
UniverseItem[]
  -> StockSnapshot[]
  -> FactorFrame
  -> StrategyResult
  -> ScanResult
  -> Telegram / Discord
```

### 6.3 核心边界

`Universe Layer` 输出：

- `UniverseItem`
- 只描述股票池身份和优先级

`Feed Layer` 输出：

- `StockSnapshot`
- 只描述原始行情、profile、metrics 和错误信息

`Factor Layer` 输出：

- `FactorValue`
- `FactorFrame`
- 只描述可研究信号

`Strategy Layer` 输出：

- `StrategyCandidate`
- `StrategyResult`
- 只描述入选、排序、分数和解释

`Delivery Layer` 输出：

- 用户可读消息

---

## 7. 数据模型设计

### 7.1 FactorValue

建议新增：

```python
@dataclass(frozen=True)
class FactorValue:
    symbol: str
    name: str
    value: float | str | bool | None
    source: str
    available: bool
    reason: str | None = None
```

字段说明：

- `symbol`：股票代码
- `name`：因子名，例如 `day_change_pct`
- `value`：因子值
- `source`：来源，例如 `quote`、`profile`、`metric`、`universe`
- `available`：是否有效
- `reason`：缺失或异常原因

### 7.2 FactorFrame

建议新增：

```python
@dataclass
class FactorFrame:
    symbol: str
    snapshot: StockSnapshot
    values: dict[str, FactorValue]
    errors: list[str]
```

作用：

- 聚合一只股票的所有因子
- 给 strategy 使用
- 保留 snapshot，便于输出时展示原始字段

### 7.3 StrategyCandidate

建议新增或替代当前 `CandidateRecord`：

```python
@dataclass
class StrategyCandidate:
    symbol: str
    display_name: str | None
    watch_priority: str
    score: float | None
    rank_fields: dict[str, float | str | bool | None]
    selected_reasons: list[str]
    missing_factors: list[str]
    snapshot: StockSnapshot
```

要求：

- `score` 可以为空，因为 V2 仍允许纯排序策略。
- `rank_fields` 用于解释为什么排在这里。
- `selected_reasons` 必须可被中文 formatter 直接展示。

---

## 8. 因子层设计

### 8.1 Factor 接口

建议定义：

```python
class Factor(Protocol):
    name: str
    required_fields: tuple[str, ...]

    def compute(self, snapshot: StockSnapshot) -> FactorValue:
        ...
```

### 8.2 第一批内置因子

V2 第一批只做低风险因子，不做研究型复杂因子。

必须支持：

- `day_change_pct`
- `price`
- `market_cap`
- `avg_volume_10d`
- `avg_volume_3m`
- `watch_priority_score`
- `is_p0`
- `asset_type`

可选支持：

- `industry`
- `has_valid_quote`
- `has_metric_data`

### 8.3 因子分类

按来源分类：

- `QuoteFactor`：来自 quote
- `ProfileFactor`：来自 profile
- `MetricFactor`：来自 metric
- `UniverseFactor`：来自股票池配置
- `DerivedFactor`：由其他字段计算得出

### 8.4 因子注册

建议新增 `FactorRegistry`：

```python
class FactorRegistry:
    def register(self, factor: Factor) -> None:
        ...

    def get(self, name: str) -> Factor:
        ...

    def compute_all(self, snapshots: list[StockSnapshot]) -> list[FactorFrame]:
        ...
```

V2 可以先用代码注册，不必做动态插件系统。

### 8.5 因子缺失处理

原则：

- 因子缺失不等于股票失败。
- 因子层要明确记录缺失原因。
- 是否剔除股票由策略层决定。

示例：

```text
day_change_pct missing -> 因子不可用
market_cap missing -> 因子不可用，但不一定剔除
avg_volume_10d missing -> 因子不可用，但不影响 V1 风格策略
```

---

## 9. 策略层设计

### 9.1 Strategy 接口

建议定义：

```python
class Strategy(Protocol):
    name: str

    def select(
        self,
        frames: list[FactorFrame],
        *,
        market_status: MarketStatus,
        top_n: int,
    ) -> StrategyResult:
        ...
```

### 9.2 StrategyResult

建议定义：

```python
@dataclass
class StrategyResult:
    strategy_name: str
    candidates: list[StrategyCandidate]
    rejected_count: int
    rejection_reasons: dict[str, int]
```

### 9.3 第一条策略

V2 必须把当前 V1 排序规则迁移成独立策略：

`DayChangeTopNStrategy`

逻辑保持不变：

1. 只接受 P0 / P1
2. 必须有 `price`
3. 必须有 `day_change_pct`
4. 按 `day_change_pct` 降序
5. 同分 P0 优先
6. 再同分市值高优先
7. 输出 Top N

### 9.4 策略解释

每个 candidate 必须带中文解释。

示例：

```text
核心观察标的
当日涨幅靠前
市场当前休市，结果基于最近可用行情
```

### 9.5 策略配置

建议配置项：

```yaml
strategy:
  active: day_change_topn
  top_n: 10
  enabled_priorities:
    - P0
    - P1
  required_factors:
    - price
    - day_change_pct
```

V2 不要求支持多个策略同时运行，但接口要允许后续扩展。

---

## 10. Scanner 重构要求

### 10.1 Scanner 新职责

V2 后 scanner 只负责流程编排：

1. 加载股票池
2. 调用 feed 拉取 snapshot
3. 调用 factor registry 计算 factor frame
4. 调用 active strategy 生成 strategy result
5. 转换为 scan result
6. 写入状态与 last scan

Scanner 不应该：

- 硬编码排序规则
- 硬编码入选理由
- 直接判断具体因子缺失是否剔除
- 直接构造复杂候选解释

### 10.2 兼容性要求

重构后外部行为保持稳定：

- `python -m stock_alert_bot.app --scan-once` 仍可用
- Telegram / Discord 输出仍可用
- `/scan`、`/status`、`/help` 仍可用
- `runtime/last_scan.json` 仍应保留核心字段
- V1 的 Top 10 逻辑不应发生非预期变化

---

## 11. 测试要求

V2 必须新增或调整测试。

### 11.1 因子层测试

必须覆盖：

- quote 因子正常计算
- profile / metric 因子正常计算
- 缺失字段返回 unavailable
- 单个因子异常不影响其他因子

### 11.2 策略层测试

必须覆盖：

- `DayChangeTopNStrategy` 与 V1 排序规则一致
- P0 同分优先
- 市值同分兜底排序
- 缺失 price 时剔除
- 缺失 `day_change_pct` 时剔除

### 11.3 Pipeline 测试

必须覆盖：

- fake feed -> factor registry -> strategy -> scan result
- 部分 symbol feed 失败仍可 `PARTIAL_SUCCESS`
- 无候选时返回 `FAILED`

### 11.4 回归测试

重构完成后至少运行：

```text
python -m pytest
python -m compileall src tests
```

---

## 12. 迁移步骤

### M1：先建接口，不改行为

新增：

- `factors/base.py`
- `factors/registry.py`
- `strategies/base.py`
- `strategies/day_change_topn.py`

当前 V1 行为不变。

### M2：迁移当前排序规则

把 `selector/ranker.py` 中的当前排序规则迁移到：

- `strategies/day_change_topn.py`

保留原有 selector wrapper，必要时做兼容转发。

### M3：接入 FactorRegistry

把 snapshot 转 factor frame。

第一批因子只覆盖当前 V1 实际使用字段。

### M4：Scanner 接入 Strategy

scanner 调用 strategy，不再直接调用旧 ranker。

### M5：清理旧 selector 逻辑

确认测试通过后，再减少旧 selector 的职责。

不要一开始就删除旧文件。

### M6：文档与配置更新

更新：

- `config/config.example.yaml`
- `README.md`
- `docs/work_docs/V1_MVP_STRATEGY.md`
- `docs/work_docs/PRODUCT_ROADMAP_MVP_TO_V5.md`

---

## 13. 宗茂任务包

立花宗茂负责 V2 重构设计与实施。

任务边界：

- 只做架构拆分
- 不新增复杂策略
- 不改变当前 Top 10 策略结果
- 不修改 Bot token / `.env`
- 不引入数据库
- 不引入回测

优先级：

1. 定义因子层接口
2. 定义策略层接口
3. 把当前 `day_change_pct` 规则迁移成独立 strategy
4. 让 scanner 通过 factor + strategy pipeline 产出结果
5. 补齐测试

---

## 14. 验收标准

V2 重构完成必须满足：

1. 原有 V1 使用方式不变
2. 当前 Top 10 排序口径不变
3. 因子层有独立接口和 registry
4. 策略层有独立接口和 registry
5. 至少有一个内置策略 `day_change_topn`
6. 新增因子不需要改 scanner 主流程
7. 新增策略不需要改 feed 或 notifier
8. 测试覆盖因子、策略、pipeline
9. `python -m pytest` 通过
10. `python -m compileall src tests` 通过

---

## 15. 风险与控制

### 15.1 风险：过度抽象

控制方式：

- V2 只抽当前已经需要的接口。
- 不做插件系统。
- 不做动态加载。
- 不做 YAML 表达复杂策略。

### 15.2 风险：重构改变行为

控制方式：

- 先 commit 当前检查点。
- 为现有 V1 排序规则补回归测试。
- 迁移后对比同一批 fake snapshots 的输出顺序。

### 15.3 风险：研究层提前复杂化

控制方式：

- 第一批因子只覆盖已有字段。
- 不做技术指标。
- 不做回测。
- 不做数据存储升级。

---

## 16. 当前结论

V2 的核心不是策略变强，而是让策略可以被替换。

当前最重要的架构目标是：

`以后新增一个因子或策略，不需要改 scanner 主流程。`

立花宗茂应以此作为重构验收线。
