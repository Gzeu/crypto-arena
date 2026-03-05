"""A2 — ETH Swing / Mean-Reversion Trader"""
from typing import List
from src.agents.base import BaseAgent, TradeProposal


class A2ETHSwingTrader(BaseAgent):
    AGENT_ID = "A2"
    ARCHETYPE = "swing_mean_reversion"

    async def propose(self, regime, snapshot, portfolio) -> List[TradeProposal]:
        eth_price = snapshot["prices"].get("ETH")
        eth_chg = snapshot["price_changes_24h"].get("ETH", 0)
        if not eth_price:
            return []
        # Mean-reversion: buy oversold dips in sideways/bear
        if eth_chg < -5 and regime["regime"] in ["Bear", "Sideways"]:
            size = min(self.max_position_usdc(portfolio) * 0.4, 400)
            return [TradeProposal(
                agent_id=self.AGENT_ID,
                symbol="ETH/USD",
                side="LONG",
                size_usdc=size,
                leverage=1.5,
                entry_price_estimate=eth_price,
                stop_loss=round(eth_price * 0.93, 2),
                take_profit=round(eth_price * 1.10, 2),
                rationale=f"ETH oversold ({eth_chg:+.1f}% 24h); contrarian bounce setup.",
                entry_logic="market now",
                regime_alignment="Sideways/Bear bounce",
            )]
        return []
