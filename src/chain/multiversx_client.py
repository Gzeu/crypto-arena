"""
MultiversX Supernova Client.
Handles quest NFT minting and cross-chain quest registration.
Falls back to dry-run if SDK is not installed.
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, Optional

from loguru import logger

try:
    from multiversx_sdk import ProxyNetworkProvider, UserSigner, Transaction
    MVX_AVAILABLE = True
except ImportError:
    MVX_AVAILABLE = False
    logger.warning("multiversx-sdk not installed — MVX client in dry-run")


class MultiversXClient:
    """
    Client for MultiversX Supernova cross-chain operations.
    Primary use: mint NFT quest badges and register arena quests.
    """

    DEVNET = "https://devnet-gateway.multiversx.com"
    MAINNET = "https://gateway.multiversx.com"

    def __init__(self):
        self._provider = None
        self._signer = None
        self._dry_run = True
        network = os.getenv("MVX_NETWORK", "devnet")
        pem_path = os.getenv("MVX_PEM_PATH", "")
        url = self.MAINNET if network == "mainnet" else self.DEVNET

        if MVX_AVAILABLE and pem_path and os.path.exists(pem_path):
            try:
                self._provider = ProxyNetworkProvider(url)
                self._signer = UserSigner.from_pem_file(pem_path)
                self._dry_run = False
                logger.success("🌐 MultiversXClient ready ({} network)", network)
            except Exception as exc:
                logger.warning("MVX client init failed: {} — dry-run", exc)
        else:
            logger.info("🌐 MultiversXClient in dry-run")

    async def mint_quest_nft(
        self,
        agent_id: str,
        quest_name: str,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        Mint an NFT badge on MultiversX for a completed quest.
        Returns tx_hash or dry-run confirmation.
        """
        ts = datetime.now(timezone.utc).isoformat()
        meta = metadata or {}
        meta.update({"agent_id": agent_id, "quest": quest_name, "ts": ts})

        if self._dry_run or not MVX_AVAILABLE:
            logger.info(
                "[MVX dry-run] Mint quest NFT '{}' for agent {}",
                quest_name, agent_id
            )
            return {
                "success": True, "dry_run": True,
                "agent_id": agent_id, "quest_name": quest_name, "ts": ts,
            }

        try:
            collection_addr = os.getenv("MVX_NFT_COLLECTION_ADDR", "")
            data_str = (
                f"mintQuestBadge@{agent_id.encode().hex()}"
                f"@{quest_name.encode().hex()}"
                f"@{json.dumps(meta).encode().hex()}"
            )
            tx = Transaction(
                sender=self._signer.get_pubkey().to_address().bech32(),
                receiver=collection_addr,
                value=0,
                gas_limit=10_000_000,
                data=data_str.encode(),
                chain_id="D",
            )
            self._signer.sign(tx)
            tx_hash = self._provider.send_transaction(tx)
            logger.success("🏅 Quest NFT minted on MVX: {}", tx_hash)
            return {"success": True, "tx_hash": tx_hash, "ts": ts}
        except Exception as exc:
            logger.error("MVX mint_quest_nft failed: {}", exc)
            return {"success": False, "error": str(exc), "ts": ts}

    async def get_agent_nfts(self, agent_address: str) -> Dict:
        """Query NFT badges held by an agent address."""
        ts = datetime.now(timezone.utc).isoformat()
        if self._dry_run or not MVX_AVAILABLE:
            return {"success": True, "dry_run": True, "nfts": [], "ts": ts}
        try:
            nfts = self._provider.get_account_nfts(agent_address)
            return {"success": True, "nfts": nfts, "ts": ts}
        except Exception as exc:
            return {"success": False, "error": str(exc), "ts": ts}
