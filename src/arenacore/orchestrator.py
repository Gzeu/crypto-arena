"""
ArenaCore Orchestrator
=======================
Main event loop that coordinates all sub-agents in CryptoArena.
Runs micro / meso / macro cycles and handles event-based triggers.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Optional
from loguru import logger

from src.state.game_state import GameState
from src.market.scout import MarketScout
from src.regime.detector import RegimeDetector
from src.risk.guardian import RiskGuardian
from src.execution.executor import TraderExecutor
from src.narrative.weaver import NarrativeWeaver
from src.reflection.agent import ReflectionAgent
from src.agents.crew import AgentCrew


class ArenaCore:
    """
    ArenaCore orchestrates the full CryptoArena game loop.
    
    Responsibilities:
    - Manage game state and agent portfolio ledgers
    - Run micro (5m), meso (1h), macro (24h) cycles
    - Respond to event-based triggers (regime shifts, liquidations, etc.)
    - Emit structured decision outputs in canonical JSON format
    """

    def __init__(self, config: dict):
        self.config = config
        self.state = GameState(config)
        self.scout = MarketScout(config)
        self.regime_detector = RegimeDetector()
        self.crew = AgentCrew(config)
        self.risk_guardian = RiskGuardian(config)
        self.executor = TraderExecutor(mode=config["game"]["execution_mode"])
        self.narrative = NarrativeWeaver()
        self.reflection = ReflectionAgent()
        self._cycle_count = 0
        logger.info("🏟️  ArenaCore initialized — Mode: {}", config["game"]["execution_mode"])

    async def run_micro_cycle(self) -> dict:
        """
        Micro cycle (~5 minutes):
        1. Pull live market snapshot
        2. Detect current regime
        3. Each agent proposes trades
        4. Risk Guardian filters
        5. Executor runs approved trades
        6. Narrative tick update
        Returns the structured decision output.
        """
        self._cycle_count += 1
        ts = datetime.now(timezone.utc).isoformat()
        logger.info("⚡ Micro cycle #{} @ {}", self._cycle_count, ts)

        # Step 1: Market snapshot
        snapshot = await self.scout.fetch_snapshot()
        self.state.add_snapshot(snapshot)

        # Step 2: Regime detection
        regime_result = self.regime_detector.detect(snapshot)
        self.state.update_regime(regime_result)

        # Step 3: Strategy proposals from each agent
        proposals = await self.crew.generate_proposals(
            regime=regime_result,
            snapshot=snapshot,
            portfolios=self.state.portfolios,
        )

        # Step 4: Risk filter
        approved, rejected = self.risk_guardian.filter(proposals, self.state.portfolios)
        if rejected:
            logger.warning("🛑 Risk Guardian rejected {} proposal(s)", len(rejected))

        # Step 5: Execute approved trades
        execution_log = await self.executor.execute_batch(approved)
        self.state.apply_executions(execution_log)

        # Step 6: Narrative tick
        tick = self.narrative.generate_tick(
            regime=regime_result,
            executions=execution_log,
            portfolios=self.state.portfolios,
        )

        output = self._build_output(
            snapshot=snapshot,
            regime=regime_result,
            approved=approved,
            rejected=rejected,
            execution_log=execution_log,
            tick=tick,
        )
        logger.info("✅ Micro cycle #{} complete — Regime: {}", self._cycle_count, regime_result["regime"])
        return output

    async def run_meso_cycle(self):
        """Hourly: evaluate performance per agent, rebalance risk parameters."""
        logger.info("📊 Meso cycle — evaluating hourly performance")
        self.state.compute_hourly_metrics()
        self.risk_guardian.adjust_parameters(self.state)
        self.state.update_leaderboard()

    async def run_macro_cycle(self):
        """Daily: full reflection, chronicle, memory update."""
        logger.info("🌙 Macro cycle — daily reflection & chronicle")
        report = self.reflection.daily_review(self.state)
        chronicle = self.narrative.generate_chronicle(self.state)
        self.state.apply_daily_reflection(report)
        logger.info("📖 Chronicle: {}", chronicle[:120])

    def _build_output(self, snapshot, regime, approved, rejected, execution_log, tick) -> dict:
        """Build the canonical JSON decision cycle output (Section 7 format)."""
        return {
            "cycle": self._cycle_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "thought": self._synthesize_thought(snapshot, regime),
            "regime_detected": regime,
            "storyline_update": tick,
            "action_plan": [a.to_dict() for a in approved],
            "rejected_proposals": [r.to_dict() for r in rejected],
            "execution": {
                "mode": self.executor.mode,
                "to_execute_now": [e["description"] for e in execution_log if e["status"] == "executed"],
                "pending_conditions": [e["description"] for e in execution_log if e["status"] == "pending"],
            },
        }

    def _synthesize_thought(self, snapshot: dict, regime: dict) -> str:
        btc = snapshot.get("prices", {}).get("BTC", "?")
        eth = snapshot.get("prices", {}).get("ETH", "?")
        sol = snapshot.get("prices", {}).get("SOL", "?")
        r = regime.get("regime", "Unknown")
        top_prob = max(regime.get("probabilities", {}).values(), default=0)
        return (
            f"Market snapshot pulled: BTC={btc}, ETH={eth}, SOL={sol}. "
            f"Regime classified as '{r}' with {top_prob:.0%} confidence. "
            f"Risk Guardian is active. All 8 agents evaluating proposals in {self.executor.mode} mode. "
            f"Cycle {self._cycle_count} — survival and information-gathering priority."
        )

    async def start(self):
        """Main entry point: start the game loop."""
        logger.info("🚀 CryptoArena STARTED")
        micro_interval = self.config["cycles"]["micro_interval_seconds"]
        meso_interval = self.config["cycles"]["meso_interval_seconds"]
        macro_interval = self.config["cycles"]["macro_interval_seconds"]

        micro_tick = 0
        meso_tick = 0

        while True:
            output = await self.run_micro_cycle()
            print(json.dumps(output, indent=2, default=str))

            micro_tick += micro_interval
            if micro_tick >= meso_interval:
                micro_tick = 0
                meso_tick += meso_interval
                await self.run_meso_cycle()

            if meso_tick >= macro_interval:
                meso_tick = 0
                await self.run_macro_cycle()

            await asyncio.sleep(micro_interval)
