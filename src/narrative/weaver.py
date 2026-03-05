"""
Narrative Weaver Agent
=======================
Generates epic storyline ticks, weekly chronicles,
and social-ready posts from market events and agent actions.
"""

from datetime import datetime, timezone
from typing import List
from loguru import logger


REGIME_INTROS = {
    "Bull": "The bulls are charging 🐂",
    "Bear": "The bears have emerged from hibernation 🐻",
    "Sideways": "The market drifts in an eerie calm 🌫️",
    "Crisis": "EMERGENCY ALERT — the arena shakes 🚨",
}


class NarrativeWeaver:
    def generate_tick(self, regime: dict, executions: List[dict], portfolios: dict) -> str:
        regime_name = regime.get("regime", "Unknown")
        intro = REGIME_INTROS.get(regime_name, "The game continues...")
        n_trades = len([e for e in executions if e["status"] == "executed"])
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        tick = (
            f"[{ts}] {intro} "
            f"{n_trades} trade(s) executed across the arena this cycle. "
        )
        if n_trades > 0:
            active_agents = list({e['agent_id'] for e in executions if e['status'] == 'executed'})
            tick += f"Active gladiators: {', '.join(active_agents)}. "
        tick += f"Regime confidence: {max(regime['probabilities'].values()):.0%}."
        logger.info("📖 Narrative tick generated")
        return tick

    def generate_chronicle(self, state) -> str:
        top = state.leaderboard[:3] if state.leaderboard else []
        if not top:
            return "The chronicles await their first entries..."
        podium = ", ".join([f"{e['agent']} ({e['pnl_pct']:+.1%})" for e in top])
        return (
            f"📜 DAILY CHRONICLE — {datetime.now(timezone.utc).strftime('%Y-%m-%d')} — "
            f"The top gladiators stand: {podium}. "
            f"The arena watches. The next chapter begins at dawn."
        )
