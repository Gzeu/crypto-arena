"""
Agent Crew Manager
==================
Coordinates all 8 specialized agents and collects
their strategy proposals each cycle.
"""

from typing import List
from loguru import logger
from src.agents.base import BaseAgent, TradeProposal
from src.agents.a1_btc_trend import A1BTCTrendFollower
from src.agents.a2_eth_swing import A2ETHSwingTrader
from src.agents.a3_sol_short import A3SOLShortHedger
from src.agents.a4_meme_sniper import A4MemeSniper
from src.agents.a5_defi_basis import A5DeFiBasisTrader
from src.agents.a6_prediction import A6PredictionMarketAgent
from src.agents.a7_index import A7RiskAdjustedIndex
from src.agents.a8_chaos import A8ChaosExplorer


AGENT_CLASSES = [
    A1BTCTrendFollower,
    A2ETHSwingTrader,
    A3SOLShortHedger,
    A4MemeSniper,
    A5DeFiBasisTrader,
    A6PredictionMarketAgent,
    A7RiskAdjustedIndex,
    A8ChaosExplorer,
]


class AgentCrew:
    def __init__(self, config: dict):
        self.agents: List[BaseAgent] = []
        agent_cfgs = {a["id"]: a for a in config.get("agents", [])}
        for cls in AGENT_CLASSES:
            agent_id = cls.AGENT_ID
            cfg = agent_cfgs.get(agent_id, {})
            self.agents.append(cls(cfg))
        logger.info("🤖 Agent Crew assembled: {} agents", len(self.agents))

    async def generate_proposals(
        self, regime: dict, snapshot: dict, portfolios: dict
    ) -> List[TradeProposal]:
        all_proposals = []
        for agent in self.agents:
            portfolio = portfolios.get(agent.agent_id)
            try:
                proposals = await agent.propose(
                    regime=regime, snapshot=snapshot, portfolio=portfolio
                )
                all_proposals.extend(proposals)
            except Exception as e:
                logger.error("❌ Agent {} proposal error: {}", agent.agent_id, e)
        logger.info("📋 Total proposals this cycle: {}", len(all_proposals))
        return all_proposals
