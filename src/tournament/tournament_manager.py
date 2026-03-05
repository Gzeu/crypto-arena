"""
Tournament Manager — weekly competition cycles.
Handles entry, scoring, prize distribution, and narrative spotlight.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional

from loguru import logger

from src.chain.base_client import BaseChainClient
from src.social.chronicle_publisher import ChroniclePublisher


class TournamentStatus(str, Enum):
    REGISTRATION = "registration"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class TournamentEntry:
    agent_id: str
    entry_karma: int = 500
    registered_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    final_pnl_pct: Optional[float] = None
    final_rank: Optional[int] = None
    karma_won: int = 0


@dataclass
class Tournament:
    tournament_id: str
    week_number: int
    name: str
    start_time: str
    end_time: str
    entry_karma: int = 500
    status: TournamentStatus = TournamentStatus.REGISTRATION
    entries: List[TournamentEntry] = field(default_factory=list)
    karma_pot: int = 0
    winner_id: Optional[str] = None
    winner_karma: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class TournamentManager:
    """
    Manages tournament lifecycle:
    1. Registration (collect entry karma)
    2. Active  (score updates every cycle)
    3. Completed (distribute prizes, post chronicle)
    """

    PRIZE_SPLIT = {1: 0.50, 2: 0.25, 3: 0.15, 4: 0.10}  # rank → % of pot

    def __init__(self, publisher: Optional[ChroniclePublisher] = None):
        self._base = BaseChainClient()
        self._publisher = publisher
        self._tournaments: Dict[str, Tournament] = {}
        self._active_id: Optional[str] = None
        logger.info("🏆 TournamentManager ready")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def create_tournament(self, week_number: int, duration_days: int = 7,
                           entry_karma: int = 500) -> Tournament:
        now = datetime.now(timezone.utc)
        tid = f"TW{week_number:03d}"
        t = Tournament(
            tournament_id=tid,
            week_number=week_number,
            name=f"Tournament Week {week_number}",
            start_time=now.isoformat(),
            end_time=(now + timedelta(days=duration_days)).isoformat(),
            entry_karma=entry_karma,
        )
        self._tournaments[tid] = t
        logger.info("🗓️  Tournament {} created — {} day(s), {} KARMA entry",
                    tid, duration_days, entry_karma)
        return t

    def register_agent(self, tournament_id: str, agent_id: str) -> bool:
        t = self._tournaments.get(tournament_id)
        if not t or t.status != TournamentStatus.REGISTRATION:
            return False
        if any(e.agent_id == agent_id for e in t.entries):
            logger.warning("{} already registered in {}", agent_id, tournament_id)
            return False
        t.entries.append(TournamentEntry(agent_id=agent_id, entry_karma=t.entry_karma))
        t.karma_pot += t.entry_karma
        logger.info("✅ {} registered for {} — Pot: {} KARMA",
                    agent_id, tournament_id, t.karma_pot)
        return True

    def start_tournament(self, tournament_id: str):
        t = self._tournaments.get(tournament_id)
        if t:
            t.status = TournamentStatus.ACTIVE
            self._active_id = tournament_id
            logger.success("🚀 Tournament {} STARTED — {} agents, {} KARMA pot",
                           tournament_id, len(t.entries), t.karma_pot)

    async def update_scores(self, scores: Dict[str, float]):
        """
        Called every cycle with {agent_id: pnl_pct} dict.
        Updates entries and checks if tournament is over.
        """
        if not self._active_id:
            return
        t = self._tournaments[self._active_id]
        if t.status != TournamentStatus.ACTIVE:
            return

        for entry in t.entries:
            if entry.agent_id in scores:
                entry.final_pnl_pct = scores[entry.agent_id]

        # Rank by PnL
        sorted_entries = sorted(
            t.entries,
            key=lambda e: e.final_pnl_pct or -999,
            reverse=True,
        )
        for rank, entry in enumerate(sorted_entries, 1):
            entry.final_rank = rank

        # Check if time's up
        end = datetime.fromisoformat(t.end_time)
        if datetime.now(timezone.utc) >= end:
            await self._complete_tournament(t)

    async def _complete_tournament(self, t: Tournament):
        t.status = TournamentStatus.COMPLETED
        sorted_entries = sorted(
            t.entries,
            key=lambda e: e.final_pnl_pct or -999,
            reverse=True,
        )

        # Distribute karma prizes
        prize_txs = []
        for rank, entry in enumerate(sorted_entries, 1):
            split_pct = self.PRIZE_SPLIT.get(rank, 0)
            karma_prize = int(t.karma_pot * split_pct)
            entry.karma_won = karma_prize
            if karma_prize > 0:
                tx = await self._base.mint_karma(
                    to_address=entry.agent_id,
                    amount_wei=karma_prize * 10 ** 18,
                )
                prize_txs.append(tx)

        t.winner_id = sorted_entries[0].agent_id
        t.winner_karma = sorted_entries[0].karma_won
        self._active_id = None

        logger.success(
            "🏆 {} COMPLETED! Winner: {} (+{:.2f}%) — {} KARMA",
            t.tournament_id,
            t.winner_id,
            sorted_entries[0].final_pnl_pct or 0,
            t.winner_karma,
        )

        # Publish result
        if self._publisher:
            podium = sorted_entries[:3]
            chronicle = (
                f"🏆 {t.name} RESULTS\n"
                + "\n".join(
                    f"{['🥇','🥈','🥉'][i]} {e.agent_id} "
                    f"{e.final_pnl_pct:+.2f}% — {e.karma_won:,} KARMA"
                    for i, e in enumerate(podium)
                )
            )
            await self._publisher.publish_chronicle(chronicle)

    def get_standings(self, tournament_id: Optional[str] = None) -> List[Dict]:
        tid = tournament_id or self._active_id
        if not tid or tid not in self._tournaments:
            return []
        t = self._tournaments[tid]
        entries = sorted(t.entries, key=lambda e: e.final_pnl_pct or -999, reverse=True)
        return [asdict(e) for e in entries]
