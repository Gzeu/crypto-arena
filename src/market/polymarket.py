"""
Polymarket Integration
======================
Fetches prediction market odds from Polymarket API.
Used by A6 (Prediction Market Agent).
"""

import httpx
from typing import List, Optional
from loguru import logger

POLYMARKET_API = "https://gamma-api.polymarket.com"


class PolymarketClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=10.0)

    async def get_crypto_markets(self) -> List[dict]:
        """Fetch active crypto-related prediction markets."""
        try:
            resp = await self.client.get(f"{POLYMARKET_API}/markets", params={
                "active": "true",
                "tag": "crypto",
                "limit": 20,
            })
            resp.raise_for_status()
            markets = resp.json()
            logger.info("📊 Polymarket: {} active crypto markets", len(markets))
            return markets
        except Exception as e:
            logger.error("❌ Polymarket fetch failed: {}", e)
            return []

    async def get_market_odds(self, market_id: str) -> Optional[dict]:
        """Get current YES/NO odds for a specific market."""
        try:
            resp = await self.client.get(f"{POLYMARKET_API}/markets/{market_id}")
            resp.raise_for_status()
            data = resp.json()
            # Polymarket returns prices in [0, 1] range
            yes_price = float(data.get("outcomePrices", [0.5, 0.5])[0])
            no_price = 1.0 - yes_price
            return {
                "market_id": market_id,
                "question": data.get("question"),
                "yes_price": yes_price,
                "no_price": no_price,
                "volume_24h": data.get("volume24hr", 0),
            }
        except Exception as e:
            logger.error("❌ Failed to fetch market {}: {}", market_id, e)
            return None

    async def find_btc_range_market(self, target_date: str) -> Optional[dict]:
        """Find 'BTC price on {date}' range market."""
        markets = await self.get_crypto_markets()
        for m in markets:
            question = m.get("question", "").lower()
            if "bitcoin price" in question and target_date in question:
                return m
        return None
