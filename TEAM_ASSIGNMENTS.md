# 四人分工文档

## 角色

- 老板：织田信长
- 服部半藏：项目统筹与分工维护
- 德川家康：待分配
- 丰臣秀吉：待分配
- 立花宗茂：待分配

## 当前分工

- 服部半藏：维护项目文档与分工文档
- 德川家康：基于 `docs/work_docs/PRD_V1_US_STOCK_ALERT_BOT.md`、`docs/work_docs/V1_MVP_STRATEGY.md` 和 `docs/work_docs/TEST_PLAN_V1.md` 开发 V1 美股选股提醒 Bot。重点是工程闭环：股票池读取、Finnhub quote 拉取、裸跑排序、Top 10 输出、Telegram / Discord 推送、命令触发、每小时调度、AWS 常驻运行。不要在 V1 中实现复杂多因子、beta、回测或未验证 alpha。
- 丰臣秀吉：继续维护 Finnhub feed 能力文档，重点确认哪些字段已实测可用，哪些接口当前不可用。V1 只把 metric 字段作为上下文或后续研究材料，不要求参与当前排序策略。
- 立花宗茂：继续维护 100 只美股观察池和 P0 / P1 / P2 分层。V1 只使用 P0 / P1；P2 暂不进入扫描。若有新增标的，需说明纳入理由和优先级。

## 工作进度

- 丰臣秀吉：已完成 Finnhub API 首轮连通性验证，并完成“字段可实现因子”整理；结果已整理至 `doc/丰臣秀吉/芬虎接口连通结果报告.md`、`doc/丰臣秀吉/芬虎接口可取字段清单.md` 和 `doc/丰臣秀吉/芬虎字段因子实现清单.md`
- 服部半藏：已补充 V1 裸跑策略定义与 V1 测试计划，分别位于 `docs/work_docs/V1_MVP_STRATEGY.md` 和 `docs/work_docs/TEST_PLAN_V1.md`

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
