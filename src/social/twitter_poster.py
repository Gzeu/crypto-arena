"""
Twitter / X poster for CryptoArena chronicles and trade alerts.
Requires Tweepy v4+ and Twitter API v2 credentials in .env.
"""

import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

from loguru import logger

try:
    import tweepy
    TWEEPY_AVAILABLE = True
except ImportError:
    TWEEPY_AVAILABLE = False
    logger.warning("tweepy not installed — Twitter posting disabled")


class TwitterPoster:
    """
    Posts chronicles, trade alerts, and challenges to Twitter/X.
    Falls back to dry-run logging if credentials are absent.
    """

    MAX_TWEET_LEN = 280
    HASHTAGS = "#CryptoArena #AIAgents #BaseL2 #DeFi"

    def __init__(self):
        self._client = None
        self._dry_run = True

        if not TWEEPY_AVAILABLE:
            return

        bearer = os.getenv("TWITTER_BEARER_TOKEN")
        api_key = os.getenv("TWITTER_API_KEY")
        api_secret = os.getenv("TWITTER_API_SECRET")
        access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        access_secret = os.getenv("TWITTER_ACCESS_SECRET")

        if all([bearer, api_key, api_secret, access_token, access_secret]):
            self._client = tweepy.Client(
                bearer_token=bearer,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_secret,
            )
            self._dry_run = False
            logger.info("🐦 TwitterPoster ready (live)")
        else:
            logger.warning("🐦 TwitterPoster in DRY-RUN (missing credentials)")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def post_chronicle(self, content: str,
                              tags: Optional[List[str]] = None) -> Dict:
        """Post a tournament chronicle thread opener."""
        extra_tags = " ".join(f"#{t}" for t in (tags or []))
        full = f"{content}\n\n{self.HASHTAGS} {extra_tags}".strip()
        return await self._send(full[:self.MAX_TWEET_LEN])

    async def post_trade_alert(self, agent_id: str, trade: Dict) -> Dict:
        """Post a single trade alert."""
        side_emoji = "🟢" if trade.get("side") == "long" else "🔴"
        pnl_str = ""
        if "pnl_pct" in trade:
            pnl_str = f" | PnL {trade['pnl_pct']:+.2f}%"

        text = (
            f"{side_emoji} {agent_id.upper()} — {trade.get('side','').upper()} "
            f"{trade.get('symbol','?')}\n"
            f"Entry ${trade.get('entry_price', '?'):,} → "
            f"Target ${trade.get('target_price', '?'):,}{pnl_str}\n"
            f"{trade.get('rationale','')[:80]}...\n"
            f"#CryptoArena #{trade.get('symbol','')}"
        )
        return await self._send(text[:self.MAX_TWEET_LEN])

    async def post_leaderboard(self, leaderboard: List[Dict]) -> Dict:
        """Post weekly leaderboard snapshot."""
        lines = ["🏆 CRYPTOARENA LEADERBOARD — Week 1\n"]
        medals = ["🥇", "🥈", "🥉"] + ["  "] * 10
        for i, entry in enumerate(leaderboard[:5]):
            lines.append(
                f"{medals[i]} {entry['agent_id']:20s} "
                f"{entry['pnl_pct']:+6.2f}%  "
                f"Karma {entry.get('karma', 0):,}"
            )
        lines.append(f"\n{self.HASHTAGS}")
        return await self._send("\n".join(lines)[:self.MAX_TWEET_LEN])

    async def post_challenge(self, challenger: str, target: str,
                              terms: str) -> Dict:
        """Post an agent-vs-agent challenge."""
        text = (
            f"⚔️ CHALLENGE ISSUED\n"
            f"{challenger} → {target}\n"
            f"Terms: {terms}\n"
            f"#CryptoArena #AgentBattle"
        )
        return await self._send(text[:self.MAX_TWEET_LEN])

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    async def _send(self, text: str) -> Dict:
        ts = datetime.now(timezone.utc).isoformat()
        if self._dry_run or self._client is None:
            logger.info("[DRY-RUN] Twitter post @ {}:\n{}", ts, text)
            return {"success": True, "dry_run": True, "text": text, "ts": ts}

        try:
            resp = self._client.create_tweet(text=text)
            tweet_id = resp.data["id"]
            url = f"https://twitter.com/i/web/status/{tweet_id}"
            logger.success("🐦 Tweet posted: {}", url)
            return {"success": True, "tweet_id": tweet_id, "url": url, "ts": ts}
        except Exception as exc:
            logger.error("Twitter post failed: {}", exc)
            return {"success": False, "error": str(exc), "ts": ts}
