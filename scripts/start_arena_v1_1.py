"""
Entry point for CryptoArena v1.1.

Usage:
  python scripts/start_arena_v1_1.py [--mode paper|live] [--tournament]

Options:
  --mode        Execution mode: paper (default) or live
  --tournament  Initialise Tournament Week 1 on startup
  --week INT    Tournament week number (default: 1)
"""

import argparse
import asyncio
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, str(Path(__file__).parent.parent))

from loguru import logger
from src.arenacore.orchestrator_v1_1 import ArenaCoreV11


def load_config(mode: str) -> dict:
    import yaml
    game_path = Path("config/game.yaml")
    agents_path = Path("config/agents.yaml")
    with open(game_path) as f:
        cfg = yaml.safe_load(f)
    with open(agents_path) as f:
        agents_cfg = yaml.safe_load(f)
    cfg["agents"] = agents_cfg.get("agents", [])
    cfg["game"]["execution_mode"] = mode
    return cfg


async def main():
    parser = argparse.ArgumentParser(description="CryptoArena v1.1")
    parser.add_argument("--mode", choices=["paper", "live"], default="paper")
    parser.add_argument("--tournament", action="store_true", default=True)
    parser.add_argument("--week", type=int, default=1)
    args = parser.parse_args()

    if args.mode == "live":
        confirm = input(
            "⚠️  LIVE MODE uses real capital. Type CONFIRM to proceed: "
        )
        if confirm.strip() != "CONFIRM":
            print("Aborted.")
            sys.exit(0)

    logger.info("🏟️  Starting CryptoArena v1.1 — mode={} tournament={}",
                args.mode, args.tournament)

    cfg = load_config(args.mode)
    arena = ArenaCoreV11(cfg)

    await arena.start(init_tournament=args.tournament)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Arena stopped by user")
