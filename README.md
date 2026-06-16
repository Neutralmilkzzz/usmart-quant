# uSMART / Futu OpenAPI 文档落地说明

我先帮你定位到了公开的官方 GitHub 仓库：

- 文档仓库：`https://github.com/FutunnOpen/futu-api-doc`
- Python SDK：`https://github.com/FutunnOpen/py-futu-api`
- 在线文档：`https://openapi.futunn.com/futu-api-doc/`

## 说明

当前机器到 GitHub 的 `git clone` 连接被重置，无法直接完整克隆仓库。

因此，这个目录里先保存了一份通过 GitHub 接口抓下来的“核心文档子集”，足够你第一天开始接 API、拉美股数据、看行情接口和交易接口：

- `docs/intro/intro.rst`
- `docs/intro/FutuOpenDGuide.rst`
- `docs/api/intro.rst`
- `docs/api/setup.rst`
- `docs/protocol/intro.rst`
- `docs/api/Trade_API.rst`
- `docs/api/Quote_API_core_excerpt.rst`

## 我当前的判断

公开可找到的官方 API 文档和 SDK 都在 `FutunnOpen` 这个 GitHub 账号下，没有找到一个以 `uSMART` 或“盈立证券”单独命名的公开官方文档仓库。

如果你在 `uSMART` 侧实际使用的就是这套 OpenAPI，那么这就是对应的文档来源。

## 下一步建议

你今天如果只做美股量化起步，优先看这几份：

1. `docs/intro/FutuOpenDGuide.rst`
2. `docs/api/setup.rst`
3. `docs/api/Quote_API_core_excerpt.rst`
4. `docs/api/Trade_API.rst`

其中对你最直接有用的接口一般是：

- `get_stock_basicinfo`
- `request_history_kline`
- `get_market_snapshot`
- `subscribe`
- `get_plate_list`
- `get_plate_stock`

## V1 美股选股提醒 Bot

当前主程序位于 `src/stock_alert_bot/`，实现范围以
`docs/work_docs/PRD_V1_US_STOCK_ALERT_BOT.md` 和
`docs/work_docs/V1_MVP_STRATEGY.md` 为准。

V1 只做：

- 读取 `data/universe_100.csv` 中的 P0 / P1 股票池
- 使用 Finnhub `market-status`、`quote`、`profile2`、`metric`
- 过滤无价格或无 `day_change_pct` 的标的
- 按 `day_change_pct` 降序排序，P0 同分优先，再按市值同分优先
- 输出 Top 10，并通过 Telegram / Discord 推送
- 支持 `/scan`、`/status`、`/help`

V1 不做回测、beta、多因子 composite score、K 线技术指标和自动交易。

### 本地开发

```powershell
python -m pip install -e .[dev]
python -m pytest
```

真实运行前需要在 `.env/` 下准备环境变量文件，例如 `.env/finnhub.env`：

```text
FINNHUB_API_KEY=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
DISCORD_BOT_TOKEN=...
DISCORD_CHANNEL_ID=...
DISCORD_APPLICATION_ID=...
DISCORD_GUILD_ID=...
```

本地跑一次真实扫描并打印到控制台：

```powershell
python -m stock_alert_bot.app --scan-once --console
```

启动常驻进程：

```powershell
python -m stock_alert_bot.app
```

### 部署

systemd 示例见 `deploy/us-stock-alert-bot.service.example`。部署到 AWS Linux 后，建议先完成一次 `--scan-once --console` 烟测，再启用 systemd 常驻运行。

辅助运维脚本：

- `deploy/install_deploy.sh`：安装系统依赖、拉取或更新 repo、创建 venv、安装 Python 包、生成 systemd 服务。
- `deploy/start_bot.sh`：优先通过 systemd 启动；若 service 不存在，则使用 `nohup` 启动。
- `deploy/stop_bot.sh`：优先停止 systemd 服务；若 service 不存在，则按 PID 文件或进程名停止。

默认部署目录是 `/opt/usmart-quant`。可以通过环境变量覆盖：

```bash
APP_DIR=/opt/usmart-quant \
REPO_URL=https://github.com/Neutralmilkzzz/usmart-quant.git \
BRANCH=main \
bash deploy/install_deploy.sh
```
