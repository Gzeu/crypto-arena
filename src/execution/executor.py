"""
Trader Executor Agent
======================
Translates approved proposals into paper trade updates
or live API calls (when real mode is enabled).
"""

from datetime import datetime, timezone
from typing import List
from loguru import logger


class TraderExecutor:
    def __init__(self, mode: str = "simulation"):
        self.mode = mode
        if mode == "live":
            logger.warning("🔴 LIVE MODE ACTIVE — real funds at risk!")
        else:
            logger.info("🟢 Simulation mode — paper trading only")

    async def execute_batch(self, approved_proposals: list) -> List[dict]:
        """Execute all approved proposals."""
        log = []
        for proposal in approved_proposals:
            entry = await self._execute_single(proposal)
            log.append(entry)
        return log

    async def _execute_single(self, proposal) -> dict:
        """Simulate or live-execute a single proposal."""
        ts = datetime.now(timezone.utc).isoformat()
        if self.mode == "simulation":
            # Paper trade: just log it
            entry_price = proposal.entry_price_estimate or 0
            log_entry = {
                "timestamp": ts,
                "agent_id": proposal.agent_id,
                "symbol": proposal.symbol,
                "side": proposal.side,
                "size_usdc": proposal.size_usdc,
                "leverage": proposal.leverage,
                "entry_price": entry_price,
                "stop_loss": proposal.stop_loss,
                "take_profit": proposal.take_profit,
                "rationale": proposal.rationale,
                "mode": "simulation",
                "status": "executed",
                "description": (
                    f"{proposal.agent_id} | {proposal.side} {proposal.symbol} "
                    f"${proposal.size_usdc:.0f} @ {entry_price} "
                    f"(SL: {proposal.stop_loss}, TP: {proposal.take_profit})"
                ),
            }
            logger.info("📝 Paper trade: {}", log_entry["description"])
            return log_entry
        else:
            # Live mode: would call CEX/DEX API here
            raise NotImplementedError("Live trading not yet wired — enable only after audit")
