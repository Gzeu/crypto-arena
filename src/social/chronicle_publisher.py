"""
Chronicle Publisher — orchestrates multi-platform posting.
Single entry point called by ArenaCore at meso/macro cycle boundaries.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, List, Optional

from loguru import logger

from src.social.twitter_poster import TwitterPoster
from src.social.discord_bot import ArenaDiscordBot


class ChroniclePublisher:
    """Unified publisher for all social channels."""

    def __init__(self, state_ref=None):
        self.twitter = TwitterPoster()
        self.discord = ArenaDiscordBot(state_ref)
        logger.info("📢 ChroniclePublisher ready")

    async def publish_chronicle(self, content: str,
                                 leaderboard: Optional[List[Dict]] = None,
                                 tags: Optional[List[str]] = None):
        """Post chronicle to all platforms."""
        results = await asyncio.gather(
            self.twitter.post_chronicle(content, tags),
            self.discord.notify(f"📖 **Chronicle Update**\n{content[:500]}"),
            return_exceptions=True,
        )
        logger.info("📢 Chronicle published to {} platform(s)", len(results))

        if leaderboard:
            await self.twitter.post_leaderboard(leaderboard)

    async def publish_trade_alert(self, agent_id: str, trade: Dict):
        """Fire trade alert across platforms."""
        await asyncio.gather(
            self.twitter.post_trade_alert(agent_id, trade),
            self.discord.notify(
                f"⚡ **Trade Alert** — {agent_id}\n"
                f"{trade.get('side','').upper()} {trade.get('symbol','?')} "
                f"@ ${trade.get('entry_price','?'):,}"
            ),
            return_exceptions=True,
        )

    async def publish_challenge(self, challenger: str, target: str, terms: str):
        """Broadcast agent-vs-agent challenge."""
        await asyncio.gather(
            self.twitter.post_challenge(challenger, target, terms),
            self.discord.notify(
                f"⚔️ **Challenge!** {challenger} vs {target}\n{terms}"
            ),
            return_exceptions=True,
        )
