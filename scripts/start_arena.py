#!/usr/bin/env python3
"""
CryptoArena — Entry Point
Usage:
    python scripts/start_arena.py [--mode simulation|live]
"""

import asyncio
import argparse
import yaml
from pathlib import Path
from loguru import logger

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.arenacore.orchestrator import ArenaCore


def load_config() -> dict:
    game_cfg_path = Path("config/game.yaml")
    agents_cfg_path = Path("config/agents.yaml")
    with open(game_cfg_path) as f:
        config = yaml.safe_load(f)
    with open(agents_cfg_path) as f:
        agents_cfg = yaml.safe_load(f)
    config["agents"] = agents_cfg["agents"]
    return config


async def main():
    parser = argparse.ArgumentParser(description="Start CryptoArena")
    parser.add_argument("--mode", default="simulation", choices=["simulation", "live"],
                        help="Execution mode (default: simulation)")
    args = parser.parse_args()

    config = load_config()
    config["game"]["execution_mode"] = args.mode

    logger.info("🏟️  Launching CryptoArena in {} mode", args.mode.upper())

    arena = ArenaCore(config)
    await arena.start()


if __name__ == "__main__":
    asyncio.run(main())
