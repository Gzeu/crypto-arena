"""A4 — Meme Sniper"""
from typing import List
from src.agents.base import BaseAgent, TradeProposal


class A4MemeSniper(BaseAgent):
    AGENT_ID = "A4"
    ARCHETYPE = "meme_sniper"

    async def propose(self, regime, snapshot, portfolio) -> List[TradeProposal]:
        memes = snapshot.get("meme_coins", [])
        if not memes:
            return []
        # Target top meme by volume with positive momentum
        top = max(memes, key=lambda m: m.get("volume_24h", 0))
        chg = top.get("price_change_24h", 0)
        if chg > 5 and regime["regime"] in ["Bull", "Sideways"]:
            size = min(self.max_position_usdc(portfolio) * 0.3, 300)
            price = top["price"]
            return [TradeProposal(
                agent_id=self.AGENT_ID,
                symbol=f"{top['symbol']}/USDC",
                side="LONG",
                size_usdc=size,
                leverage=1.0,
                entry_price_estimate=price,
                stop_loss=round(price * 0.85, 6),
                take_profit=round(price * 1.30, 6),
                rationale=f"{top['symbol']} volume surge ({chg:+.1f}% 24h); meme momentum play.",
                entry_logic="market now",
                regime_alignment="Meme momentum",
            )]
        return []
