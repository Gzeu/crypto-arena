"""
Game State Manager
==================
Central store for all agent portfolios, market snapshots,
regime history, and leaderboard.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional
from loguru import logger


@dataclass
class Position:
    symbol: str
    side: str          # LONG | SHORT | LP
    size_usdc: float
    leverage: float
    entry_price: float
    stop_loss: float
    take_profit: float
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    rationale: str = ""


@dataclass
class AgentPortfolio:
    agent_id: str
    name: str
    cash_usdc: float = 10_000.0
    positions: List[Position] = field(default_factory=list)
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    daily_drawdown: float = 0.0
    peak_equity: float = 10_000.0
    win_count: int = 0
    loss_count: int = 0
    narrative_score: float = 0.0
    de_risk_mode: bool = False

    @property
    def total_equity(self) -> float:
        return self.cash_usdc + self.unrealized_pnl

    @property
    def win_rate(self) -> float:
        total = self.win_count + self.loss_count
        return self.win_count / total if total > 0 else 0.0


class GameState:
    def __init__(self, config: dict):
        self.config = config
        self.portfolios: Dict[str, AgentPortfolio] = {}
        self.snapshots: List[dict] = []
        self.regime_history: List[dict] = []
        self.current_regime: Optional[dict] = None
        self.leaderboard: List[dict] = []
        self.cycle_count: int = 0
        self._init_portfolios()
        logger.info("GameState initialized with {} agents", len(self.portfolios))

    def _init_portfolios(self):
        initial_capital = self.config["capital"]["initial_usdc_per_agent"]
        for agent_cfg in self.config.get("agents", []):
            agent_id = agent_cfg["id"]
            self.portfolios[agent_id] = AgentPortfolio(
                agent_id=agent_id,
                name=agent_cfg["name"],
                cash_usdc=initial_capital,
                peak_equity=initial_capital,
            )

    def add_snapshot(self, snapshot: dict):
        self.snapshots.append(snapshot)
        if len(self.snapshots) > 1000:
            self.snapshots.pop(0)  # rolling window

    def update_regime(self, regime: dict):
        self.current_regime = regime
        self.regime_history.append({**regime, "ts": datetime.now(timezone.utc).isoformat()})

    def apply_executions(self, execution_log: List[dict]):
        for log_entry in execution_log:
            if log_entry["status"] != "executed":
                continue
            agent_id = log_entry["agent_id"]
            portfolio = self.portfolios.get(agent_id)
            if not portfolio:
                continue
            pos = Position(
                symbol=log_entry["symbol"],
                side=log_entry["side"],
                size_usdc=log_entry["size_usdc"],
                leverage=log_entry["leverage"],
                entry_price=log_entry["entry_price"],
                stop_loss=log_entry["stop_loss"],
                take_profit=log_entry["take_profit"],
                rationale=log_entry.get("rationale", ""),
            )
            portfolio.positions.append(pos)
            portfolio.cash_usdc -= log_entry["size_usdc"]
            logger.debug("📌 {} | {} {} {} @ {}",
                         agent_id, pos.side, pos.symbol, pos.size_usdc, pos.entry_price)

    def compute_hourly_metrics(self):
        """Recompute drawdown and equity metrics for all agents."""
        for portfolio in self.portfolios.values():
            eq = portfolio.total_equity
            if eq > portfolio.peak_equity:
                portfolio.peak_equity = eq
            dd = (portfolio.peak_equity - eq) / portfolio.peak_equity
            portfolio.daily_drawdown = dd
            if dd >= self.config["risk"]["daily_max_drawdown_pct"]:
                portfolio.de_risk_mode = True
                logger.warning("⚠️  {} hit daily drawdown limit ({:.1%}) — DE-RISK MODE ON",
                                portfolio.agent_id, dd)

    def update_leaderboard(self):
        pnl_weight = self.config["leaderboard"]["pnl_weight"]
        nar_weight = self.config["leaderboard"]["narrative_score_weight"]
        entries = []
        for p in self.portfolios.values():
            pnl_pct = (p.total_equity - 10_000) / 10_000
            score = pnl_pct * pnl_weight + (p.narrative_score / 100) * nar_weight
            entries.append({"agent": p.name, "equity": p.total_equity,
                             "pnl_pct": pnl_pct, "score": score})
        self.leaderboard = sorted(entries, key=lambda x: x["score"], reverse=True)

    def apply_daily_reflection(self, report: dict):
        for agent_id, changes in report.get("policy_changes", {}).items():
            logger.info("🧠 Reflection update for {}: {}", agent_id, changes)
