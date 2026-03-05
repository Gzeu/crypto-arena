"""A8 — Chaos / Exploration Agent"""
import random
from typing import List
from src.agents.base import BaseAgent, TradeProposal


class A8ChaosExplorer(BaseAgent):
    AGENT_ID = "A8"
    ARCHETYPE = "chaos_exploration"

    SYMBOLS = ["BTC", "ETH", "SOL"]

    async def propose(self, regime, snapshot, portfolio) -> List[TradeProposal]:
        # Very small random exploration trade each cycle
        symbol = random.choice(self.SYMBOLS)
        price = snapshot["prices"].get(symbol)
        if not price:
            return []
        side = random.choice(["LONG", "SHORT"])
        size = min(self.max_position_usdc(portfolio) * 0.3, 200)
        sl = round(price * (0.92 if side == "LONG" else 1.08), 2)
        tp = round(price * (1.15 if side == "LONG" else 0.85), 2)
        return [TradeProposal(
            agent_id=self.AGENT_ID,
            symbol=f"{symbol}/USD",
            side=side,
            size_usdc=size,
            leverage=1.0,
            entry_price_estimate=price,
            stop_loss=sl,
            take_profit=tp,
            rationale=f"Chaos exploration: random {side} on {symbol} to probe market edges.",
            entry_logic="market now",
            regime_alignment="Exploratory",
        )]
