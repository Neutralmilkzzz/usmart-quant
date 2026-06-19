# 项目进度记录

## 当前阶段

阶段名称：`V2 架构重构规划阶段`

当前目标不是直接改代码，而是先把 V2 重构边界固化：

1. 保存重构前代码检查点
2. 明确五层架构边界
3. 写出 V2 因子层与策略层解耦 PRD
4. 将重构任务分配给立花宗茂

## 当前结论

- 项目目录已建立：`C:\Users\ZHAOKAI\usmart-quant`
- 本地 Git 仓库已初始化
- GitHub private repo 已创建：`Neutralmilkzzz/usmart-quant`
- 当前无法正常 `git push`，原因是到 GitHub 的 HTTPS 连接被重置
- `.env/` 已加入 `.gitignore`
- Finnhub API Key 已保存到本地 `.env/finnhub.env`
- 重构前代码检查点已提交：`48bac02` `Checkpoint V1 localized bot snapshot`
- 重构前中文化测试检查点已提交：`ed0b961` `Checkpoint localization tests before V2 refactor`
- V2 重构方向已确定：拆出 Universe / Feed / Factor / Strategy / Delivery 五层
- 德川家康负责中文化，立花宗茂负责 V2 因子层与策略层重构
- 已确认 Finnhub 免费额度为 `60 calls/min`，项目当前决定接受低频长扫描，不优先缩小股票池
- 已新增持仓观察 MVP：支持 Telegram 命令录入持仓标的并查询当前价格、今日涨幅、整体涨幅和总盈利

## 已完成事项

### 1. 项目基础文档

- `PROJECT.md`
- `TEAM_ASSIGNMENTS.md`
- `README.md`
- `docs/work_docs/PRODUCT_ROADMAP_MVP_TO_V5.md`
- `docs/work_docs/PRD_V2_FACTOR_STRATEGY_REFACTOR.md`
- `docs/work_docs/FINNHUB_RATE_LIMIT_PLAN.md`

### 2. uSMART / Futu OpenAPI 资料落地

已保存核心本地文档，包括：

- `docs/api/`
- `docs/intro/`
- `docs/protocol/`

### 3. Finnhub 资料整理

已保存：

- `docs/finnhub/README.md`
- `docs/finnhub/Finnhub-API-README.md`
- `docs/finnhub/finnhub-python-README.md`
- `docs/finnhub/FINNHUB_API_DOCS.md`

### 4. 德川家康任务资料

已保存：

- `docs/德川加康/BOT_DEV_DOCS.md`

内容覆盖：

- Telegram Bot 发消息
- Telegram 命令配置
- Discord 发消息
- Discord Slash Command

### 5. 当前已知的其他工作产出

当前工作区里已经存在但尚未纳入 Git 跟踪的文档：

- `doc/丰臣秀吉/芬虎接口可取字段清单.md`
- `doc/丰臣秀吉/芬虎接口连通结果报告.md`
- `doc/丰臣秀吉/芬虎字段因子实现清单.md`
- `doc/丰臣秀吉/秀吉文档使用说明.md`
- `docs/work_docs/FINNHUB_CONNECTIVITY_REPORT.md`
- `docs/work_docs/FINNHUB_FIELD_CATALOG.md`

这些文档说明：字段确认与 feed 能力梳理工作已经开始，后续应纳入阶段管理。

## 当前分工状态

### 服部半藏

- 维护项目文档
- 维护分工文档
- 维护阶段进度

### 德川家康

- 开发 Telegram 版本和 Discord 版本 Bot
- 当前优先事项：打通发消息与命令 / 斜杠命令
- 参考文档：`docs/德川加康/BOT_DEV_DOCS.md`

### 丰臣秀吉

- 先确认 Finnhub API 返回字段与 feed 能力
- 先回答“能拿到哪些字段、能拼出哪些可实现因子”
- 继续负责免费额度限流方案设计
- 当前原则：接受慢速扫描，不优先缩小股票池

### 立花宗茂

- 负责 V2 因子层与策略层解耦重构
- 主参考文档：`docs/work_docs/PRD_V2_FACTOR_STRATEGY_REFACTOR.md`
- 目标：后续新增因子或策略时，不需要改 scanner 主流程

## 当前未完成事项

1. 德川家康完成 Telegram / Discord 输出中文化
2. 立花宗茂按 V2 PRD 拆出 factor registry
3. 立花宗茂按 V2 PRD 拆出 strategy registry
4. 将当前 Top 10 裸跑规则迁移为 `DayChangeTopNStrategy`
5. 丰臣秀吉设计 `55-60 calls/min` 约束下的慢速扫描方案

## 下一步建议

优先级从高到低：

1. 德川家康先完成中文化，避免用户侧输出继续混杂英文
2. 立花宗茂按 V2 PRD 先建接口，不立刻大规模删除旧代码
3. 丰臣秀吉先产出 Finnhub 免费额度节流设计，不急着缩池
4. 用回归测试锁住 V1 排序结果
5. 再迁移 scanner 到 factor + strategy pipeline

## 最新阶段更新

已新增正式 PRD：

- `docs/work_docs/PRD_V1_US_STOCK_ALERT_BOT.md`

该 PRD 已冻结 V1 的产品范围、系统模块、股票池口径、因子框架、Bot 命令、状态机、AWS Linux 部署要求、测试要求与验收标准。

已新增 V1 策略修正文档与测试计划：

- `docs/work_docs/V1_MVP_STRATEGY.md`
- `docs/work_docs/TEST_PLAN_V1.md`

当前策略口径已调整为 MVP 裸跑实时扫描：不做回测、不做 beta、不做复杂多因子叠加。V1 只做 P0 / P1 股票池内的实时 quote 筛选与 `day_change_pct` 排序，输出 Top 10 给用户人工判断。

已新增版本演进路线图：

- `docs/work_docs/PRODUCT_ROADMAP_MVP_TO_V5.md`

该文档用于说明本项目如何从 MVP 演进到 V1、V2、V3、V4、V5，并明确当前先暂停 coding、只维护文档。

已新增 V2 重构 PRD：

- `docs/work_docs/PRD_V2_FACTOR_STRATEGY_REFACTOR.md`

该文档明确 V2 的核心目标是拆出因子层与策略层，让后续新增因子或策略时不需要改 scanner 主流程。V2 不改变当前 `day_change_pct` Top 10 策略口径，不引入回测，不引入自动交易。

已新增 Finnhub 免费额度限流方案文档：

- `docs/work_docs/FINNHUB_RATE_LIMIT_PLAN.md`

该文档明确当前项目对免费额度的处理原则不是缩池，而是接受低频长扫描，按 `55-60 calls/min` 约束设计节流、排队和缓存方案。

## 2026-06-19 立花宗茂持仓观察更新

已新增持仓观察 MVP：

- 新增 `src/stock_alert_bot/portfolio.py`
- 新增 `runtime/positions.json` 作为默认持仓观察存储文件
- 新增 Telegram 命令 `/position_add SYMBOL BUY_PRICE AMOUNT`
- 新增 Telegram / Discord 查询命令 `/holdings`
- 录入时先通过当前 feed 校验 symbol，并要求能返回有效现价
- 支持观察池外标的录入，例如 `QQQ`、`SOXX` 或其他当前 feed 可识别的 symbol
- `/holdings` 一次性展示当前价、今日涨幅、买入价、现价、整体涨幅、当前市值和总盈利

验证结果：

- `python -m pytest tests\test_portfolio.py tests\test_formatter.py tests\test_scan_pipeline.py`：17 passed
- `python -m compileall src tests`：通过

## Git 回滚定位说明

如果未来发生 Git 回滚，判断当前处于哪个阶段时，优先查看本文件。

若本文件存在，且内容与下列特征一致，则说明项目仍处于：

`V2 架构重构规划阶段`

该阶段的特征是：

- 重构前检查点已经存在：`48bac02` 和 `ed0b961`
- V2 PRD 已存在：`docs/work_docs/PRD_V2_FACTOR_STRATEGY_REFACTOR.md`
- 当前计划先拆因子层和策略层，而不是新增复杂策略

## 2026-06-16 德川家康开发更新

已按 `docs/work_docs/HANDOFF_TO_TOKUGAWA.md` 和
`docs/work_docs/PRD_V1_US_STOCK_ALERT_BOT.md` 进入 V1 主程序开发。

当前已完成：

- Python `src/stock_alert_bot/` 项目骨架
- `data/universe_100.csv` 机器可读股票池
- 配置示例 `config/config.example.yaml`
- Finnhub `market-status` / `quote` / `profile2` / `metric` 封装
- P0 / P1 裸跑 selector
- Top 10 formatter
- Telegram / Discord 通知与命令模块
- 内部 scheduler
- `runtime/state.json` 与 `runtime/last_scan.json` 状态输出
- systemd 示例 `deploy/us-stock-alert-bot.service.example`
- 最小测试集

验证结果：

- `python -m pytest`：20 passed
- `python -m compileall src tests`：通过

仍需真实环境联调：

- Finnhub 真实 API 扫描烟测
- Telegram `/scan` `/status` `/help`
- Discord slash command `/scan` `/status` `/help`
- AWS Linux systemd 常驻运行
