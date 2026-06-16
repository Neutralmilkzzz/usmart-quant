# V1 测试计划

## 测试目标

V1 测试目标不是验证选股策略能赚钱。

V1 测试目标是验证工程闭环可靠：

1. 股票池能正确读取
2. Finnhub feed 能正确封装
3. 单个股票失败不会拖垮整轮扫描
4. 裸跑排序逻辑正确
5. Top 10 输出稳定
6. Telegram / Discord 消息格式正确
7. `/scan`、`/status`、`/help` 可用
8. 每小时调度不会和手动扫描并发冲突
9. AWS Linux 常驻运行时可恢复、可排错

## 测试边界

V1 不测试：

- 策略收益
- 回测表现
- beta 有效性
- 多因子有效性
- 分钟级行情
- tick 级行情
- 真实交易链路

## 测试分层

### 1. Unit Tests

单元测试只测纯逻辑，不打真实 API。

#### 1.1 Universe Loader

测试文件：

- `tests/test_universe_loader.py`

必须覆盖：

- 正常读取 `universe_100.csv`
- 只保留 P0 / P1
- P2 被排除
- 空 symbol 被跳过
- 重复 symbol 被去重
- 缺少必要列时报明确错误
- 文件不存在时报明确错误

验收：

- 输入 100 只观察池
- 输出只包含 P0 / P1
- 输出 symbol 唯一

#### 1.2 Finnhub Client Mapping

测试文件：

- `tests/test_finnhub_client.py`

使用 fake response。

必须覆盖：

- quote 正常映射到内部模型
- profile2 正常映射到内部模型
- metric 正常保存到 `metrics` 字典
- quote 缺少 `c` 时不崩溃
- quote 缺少 `dp` 时不崩溃
- API timeout 被转成可记录错误
- 单 symbol 失败返回带错误的 snapshot

验收：

- 不允许 API 异常直接向上炸穿整轮扫描

#### 1.3 Naked Strategy Selector

测试文件：

- `tests/test_selector.py`

当前策略：

- 只保留 P0 / P1
- quote 必须有 `price` 和 `day_change_pct`
- 按 `day_change_pct` 降序
- 同分时 P0 优先
- 再同分时市值高优先
- 输出 Top 10

必须覆盖：

- 涨幅最高的排第一
- P0 / P1 正常参与排序
- P2 不参与
- price 缺失的股票不参与
- day_change_pct 缺失的股票不参与
- 结果最多 10 条
- 少于 10 条时返回实际数量
- 市场关闭时仍可排序，但结果带 market closed 标记

验收：

- 排序结果可预测
- 不出现复杂因子字段依赖

#### 1.4 Message Formatter

测试文件：

- `tests/test_formatter.py`

必须覆盖：

- Top 10 格式化为文本
- 空结果返回明确消息
- market open / closed 都能显示
- 单条消息不会超过配置长度
- 超长时能拆分
- 数字格式稳定，比如百分比保留 2 位

验收：

- Telegram / Discord 共用 formatter 的核心逻辑

#### 1.5 State Machine

测试文件：

- `tests/test_state_machine.py`

必须覆盖：

- `IDLE -> RUNNING -> SUCCESS`
- `RUNNING -> PARTIAL_SUCCESS`
- `RUNNING -> FAILED`
- 正在 RUNNING 时拒绝第二次 scan
- scan 完成后恢复 IDLE
- state 能写入 `runtime/state.json`

验收：

- 并发保护可测试

### 2. Integration Tests

集成测试跑完整链路，但仍默认使用 fake Finnhub 和 fake notifier。

#### 2.1 Full Scan With Fake Feed

测试文件：

- `tests/test_scan_pipeline.py`

流程：

1. 读取测试股票池
2. fake feed 返回 quote/profile/metric
3. selector 输出 Top 10
4. formatter 生成消息
5. fake notifier 记录发送内容

验收：

- 扫描链路完整跑完
- notifier 收到 1 条或多条消息
- 状态为 SUCCESS

#### 2.2 Partial Failure

场景：

- 10 只股票中 3 只 API 失败
- 其余 7 只正常

验收：

- 状态为 PARTIAL_SUCCESS
- 输出 7 条以内结果
- 错误被记录
- 程序不退出

#### 2.3 All Failure

场景：

- 全部 symbol API 失败

验收：

- 状态为 FAILED
- 不发送误导性的 Top 10
- 发送或记录明确错误摘要

#### 2.4 Manual Scan Lock

场景：

- 自动扫描正在运行
- 用户触发 `/scan`

验收：

- 第二次扫描不启动
- 返回 `Scan already running`

### 3. Bot Command Tests

#### 3.1 Telegram Commands

建议测试：

- `/scan`
- `/status`
- `/help`

验收：

- `/scan` 能调用 scanner
- `/status` 返回最近状态
- `/help` 返回命令列表
- 非授权 chat_id 被忽略或拒绝

#### 3.2 Discord Commands

建议测试：

- `/scan`
- `/status`
- `/help`

验收：

- slash command 能调用 scanner
- 只响应配置的 guild/channel
- 已有扫描运行时返回占用提示

### 4. Manual Smoke Tests

上线前必须人工跑一次。

#### 4.1 Local Smoke

步骤：

1. 安装依赖
2. 配置 `.env/`
3. 跑一次本地 scan
4. 检查 Top 10 输出
5. 检查 runtime state

验收：

- 本地 scan 不崩
- 输出可读

#### 4.2 Telegram Smoke

步骤：

1. 启动 bot
2. 发送 `/help`
3. 发送 `/status`
4. 发送 `/scan`

验收：

- 三个命令都有响应

#### 4.3 Discord Smoke

步骤：

1. 启动 bot
2. 注册 slash commands
3. 执行 `/help`
4. 执行 `/status`
5. 执行 `/scan`

验收：

- 三个 slash commands 都可用

#### 4.4 AWS Smoke

步骤：

1. 部署到 AWS
2. 通过 systemd 启动
3. 查看 `systemctl status`
4. 查看 `journalctl`
5. 手动触发 `/scan`
6. 等待下一次小时级自动扫描

验收：

- 服务常驻
- 崩溃后能自动重启
- 日志可查
- 自动扫描可触发

## 测试数据

建议建立：

- `tests/fixtures/universe_sample.csv`
- `tests/fixtures/finnhub_quote_success.json`
- `tests/fixtures/finnhub_quote_missing_price.json`
- `tests/fixtures/finnhub_profile_success.json`
- `tests/fixtures/finnhub_metric_success.json`

测试数据必须不包含真实 API key。

## CI 建议

V1 可以先不强制 CI，但测试命令应标准化：

```bash
pytest
```

后续 GitHub push 稳定后再接 GitHub Actions。

## 最小测试完成标准

在德川家康提交 V1 代码前，至少应通过：

1. Universe loader 单元测试
2. Selector 单元测试
3. Formatter 单元测试
4. State machine 单元测试
5. Full scan fake feed 集成测试

Bot 命令测试可以在消息通道实现后补齐。
