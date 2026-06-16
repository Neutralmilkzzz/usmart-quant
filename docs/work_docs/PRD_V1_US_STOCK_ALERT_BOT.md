# PRD：V1 美股选股提醒 Bot

## 1. 文档信息

文档版本：`V1.0`

创建日期：`2026-06-16`

项目目录：`C:\Users\ZHAOKAI\usmart-quant`

产品负责人：织田信长

项目统筹：服部半藏

主要开发负责人建议：德川家康

相关前置文档：

- `docs/work_docs/V1_STOCK_SCANNER_SPEC.md`
- `docs/work_docs/V1_MVP_STRATEGY.md`
- `docs/work_docs/TEST_PLAN_V1.md`
- `docs/work_docs/FINNHUB_FIELD_CATALOG.md`
- `doc/丰臣秀吉/芬虎字段因子实现清单.md`
- `docs/立花宗茂/美股核心观察池100清单.md`
- `docs/德川加康/BOT_DEV_DOCS.md`

重要修订：

- V1 策略以 `docs/work_docs/V1_MVP_STRATEGY.md` 为准
- V1 不做回测、不做 beta、不做复杂多因子叠加
- V1 当前只是实时扫描和提醒系统，不是已验证 alpha 策略

---

## 2. 项目背景

本项目要开发一个 24 小时运行在 Linux / AWS 服务器上的美股选股提醒 Bot。

Bot 不负责自动交易，也不连接券商下单接口。它只做以下事情：

1. 定时扫描一组预设美股观察池
2. 基于 Finnhub 可用 feed 抓取行情与基础字段
3. 使用 V1 裸跑规则过滤无效 quote，并按实时涨跌幅排序
4. 选出 Top 10 候选股票供人工判断
5. 通过 Telegram 和 Discord 推送结果
6. 支持用户通过命令立即触发一次扫描

本项目的核心目标不是追求第一版策略有效性，而是先跑通完整工程闭环：

`股票池 -> feed -> 实时 quote -> 裸跑排序 -> Top 10 -> 消息推送 -> Linux 常驻运行`

---

## 3. 当前已确认事实

### 3.1 股票池

已由立花宗茂整理出 100 只美股核心观察池：

- 25 只 ETF
- 75 只个股
- 每个标的带有 `P0 / P1 / P2` 优先级

V1 只扫描：

- `P0`
- `P1`

V1 暂不扫描：

- `P2`

### 3.2 数据源

V1 数据源固定为 Finnhub。

当前 API key 已验证可用接口：

- `GET /stock/symbol?exchange=US`
- `GET /quote?symbol=...`
- `GET /stock/profile2?symbol=...`
- `GET /stock/market-status?exchange=US`
- `GET /stock/metric?symbol=...&metric=all`

当前 API key 已验证不可用接口：

- `GET /stock/candle`

因此 V1 不做 K 线技术指标，不做分钟级行情，不做逐笔或盘口因子。

### 3.3 触发方式

V1 必须支持两类触发：

1. 每小时自动扫描一次
2. 用户通过 Telegram / Discord 命令立即触发一次扫描

### 3.4 输出方式

V1 同时支持：

- Telegram 消息推送
- Discord 消息推送

---

## 4. 产品目标

### 4.1 MVP 目标

完成一个可以稳定运行的美股扫描提醒系统。

MVP 成功标准：

1. 程序能读取 P0 / P1 股票池
2. 程序能调用 Finnhub 拉取所需字段
3. 程序能对候选池做过滤和简单排序
4. 程序能输出 Top 10
5. 程序能推送到 Telegram
6. 程序能推送到 Discord
7. 程序能每小时自动运行
8. 用户能用命令手动触发扫描
9. 程序能在 AWS Linux 上通过 systemd 常驻运行
10. 程序发生 API 错误时不会崩溃退出

### 4.2 非目标

V1 不做：

- 自动下单
- 账户持仓管理
- 真实交易执行
- 回测系统
- beta 因子
- 复杂多因子叠加
- 未验证 alpha 策略
- 分钟级策略
- tick 级策略
- order book 微观结构策略
- Web UI
- 多用户权限系统
- 复杂策略配置后台

---

## 5. 用户角色

### 5.1 老板 / 投资决策者

用户：织田信长

主要行为：

- 接收每小时选股提醒
- 通过手机快速查看候选股
- 通过命令手动触发扫描
- 根据 Bot 输出进一步人工判断是否交易

### 5.2 Bot 开发者

主要执行者：德川家康

主要职责：

- 搭建程序框架
- 实现 feed 接入
- 实现扫描引擎
- 实现 Telegram / Discord 推送
- 实现 Linux 部署

### 5.3 策略维护者

主要职责：

- 维护股票池
- 调整 V1 排序口径
- 调整过滤阈值
- 观察提醒质量

---

## 6. 核心用户故事

### 6.1 自动扫描

作为老板，我希望系统每小时自动扫描一次 P0 / P1 美股观察池，并把 Top 10 结果发到我的手机上，这样我不用自己手动盯盘。

验收条件：

- 程序每小时触发一次扫描
- 扫描完成后发送 Telegram 和 Discord 消息
- 消息包含 Top 10 股票和触发理由
- 单次扫描失败时记录错误，不影响下一小时扫描

### 6.2 手动扫描

作为老板，我希望在 Telegram 或 Discord 里输入命令后，Bot 能立即执行一次扫描并返回结果。

验收条件：

- Telegram 支持 `/scan`
- Discord 支持 `/scan`
- 命令触发后立即开始扫描
- 扫描期间避免重复执行并发扫描
- 扫描完成后返回 Top 10

### 6.3 查看状态

作为老板，我希望能查询 Bot 是否正在运行、上次扫描时间、上次扫描是否成功。

验收条件：

- Telegram 支持 `/status`
- Discord 支持 `/status`
- 返回内容至少包含：
  - 当前运行状态
  - 上次扫描时间
  - 上次扫描结果数量
  - 上次错误信息，如有

### 6.4 查看帮助

作为老板，我希望能通过命令查看当前支持哪些操作。

验收条件：

- Telegram 支持 `/help`
- Discord 支持 `/help`
- 返回命令列表和简短说明

---

## 7. 功能范围

## 7.1 股票池模块

### 功能要求

程序需要维护一份机器可读的股票池文件。

建议文件：

- `data/universe_100.csv`

V1 必须从该文件读取股票池。

字段建议：

```csv
symbol,name,asset_type,category,watch_priority,notes
```

字段解释：

- `symbol`：股票代码，例如 `AAPL`
- `name`：名称
- `asset_type`：`stock` 或 `etf`
- `category`：分类，例如 `core_tech`、`semi`、`broad_etf`
- `watch_priority`：`P0`、`P1`、`P2`
- `notes`：纳入原因

### V1 处理逻辑

1. 读取 `data/universe_100.csv`
2. 校验必要字段是否存在
3. 去除空 symbol
4. 去重
5. 只保留 `watch_priority in ["P0", "P1"]`
6. 输出本轮扫描股票列表

### 异常处理

- 文件不存在：程序启动失败，并输出明确错误
- 字段缺失：程序启动失败，并指出缺失字段
- P0 / P1 为空：程序启动失败
- 单个 symbol 格式异常：跳过并记录 warning

---

## 7.2 Finnhub Feed 模块

### 功能要求

Feed 模块负责统一访问 Finnhub。

必须封装为独立模块，不允许业务层直接散落 HTTP 请求。

建议接口：

```python
get_market_status(exchange: str = "US") -> MarketStatus
get_quote(symbol: str) -> Quote
get_profile(symbol: str) -> Profile
get_metrics(symbol: str) -> Metrics
fetch_snapshot(symbol: str) -> StockSnapshot
```

### 必须使用的 Finnhub 接口

#### Market Status

用途：

- 判断当前美股市场状态
- 写入扫描上下文

Endpoint：

```text
GET /stock/market-status?exchange=US
```

关键字段：

- `isOpen`
- `session`
- `holiday`
- `timezone`
- `t`

#### Quote

用途：

- 获取当前价和日内变化

Endpoint：

```text
GET /quote?symbol={symbol}
```

关键字段：

- `c`：当前价
- `d`：涨跌额
- `dp`：涨跌幅百分比
- `h`：当日高
- `l`：当日低
- `o`：开盘价
- `pc`：前收盘价
- `t`：时间戳

#### Profile

用途：

- 获取公司基础信息

Endpoint：

```text
GET /stock/profile2?symbol={symbol}
```

关键字段：

- `ticker`
- `name`
- `country`
- `currency`
- `exchange`
- `ipo`
- `marketCapitalization`
- `shareOutstanding`
- `floatingShare`
- `finnhubIndustry`

#### Metrics

用途：

- 获取估值、质量、成长、动量、风险等字段

Endpoint：

```text
GET /stock/metric?symbol={symbol}&metric=all
```

关键字段见：

- `docs/work_docs/FINNHUB_FIELD_CATALOG.md`
- `doc/丰臣秀吉/芬虎字段因子实现清单.md`

### API 可靠性要求

Feed 模块必须具备：

- 请求超时
- 重试
- 错误码处理
- rate limit 处理
- 缺失字段容错
- 单 symbol 失败不影响全局扫描

建议默认值：

- HTTP timeout：`10s`
- retry 次数：`3`
- retry backoff：指数退避，初始 `1s`

### API Key

API key 从环境变量读取：

```text
FINNHUB_API_KEY
```

不允许硬编码。

不允许提交 `.env/`。

---

## 7.3 原始数据结构

建议内部统一成 `StockSnapshot`。

字段：

```python
symbol: str
name: str | None
asset_type: str | None
watch_priority: str
price: float | None
day_change: float | None
day_change_pct: float | None
day_high: float | None
day_low: float | None
day_open: float | None
prev_close: float | None
market_cap: float | None
industry: str | None
metrics: dict
quote_timestamp: int | None
fetched_at: datetime
errors: list[str]
```

要求：

- 保留原始 `metrics` 字典
- 抽取常用字段到顶层
- 单个字段缺失不应导致整只股票失败

---

## 7.4 V1 裸跑策略模块

### 功能要求

V1 不实现复杂因子模块。

策略模块只负责把 `StockSnapshot` 转换为一个可排序的候选记录。

建议输出结构：

```python
CandidateRecord
```

字段：

```python
symbol
name
watch_priority
price
day_change_pct
market_cap
avg_volume_10d
avg_volume_3m
selected_reason
missing_fields
```

### V1 排序规则

当前策略只使用实时 quote 的 `day_change_pct`。

排序规则：

1. `day_change_pct` 从高到低
2. 同分时 `P0` 优先于 `P1`
3. 再同分时 `market_cap` 更高者优先

当前排序不使用：

- beta
- 质量因子
- 估值因子
- 成长因子
- 多因子 composite score

Metric 字段可以抓取和保存，但 V1 仅作为上下文或后续研究材料。

### 缺失字段处理

原则：

- 不因单字段缺失直接剔除股票
- `price` 或 `day_change_pct` 缺失的股票不能参与 V1 排序

建议规则：

- `price` 缺失：跳过
- `day_change_pct` 缺失：跳过
- `market_cap` 缺失：仍可参与，但同分时排在有市值数据的标的之后

---

## 7.5 过滤模块

### 过滤逻辑

V1 使用“先过滤，再排序”。

硬过滤条件：

1. `watch_priority` 必须是 `P0` 或 `P1`
2. 当前价格必须存在
3. 当前涨跌幅必须存在

默认配置建议：

```yaml
require_price: true
require_day_change_pct: true
```

说明：

- 市值和成交量字段可以展示，但 V1 不强制作为筛选条件
- 后续若要增加阈值，必须先作为配置项添加，不要写死

---

## 7.6 选择器模块

### 功能要求

选择器负责输出 Top 10。

流程：

1. 接收全部 `FactorRecord`
2. 应用过滤条件
3. 按 V1 排序规则排序
4. 取前 10
5. 生成 `selected_reason`

### selected_reason 规则

每只入选股票至少给出 1 到 3 条理由。

示例：

```text
P0/P1 观察池内当日涨幅靠前。
```

生成规则：

- 若是 P0：加入“核心观察标的”
- 若 `day_change_pct` 排名前 10：加入“当日涨幅靠前”
- 若市场关闭：加入“市场关闭，基于最近 quote”
- 若 profile / metric 字段缺失：不影响 reason

---

## 7.7 消息推送模块

### 支持通道

V1 支持：

- Telegram
- Discord

两个通道共用同一个扫描结果，不允许各自重复跑一遍扫描。

### 消息格式

每轮扫描发送一条 summary 消息。

建议格式：

```text
US Stock Scan - Top 10
Time: 2026-06-16 10:00 ET
Universe: P0/P1
Market: Open

1. NVDA | Price 132.40 | Day +2.4% | Priority P0
   Reason: 核心观察标的；当日涨幅靠前

2. MSFT | Price 445.10 | Day +0.8% | Priority P0
   Reason: 核心观察标的；当日涨幅靠前
```

每个标的至少展示：

- 排名
- symbol
- price
- day_change_pct
- selected_reason

可选展示：

- market_cap

### 长消息处理

Telegram 和 Discord 都可能有消息长度限制。

要求：

- 若消息过长，拆分为多条
- Top 10 通常应控制在单条消息内
- 失败时记录错误

---

## 7.8 Bot 命令模块

### 统一命令

V1 支持以下命令：

```text
/scan
/status
/help
```

### `/scan`

作用：

- 立即触发一次扫描

行为：

1. 检查当前是否已有扫描任务在运行
2. 若无任务，立即启动扫描
3. 扫描完成后返回 Top 10
4. 若扫描失败，返回错误摘要

并发规则：

- 同一时间只允许一个扫描任务运行
- 若已有扫描任务运行，返回：

```text
Scan already running. Please wait.
```

### `/status`

返回：

- bot 是否在线
- scheduler 是否启用
- 上次扫描时间
- 上次扫描是否成功
- 上次 Top 10 数量
- 上次错误

### `/help`

返回：

```text
/scan - run scan now
/status - show bot and scanner status
/help - show commands
```

### Telegram 命令实现要求

可以先用 polling。

V1 接受：

- 本地或 AWS 上用 polling 运行

V1 暂不要求：

- webhook
- HTTPS 证书
- 多用户权限

### Discord 命令实现要求

必须支持 slash command。

建议：

- 开发环境先注册 guild command，生效快
- 稳定后再考虑 global command

---

## 7.9 Scheduler 模块

### 功能要求

自动扫描每小时运行一次。

建议方式：

- 程序内部使用 APScheduler
- 或者 Linux systemd timer / cron

V1 推荐：

- 程序内部 scheduler
- systemd 只负责守护进程

原因：

- 手动命令和自动扫描可共享同一个锁、状态和上下文
- 更容易避免并发扫描

### 定时规则

默认：

```text
每小时整点运行一次
```

配置项：

```yaml
scan_interval_minutes: 60
```

### 市场状态处理

V1 可接受美股休市时仍然运行扫描，但消息中必须标注市场状态。

建议：

- 若 `market_status.isOpen = false`，仍允许扫描
- 消息顶部显示 `Market: Closed`
- 后续版本可配置“只在开市时扫描”

---

## 7.10 状态机

V1 需要一个清晰但不过度复杂的运行状态机。

### Scanner 状态

状态枚举：

```text
IDLE
SCHEDULED
RUNNING
SUCCESS
PARTIAL_SUCCESS
FAILED
COOLDOWN
```

### 状态定义

#### IDLE

当前没有扫描任务。

#### SCHEDULED

定时器已计划下一次扫描。

#### RUNNING

扫描正在执行。

#### SUCCESS

扫描完成，且至少输出 1 条候选结果，无关键错误。

#### PARTIAL_SUCCESS

扫描完成，但部分 symbol 抓取失败。

#### FAILED

扫描失败，没有可用结果。

#### COOLDOWN

扫描刚结束，短时间内避免重复触发。

### 状态转移

```text
IDLE -> RUNNING
SCHEDULED -> RUNNING
RUNNING -> SUCCESS
RUNNING -> PARTIAL_SUCCESS
RUNNING -> FAILED
SUCCESS -> IDLE
PARTIAL_SUCCESS -> IDLE
FAILED -> IDLE
```

### 并发控制

规则：

- 任意时刻只能有一个 `RUNNING`
- 自动扫描触发时，如果已有手动扫描在运行，则跳过本轮自动扫描
- 手动扫描触发时，如果已有自动扫描在运行，则返回“扫描正在运行”

### 状态持久化

V1 最少需要内存状态。

建议同时写入本地状态文件：

- `runtime/state.json`

内容：

```json
{
  "last_scan_started_at": "...",
  "last_scan_finished_at": "...",
  "last_scan_status": "SUCCESS",
  "last_result_count": 10,
  "last_error": null
}
```

---

## 8. 技术方案

## 8.1 推荐语言

推荐使用 Python。

原因：

- 适合数据处理
- Finnhub Python SDK 可用
- Telegram / Discord Bot 库成熟
- Linux 部署简单
- 后续接 pandas / numpy / sklearn 方便

## 8.2 推荐依赖

建议：

```text
python-dotenv
pydantic
httpx
tenacity
pandas
numpy
APScheduler
python-telegram-bot
discord.py
PyYAML
structlog 或 logging
pytest
```

是否使用 Finnhub 官方 SDK：

- 可以使用
- 但建议封装在 `feed` 模块里
- 不要让策略层依赖 SDK 细节

## 8.3 推荐目录结构

```text
usmart-quant/
  src/
    stock_alert_bot/
      __init__.py
      app.py
      config.py
      models.py
      universe/
        __init__.py
        loader.py
      feed/
        __init__.py
        finnhub_client.py
      factors/
        __init__.py
        calculator.py
        scoring.py
      selector/
        __init__.py
        filters.py
        ranker.py
      notifier/
        __init__.py
        telegram_bot.py
        discord_bot.py
        formatter.py
      scheduler/
        __init__.py
        runner.py
      state/
        __init__.py
        machine.py
        store.py
      utils/
        __init__.py
        logging.py
  data/
    universe_100.csv
  config/
    config.example.yaml
  runtime/
    .gitkeep
  tests/
  docs/
  .env/
  .gitignore
  pyproject.toml
  README.md
```

## 8.4 配置文件

建议提供：

- `config/config.example.yaml`

示例：

```yaml
scanner:
  scan_interval_minutes: 60
  top_n: 10
  enabled_priorities:
    - P0
    - P1

filters:
  min_market_cap: 10000
  min_avg_volume_10d: 1000000
  min_avg_volume_3m: 1000000

strategy:
  sort_field: day_change_pct
  sort_direction: desc
  prefer_p0_on_tie: true

finnhub:
  timeout_seconds: 10
  max_retries: 3

notifier:
  telegram_enabled: true
  discord_enabled: true
```

## 8.5 环境变量

`.env/` 目录不进入 Git。

必需环境变量：

```text
FINNHUB_API_KEY
```

Telegram 需要：

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

Discord 需要：

```text
DISCORD_BOT_TOKEN
DISCORD_CHANNEL_ID
DISCORD_APPLICATION_ID
DISCORD_GUILD_ID
```

---

## 9. 数据存储

V1 不需要数据库。

本地文件即可：

- `runtime/state.json`
- `runtime/last_scan.json`
- `runtime/logs/`

### last_scan.json

建议保存最近一次 Top 10 完整结果。

用途：

- `/status` 可引用
- 程序重启后仍知道上次结果
- debug 方便

---

## 10. 日志与监控

### 日志要求

必须记录：

- 程序启动
- 程序停止
- 自动扫描触发
- 手动扫描触发
- 每轮扫描开始时间
- 每轮扫描结束时间
- 扫描股票数量
- 成功数量
- 失败数量
- Top 10 输出
- API 错误
- 推送错误

### 日志级别

- `INFO`：正常流程
- `WARNING`：单 symbol 失败、字段缺失
- `ERROR`：整轮扫描失败、推送失败
- `DEBUG`：开发调试

### 日志位置

建议：

- 标准输出给 systemd 捕获
- 同时可选写入 `runtime/logs/app.log`

---

## 11. 部署要求

## 11.1 目标环境

目标环境：

- AWS Linux 服务器
- 24 小时运行
- systemd 守护

## 11.2 systemd 服务

建议服务名：

```text
us-stock-alert-bot.service
```

行为：

- 开机自启
- 崩溃自动重启
- 输出日志到 journald

建议 systemd 配置：

```ini
[Unit]
Description=US Stock Alert Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/opt/usmart-quant
EnvironmentFile=/opt/usmart-quant/.env/finnhub.env
ExecStart=/opt/usmart-quant/.venv/bin/python -m stock_alert_bot.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

实际路径可按 AWS 服务器目录调整。

## 11.3 部署步骤

建议：

1. 将 repo 拉到 AWS
2. 创建 Python venv
3. 安装依赖
4. 创建 `.env/` 并写入 token
5. 配置 `config/config.yaml`
6. 运行一次手动扫描测试
7. 配置 systemd
8. 启动服务
9. 查看日志

---

## 12. 安全要求

### 12.1 Secret 管理

禁止提交：

- Finnhub API Key
- Telegram Bot Token
- Discord Bot Token
- Discord channel / guild 的敏感配置，如需要隐藏

必须加入 `.gitignore`：

```text
.env/
runtime/
```

### 12.2 命令权限

V1 可先不做复杂多用户权限。

但建议最少实现：

- Telegram 只响应指定 `chat_id`
- Discord 只响应指定 guild / channel

否则 Bot 被邀请到其他地方后可能被误用。

---

## 13. 错误处理

### 13.1 Finnhub API 失败

单 symbol 失败：

- 记录 warning
- 继续扫描其他 symbol

大量 symbol 失败：

- 若可用结果仍 >= 1，状态为 `PARTIAL_SUCCESS`
- 若可用结果为 0，状态为 `FAILED`

### 13.2 推送失败

Telegram 失败：

- 记录 error
- Discord 仍然尝试发送

Discord 失败：

- 记录 error
- Telegram 仍然尝试发送

两者都失败：

- 状态写入失败原因
- 不让程序退出

### 13.3 配置缺失

启动时检查：

- `FINNHUB_API_KEY`
- 至少一个通知通道可用
- 股票池文件存在

缺失关键配置时：

- 程序启动失败
- 打印明确错误

---

## 14. 测试要求

## 14.1 单元测试

必须覆盖：

- 股票池读取
- P0 / P1 过滤
- 缺失字段处理
- 裸跑排序规则
- Top 10 输出
- 消息格式化
- 状态机转移

## 14.2 集成测试

必须覆盖：

- 使用 fake Finnhub client 跑完整扫描
- 使用 fake notifier 验证消息发送
- `/scan` 命令触发扫描
- 并发 scan 只执行一次

## 14.3 手动测试

上线前手动验证：

1. 本地运行程序
2. 执行一次 scan
3. Telegram 收到消息
4. Discord 收到消息
5. `/status` 正常返回
6. 断网或 API 失败时程序不崩

---

## 15. 验收标准

V1 完成必须满足：

1. `python -m stock_alert_bot.app` 可启动
2. 能读取 P0 / P1 股票池
3. 能调用 Finnhub 获取 quote / profile / metric
4. 能完成过滤和裸跑排序
5. 能产出 Top 10
6. 能发送 Telegram 消息
7. 能发送 Discord 消息
8. Telegram `/scan` 可用
9. Discord `/scan` 可用
10. `/status` 可用
11. 每小时自动扫描可用
12. 单 symbol API 失败不影响整轮扫描
13. `.env/` 不进入 Git
14. AWS Linux 上可用 systemd 常驻运行

---

## 16. 里程碑

### M1：项目骨架

完成：

- Python 项目结构
- 配置加载
- 日志
- 股票池 CSV
- 基础模型

### M2：Feed 打通

完成：

- Finnhub client
- market status
- quote
- profile2
- metric
- 错误处理与重试

### M3：裸跑选股

完成：

- 过滤模块
- 按 `day_change_pct` 排序
- Top 10 输出

### M4：消息推送

完成：

- Telegram 推送
- Discord 推送
- 消息 formatter

### M5：命令与调度

完成：

- Telegram `/scan`
- Discord `/scan`
- `/status`
- 每小时 scheduler
- 并发锁

### M6：AWS 部署

完成：

- systemd service
- AWS 上 24 小时运行
- 日志检查
- 重启恢复

---

## 17. 开发任务拆分建议

理论上一个 AI 可以完成全部开发。

若要并行，可以拆成三个工作流：

### 工作流 A：核心扫描引擎

负责人建议：德川家康

内容：

- 项目骨架
- feed
- selector
- state
- scheduler

### 工作流 B：通知通道

负责人建议：可由另一个 AI 并行

内容：

- Telegram bot
- Discord bot
- slash command
- message formatter

### 工作流 C：数据与配置

负责人建议：立花宗茂 / 丰臣秀吉

内容：

- universe csv
- field schema
- V1 策略口径说明
- config defaults

如果只安排一个 AI，优先顺序应为：

1. 核心扫描引擎
2. Telegram 推送
3. Discord 推送
4. 定时调度
5. AWS 部署

---

## 18. V1 之后的扩展方向

V2 可以考虑：

- 引入 K 线 feed
- 增加技术指标
- 增加盘中突破逻辑
- 增加重复提醒抑制
- 增加 watchlist 动态更新
- 增加持仓状态标记
- 增加简单 Web dashboard
- 增加更复杂的状态机
- 增加多 feed fallback

---

## 19. 当前立即下一步

德川家康拿到本 PRD 后，建议先做：

1. 创建 Python 项目骨架
2. 整理 `data/universe_100.csv`
3. 创建 `config/config.example.yaml`
4. 实现 `universe.loader`
5. 实现 Finnhub feed client
6. 用 fake notifier 先跑通本地 scan

在本地 scan 能产出 Top 10 之前，不要先写复杂 Telegram / Discord 命令逻辑。
