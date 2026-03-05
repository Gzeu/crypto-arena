"""A3 — SOL Short / Hedge Specialist"""
from typing import List
from src.agents.base import BaseAgent, TradeProposal


class A3SOLShortHedger(BaseAgent):
    AGENT_ID = "A3"
    ARCHETYPE = "short_hedger"

    async def propose(self, regime, snapshot, portfolio) -> List[TradeProposal]:
        sol_price = snapshot["prices"].get("SOL")
        if not sol_price:
            return []
        if regime["regime"] in ["Bear", "Crisis"]:
            size = min(self.max_position_usdc(portfolio) * 0.4, 400)
            return [TradeProposal(
                agent_id=self.AGENT_ID,
                symbol="SOL/USD",
                side="SHORT",
                size_usdc=size,
                leverage=2.0,
                entry_price_estimate=sol_price,
                stop_loss=round(sol_price * 1.05, 2),
                take_profit=round(sol_price * 0.82, 2),
                rationale="Bear regime; SOL short to hedge portfolio and capture downside.",
                entry_logic="limit at current ask + 0.2%",
                regime_alignment="Bear",
            )]
        return []
