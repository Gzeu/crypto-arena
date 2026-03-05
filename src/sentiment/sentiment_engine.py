"""
Sentiment Engine v1.2 — aggregates sentiment from:
  1. Fear & Greed Index (alternative.me)
  2. CryptoPanic news headlines
  3. Twitter/X search (Tweepy)
  4. On-chain signal: BTC funding rate proxy

Outputs a normalised score  −1.0 (extreme fear) → +1.0 (extreme greed)
and per-source breakdowns consumed by RegimeDetectorV2.
"""

import asyncio
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional

import aiohttp
from loguru import logger


class SentimentEngine:
    """
    Multi-source sentiment aggregator.
    All sources fail gracefully — missing sources default to 0.0 (neutral).
    """

    FNG_URL  = "https://api.alternative.me/fng/?limit=1"
    NEWS_URL = "https://cryptopanic.com/api/v1/posts/"
    WEIGHTS  = {
        "fear_greed": 0.40,
        "news":       0.35,
        "twitter":    0.15,
        "funding":    0.10,
    }

    def __init__(self):
        self._news_key    = os.getenv("CRYPTOPANIC_API_KEY", "")
        self._twitter_key = os.getenv("TWITTER_BEARER_TOKEN", "")
        self._cache: Optional[Dict] = None
        self._cache_ts: float = 0.0
        self._cache_ttl: float = 300.0  # 5 min cache
        logger.info("🌡️  SentimentEngine ready")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_sentiment(self, force: bool = False) -> Dict:
        """
        Returns:
        {
            score: float,          # -1.0 to +1.0
            label: str,            # Extreme Fear / Fear / Neutral / Greed / Extreme Greed
            sources: {
                fear_greed: {score, value, label},
                news:       {score, headlines},
                twitter:    {score, sample_tweets},
                funding:    {score},
            },
            ts: str,
        }
        """
        now = datetime.now(timezone.utc).timestamp()
        if not force and self._cache and (now - self._cache_ts) < self._cache_ttl:
            return self._cache

        results = await asyncio.gather(
            self._fetch_fear_greed(),
            self._fetch_news(),
            self._fetch_twitter(),
            self._fetch_funding_proxy(),
            return_exceptions=True,
        )

        fear_greed = results[0] if not isinstance(results[0], Exception) else {"score": 0.0}
        news       = results[1] if not isinstance(results[1], Exception) else {"score": 0.0}
        twitter    = results[2] if not isinstance(results[2], Exception) else {"score": 0.0}
        funding    = results[3] if not isinstance(results[3], Exception) else {"score": 0.0}

        aggregate = (
            fear_greed["score"] * self.WEIGHTS["fear_greed"]
            + news["score"]       * self.WEIGHTS["news"]
            + twitter["score"]    * self.WEIGHTS["twitter"]
            + funding["score"]    * self.WEIGHTS["funding"]
        )
        aggregate = max(-1.0, min(1.0, aggregate))

        output = {
            "score": round(aggregate, 4),
            "label": self._label(aggregate),
            "sources": {
                "fear_greed": fear_greed,
                "news":       news,
                "twitter":    twitter,
                "funding":    funding,
            },
            "ts": datetime.now(timezone.utc).isoformat(),
        }
        self._cache = output
        self._cache_ts = now
        logger.debug("🌡️  Sentiment: {} ({:+.3f})", output["label"], aggregate)
        return output

    # ------------------------------------------------------------------
    # Sources
    # ------------------------------------------------------------------

    async def _fetch_fear_greed(self) -> Dict:
        """Fetch Fear & Greed Index from alternative.me (free, no key)."""
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(self.FNG_URL, timeout=aiohttp.ClientTimeout(total=8)) as r:
                    data = await r.json()
            value = int(data["data"][0]["value"])       # 0–100
            score = (value - 50) / 50.0                 # −1 to +1
            label = data["data"][0]["value_classification"]
            return {"score": score, "value": value, "label": label}
        except Exception as exc:
            logger.warning("Fear&Greed fetch failed: {}", exc)
            return {"score": 0.0, "value": 50, "label": "Neutral"}

    async def _fetch_news(self) -> Dict:
        """Fetch CryptoPanic headlines and compute basic sentiment."""
        if not self._news_key:
            return {"score": 0.0, "headlines": []}
        try:
            params = {
                "auth_token": self._news_key,
                "filter": "hot",
                "public": "true",
                "kind": "news",
                "currencies": "BTC,ETH,SOL",
            }
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    self.NEWS_URL, params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as r:
                    data = await r.json()

            results = data.get("results", [])[:20]
            headlines = [r["title"] for r in results]

            # Simple keyword-based scoring
            pos_words = {"bull", "surge", "rally", "ath", "pump", "green",
                         "gain", "rise", "adoption", "partnership", "launch"}
            neg_words = {"crash", "dump", "liquidat", "ban", "hack", "scam",
                         "fraud", "fear", "panic", "drop", "lose", "lost"}

            scores = []
            for h in headlines:
                h_lower = h.lower()
                pos = sum(1 for w in pos_words if w in h_lower)
                neg = sum(1 for w in neg_words if w in h_lower)
                if pos + neg > 0:
                    scores.append((pos - neg) / (pos + neg))

            score = sum(scores) / len(scores) if scores else 0.0
            return {"score": round(score, 4), "headlines": headlines[:5]}
        except Exception as exc:
            logger.warning("CryptoPanic fetch failed: {}", exc)
            return {"score": 0.0, "headlines": []}

    async def _fetch_twitter(self) -> Dict:
        """Fetch recent #BTC #ETH tweets and compute sentiment."""
        if not self._twitter_key:
            return {"score": 0.0, "sample_tweets": []}
        try:
            headers = {"Authorization": f"Bearer {self._twitter_key}"}
            params = {
                "query": "(#BTC OR #ETH OR #SOL) lang:en -is:retweet",
                "max_results": 20,
                "tweet.fields": "public_metrics",
            }
            async with aiohttp.ClientSession() as s:
                async with s.get(
                    "https://api.twitter.com/2/tweets/search/recent",
                    headers=headers, params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as r:
                    data = await r.json()

            tweets = data.get("data", [])
            pos_kw = {"bullish", "moon", "long", "buy", "pump", "ath", "up"}
            neg_kw = {"bearish", "short", "dump", "crash", "sell", "down", "rug"}

            scores = []
            for t in tweets:
                txt = t["text"].lower()
                pos = sum(1 for w in pos_kw if w in txt)
                neg = sum(1 for w in neg_kw if w in txt)
                if pos + neg > 0:
                    scores.append((pos - neg) / (pos + neg))

            score = sum(scores) / len(scores) if scores else 0.0
            sample = [t["text"][:80] for t in tweets[:3]]
            return {"score": round(score, 4), "sample_tweets": sample}
        except Exception as exc:
            logger.warning("Twitter sentiment fetch failed: {}", exc)
            return {"score": 0.0, "sample_tweets": []}

    async def _fetch_funding_proxy(self) -> Dict:
        """
        Proxy BTC funding rate via CoinGecko derivatives (free endpoint).
        Positive funding → bulls paying → +score; negative → bears paying → -score.
        """
        try:
            url = "https://api.coingecko.com/api/v3/derivatives"
            async with aiohttp.ClientSession() as s:
                async with s.get(url, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    data = await r.json()
            btc_perps = [
                d for d in data
                if "BTC" in d.get("base", "").upper()
                and d.get("funding_rate") is not None
            ][:5]
            if not btc_perps:
                return {"score": 0.0}
            avg_rate = sum(float(d["funding_rate"]) for d in btc_perps) / len(btc_perps)
            # Typical funding range: -0.03% to +0.03% per 8h
            score = max(-1.0, min(1.0, avg_rate * 100))
            return {"score": round(score, 4), "avg_funding_rate": avg_rate}
        except Exception as exc:
            logger.warning("Funding proxy fetch failed: {}", exc)
            return {"score": 0.0}

    @staticmethod
    def _label(score: float) -> str:
        if score <= -0.6:  return "Extreme Fear"
        if score <= -0.2:  return "Fear"
        if score <=  0.2:  return "Neutral"
        if score <=  0.6:  return "Greed"
        return "Extreme Greed"
