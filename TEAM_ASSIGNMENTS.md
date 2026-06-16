# 四人分工文档

## 角色

- 老板：织田信长
- 服部半藏：项目统筹与分工维护
- 德川家康：待分配
- 丰臣秀吉：待分配
- 立花宗茂：待分配

## 当前工作原则

- 当前阶段先完成 V2 重构 PRD 和任务分配，暂不直接进入重构实现
- 现有代码已通过 `48bac02` 和 `ed0b961` 保存为重构前检查点
- 所有后续开发任务，以 `docs/work_docs/PRODUCT_ROADMAP_MVP_TO_V5.md` 为总路线图
- V2 的重点是拆出因子层和策略层，让后续研究能独立扩展

## 当前分工

- 服部半藏：维护项目文档、分工文档、路线图文档和阶段进度；负责把老板口头决策落成文档，并维护 MVP 到 V5 的演进计划
- 德川家康：负责 Telegram / Discord 用户可见文案中文化。范围包括 `/scan`、`/status`、`/help`、扫描结果标题、状态提示、错误提示。不得改动策略、feed、状态机和股票池口径。
- 丰臣秀吉：继续维护 Finnhub feed 能力文档，重点确认哪些字段已实测可用，哪些接口当前不可用。V1 只把 metric 字段作为上下文或后续研究材料，不要求参与当前排序策略。
- 立花宗茂：负责 V2 因子层与策略层解耦重构。主参考文档为 `docs/work_docs/PRD_V2_FACTOR_STRATEGY_REFACTOR.md`。目标是把当前 `day_change_pct` Top N 规则迁移成独立 strategy，并新增 factor registry / strategy registry，使后续新增因子或策略不需要改 scanner 主流程。

## 工作进度

- 丰臣秀吉：已完成 Finnhub API 首轮连通性验证，并完成“字段可实现因子”整理；结果已整理至 `doc/丰臣秀吉/芬虎接口连通结果报告.md`、`doc/丰臣秀吉/芬虎接口可取字段清单.md` 和 `doc/丰臣秀吉/芬虎字段因子实现清单.md`
- 服部半藏：已补充 V1 裸跑策略定义与 V1 测试计划，分别位于 `docs/work_docs/V1_MVP_STRATEGY.md` 和 `docs/work_docs/TEST_PLAN_V1.md`
- 服部半藏：已新增版本演进路线图 `docs/work_docs/PRODUCT_ROADMAP_MVP_TO_V5.md`，用于定义后续从文档期进入开发期的顺序
- 服部半藏：已在重构前提交当前代码检查点 `48bac02` 和中文化测试检查点 `ed0b961`，并新增 V2 重构 PRD `docs/work_docs/PRD_V2_FACTOR_STRATEGY_REFACTOR.md`

## V1 策略口径

V1 当前不是 QR 阶段，不做研究型策略。

V1 当前策略是：

- 只扫描 P0 / P1
- 只依赖 Finnhub 实时 quote 和已验证基础字段
- 过滤无效 quote
- 按 `day_change_pct` 从高到低排序
- 同分时 P0 优先
- 再同分时市值高优先
- 输出 Top 10

V1 不做：

- 回测
- beta
- 复杂多因子叠加
- 质量 / 估值 / 成长混合打分
- K 线技术指标
- 任何交易建议

## 下一轮待触发任务

- 任务 A：把 Telegram / Discord 输出文案从英文切到中文
- 任务 B：由立花宗茂按 V2 PRD 拆分因子层与策略层
- 任务 C：把当前 `day_change_pct` 排序规则迁移为 `DayChangeTopNStrategy`
- 任务 D：补因子层、策略层和 pipeline 回归测试
