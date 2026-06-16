# 发给德川家康的开发交接说明

德川家康，请按下面顺序阅读和开发。

## 你需要阅读的文档

### 1. 主 PRD

路径：

`docs/work_docs/PRD_V1_US_STOCK_ALERT_BOT.md`

用途：

- 看完整产品需求
- 看模块拆分
- 看部署、日志、状态机、验收标准

### 2. 当前 V1 策略口径

路径：

`docs/work_docs/V1_MVP_STRATEGY.md`

用途：

- 看当前真正要实现的策略
- 这是策略口径的最高优先级文档

核心结论：

- V1 不做回测
- V1 不做 beta
- V1 不做复杂多因子叠加
- V1 不做质量 / 估值 / 成长混合打分
- V1 只做 P0 / P1 股票池的实时 quote 裸跑扫描
- 排序规则：按 `day_change_pct` 从高到低
- 同分时：P0 优先
- 再同分时：市值高优先
- 输出 Top 10

### 3. V1 测试计划

路径：

`docs/work_docs/TEST_PLAN_V1.md`

用途：

- 看必须补哪些测试
- 写代码时同步写测试
- 不要等主程序写完再补测试

最小必须覆盖：

- universe loader
- Finnhub fake feed
- 裸跑 selector
- formatter
- state machine
- fake full scan integration

### 4. Bot 开发资料

路径：

`docs/德川加康/BOT_DEV_DOCS.md`

用途：

- 看 Telegram 发消息、命令
- 看 Discord 发消息、slash command

V1 必须实现：

- Telegram `/scan`
- Telegram `/status`
- Telegram `/help`
- Discord `/scan`
- Discord `/status`
- Discord `/help`

### 5. Finnhub 字段资料

路径：

`docs/work_docs/FINNHUB_FIELD_CATALOG.md`

以及：

`doc/丰臣秀吉/芬虎接口可取字段清单.md`

用途：

- 看当前 Finnhub API key 实测能拿到哪些字段
- 不要使用未验证或当前无权限的 endpoint

当前明确不可用：

- `stock/candle`

因此不要实现 K 线技术指标。

### 6. 股票池资料

路径：

`docs/立花宗茂/美股核心观察池100清单.md`

用途：

- 用它整理程序可读的 `data/universe_100.csv`

V1 只使用：

- P0
- P1

V1 不使用：

- P2

## 不要按旧口径开发

`docs/work_docs/V1_STOCK_SCANNER_SPEC.md` 是历史规格文档，里面曾经出现过“因子打分”的旧思路。

如果该文档和以下两个文档冲突，以以下两个文档为准：

1. `docs/work_docs/V1_MVP_STRATEGY.md`
2. `docs/work_docs/PRD_V1_US_STOCK_ALERT_BOT.md`

## 你当前要开发的东西

目标：

开发 V1 美股选股提醒 Bot。

V1 本质：

一个实时扫描和提醒系统，不是量化研究系统。

核心闭环：

```text
P0/P1 股票池
-> Finnhub quote
-> 过滤无效数据
-> 按 day_change_pct 排序
-> Top 10
-> Telegram / Discord 推送
-> 每小时自动运行
-> 支持手动 /scan
```

## 推荐开发顺序

### Step 1. 项目骨架

建立 Python 项目结构：

```text
src/stock_alert_bot/
data/
config/
runtime/
tests/
```

### Step 2. 股票池

从立花宗茂文档整理：

`data/universe_100.csv`

字段至少包含：

```csv
symbol,name,asset_type,category,watch_priority,notes
```

实现：

- 读取 CSV
- 只保留 P0 / P1
- 去重
- 跳过空 symbol

### Step 3. Finnhub feed

实现 Finnhub client。

V1 需要：

- `market-status`
- `quote`
- `profile2`
- `metric`

但是 V1 排序只依赖：

- quote 当前价 `c`
- quote 日涨跌幅 `dp`

### Step 4. Selector

实现裸跑 selector。

规则：

1. 过滤 P0 / P1
2. 过滤无当前价的股票
3. 过滤无 `day_change_pct` 的股票
4. 按 `day_change_pct` 降序
5. 同分 P0 优先
6. 再同分市值高优先
7. 输出 Top 10

### Step 5. Formatter

格式化 Top 10 消息。

每条结果至少包含：

- 排名
- symbol
- name
- priority
- price
- day_change_pct
- reason

### Step 6. Fake notifier

先不要急着接真实 Telegram / Discord。

先实现 fake notifier，把消息打印到控制台或测试对象里。

确保本地 full scan 能跑通。

### Step 7. Telegram / Discord

接入真实 bot。

必须支持：

- `/scan`
- `/status`
- `/help`

### Step 8. Scheduler

实现每小时自动扫描。

要求：

- 手动扫描和自动扫描不能并发
- 已有扫描运行时，新的 `/scan` 返回 busy 信息

### Step 9. AWS 部署

目标：

- Linux
- systemd
- 24 小时运行
- 崩溃自动重启
- 日志可查

## 当前不要做的事情

不要做：

- 回测
- beta
- alpha 研究
- 复杂状态机
- 多因子 composite score
- K 线技术指标
- 分钟级策略
- 自动交易
- Web UI

## 最小验收标准

本地：

- 能读取 P0 / P1 股票池
- 能 fake feed 跑出 Top 10
- selector 测试通过
- formatter 测试通过
- state machine 测试通过

真实 feed：

- 能用 Finnhub 拉 quote
- 单只股票失败不影响整轮扫描

Bot：

- Telegram `/scan` 可用
- Discord `/scan` 可用
- `/status` 可用
- `/help` 可用

部署：

- AWS systemd 可启动
- 每小时自动扫描可用
- 日志可查
