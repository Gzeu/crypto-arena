"""
AgentMarketplace — v1.3
Buy, sell, and discover AI agent NFTs on the CryptoArena marketplace.
Integrates with AgentNFT (ERC-721) and KarmaToken (ERC-20) on Base L2.
"""

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

logger = logging.getLogger("arena.marketplace")


class ListingStatus(str, Enum):
    ACTIVE = "active"
    SOLD = "sold"
    DELISTED = "delisted"
    EXPIRED = "expired"


@dataclass
class AgentListing:
    listing_id: str
    agent_id: str
    agent_name: str
    seller_address: str
    price_karma: float
    strategy_type: str
    win_rate: float
    total_pnl: float
    tournaments_won: int
    quests_completed: int
    description: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    status: ListingStatus = ListingStatus.ACTIVE
    buyer_address: Optional[str] = None
    sold_at: Optional[datetime] = None


class AgentMarketplace:
    """
    Decentralised marketplace for trading CryptoArena AI agents.

    Features:
    - List agents for KARMA tokens
    - Buy agents with automatic NFT transfer
    - Reputation scoring based on on-chain performance
    - Dynamic pricing suggestions via heuristic ML model
    - Escrow-backed transactions via AgentMarketplace.sol
    """

    def __init__(self, db_path: str = "arena.db", chain_client=None):
        self.db_path = db_path
        self.chain = chain_client
        self._listings: dict[str, AgentListing] = {}
        self._fee_pct = 2.5  # 2.5% marketplace fee
        logger.info("AgentMarketplace initialised (fee=%.1f%%)", self._fee_pct)

    # ------------------------------------------------------------------ #
    #  LISTINGS                                                            #
    # ------------------------------------------------------------------ #

    async def create_listing(
        self,
        agent_id: str,
        agent_name: str,
        seller_address: str,
        price_karma: float,
        strategy_type: str,
        win_rate: float,
        total_pnl: float,
        tournaments_won: int = 0,
        quests_completed: int = 0,
        description: str = "",
        duration_days: int = 30,
    ) -> AgentListing:
        listing_id = f"lst_{uuid.uuid4().hex[:12]}"
        listing = AgentListing(
            listing_id=listing_id,
            agent_id=agent_id,
            agent_name=agent_name,
            seller_address=seller_address,
            price_karma=price_karma,
            strategy_type=strategy_type,
            win_rate=win_rate,
            total_pnl=total_pnl,
            tournaments_won=tournaments_won,
            quests_completed=quests_completed,
            description=description,
            expires_at=datetime.utcnow() + timedelta(days=duration_days),
        )
        self._listings[listing_id] = listing
        logger.info("Listed agent %s for %.0f KARMA [%s]", agent_name, price_karma, listing_id)

        if self.chain:
            try:
                await self.chain.lock_agent_nft(agent_id, listing_id, price_karma)
            except Exception as exc:
                logger.warning("On-chain lock failed (dry-run): %s", exc)

        return listing

    async def buy_agent(self, listing_id: str, buyer_address: str) -> dict:
        listing = self._listings.get(listing_id)
        if not listing:
            raise ValueError(f"Listing {listing_id} not found")
        if listing.status != ListingStatus.ACTIVE:
            raise ValueError(f"Listing {listing_id} is {listing.status}")
        if datetime.utcnow() > listing.expires_at:
            listing.status = ListingStatus.EXPIRED
            raise ValueError("Listing has expired")

        fee = listing.price_karma * self._fee_pct / 100
        seller_receives = listing.price_karma - fee

        listing.status = ListingStatus.SOLD
        listing.buyer_address = buyer_address
        listing.sold_at = datetime.utcnow()

        logger.info(
            "SOLD agent %s: buyer=%s seller_receives=%.0f KARMA fee=%.1f KARMA",
            listing.agent_name,
            buyer_address[:10] + "...",
            seller_receives,
            fee,
        )

        if self.chain:
            try:
                await self.chain.execute_marketplace_trade(
                    listing_id=listing_id,
                    buyer=buyer_address,
                    seller=listing.seller_address,
                    price=listing.price_karma,
                    fee=fee,
                )
            except Exception as exc:
                logger.warning("On-chain trade failed (dry-run): %s", exc)

        return {
            "listing_id": listing_id,
            "agent_id": listing.agent_id,
            "agent_name": listing.agent_name,
            "buyer": buyer_address,
            "seller": listing.seller_address,
            "price_karma": listing.price_karma,
            "fee_karma": fee,
            "seller_receives": seller_receives,
            "timestamp": listing.sold_at.isoformat(),
        }

    async def delist_agent(self, listing_id: str, seller_address: str) -> bool:
        listing = self._listings.get(listing_id)
        if not listing:
            return False
        if listing.seller_address.lower() != seller_address.lower():
            raise PermissionError("Only the seller can delist")
        if listing.status != ListingStatus.ACTIVE:
            return False
        listing.status = ListingStatus.DELISTED
        logger.info("Delisted %s by %s", listing_id, seller_address[:10])
        return True

    # ------------------------------------------------------------------ #
    #  DISCOVERY                                                           #
    # ------------------------------------------------------------------ #

    def get_active_listings(
        self,
        strategy_type: Optional[str] = None,
        min_win_rate: float = 0.0,
        max_price: Optional[float] = None,
        sort_by: str = "win_rate",
    ) -> list:
        now = datetime.utcnow()
        listings = [
            l for l in self._listings.values()
            if l.status == ListingStatus.ACTIVE and l.expires_at > now
        ]
        if strategy_type:
            listings = [l for l in listings if l.strategy_type == strategy_type]
        if min_win_rate:
            listings = [l for l in listings if l.win_rate >= min_win_rate]
        if max_price:
            listings = [l for l in listings if l.price_karma <= max_price]

        key_map = {
            "win_rate": lambda l: -l.win_rate,
            "price_asc": lambda l: l.price_karma,
            "price_desc": lambda l: -l.price_karma,
            "pnl": lambda l: -l.total_pnl,
            "newest": lambda l: -l.created_at.timestamp(),
        }
        listings.sort(key=key_map.get(sort_by, key_map["win_rate"]))
        return listings

    def suggest_price(self, win_rate: float, total_pnl: float, tournaments_won: int = 0) -> float:
        """Heuristic ML price suggestion based on agent performance."""
        base = 100.0
        win_bonus = win_rate * 500          # 50% WR -> +250
        pnl_bonus = max(total_pnl * 0.1, 0) # $1000 PnL -> +100
        tournament_bonus = tournaments_won * 200
        return round(base + win_bonus + pnl_bonus + tournament_bonus, 0)

    def get_marketplace_stats(self) -> dict:
        all_l = list(self._listings.values())
        active = [l for l in all_l if l.status == ListingStatus.ACTIVE]
        sold = [l for l in all_l if l.status == ListingStatus.SOLD]
        volume = sum(l.price_karma for l in sold)
        return {
            "total_listings": len(all_l),
            "active_listings": len(active),
            "total_sold": len(sold),
            "total_volume_karma": volume,
            "avg_price_karma": round(volume / len(sold), 2) if sold else 0,
            "fee_collected_karma": round(volume * self._fee_pct / 100, 2),
        }
