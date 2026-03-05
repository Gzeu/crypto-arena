"""
Live Executor Module
====================
Real CEX/DEX execution when live mode is enabled.
Wires to Binance, Uniswap, and prediction markets.
"""

import os
import hmac
import hashlib
import time
import httpx
from typing import Optional
from loguru import logger

BINANCE_BASE = "https://api.binance.com"


class LiveExecutor:
    """
    CRITICAL: Only use in production with:
    - Audited smart contracts
    - MPC / hardware wallet signing
    - Strict position size and leverage limits
    - Real-time monitoring and kill-switch
    """

    def __init__(self):
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        if not self.api_key or not self.api_secret:
            logger.warning("⚠️  Binance credentials missing — live mode will fail")
        self.client = httpx.AsyncClient(timeout=15.0)

    def _sign_request(self, params: dict) -> dict:
        """Sign Binance API request with HMAC SHA256."""
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        signature = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        params["signature"] = signature
        return params

    async def market_order(
        self, symbol: str, side: str, quantity: float
    ) -> Optional[dict]:
        """
        Place market order on Binance spot.
        symbol: e.g. 'BTCUSDT'
        side: 'BUY' or 'SELL'
        quantity: in base asset (BTC, ETH, etc.)
        """
        params = {
            "symbol": symbol.replace("/", ""),
            "side": side.upper(),
            "type": "MARKET",
            "quantity": quantity,
            "timestamp": int(time.time() * 1000),
        }
        params = self._sign_request(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        try:
            resp = await self.client.post(
                f"{BINANCE_BASE}/api/v3/order",
                params=params,
                headers=headers,
            )
            resp.raise_for_status()
            order = resp.json()
            logger.info("✅ Live order executed: {} {} {} @ {}",
                         side, quantity, symbol, order.get("fills", [{}])[0].get("price"))
            return order
        except Exception as e:
            logger.error("❌ Live order failed: {}", e)
            return None

    async def futures_order(
        self, symbol: str, side: str, quantity: float, leverage: int
    ) -> Optional[dict]:
        """
        Place futures order on Binance with leverage.
        Requires futures account enabled and margin available.
        """
        # Set leverage first
        await self._set_leverage(symbol, leverage)
        params = {
            "symbol": symbol.replace("/", "").replace("-PERP", ""),
            "side": side.upper(),
            "type": "MARKET",
            "quantity": quantity,
            "timestamp": int(time.time() * 1000),
        }
        params = self._sign_request(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        try:
            resp = await self.client.post(
                f"{BINANCE_BASE}/fapi/v1/order",
                params=params,
                headers=headers,
            )
            resp.raise_for_status()
            order = resp.json()
            logger.info("✅ Live futures order: {} {} {} {}x",
                         side, quantity, symbol, leverage)
            return order
        except Exception as e:
            logger.error("❌ Live futures order failed: {}", e)
            return None

    async def _set_leverage(self, symbol: str, leverage: int):
        params = {
            "symbol": symbol.replace("/", "").replace("-PERP", ""),
            "leverage": leverage,
            "timestamp": int(time.time() * 1000),
        }
        params = self._sign_request(params)
        headers = {"X-MBX-APIKEY": self.api_key}
        try:
            await self.client.post(
                f"{BINANCE_BASE}/fapi/v1/leverage",
                params=params,
                headers=headers,
            )
        except Exception as e:
            logger.warning("⚠️  Failed to set leverage: {}", e)
