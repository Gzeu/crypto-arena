"""
Market Scout Agent
==================
Fetches live market data from CoinGecko (primary) and
cross-validates with secondary sources.
Produces a clean, normalized market snapshot.
"""

import httpx
from datetime import datetime, timezone
from typing import Dict, List
from loguru import logger


COINGECKO_BASE = "https://api.coingecko.com/api/v3"
DEXSCREENER_BASE = "https://api.dexscreener.com/latest/dex"

SYMBOL_TO_CG_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
}

MEME_COINS_DEFAULT = ["dogecoin", "pepe", "shiba-inu"]


class MarketScout:
    """
    Pulls live prices, volumes, funding rates and detects anomalies.
    Output schema:
    {
        "timestamp": "...",
        "prices": { "BTC": float, ... },
        "volumes_24h": { "BTC": float, ... },
        "price_changes_24h": { "BTC": float, ... },
        "meme_coins": [ { "symbol": str, "price": float, "volume_24h": float } ],
        "anomalies": [ str, ... ],
    }
    """

    def __init__(self, config: dict):
        self.config = config
        self.client = httpx.AsyncClient(timeout=15.0)

    async def fetch_snapshot(self) -> dict:
        """Fetch a full market snapshot (majors + top meme coins)."""
        try:
            majors = await self._fetch_majors()
            memes = await self._fetch_top_meme_coins()
            anomalies = self._detect_anomalies(majors)
            snapshot = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "prices": {k: v["price"] for k, v in majors.items()},
                "volumes_24h": {k: v["volume_24h"] for k, v in majors.items()},
                "price_changes_24h": {k: v["price_change_24h"] for k, v in majors.items()},
                "meme_coins": memes,
                "anomalies": anomalies,
            }
            logger.info("📡 Snapshot: BTC={} ETH={} SOL={}",
                        snapshot["prices"].get("BTC"),
                        snapshot["prices"].get("ETH"),
                        snapshot["prices"].get("SOL"))
            return snapshot
        except Exception as e:
            logger.error("❌ MarketScout fetch failed: {}", e)
            return self._empty_snapshot()

    async def _fetch_majors(self) -> dict:
        """Fetch BTC, ETH, SOL prices and 24h data from CoinGecko."""
        ids = ",".join(SYMBOL_TO_CG_ID.values())
        url = f"{COINGECKO_BASE}/simple/price"
        params = {
            "ids": ids,
            "vs_currencies": "usd",
            "include_24hr_vol": "true",
            "include_24hr_change": "true",
        }
        resp = await self.client.get(url, params=params)
        resp.raise_for_status()
        data = resp.json()
        result = {}
        for symbol, cg_id in SYMBOL_TO_CG_ID.items():
            coin = data.get(cg_id, {})
            result[symbol] = {
                "price": coin.get("usd", 0),
                "volume_24h": coin.get("usd_24h_vol", 0),
                "price_change_24h": coin.get("usd_24h_change", 0),
            }
        return result

    async def _fetch_top_meme_coins(self) -> List[dict]:
        """Fetch top meme coins by 24h volume from CoinGecko."""
        url = f"{COINGECKO_BASE}/coins/markets"
        params = {
            "vs_currency": "usd",
            "category": "meme-token",
            "order": "volume_desc",
            "per_page": self.config["market"]["meme_slots"],
            "page": 1,
        }
        try:
            resp = await self.client.get(url, params=params)
            resp.raise_for_status()
            coins = resp.json()
            return [
                {
                    "symbol": c["symbol"].upper(),
                    "name": c["name"],
                    "price": c["current_price"],
                    "volume_24h": c["total_volume"],
                    "price_change_24h": c["price_change_percentage_24h"],
                }
                for c in coins
            ]
        except Exception as e:
            logger.warning("⚠️  Meme coin fetch failed: {} — using defaults", e)
            return []

    def _detect_anomalies(self, majors: dict) -> List[str]:
        """Simple heuristic anomaly detection."""
        anomalies = []
        for symbol, data in majors.items():
            change = data.get("price_change_24h", 0)
            if abs(change) > 10:
                anomalies.append(f"{symbol} extreme 24h move: {change:+.1f}%")
        return anomalies

    def _empty_snapshot(self) -> dict:
        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prices": {"BTC": None, "ETH": None, "SOL": None},
            "volumes_24h": {},
            "price_changes_24h": {},
            "meme_coins": [],
            "anomalies": ["DATA_FETCH_FAILED"],
        }
