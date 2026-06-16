from __future__ import annotations

import json
import logging
import urllib.parse
import urllib.request
from typing import Any

from stock_alert_bot.notifier.commands import BotCommandHandler

LOGGER = logging.getLogger(__name__)


class DiscordNotifier:
    name = "discord"

    def __init__(
        self,
        *,
        token: str,
        channel_id: str,
        application_id: str | None = None,
        guild_id: str | None = None,
        timeout_seconds: float = 10,
    ) -> None:
        self.token = token
        self.channel_id = str(channel_id)
        self.application_id = str(application_id) if application_id else None
        self.guild_id = str(guild_id) if guild_id else None
        self.timeout_seconds = timeout_seconds
        self.base_url = "https://discord.com/api/v10"

    def send_messages(self, messages: list[str]) -> None:
        for message in messages:
            self._request(
                "POST",
                f"/channels/{self.channel_id}/messages",
                {"content": message},
            )

    def register_slash_commands(self) -> None:
        if not self.application_id:
            raise ValueError("DISCORD_APPLICATION_ID is required to register slash commands.")
        commands = [
            {"name": "scan", "type": 1, "description": "立即执行一次扫描"},
            {"name": "status", "type": 1, "description": "查看 Bot 和扫描器状态"},
            {"name": "progress", "type": 1, "description": "查看当前扫描进度"},
            {"name": "help", "type": 1, "description": "查看命令列表"},
        ]
        if self.guild_id:
            endpoint = f"/applications/{self.application_id}/guilds/{self.guild_id}/commands"
        else:
            endpoint = f"/applications/{self.application_id}/commands"
        self._request("PUT", endpoint, commands)

    def run_slash_bot(self, command_handler: BotCommandHandler) -> None:
        try:
            import discord
            from discord import app_commands
        except ImportError as exc:
            raise RuntimeError("discord.py is required for Discord slash command polling.") from exc

        intents = discord.Intents.default()
        client = discord.Client(intents=intents)
        tree = app_commands.CommandTree(client)
        allowed_channel_id = int(self.channel_id)
        guild = discord.Object(id=int(self.guild_id)) if self.guild_id else None

        async def _send_response(interaction: discord.Interaction, command: str) -> None:
            if interaction.channel_id != allowed_channel_id:
                await interaction.response.send_message("This channel is not configured.", ephemeral=True)
                return
            await interaction.response.defer(thinking=True)
            responses = command_handler.handle_command(command)
            await interaction.followup.send(responses[0])
            for extra in responses[1:]:
                await interaction.followup.send(extra)

        @tree.command(name="scan", description="立即执行一次扫描", guild=guild)
        async def scan(interaction: discord.Interaction) -> None:
            await _send_response(interaction, "/scan")

        @tree.command(name="status", description="查看 Bot 和扫描器状态", guild=guild)
        async def status(interaction: discord.Interaction) -> None:
            await _send_response(interaction, "/status")

        @tree.command(name="progress", description="查看当前扫描进度", guild=guild)
        async def progress(interaction: discord.Interaction) -> None:
            await _send_response(interaction, "/progress")

        @tree.command(name="help", description="查看命令列表", guild=guild)
        async def help_command(interaction: discord.Interaction) -> None:
            await _send_response(interaction, "/help")

        @client.event
        async def on_ready() -> None:
            if guild:
                await tree.sync(guild=guild)
            else:
                await tree.sync()
            LOGGER.info("discord_slash_bot_ready user=%s", client.user)

        client.run(self.token)

    def _request(self, method: str, endpoint: str, payload: Any) -> Any:
        data = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{self.base_url}{endpoint}",
            data=data,
            method=method,
            headers={
                "Authorization": f"Bot {self.token}",
                "Content-Type": "application/json",
                "User-Agent": "usmart-quant/0.1",
            },
        )
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            body = response.read().decode("utf-8")
        return json.loads(body) if body else None
