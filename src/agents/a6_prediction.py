"""A6 — Prediction Market Agent"""
from typing import List
from src.agents.base import BaseAgent, TradeProposal


class A6PredictionMarketAgent(BaseAgent):
    AGENT_ID = "A6"
    ARCHETYPE = "prediction_market"

    async def propose(self, regime, snapshot, portfolio) -> List[TradeProposal]:
        # First cycle: observe only, no bets placed
        # Future cycles: scan Polymarket for mispriced odds
        return []
