"""
Quest Manager — defines, tracks, and rewards agent quests.
Quests run on MultiversX Supernova (NFT badges) and Base (Karma tokens).
"""

import asyncio
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional

from loguru import logger

from src.chain.multiversx_client import MultiversXClient
from src.chain.base_client import BaseChainClient


class QuestStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    PENDING = "pending"


@dataclass
class Quest:
    quest_id: str
    name: str
    description: str
    quest_type: str          # 'survival' | 'profit' | 'drawdown' | 'trade_count'
    requirements: Dict
    rewards: Dict            # {'karma': int, 'nft_badge': bool, 'title': str}
    chain: str = "multiversx"
    active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class QuestProgress:
    agent_id: str
    quest_id: str
    status: QuestStatus = QuestStatus.ACTIVE
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: Optional[str] = None
    nft_tx_hash: Optional[str] = None
    progress_pct: float = 0.0
    metadata: Dict = field(default_factory=dict)


class QuestManager:
    """
    Manages all quests across Tournament Week cycles.
    Called by ArenaCore every meso/macro cycle to check progress.
    """

    # Built-in quests for Tournament Week 1
    DEFAULT_QUESTS: List[Dict] = [
        {
            "quest_id": "Q001",
            "name": "Bear Survivor",
            "description": "Survive 7 days without liquidation in bear market",
            "quest_type": "survival",
            "requirements": {"duration_days": 7, "min_pnl_pct": -10.0},
            "rewards": {"karma": 1000, "nft_badge": True, "title": "Bear Survivor 🐻"},
            "chain": "multiversx",
        },
        {
            "quest_id": "Q002",
            "name": "10x Alpha Hunter",
            "description": "Achieve +10% return in a single week",
            "quest_type": "profit",
            "requirements": {"target_pnl_pct": 10.0, "duration_days": 7},
            "rewards": {"karma": 2500, "nft_badge": True, "title": "Alpha Hunter 🎯"},
            "chain": "multiversx",
        },
        {
            "quest_id": "Q003",
            "name": "Iron Hands",
            "description": "Hold a position for 48h+ with <5% drawdown",
            "quest_type": "drawdown",
            "requirements": {"hold_hours": 48, "max_drawdown_pct": 5.0},
            "rewards": {"karma": 500, "nft_badge": False, "title": "Iron Hands 🔩"},
            "chain": "base",
        },
        {
            "quest_id": "Q004",
            "name": "Volume King",
            "description": "Execute 20+ trades in Tournament Week 1",
            "quest_type": "trade_count",
            "requirements": {"min_trades": 20, "duration_days": 7},
            "rewards": {"karma": 750, "nft_badge": True, "title": "Volume King 👑"},
            "chain": "base",
        },
    ]

    def __init__(self):
        self._mvx = MultiversXClient()
        self._base = BaseChainClient()
        self._quests: Dict[str, Quest] = {}
        self._progress: Dict[str, Dict[str, QuestProgress]] = {}  # {agent_id: {quest_id: progress}}
        self._load_default_quests()
        logger.info("🗺️  QuestManager ready — {} quests loaded", len(self._quests))

    def _load_default_quests(self):
        for q in self.DEFAULT_QUESTS:
            self._quests[q["quest_id"]] = Quest(**q)

    def enroll_agent(self, agent_id: str):
        """Enroll an agent in all active quests."""
        self._progress[agent_id] = {}
        for quest_id, quest in self._quests.items():
            if quest.active:
                self._progress[agent_id][quest_id] = QuestProgress(
                    agent_id=agent_id,
                    quest_id=quest_id,
                )
        logger.info("📜 Agent {} enrolled in {} quests", agent_id, len(self._progress[agent_id]))

    async def tick(self, agent_id: str, agent_state: Dict):
        """
        Called every cycle. Updates progress and triggers completion.
        agent_state keys: pnl_pct, trade_count, days_active,
                          max_drawdown_pct, current_position_hours
        """
        if agent_id not in self._progress:
            self.enroll_agent(agent_id)

        for quest_id, progress in list(self._progress[agent_id].items()):
            if progress.status != QuestStatus.ACTIVE:
                continue
            quest = self._quests[quest_id]
            completed = await self._check_completion(quest, progress, agent_state)
            failed = self._check_failure(quest, progress, agent_state)

            if completed:
                await self._complete_quest(agent_id, quest_id, progress)
            elif failed:
                progress.status = QuestStatus.FAILED
                logger.warning("💀 Agent {} FAILED quest '{}'", agent_id, quest.name)

    async def _check_completion(self, quest: Quest,
                                 progress: QuestProgress,
                                 state: Dict) -> bool:
        req = quest.requirements
        t = quest.quest_type

        if t == "survival":
            days = state.get("days_active", 0)
            pnl = state.get("pnl_pct", 0)
            progress.progress_pct = min(100.0, days / req["duration_days"] * 100)
            return (days >= req["duration_days"]
                    and pnl >= req["min_pnl_pct"])

        if t == "profit":
            pnl = state.get("pnl_pct", 0)
            days = state.get("days_active", 0)
            progress.progress_pct = min(100.0, pnl / req["target_pnl_pct"] * 100)
            return (pnl >= req["target_pnl_pct"]
                    and days <= req["duration_days"])

        if t == "drawdown":
            hours = state.get("current_position_hours", 0)
            dd = state.get("max_drawdown_pct", 100)
            progress.progress_pct = min(100.0, hours / req["hold_hours"] * 100)
            return (hours >= req["hold_hours"]
                    and dd <= req["max_drawdown_pct"])

        if t == "trade_count":
            trades = state.get("trade_count", 0)
            progress.progress_pct = min(100.0, trades / req["min_trades"] * 100)
            return trades >= req["min_trades"]

        return False

    def _check_failure(self, quest: Quest,
                       progress: QuestProgress,
                       state: Dict) -> bool:
        req = quest.requirements
        if quest.quest_type == "survival":
            return state.get("pnl_pct", 0) < req["min_pnl_pct"] - 5
        return False

    async def _complete_quest(self, agent_id: str, quest_id: str,
                               progress: QuestProgress):
        quest = self._quests[quest_id]
        progress.status = QuestStatus.COMPLETED
        progress.completed_at = datetime.now(timezone.utc).isoformat()
        progress.progress_pct = 100.0

        logger.success("🏆 Agent {} completed quest '{}'", agent_id, quest.name)

        # Mint NFT badge
        if quest.rewards.get("nft_badge"):
            result = await self._mvx.mint_quest_nft(
                agent_id=agent_id,
                quest_name=quest.name,
                metadata={"quest_id": quest_id, "rewards": quest.rewards},
            )
            progress.nft_tx_hash = result.get("tx_hash")

        # Mint Karma
        if quest.rewards.get("karma", 0) > 0:
            karma_wei = quest.rewards["karma"] * 10 ** 18
            await self._base.mint_karma(
                to_address=agent_id,
                amount_wei=karma_wei,
            )

    def get_all_progress(self) -> Dict:
        """Return serialisable quest progress for all agents."""
        result = {}
        for agent_id, quests in self._progress.items():
            result[agent_id] = {
                qid: asdict(prog) for qid, prog in quests.items()
            }
        return result
