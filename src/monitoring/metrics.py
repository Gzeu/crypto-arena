"""
Prometheus metrics for CryptoArena v1.2.
Exposed via /metrics endpoint on the FastAPI web server.
All metric names prefixed with `arena_`.
"""

try:
    from prometheus_client import (
        Counter, Gauge, Histogram, Summary, REGISTRY,
        generate_latest, CONTENT_TYPE_LATEST,
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

from loguru import logger


class ArenaMetrics:
    """
    Singleton metrics registry.
    Call ArenaMetrics.get() to obtain the shared instance.
    """
    _instance = None

    def __init__(self):
        if not PROMETHEUS_AVAILABLE:
            logger.warning("prometheus_client not installed — metrics disabled")
            return

        # ── Counters ────────────────────────────────────────
        self.cycle_count = Counter(
            "arena_cycle_count", "Total micro cycles executed"
        )
        self.trades_total = Counter(
            "arena_trades_total", "Total trades executed",
            ["agent_id", "side", "symbol"]
        )
        self.quests_completed = Counter(
            "arena_quests_completed_total", "Quests completed",
            ["agent_id", "quest_id"]
        )
        self.social_posts = Counter(
            "arena_social_posts_total", "Social posts published",
            ["platform", "post_type"]
        )

        # ── Gauges ─────────────────────────────────────────
        self.agent_pnl_pct = Gauge(
            "arena_agent_pnl_pct", "Agent PnL percentage",
            ["agent_id"]
        )
        self.agent_karma = Gauge(
            "arena_agent_karma", "Agent Karma token balance",
            ["agent_id"]
        )
        self.agent_win_rate = Gauge(
            "arena_agent_win_rate", "Agent win rate (0–1)",
            ["agent_id"]
        )
        self.max_drawdown_pct = Gauge(
            "arena_max_drawdown_pct", "Agent max drawdown percentage",
            ["agent_id"]
        )
        self.daily_loss_pct = Gauge(
            "arena_daily_loss_pct", "Agent daily loss percentage",
            ["agent_id"]
        )
        self.quest_progress = Gauge(
            "arena_quest_progress", "Quest progress 0–100",
            ["agent_id", "quest_id"]
        )
        self.sentiment_score = Gauge(
            "arena_sentiment_score", "Aggregate market sentiment (-1 to 1)"
        )
        self.regime_confidence = Gauge(
            "arena_regime_confidence", "Regime detection confidence (0–1)"
        )
        self.btc_price = Gauge("arena_btc_price_usd", "BTC price in USD")
        self.eth_price = Gauge("arena_eth_price_usd", "ETH price in USD")
        self.sol_price = Gauge("arena_sol_price_usd", "SOL price in USD")
        self.tournament_karma_pot = Gauge(
            "arena_tournament_karma_pot", "Current tournament Karma pot"
        )

        # ── Histograms ─────────────────────────────────────
        self.cycle_duration = Histogram(
            "arena_cycle_duration_seconds", "Micro cycle duration",
            buckets=[0.1, 0.5, 1, 2, 5, 10, 30]
        )
        self.trade_pnl = Histogram(
            "arena_trade_pnl_pct", "Distribution of trade PnL %",
            ["agent_id"],
            buckets=[-20, -10, -5, -2, 0, 2, 5, 10, 20, 50]
        )

        logger.info("📊 ArenaMetrics registered ({} metrics)", 15)

    @classmethod
    def get(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def update_from_state(self, state):
        """Bulk update all gauges from GameState snapshot."""
        if not PROMETHEUS_AVAILABLE:
            return
        try:
            for aid, portfolio in state.portfolios.items():
                self.agent_pnl_pct.labels(agent_id=aid).set(
                    getattr(portfolio, "pnl_pct", 0)
                )
                self.agent_karma.labels(agent_id=aid).set(
                    getattr(portfolio, "karma", 0)
                )
                self.agent_win_rate.labels(agent_id=aid).set(
                    getattr(portfolio, "win_rate", 0)
                )
                self.max_drawdown_pct.labels(agent_id=aid).set(
                    getattr(portfolio, "max_drawdown_pct", 0)
                )
                self.daily_loss_pct.labels(agent_id=aid).set(
                    getattr(portfolio, "daily_loss_pct", 0)
                )
            prices = getattr(state, "latest_prices", {})
            if prices.get("BTC"):
                self.btc_price.set(prices["BTC"])
            if prices.get("ETH"):
                self.eth_price.set(prices["ETH"])
            if prices.get("SOL"):
                self.sol_price.set(prices["SOL"])
            regime = getattr(state, "current_regime", {})
            self.regime_confidence.set(regime.get("confidence", 0))
        except Exception as exc:
            logger.warning("Metrics update error: {}", exc)

    @staticmethod
    def export():
        """Return latest metrics as bytes (for /metrics endpoint)."""
        if not PROMETHEUS_AVAILABLE:
            return b"", "text/plain"
        return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
