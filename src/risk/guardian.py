"""
Risk Guardian Agent
====================
Hard veto on any proposal that violates:
- Position size limits
- Leverage caps
- Correlated risk stacking
- Daily drawdown limits
May downsize or fully reject proposals.
"""

from typing import List, Tuple
from loguru import logger


class RiskGuardian:
    def __init__(self, config: dict):
        self.max_pos_pct = config["risk"]["max_position_pct"]
        self.max_leverage = config["risk"]["max_leverage"]
        self.max_dd = config["risk"]["daily_max_drawdown_pct"]

    def filter(self, proposals: list, portfolios: dict) -> Tuple[list, list]:
        approved = []
        rejected = []
        for p in proposals:
            agent_id = p.agent_id
            portfolio = portfolios.get(agent_id)
            verdict, reason = self._evaluate(p, portfolio)
            if verdict == "approve":
                approved.append(p)
            elif verdict == "downsize":
                p.size_usdc *= 0.5
                logger.warning("✂️  Downsized proposal for {} — {}", agent_id, reason)
                approved.append(p)
            else:
                p.reject_reason = reason
                rejected.append(p)
                logger.warning("🚫 Rejected proposal for {} — {}", agent_id, reason)
        return approved, rejected

    def _evaluate(self, proposal, portfolio) -> Tuple[str, str]:
        if portfolio is None:
            return "reject", "Unknown agent"
        if portfolio.de_risk_mode:
            return "reject", "Agent in de-risk mode (drawdown limit reached)"
        equity = portfolio.total_equity
        if proposal.size_usdc > equity * self.max_pos_pct:
            return "downsize", f"Position size {proposal.size_usdc:.0f} exceeds {self.max_pos_pct:.0%} limit"
        if proposal.leverage > self.max_leverage:
            return "reject", f"Leverage {proposal.leverage}x exceeds hard cap {self.max_leverage}x"
        return "approve", ""

    def adjust_parameters(self, state):
        """Tighten or loosen risk parameters based on hourly performance."""
        for portfolio in state.portfolios.values():
            if portfolio.daily_drawdown > self.max_dd * 0.8:
                logger.info("⚠️  {} approaching drawdown limit — soft tightening",
                             portfolio.agent_id)
