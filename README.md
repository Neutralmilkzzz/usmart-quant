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
