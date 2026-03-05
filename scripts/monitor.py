#!/usr/bin/env python3
"""
CryptoArena Real-Time Monitor
Usage:
    python scripts/monitor.py

Monitors running ArenaCore instance via shared game state.
"""

import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.monitoring.dashboard import ArenaMonitor
from src.state.game_state import GameState
import yaml


def load_config() -> dict:
    with open("config/game.yaml") as f:
        config = yaml.safe_load(f)
    with open("config/agents.yaml") as f:
        agents_cfg = yaml.safe_load(f)
    config["agents"] = agents_cfg["agents"]
    return config


async def main():
    config = load_config()
    state = GameState(config)
    monitor = ArenaMonitor(state)
    await monitor.run(update_interval=5)


if __name__ == "__main__":
    asyncio.run(main())
