"""
Marketplace REST API — v1.3
FastAPI server exposing CryptoArena marketplace endpoints.
Run: uvicorn src.marketplace.marketplace_api:app --port 8001
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Optional

try:
    from fastapi import FastAPI, HTTPException, WebSocket
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    FastAPI = object  # type: ignore

from src.marketplace.agent_marketplace import AgentMarketplace

logger = logging.getLogger("arena.marketplace.api")
_marketplace = AgentMarketplace()

if HAS_FASTAPI:
    app = FastAPI(
        title="CryptoArena Agent Marketplace API",
        description="Buy, sell, and discover AI trading agents",
        version="1.3.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    class CreateListingRequest(BaseModel):
        agent_id: str
        agent_name: str
        seller_address: str
        price_karma: float
        strategy_type: str
        win_rate: float
        total_pnl: float
        tournaments_won: int = 0
        quests_completed: int = 0
        description: str = ""
        duration_days: int = 30

    class BuyRequest(BaseModel):
        buyer_address: str

    @app.get("/health")
    async def health():
        return {"status": "ok", "version": "1.3.0", "service": "CryptoArena Marketplace"}

    @app.get("/marketplace/listings")
    async def get_listings(
        strategy_type: Optional[str] = None,
        min_win_rate: float = 0.0,
        max_price: Optional[float] = None,
        sort_by: str = "win_rate",
    ):
        listings = _marketplace.get_active_listings(
            strategy_type=strategy_type,
            min_win_rate=min_win_rate,
            max_price=max_price,
            sort_by=sort_by,
        )
        return {"listings": [vars(l) for l in listings], "count": len(listings)}

    @app.post("/marketplace/listings")
    async def create_listing(req: CreateListingRequest):
        listing = await _marketplace.create_listing(**req.dict())
        return {"listing": vars(listing), "message": "Listing created successfully"}

    @app.post("/marketplace/listings/{listing_id}/buy")
    async def buy_agent(listing_id: str, req: BuyRequest):
        try:
            result = await _marketplace.buy_agent(listing_id, req.buyer_address)
            return result
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc))
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc))

    @app.delete("/marketplace/listings/{listing_id}")
    async def delist_agent(listing_id: str, seller_address: str):
        try:
            ok = await _marketplace.delist_agent(listing_id, seller_address)
            return {"success": ok}
        except PermissionError as exc:
            raise HTTPException(status_code=403, detail=str(exc))

    @app.get("/marketplace/price-suggest")
    async def price_suggest(win_rate: float, total_pnl: float, tournaments_won: int = 0):
        price = _marketplace.suggest_price(win_rate, total_pnl, tournaments_won)
        return {"suggested_price_karma": price}

    @app.get("/marketplace/stats")
    async def marketplace_stats():
        return _marketplace.get_marketplace_stats()

    @app.websocket("/marketplace/ws/live")
    async def ws_live_listings(websocket: WebSocket):
        """WebSocket feed — pushes snapshot every 10s."""
        await websocket.accept()
        logger.info("WebSocket client connected to marketplace live feed")
        try:
            while True:
                stats = _marketplace.get_marketplace_stats()
                listings = _marketplace.get_active_listings()
                payload = {
                    "type": "snapshot",
                    "stats": stats,
                    "active_count": len(listings),
                }
                await websocket.send_text(json.dumps(payload, default=str))
                await asyncio.sleep(10)
        except Exception:
            logger.info("WebSocket client disconnected")
else:
    logger.warning("FastAPI not installed — marketplace API unavailable. Run: pip install fastapi uvicorn")
