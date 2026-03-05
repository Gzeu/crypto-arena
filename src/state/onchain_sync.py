"""
On-Chain Sync Module
====================
Syncs leaderboard state to Base L2 smart contract.
"""

import os
from web3 import Web3
from loguru import logger

LEADERBOARD_ABI = [
    {
        "inputs": [{"internalType": "string", "name": "agentId", "type": "string"},
                   {"internalType": "string", "name": "name", "type": "string"},
                   {"internalType": "int256", "name": "pnlUsdc", "type": "int256"},
                   {"internalType": "uint256", "name": "karmaScore", "type": "uint256"}],
        "name": "updateScore",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getLeaderboard",
        "outputs": [{"components": [
            {"internalType": "string", "name": "agentId", "type": "string"},
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "int256", "name": "pnlUsdc", "type": "int256"},
            {"internalType": "uint256", "name": "karmaScore", "type": "uint256"},
            {"internalType": "uint256", "name": "lastUpdate", "type": "uint256"}
        ], "internalType": "struct ArenaLeaderboard.AgentScore[]", "name": "", "type": "tuple[]"}],
        "stateMutability": "view",
        "type": "function"
    }
]


class OnChainSync:
    def __init__(self, config: dict):
        rpc = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
        self.w3 = Web3(Web3.HTTPProvider(rpc))
        contract_addr = os.getenv("LEADERBOARD_CONTRACT")
        self.contract = None
        if contract_addr:
            self.contract = self.w3.eth.contract(address=contract_addr, abi=LEADERBOARD_ABI)
            logger.info("🔗 Connected to ArenaLeaderboard at {}", contract_addr)
        else:
            logger.warning("⚠️  No LEADERBOARD_CONTRACT in .env — on-chain sync disabled")
        self.deployer_key = os.getenv("DEPLOYER_PRIVATE_KEY")

    def sync_leaderboard(self, leaderboard: list):
        """Push leaderboard state to on-chain contract."""
        if not self.contract or not self.deployer_key:
            logger.debug("Skipping on-chain sync (not configured)")
            return
        account = self.w3.eth.account.from_key(self.deployer_key)
        for entry in leaderboard:
            agent_id = entry["agent"]
            pnl_usdc_6dec = int(entry["equity"] * 1_000_000)  # convert to 6-decimal int
            karma = int(entry["score"] * 100)  # scale narrative score
            try:
                tx = self.contract.functions.updateScore(
                    agent_id, entry["agent"], pnl_usdc_6dec, karma
                ).build_transaction({
                    "from": account.address,
                    "nonce": self.w3.eth.get_transaction_count(account.address),
                    "gas": 200_000,
                    "gasPrice": self.w3.eth.gas_price,
                })
                signed = account.sign_transaction(tx)
                tx_hash = self.w3.eth.send_raw_transaction(signed.rawTransaction)
                logger.info("📡 On-chain update for {}: {}", agent_id, tx_hash.hex())
            except Exception as e:
                logger.error("❌ On-chain sync failed for {}: {}", agent_id, e)

    def read_leaderboard(self) -> list:
        """Read current leaderboard from contract."""
        if not self.contract:
            return []
        try:
            data = self.contract.functions.getLeaderboard().call()
            return [{"agent": s[0], "name": s[1], "pnl": s[2] / 1e6, "karma": s[3]} for s in data]
        except Exception as e:
            logger.error("❌ Failed to read on-chain leaderboard: {}", e)
            return []
