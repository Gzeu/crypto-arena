"""
Reflection Agent
=================
Daily review of all agent performance.
Updates soft policy parameters and per-agent memory.
"""

from loguru import logger


class ReflectionAgent:
    def daily_review(self, state) -> dict:
        policy_changes = {}
        for agent_id, portfolio in state.portfolios.items():
            changes = {}
            if portfolio.win_rate < 0.40 and (portfolio.win_count + portfolio.loss_count) >= 5:
                changes["size_multiplier"] = 0.8
                logger.info("🔽 {} win rate low ({:.0%}) — reducing size",
                             agent_id, portfolio.win_rate)
            elif portfolio.win_rate > 0.65 and portfolio.daily_drawdown < 0.05:
                changes["size_multiplier"] = 1.1
                logger.info("🔼 {} performing well — slightly increasing size", agent_id)
            if portfolio.de_risk_mode:
                changes["de_risk_reset"] = True
                portfolio.de_risk_mode = False
                logger.info("♻️  {} de-risk mode reset for new day", agent_id)
            if changes:
                policy_changes[agent_id] = changes
        return {"policy_changes": policy_changes}
