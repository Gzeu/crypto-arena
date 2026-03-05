"""
Base Agent & TradeProposal
==========================
Abstract base class for all CryptoArena agents.
Defines the interface every agent must implement.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TradeProposal:
    agent_id: str
    symbol: str
    side: str                    # LONG | SHORT | LP | BET-YES | BET-NO
    size_usdc: float
    leverage: float
    entry_price_estimate: Optional[float]
    stop_loss: float             # price or pct string e.g. '-7%'
    take_profit: float           # price or pct string
    rationale: str
    entry_logic: str = "market now"
    regime_alignment: str = ""
    reject_reason: str = ""

    def to_dict(self) -> dict:
        return {
            "agent": self.agent_id,
            "symbol": self.symbol,
            "side": self.side,
            "size": f"{self.size_usdc:.0f} USDC notional",
            "leverage": self.leverage,
            "entry_logic": self.entry_logic,
            "risk": {
                "stop_loss": str(self.stop_loss),
                "take_profit": str(self.take_profit),
            },
            "rationale": self.rationale,
        }


class BaseAgent(ABC):
    AGENT_ID: str = "A0"
    ARCHETYPE: str = "base"

    def __init__(self, config: dict):
        self.config = config
        self.agent_id = self.AGENT_ID
        self.risk_profile = config.get("risk_profile", {})
        self.strategy_params = config.get("strategy_params", {})

    @abstractmethod
    async def propose(
        self, regime: dict, snapshot: dict, portfolio
    ) -> List[TradeProposal]:
        """Generate trade proposals based on regime, snapshot and own portfolio."""
        ...

    def max_position_usdc(self, portfolio) -> float:
        if portfolio is None:
            return 500.0
        pct = self.risk_profile.get("max_position_pct", 0.10)
        return portfolio.total_equity * pct

    def is_regime_aligned(self, regime: dict, preferred_regimes: List[str]) -> bool:
        return regime.get("regime") in preferred_regimes
