"""
Pytest suite for AgentMarketplace — v1.3
7 tests: create, buy, delist, price suggest, stats, guard, duplicate
"""

import asyncio
import pytest
from src.marketplace.agent_marketplace import AgentMarketplace, ListingStatus


@pytest.fixture
def mp():
    return AgentMarketplace()


@pytest.fixture
def listing_kwargs():
    return dict(
        agent_id="agent_001",
        agent_name="BTC Titan",
        seller_address="0xSELLER",
        price_karma=500.0,
        strategy_type="trend_following",
        win_rate=0.65,
        total_pnl=1200.0,
        tournaments_won=2,
        quests_completed=3,
        description="Battle-tested BTC trend follower",
    )


def test_create_listing(mp, listing_kwargs):
    listing = asyncio.run(mp.create_listing(**listing_kwargs))
    assert listing.status == ListingStatus.ACTIVE
    assert listing.price_karma == 500.0
    assert listing.agent_name == "BTC Titan"
    assert listing.listing_id.startswith("lst_")


def test_buy_agent(mp, listing_kwargs):
    listing = asyncio.run(mp.create_listing(**listing_kwargs))
    result = asyncio.run(mp.buy_agent(listing.listing_id, "0xBUYER"))
    assert result["price_karma"] == 500.0
    assert result["fee_karma"] == pytest.approx(12.5, rel=0.01)
    assert result["seller_receives"] == pytest.approx(487.5, rel=0.01)
    assert mp._listings[listing.listing_id].status == ListingStatus.SOLD


def test_cannot_buy_sold_listing(mp, listing_kwargs):
    listing = asyncio.run(mp.create_listing(**listing_kwargs))
    asyncio.run(mp.buy_agent(listing.listing_id, "0xBUYER"))
    with pytest.raises(ValueError, match="sold"):
        asyncio.run(mp.buy_agent(listing.listing_id, "0xBUYER2"))


def test_delist_agent(mp, listing_kwargs):
    listing = asyncio.run(mp.create_listing(**listing_kwargs))
    ok = asyncio.run(mp.delist_agent(listing.listing_id, "0xSELLER"))
    assert ok is True
    assert mp._listings[listing.listing_id].status == ListingStatus.DELISTED


def test_delist_wrong_seller_raises(mp, listing_kwargs):
    listing = asyncio.run(mp.create_listing(**listing_kwargs))
    with pytest.raises(PermissionError):
        asyncio.run(mp.delist_agent(listing.listing_id, "0xHACKER"))


def test_price_suggest(mp):
    price = mp.suggest_price(win_rate=0.6, total_pnl=1000.0, tournaments_won=1)
    # base=100, win=300, pnl=100, tournament=200 -> 700
    assert price == 700.0


def test_marketplace_stats(mp, listing_kwargs):
    asyncio.run(mp.create_listing(**listing_kwargs))
    stats = mp.get_marketplace_stats()
    assert stats["active_listings"] == 1
    assert stats["total_sold"] == 0
    assert stats["total_volume_karma"] == 0
