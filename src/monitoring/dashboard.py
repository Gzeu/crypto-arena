"""
Real-Time Monitoring Dashboard
===============================
Rich terminal UI for live game state visualization.
"""

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from datetime import datetime
import asyncio

console = Console()


class ArenaMonitor:
    def __init__(self, state):
        self.state = state
        self.layout = Layout()
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )
        self.layout["body"].split_row(
            Layout(name="leaderboard"),
            Layout(name="regime"),
        )

    def generate_layout(self) -> Layout:
        self.layout["header"].update(self._render_header())
        self.layout["leaderboard"].update(self._render_leaderboard())
        self.layout["regime"].update(self._render_regime())
        self.layout["footer"].update(self._render_footer())
        return self.layout

    def _render_header(self) -> Panel:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
        return Panel(
            f"🏟️  [bold cyan]CryptoArena LIVE[/bold cyan] | Cycle #{self.state.cycle_count} | {ts}",
            style="bold white on blue",
        )

    def _render_leaderboard(self) -> Panel:
        table = Table(title="🏆 Leaderboard", expand=True)
        table.add_column("Rank", justify="center", style="cyan")
        table.add_column("Agent", style="magenta")
        table.add_column("Equity", justify="right", style="green")
        table.add_column("PnL %", justify="right")
        table.add_column("Win Rate", justify="center")
        for i, entry in enumerate(self.state.leaderboard[:8], start=1):
            pnl_pct = entry["pnl_pct"] * 100
            color = "green" if pnl_pct > 0 else "red" if pnl_pct < 0 else "yellow"
            portfolio = self.state.portfolios.get(entry["agent"].split()[0], None)
            wr = portfolio.win_rate if portfolio else 0
            table.add_row(
                f"#{i}",
                entry["agent"],
                f"${entry['equity']:,.0f}",
                f"[{color}]{pnl_pct:+.1f}%[/{color}]",
                f"{wr:.0%}",
            )
        return Panel(table, border_style="blue")

    def _render_regime(self) -> Panel:
        regime = self.state.current_regime or {"regime": "Unknown", "probabilities": {}}
        probs = regime.get("probabilities", {})
        table = Table(title="🎯 Market Regime", expand=True)
        table.add_column("Regime", style="cyan")
        table.add_column("Probability", justify="right", style="yellow")
        for r in ["Bull", "Bear", "Sideways", "Crisis"]:
            p = probs.get(r, 0)
            color = "green" if r == regime["regime"] else "dim"
            table.add_row(f"[{color}]{r}[/{color}]", f"{p:.0%}")
        return Panel(table, border_style="yellow")

    def _render_footer(self) -> Panel:
        mode = self.state.config["game"]["execution_mode"].upper()
        color = "red" if mode == "LIVE" else "green"
        return Panel(
            f"Mode: [{color}]{mode}[/{color}] | Press Ctrl+C to stop",
            style="dim",
        )

    async def run(self, update_interval: int = 5):
        """Run live dashboard with periodic updates."""
        with Live(self.generate_layout(), refresh_per_second=1, screen=True) as live:
            while True:
                await asyncio.sleep(update_interval)
                live.update(self.generate_layout())
