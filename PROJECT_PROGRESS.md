# 项目进度记录

## 当前阶段

阶段名称：`文档冻结与版本规划阶段`

当前目标不是继续写主程序，而是先把以下文档与阶段边界固化：

1. 当前策略边界确认
2. 当前版本边界确认
3. MVP 到 V5 演进计划落地
4. 团队下一轮任务口径统一

## 当前结论

- 项目目录已建立：`C:\Users\ZHAOKAI\usmart-quant`
- 本地 Git 仓库已初始化
- GitHub private repo 已创建：`Neutralmilkzzz/usmart-quant`
- 当前无法正常 `git push`，原因是到 GitHub 的 HTTPS 连接被重置
- `.env/` 已加入 `.gitignore`
- Finnhub API Key 已保存到本地 `.env/finnhub.env`
- 现阶段按老板指令，暂停新增 coding，只继续写 doc
- 后续要把 Bot 输出文案从英文改为中文，但本轮不改代码

## 已完成事项

### 1. 项目基础文档

- `PROJECT.md`
- `TEAM_ASSIGNMENTS.md`
- `README.md`
- `docs/work_docs/PRODUCT_ROADMAP_MVP_TO_V5.md`

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
- 字段确认完成后再进入实现阶段

### 立花宗茂

- 整理“筛选所有美股自选股”的文档
- 明确股票池来源、筛选口径、必要字段与输出结构

## 当前未完成事项

1. 把“英文改中文”的范围拆成可执行任务
2. 复核现有 PRD 与现有代码是否完全一致
3. 等容量恢复后决定是否继续推进 V1 落地
4. 明确 V2 到 V5 的进入条件
5. 视网络情况决定何时再尝试 push 到 GitHub

## 下一步建议

优先级从高到低：

1. 冻结当前路线图 `docs/work_docs/PRODUCT_ROADMAP_MVP_TO_V5.md`
2. 把中文化任务写入正式任务列表
3. 等容量恢复后，先做中文化与 V1 稳定化
4. 之后再决定是否进入 V2 功能增强

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

## Git 回滚定位说明

如果未来发生 Git 回滚，判断当前处于哪个阶段时，优先查看本文件。

若本文件存在，且内容与下列特征一致，则说明项目仍处于：

`文档冻结与版本规划阶段`

该阶段的特征是：

- 本轮不继续加代码
- 已有代码可视为样板或已完成底稿
- 当前优先保障版本边界、任务边界和中文化计划清晰

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
