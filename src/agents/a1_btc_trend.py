"""A1 — BTC Trend Follower"""
from typing import List
from src.agents.base import BaseAgent, TradeProposal


class A1BTCTrendFollower(BaseAgent):
    AGENT_ID = "A1"
    ARCHETYPE = "trend_follower"

    async def propose(self, regime, snapshot, portfolio) -> List[TradeProposal]:
        if not self.is_regime_aligned(regime, ["Bull"]):
            return []  # Only trend-follow in Bull regime
        btc_price = snapshot["prices"].get("BTC")
        if not btc_price:
            return []
        size = min(self.max_position_usdc(portfolio) * 0.5, 500)  # first cycle: small
        return [TradeProposal(
            agent_id=self.AGENT_ID,
            symbol="BTC/USD",
            side="LONG",
            size_usdc=size,
            leverage=self.risk_profile.get("preferred_leverage", 2.0),
            entry_price_estimate=btc_price,
            stop_loss=round(btc_price * 0.93, 2),
            take_profit=round(btc_price * 1.12, 2),
            rationale="Bull regime confirmed; riding BTC momentum with trend-following setup.",
            entry_logic="market now, within current spread",
            regime_alignment="Bull",
        )]
