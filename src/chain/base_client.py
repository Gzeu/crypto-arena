"""
Base L2 On-Chain Client.
Handles Karma token minting/burning, leaderboard sync, and agent NFT ops.
Uses web3.py; requires BASE_RPC_URL + PRIVATE_KEY in .env.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger

try:
    from web3 import Web3
    from eth_account import Account
    WEB3_AVAILABLE = True
except ImportError:
    WEB3_AVAILABLE = False
    logger.warning("web3 not installed — Base L2 client disabled")


class BaseChainClient:
    """
    Thin wrapper around Base L2 smart contracts.
    Degrades gracefully to dry-run logging if web3 or credentials are missing.
    """

    def __init__(self):
        self._w3 = None
        self._account = None
        self._dry_run = True
        self._karma_contract = None
        self._leaderboard_contract = None

        rpc = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
        pk = os.getenv("PRIVATE_KEY", "")

        if WEB3_AVAILABLE and pk:
            try:
                self._w3 = Web3(Web3.HTTPProvider(rpc))
                self._account = Account.from_key(pk)
                self._dry_run = not self._w3.is_connected()
                if not self._dry_run:
                    self._load_contracts()
                    logger.success(
                        "⛓️  BaseChainClient live — wallet {}",
                        self._account.address[:10] + "...",
                    )
                else:
                    logger.warning("⛓️  Base RPC unreachable — dry-run mode")
            except Exception as exc:
                logger.warning("BaseChainClient init failed: {} — dry-run", exc)
        else:
            logger.info("⛓️  BaseChainClient in dry-run (no web3/key)")

    def _load_contracts(self):
        cfg_path = Path("config/contracts.json")
        if not cfg_path.exists():
            logger.warning("config/contracts.json not found — deploy contracts first")
            return
        with open(cfg_path) as f:
            cfg = json.load(f)

        karma_abi_path = Path("contracts/abi/KarmaToken.json")
        lb_abi_path = Path("contracts/abi/ArenaLeaderboard.json")

        if karma_abi_path.exists() and cfg.get("karma_token"):
            with open(karma_abi_path) as f:
                karma_abi = json.load(f)
            self._karma_contract = self._w3.eth.contract(
                address=Web3.to_checksum_address(cfg["karma_token"]),
                abi=karma_abi,
            )

        if lb_abi_path.exists() and cfg.get("leaderboard"):
            with open(lb_abi_path) as f:
                lb_abi = json.load(f)
            self._leaderboard_contract = self._w3.eth.contract(
                address=Web3.to_checksum_address(cfg["leaderboard"]),
                abi=lb_abi,
            )

    # ------------------------------------------------------------------
    # Karma token
    # ------------------------------------------------------------------

    async def mint_karma(self, to_address: str, amount_wei: int) -> Dict:
        ts = datetime.now(timezone.utc).isoformat()
        if self._dry_run or not self._karma_contract:
            logger.info("[dry-run] Mint {} KARMA → {}", amount_wei, to_address[:10])
            return {"success": True, "dry_run": True, "amount": amount_wei, "ts": ts}
        try:
            tx = self._karma_contract.functions.mint(
                Web3.to_checksum_address(to_address), amount_wei
            ).build_transaction({
                "from": self._account.address,
                "nonce": self._w3.eth.get_transaction_count(self._account.address),
                "gas": 100_000,
                "maxFeePerGas": self._w3.eth.gas_price * 2,
                "maxPriorityFeePerGas": self._w3.to_wei(1, "gwei"),
            })
            signed = self._account.sign_transaction(tx)
            tx_hash = self._w3.eth.send_raw_transaction(signed.rawTransaction).hex()
            logger.success("💎 Karma minted: {}", tx_hash)
            return {"success": True, "tx_hash": tx_hash, "ts": ts}
        except Exception as exc:
            logger.error("mint_karma failed: {}", exc)
            return {"success": False, "error": str(exc), "ts": ts}

    async def burn_karma(self, from_address: str, amount_wei: int) -> Dict:
        ts = datetime.now(timezone.utc).isoformat()
        if self._dry_run or not self._karma_contract:
            logger.info("[dry-run] Burn {} KARMA from {}", amount_wei, from_address[:10])
            return {"success": True, "dry_run": True, "ts": ts}
        try:
            tx = self._karma_contract.functions.burn(
                Web3.to_checksum_address(from_address), amount_wei
            ).build_transaction({
                "from": self._account.address,
                "nonce": self._w3.eth.get_transaction_count(self._account.address),
                "gas": 80_000,
                "maxFeePerGas": self._w3.eth.gas_price * 2,
                "maxPriorityFeePerGas": self._w3.to_wei(1, "gwei"),
            })
            signed = self._account.sign_transaction(tx)
            tx_hash = self._w3.eth.send_raw_transaction(signed.rawTransaction).hex()
            return {"success": True, "tx_hash": tx_hash, "ts": ts}
        except Exception as exc:
            return {"success": False, "error": str(exc), "ts": ts}

    # ------------------------------------------------------------------
    # Leaderboard
    # ------------------------------------------------------------------

    async def sync_leaderboard(self, agents: List[Dict]) -> Dict:
        """Push full leaderboard state on-chain."""
        ts = datetime.now(timezone.utc).isoformat()
        if self._dry_run or not self._leaderboard_contract:
            logger.info("[dry-run] Leaderboard sync — {} agents", len(agents))
            return {"success": True, "dry_run": True, "count": len(agents), "ts": ts}
        hashes = []
        for i, a in enumerate(agents):
            try:
                pnl_cents = int(a.get("pnl", 0) * 100)
                win_bp = int(a.get("win_rate", 0) * 10_000)
                karma = int(a.get("karma", 0))
                nft_id = a.get("nft_token_id", i + 1)
                wallet = Web3.to_checksum_address(
                    a.get("wallet", "0x" + "0" * 40)
                )
                tx = self._leaderboard_contract.functions.updateAgent(
                    a["agent_id"], wallet, nft_id,
                    pnl_cents, win_bp, karma, i + 1
                ).build_transaction({
                    "from": self._account.address,
                    "nonce": self._w3.eth.get_transaction_count(
                        self._account.address) + len(hashes),
                    "gas": 150_000,
                    "maxFeePerGas": self._w3.eth.gas_price * 2,
                    "maxPriorityFeePerGas": self._w3.to_wei(1, "gwei"),
                })
                signed = self._account.sign_transaction(tx)
                h = self._w3.eth.send_raw_transaction(signed.rawTransaction).hex()
                hashes.append(h)
            except Exception as exc:
                logger.error("Leaderboard sync error for {}: {}", a.get("agent_id"), exc)
        logger.success("📊 Leaderboard synced — {} tx(s)", len(hashes))
        return {"success": True, "tx_hashes": hashes, "ts": ts}
