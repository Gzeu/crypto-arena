"""A5 — DeFi / Basis Trader"""
from typing import List
from src.agents.base import BaseAgent, TradeProposal


class A5DeFiBasisTrader(BaseAgent):
    AGENT_ID = "A5"
    ARCHETYPE = "defi_basis"

    async def propose(self, regime, snapshot, portfolio) -> List[TradeProposal]:
        # Basis / funding rate play: in any regime, look for yield
        # In MVP, probe with a small BTC spot long vs perp short (cash-and-carry)
        btc_price = snapshot["prices"].get("BTC")
        if not btc_price:
            return []
        size = min(self.max_position_usdc(portfolio) * 0.2, 200)
        return [TradeProposal(
            agent_id=self.AGENT_ID,
            symbol="BTC/USD",
            side="LONG",
            size_usdc=size,
            leverage=1.0,
            entry_price_estimate=btc_price,
            stop_loss=round(btc_price * 0.95, 2),
            take_profit=round(btc_price * 1.05, 2),
            rationale="Spot BTC leg of cash-and-carry basis trade; awaiting funding rate data.",
            entry_logic="market now — spot only",
            regime_alignment="Any (yield focus)",
        )]
