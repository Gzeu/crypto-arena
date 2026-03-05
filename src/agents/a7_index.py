"""A7 — Risk-Adjusted Index Agent"""
from typing import List
from src.agents.base import BaseAgent, TradeProposal


class A7RiskAdjustedIndex(BaseAgent):
    AGENT_ID = "A7"
    ARCHETYPE = "index_balanced"

    TARGET_WEIGHTS = {"BTC": 0.50, "ETH": 0.30, "SOL": 0.20}

    async def propose(self, regime, snapshot, portfolio) -> List[TradeProposal]:
        proposals = []
        if regime["regime"] == "Crisis":
            return []  # Hold cash in crisis
        total_equity = portfolio.total_equity if portfolio else 10000
        deploy = total_equity * 0.05  # first cycle: 5% deployment
        for symbol, weight in self.TARGET_WEIGHTS.items():
            price = snapshot["prices"].get(symbol)
            if not price:
                continue
            size = deploy * weight
            proposals.append(TradeProposal(
                agent_id=self.AGENT_ID,
                symbol=f"{symbol}/USD",
                side="LONG",
                size_usdc=size,
                leverage=1.0,
                entry_price_estimate=price,
                stop_loss=round(price * 0.90, 2),
                take_profit=round(price * 1.15, 2),
                rationale=f"Index rebalance: {weight:.0%} target weight for {symbol}.",
                entry_logic="market now — spot",
                regime_alignment="Any (index)",
            ))
        return proposals
