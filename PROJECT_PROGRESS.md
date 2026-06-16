# 项目进度记录

## 当前阶段

阶段名称：`MVP 前置梳理阶段`

当前目标还不是编写主程序，而是先把以下关键前置条件跑通：

1. 数据源可用性确认
2. Bot 消息通道开发资料整理
3. 团队分工明确
4. 本地项目骨架与文档结构建立

## 当前结论

- 项目目录已建立：`C:\Users\ZHAOKAI\usmart-quant`
- 本地 Git 仓库已初始化
- GitHub private repo 已创建：`Neutralmilkzzz/usmart-quant`
- 当前无法正常 `git push`，原因是到 GitHub 的 HTTPS 连接被重置
- `.env/` 已加入 `.gitignore`
- Finnhub API Key 已保存到本地 `.env/finnhub.env`

## 已完成事项

### 1. 项目基础文档

- `PROJECT.md`
- `TEAM_ASSIGNMENTS.md`
- `README.md`

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

1. 将当前未跟踪的工作文档纳入 Git 管理
2. 明确第一版美股股票池定义
3. 明确 Finnhub 可支持的实际因子集合
4. 决定 Telegram / Discord 哪一个先做主通道
5. 输出主程序 PRD 或系统设计草稿

## 下一步建议

优先级从高到低：

1. 整理并确认丰臣秀吉产出的字段文档
2. 让立花宗茂提交“美股自选股筛选文档”
3. 基于字段能力讨论第一版可实现因子
4. 再进入主程序框架设计

## Git 回滚定位说明

如果未来发生 Git 回滚，判断当前处于哪个阶段时，优先查看本文件。

若本文件存在，且内容与下列特征一致，则说明项目仍处于：

`MVP 前置梳理阶段`

该阶段的特征是：

- 还没有正式进入主程序编码
- 正在确认 feed、字段、Bot 通道和筛选框架
- 分工已建立，但策略与状态机尚未定稿
