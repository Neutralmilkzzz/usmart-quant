# 德川家康任务文档：Telegram / Discord Bot 开发资料

## 任务目标

开发两个版本的 Bot：

1. Telegram 版本
2. Discord 版本

当前阶段先打通两个关键能力：

- 发消息
- 命令 / 斜杠命令

---

## Telegram Bot

### 官方文档

- Telegram Bot API: https://core.telegram.org/bots/api

### 基本调用方式

Telegram Bot API 是基于 HTTP 的接口。

请求格式：

```text
https://api.telegram.org/bot<token>/METHOD_NAME
```

适合 MVP 的接入方式：

- 直接走 HTTPS API
- 本地脚本可先用轮询
- 后续稳定后可切 webhook

### 发消息

关键方法：

- `sendMessage`

作用：

- 发送纯文本消息

关键参数：

- `chat_id`
- `text`
- `parse_mode`（可选）

示例：

```bash
curl "https://api.telegram.org/bot<token>/sendMessage" \
  -d "chat_id=<chat_id>" \
  -d "text=hello from bot"
```

### 命令

关键方法：

- `setMyCommands`

作用：

- 设置 bot 命令列表

关键参数：

- `commands`
- `scope`（可选）
- `language_code`（可选）

示例思路：

```json
[
  { "command": "start", "description": "start bot" },
  { "command": "scan", "description": "run stock scan" }
]
```

### 接收更新

两种方式：

1. `getUpdates`
2. `setWebhook`

建议：

- MVP 先用 `getUpdates`
- 正式上线再考虑 `setWebhook`

### Telegram 版本第一步建议

1. 创建 bot token
2. 用 `sendMessage` 给自己发一条测试消息
3. 用 `setMyCommands` 设置 `/start`、`/scan`、`/watchlist`
4. 用 `getUpdates` 验证是否能收到命令输入

---

## Discord Bot

### 官方文档

- Application Commands: https://docs.discord.com/developers/interactions/application-commands
- Message Resource: https://docs.discord.com/developers/resources/message

### 两类核心能力

1. 发消息
2. Slash Commands

### Slash Commands

Discord 的 slash command 属于 `CHAT_INPUT` 类型的 application command。

关键点：

- `CHAT_INPUT` 就是斜杠命令
- 命令名长度 1-32
- 描述长度 1-100
- 最多 25 个 options

常见开发方式：

1. 直接调用 Discord HTTP API 注册命令
2. 用 SDK（如 `discord.py` / `discord.js`）注册命令

官方 HTTP 创建全局命令端点：

```text
POST https://discord.com/api/v10/applications/<application_id>/commands
```

一个最小 slash command 的结构：

```json
{
  "name": "scan",
  "type": 1,
  "description": "Run stock scan"
}
```

### 发消息

官方消息发送端点：

```text
POST /channels/{channel.id}/messages
```

用途：

- 向 guild text channel 或 DM channel 发消息

限制与注意事项：

- 需要 `SEND_MESSAGES`
- 回复消息时需要 `READ_MESSAGE_HISTORY`
- 单次请求最大 25 MiB

最小 JSON 示例：

```json
{
  "content": "hello from bot"
}
```

### Discord 版本第一步建议

1. 创建应用与 bot
2. 邀请 bot 进入测试服务器
3. 先测试普通消息发送
4. 注册 `/scan`
5. 让 `/scan` 返回一条固定测试消息

---

## Telegram / Discord 的职责差异

### Telegram 版本

更适合：

- 直接通知自己
- 简单命令交互
- 移动端快速查看

### Discord 版本

更适合：

- 多频道组织消息
- 结构化命令
- 后续扩展 watchlist、scan、admin 命令

---

## 对德川家康的具体开发任务建议

### 第一阶段：基础打通

Telegram：

- 打通 `sendMessage`
- 打通 `setMyCommands`
- 打通 `getUpdates`

Discord：

- 打通 channel message send
- 打通 slash command 注册
- 打通 `/scan` 的固定回复

### 第二阶段：为主项目做接口适配

统一输出一个内部接口，例如：

```python
send_alert(platform, target, text)
register_commands(platform)
```

这样后面主程序不需要关心 Telegram 和 Discord 的具体实现差异。

---

## 实施建议

先不要接入真实选股逻辑。

先做两个最小测试：

1. Telegram bot 能收到 `/scan` 并回复 `"scan ok"`
2. Discord bot 能执行 `/scan` 并回复 `"scan ok"`

只要这两步打通，消息层就算跑通了。

---

## 参考来源

- Telegram Bot API: https://core.telegram.org/bots/api
- Discord Application Commands: https://docs.discord.com/developers/interactions/application-commands
- Discord Message Resource: https://docs.discord.com/developers/resources/message
