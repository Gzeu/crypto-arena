"""
ArenaCore Orchestrator v1.1
============================
Upgrade over v1.0:
  - Persistent agent memory (Mem0)
  - Social publishing (Twitter/X + Discord)
  - On-chain sync (Base L2: Karma, Leaderboard, NFTs)
  - Quest system (MultiversX Supernova + Base)
  - Tournament mode (weekly cycles)
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Optional

from loguru import logger

# Core (v1.0 components, reused)
from src.state.game_state import GameState
from src.market.scout import MarketScout
from src.regime.detector import RegimeDetector
from src.risk.guardian import RiskGuardian
from src.execution.executor import TraderExecutor
from src.narrative.weaver import NarrativeWeaver
from src.reflection.agent import ReflectionAgent
from src.agents.crew import AgentCrew

# NEW v1.1
from src.memory.mem0_manager import AgentMemoryManager
from src.social.chronicle_publisher import ChroniclePublisher
from src.chain.base_client import BaseChainClient
from src.quests.quest_manager import QuestManager
from src.tournament.tournament_manager import TournamentManager


class ArenaCoreV11:
    """
    CryptoArena Orchestrator v1.1 — production-grade, fully autonomous.

    New additions vs v1.0
    ---------------------
    * memory_managers  : per-agent Mem0 persistent memory
    * publisher        : multi-platform social posts (Twitter + Discord)
    * base_chain       : Base L2 on-chain sync (Karma, Leaderboard)
    * quest_manager    : quest lifecycle + NFT badge minting
    * tournament       : weekly tournament mode
    """

    SOCIAL_POST_EVERY_N_MESO = 6   # post chronicle every 6 meso ticks (~6 h)
    ONCHAIN_SYNC_EVERY_N_MESO = 12  # sync leaderboard on-chain every 12 h

    def __init__(self, config: dict):
        self.config = config
        self.mode = config["game"]["execution_mode"]  # 'paper' | 'live'

        # --- v1.0 core ---
        self.state = GameState(config)
        self.scout = MarketScout(config)
        self.regime_detector = RegimeDetector()
        self.crew = AgentCrew(config)
        self.risk_guardian = RiskGuardian(config)
        self.executor = TraderExecutor(mode=self.mode)
        self.narrative = NarrativeWeaver()
        self.reflection = ReflectionAgent()

        # --- v1.1 new ---
        agent_ids = [a["id"] for a in config.get("agents", [])]
        self.memory_managers = {
            aid: AgentMemoryManager(aid, config)
            for aid in agent_ids
        }
        self.publisher = ChroniclePublisher(self.state)
        self.base_chain = BaseChainClient()
        self.quest_manager = QuestManager()
        self.tournament = TournamentManager(publisher=self.publisher)

        self._cycle_count = 0
        self._meso_count = 0
        self._tournament_id: Optional[str] = None

        logger.success(
            "🏟️  ArenaCoreV11 ready — Mode: {} | Agents: {}",
            self.mode, len(agent_ids)
        )

    # ------------------------------------------------------------------
    # Micro cycle  (~5 min)
    # ------------------------------------------------------------------

    async def run_micro_cycle(self) -> dict:
        self._cycle_count += 1
        ts = datetime.now(timezone.utc).isoformat()
        logger.info("⚡ Micro cycle #{} @ {}", self._cycle_count, ts)

        # 1. Market snapshot
        snapshot = await self.scout.fetch_snapshot()
        self.state.add_snapshot(snapshot)

        # 2. Regime detection
        regime = self.regime_detector.detect(snapshot)
        self.state.update_regime(regime)

        # 3. Memory-augmented proposals
        proposals = await self._memory_augmented_proposals(regime, snapshot)

        # 4. Risk filter
        approved, rejected = self.risk_guardian.filter(proposals, self.state.portfolios)

        # 5. Execute
        exec_log = await self.executor.execute_batch(approved)
        self.state.apply_executions(exec_log)

        # 6. Post-trade reflection (store lessons)
        await self._post_trade_reflect(exec_log)

        # 7. Quest tick for each agent
        await self._tick_quests()

        # 8. Tournament score update
        if self._tournament_id:
            scores = {
                aid: self.state.portfolios[aid].pnl_pct
                for aid in self.state.portfolios
            }
            await self.tournament.update_scores(scores)

        # 9. Narrative tick
        tick = self.narrative.generate_tick(
            regime=regime,
            executions=exec_log,
            portfolios=self.state.portfolios,
        )

        # 10. Trade alert on significant moves
        for e in exec_log:
            if e.get("status") == "executed" and abs(e.get("notional", 0)) > 10_000:
                await self.publisher.publish_trade_alert(e["agent_id"], e)

        output = self._build_output(snapshot, regime, approved, rejected, exec_log, tick)
        logger.info("✅ Micro #{} — Regime: {}", self._cycle_count, regime["regime"])
        return output

    # ------------------------------------------------------------------
    # Meso cycle  (~1 h)
    # ------------------------------------------------------------------

    async def run_meso_cycle(self):
        self._meso_count += 1
        logger.info("📊 Meso cycle #{}", self._meso_count)

        self.state.compute_hourly_metrics()
        self.risk_guardian.adjust_parameters(self.state)
        self.state.update_leaderboard()

        # Social: post every N meso ticks
        if self._meso_count % self.SOCIAL_POST_EVERY_N_MESO == 0:
            chronicle = self.narrative.generate_chronicle(self.state)
            lb = self.state.get_leaderboard()
            await self.publisher.publish_chronicle(
                chronicle, leaderboard=lb,
                tags=["Tournament", f"Week{self._meso_count // self.SOCIAL_POST_EVERY_N_MESO}"]
            )

        # On-chain: sync leaderboard periodically
        if self._meso_count % self.ONCHAIN_SYNC_EVERY_N_MESO == 0:
            lb = self.state.get_leaderboard()
            await self.base_chain.sync_leaderboard(lb)

    # ------------------------------------------------------------------
    # Macro cycle  (daily)
    # ------------------------------------------------------------------

    async def run_macro_cycle(self):
        logger.info("🌙 Macro cycle — daily reflection")

        report = self.reflection.daily_review(self.state)
        self.state.apply_daily_reflection(report)

        chronicle = self.narrative.generate_chronicle(self.state)
        lb = self.state.get_leaderboard()
        await self.publisher.publish_chronicle(
            chronicle, leaderboard=lb, tags=["DailyChronicle"]
        )

        # Store daily market pattern memory for each agent
        regime = self.state.current_regime
        for aid, mem in self.memory_managers.items():
            await mem.record_market_pattern(
                pattern=regime.get("regime", "Unknown"),
                conditions={
                    "confidence": regime.get("confidence", 0),
                    "btc": self.state.latest_snapshot.get("prices", {}).get("BTC"),
                },
            )

    # ------------------------------------------------------------------
    # Tournament helpers
    # ------------------------------------------------------------------

    def init_tournament(self, week: int = 1) -> str:
        t = self.tournament.create_tournament(week_number=week)
        for aid in self.state.portfolios:
            self.tournament.register_agent(t.tournament_id, aid)
        self.tournament.start_tournament(t.tournament_id)
        self._tournament_id = t.tournament_id
        logger.success("🏆 Tournament {} initialised", t.tournament_id)
        return t.tournament_id

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    async def _memory_augmented_proposals(self, regime, snapshot):
        """Generate proposals with memory context injected."""
        proposals = await self.crew.generate_proposals(
            regime=regime,
            snapshot=snapshot,
            portfolios=self.state.portfolios,
        )
        for prop in proposals:
            aid = prop.agent_id
            if aid in self.memory_managers:
                memories = await self.memory_managers[aid].recall(
                    query=f"{snapshot.get('prices',{}).get('BTC','?')} {regime['regime']}",
                    memory_type="lesson",
                    limit=3,
                )
                prop.memory_context = memories
        return proposals

    async def _post_trade_reflect(self, exec_log):
        for e in exec_log:
            aid = e.get("agent_id")
            if aid and aid in self.memory_managers and e.get("pnl_pct") is not None:
                await self.memory_managers[aid].reflect_on_trade(e)

    async def _tick_quests(self):
        for aid in self.state.portfolios:
            p = self.state.portfolios[aid]
            agent_state = {
                "pnl_pct": getattr(p, "pnl_pct", 0),
                "trade_count": getattr(p, "trade_count", 0),
                "days_active": self._cycle_count // 288,  # 288 5-min cycles = 1 day
                "max_drawdown_pct": getattr(p, "max_drawdown_pct", 0),
                "current_position_hours": getattr(p, "current_position_hours", 0),
            }
            await self.quest_manager.tick(aid, agent_state)

    def _build_output(self, snapshot, regime, approved, rejected, exec_log, tick) -> dict:
        return {
            "version": "1.1",
            "cycle": self._cycle_count,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mode": self.mode,
            "thought": self._synthesize_thought(snapshot, regime),
            "regime_detected": regime,
            "storyline_update": tick,
            "action_plan": [a.to_dict() for a in approved],
            "rejected_proposals": [r.to_dict() for r in rejected],
            "execution": {
                "mode": self.executor.mode,
                "executed": [e["description"] for e in exec_log if e["status"] == "executed"],
                "pending": [e["description"] for e in exec_log if e["status"] == "pending"],
            },
            "quest_progress": self.quest_manager.get_all_progress(),
            "tournament": (
                self.tournament.get_standings(self._tournament_id)
                if self._tournament_id else []
            ),
        }

    def _synthesize_thought(self, snapshot, regime) -> str:
        prices = snapshot.get("prices", {})
        btc = prices.get("BTC", "?")
        eth = prices.get("ETH", "?")
        sol = prices.get("SOL", "?")
        r = regime.get("regime", "Unknown")
        conf = regime.get("confidence", 0)
        return (
            f"[v1.1] BTC={btc} ETH={eth} SOL={sol}. "
            f"Regime '{r}' @ {conf:.0%}. "
            f"Memory-augmented proposals active. "
            f"Quest tracker running. "
            f"Tournament {'active' if self._tournament_id else 'idle'}. "
            f"Cycle {self._cycle_count}."
        )

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    async def start(self, init_tournament: bool = True):
        """Start the full v1.1 game loop."""
        logger.success("🚀 CryptoArena v1.1 STARTED")

        if init_tournament:
            self.init_tournament(week=1)

        cycles = self.config["cycles"]
        micro_s = cycles["micro_interval_seconds"]
        meso_s  = cycles["meso_interval_seconds"]
        macro_s = cycles["macro_interval_seconds"]

        micro_tick = meso_tick = 0

        while True:
            output = await self.run_micro_cycle()
            print(json.dumps(output, indent=2, default=str))

            micro_tick += micro_s
            if micro_tick >= meso_s:
                micro_tick = 0
                meso_tick += meso_s
                await self.run_meso_cycle()

            if meso_tick >= macro_s:
                meso_tick = 0
                await self.run_macro_cycle()

            await asyncio.sleep(micro_s)
