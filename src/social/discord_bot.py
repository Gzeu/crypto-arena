"""
Discord bot for CryptoArena community.
Provides slash commands and pushes live notifications to configured channels.
"""

import os
from typing import Optional

from loguru import logger

try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    logger.warning("discord.py not installed — Discord bot disabled")


class ArenaDiscordBot:
    """
    Discord bot with commands + push notifications.
    Call start() as an asyncio task alongside ArenaCore.
    """

    def __init__(self, state_ref=None):
        self._state = state_ref
        self._bot: Optional[object] = None
        self._channel_id = int(os.getenv("DISCORD_CHANNEL_ID", "0") or 0)
        self._token = os.getenv("DISCORD_BOT_TOKEN", "")

        if not DISCORD_AVAILABLE or not self._token:
            logger.warning("Discord bot disabled (missing library or token)")
            return

        intents = discord.Intents.default()
        intents.message_content = True
        bot = commands.Bot(command_prefix="!arena ", intents=intents)
        self._bot = bot
        self._register_commands(bot)

    def _register_commands(self, bot):
        state = self._state

        @bot.event
        async def on_ready():
            logger.success("🤖 Discord bot logged in as {}", bot.user)

        @bot.command(name="leaderboard", help="Show current leaderboard")
        async def leaderboard(ctx):
            if state:
                lb = state.get_leaderboard()
                lines = ["**🏆 CryptoArena Leaderboard**"]
                for i, row in enumerate(lb[:8], 1):
                    lines.append(
                        f"`{i}.` **{row['agent_id']}** — "
                        f"{row['pnl_pct']:+.2f}% | "
                        f"Karma {row.get('karma', 0):,}"
                    )
                await ctx.send("\n".join(lines))
            else:
                await ctx.send("Arena not initialised yet.")

        @bot.command(name="agent", help="Stats for a specific agent")
        async def agent(ctx, agent_id: str):
            if state:
                data = state.get_agent_stats(agent_id)
                if data:
                    await ctx.send(
                        f"**{agent_id}**\n"
                        f"PnL: {data['pnl_pct']:+.2f}%\n"
                        f"Trades: {data['trade_count']}\n"
                        f"Win rate: {data['win_rate']:.0%}\n"
                        f"Karma: {data.get('karma', 0):,}"
                    )
                else:
                    await ctx.send(f"Agent '{agent_id}' not found.")
            else:
                await ctx.send("Arena not initialised yet.")

        @bot.command(name="regime", help="Current market regime")
        async def regime(ctx):
            if state:
                r = state.current_regime
                await ctx.send(
                    f"**📊 Current Regime:** {r.get('regime', '?')} "
                    f"({r.get('confidence', 0):.0%} confidence)"
                )
            else:
                await ctx.send("Arena not initialised yet.")

    async def start(self):
        if self._bot and self._token:
            await self._bot.start(self._token)

    async def notify(self, message: str):
        """Push a notification to the configured channel."""
        if not DISCORD_AVAILABLE or not self._bot:
            logger.info("[Discord dry-run] {}", message)
            return
        channel = self._bot.get_channel(self._channel_id)
        if channel:
            await channel.send(message)
        else:
            logger.warning("Discord channel {} not found", self._channel_id)
