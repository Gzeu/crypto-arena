#!/usr/bin/env python3
"""
start_marketplace.py — v1.3
Launch the CryptoArena Agent Marketplace API server.

Usage:
    python scripts/start_marketplace.py
    python scripts/start_marketplace.py --port 8001 --reload
"""

import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s %(message)s",
)
logger = logging.getLogger("arena.marketplace.launcher")


def main() -> None:
    parser = argparse.ArgumentParser(description="CryptoArena Marketplace API")
    parser.add_argument("--port",   type=int, default=8001,      help="TCP port (default 8001)")
    parser.add_argument("--host",   default="0.0.0.0",           help="Bind host")
    parser.add_argument("--reload", action="store_true",          help="Hot-reload (dev mode)")
    args = parser.parse_args()

    try:
        import uvicorn  # noqa: F401
    except ImportError:
        logger.error("uvicorn not installed. Run: pip install uvicorn[standard]")
        sys.exit(1)

    import uvicorn

    banner = f"""
  ╔══════════════════════════════════════════════════╗
  ║   🏪 CryptoArena Agent Marketplace v1.3          ║
  ║   http://{args.host}:{args.port}                        ║
  ║   Docs  → http://{args.host}:{args.port}/docs           ║
  ║   Stats → http://{args.host}:{args.port}/marketplace/stats║
  ║   WS    → ws://{args.host}:{args.port}/marketplace/ws/live║
  ╚══════════════════════════════════════════════════╝"""
    logger.info(banner)

    uvicorn.run(
        "src.marketplace.marketplace_api:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info",
    )


if __name__ == "__main__":
    main()
