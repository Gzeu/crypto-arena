"""
Deploy CryptoArena v1.1 smart contracts to Base L2 (or Sepolia testnet).

Usage:
  python scripts/deploy_contracts_v1_1.py --network base-sepolia
  python scripts/deploy_contracts_v1_1.py --network base

Requires: BASE_RPC_URL + PRIVATE_KEY in .env
Optional: BASESCAN_API_KEY for automatic verification.
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from web3 import Web3
    from eth_account import Account
except ImportError:
    print("❌ web3 not installed. Run: pip install web3")
    sys.exit(1)

NETWORKS = {
    "base": {
        "rpc": "https://mainnet.base.org",
        "chain_id": 8453,
        "explorer": "https://basescan.org",
    },
    "base-sepolia": {
        "rpc": "https://sepolia.base.org",
        "chain_id": 84532,
        "explorer": "https://sepolia.basescan.org",
    },
}


def load_compiled(contract_name: str) -> dict:
    """Load compiled ABI + bytecode from contracts/abi/ directory."""
    path = Path(f"contracts/abi/{contract_name}.json")
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found.\n"
            "Compile contracts first: npx hardhat compile"
        )
    with open(path) as f:
        return json.load(f)


def deploy_contract(w3: Web3, account, abi: list, bytecode: str,
                    *args, label: str = "Contract") -> str:
    """Deploy a contract and return its address."""
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx = Contract.constructor(*args).build_transaction({
        "from": account.address,
        "nonce": w3.eth.get_transaction_count(account.address),
        "gas": 3_000_000,
        "maxFeePerGas": w3.eth.gas_price * 2,
        "maxPriorityFeePerGas": w3.to_wei(1, "gwei"),
    })
    signed = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print(f"  ⏳ {label} deploying... tx: {tx_hash.hex()}")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)
    addr = receipt["contractAddress"]
    print(f"  ✅ {label} deployed at {addr}")
    return addr


async def main():
    parser = argparse.ArgumentParser(description="Deploy CryptoArena v1.1 contracts")
    parser.add_argument("--network", default="base-sepolia",
                        choices=list(NETWORKS.keys()))
    args = parser.parse_args()

    net = NETWORKS[args.network]
    rpc = os.getenv("BASE_RPC_URL", net["rpc"])
    pk  = os.getenv("PRIVATE_KEY", "")

    if not pk:
        print("❌ PRIVATE_KEY not set in .env")
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(rpc))
    if not w3.is_connected():
        print(f"❌ Cannot connect to {rpc}")
        sys.exit(1)

    account = Account.from_key(pk)
    balance = w3.from_wei(w3.eth.get_balance(account.address), "ether")

    print(f"\n🔗 Network  : {args.network}")
    print(f"📬 Deployer : {account.address}")
    print(f"💰 Balance  : {balance:.6f} ETH")
    print("")

    if balance < 0.01:
        print("⚠️  Low balance — deployment may fail")

    addresses = {}

    # --- KarmaToken ---
    try:
        compiled = load_compiled("KarmaToken")
        addr = deploy_contract(
            w3, account,
            compiled["abi"], compiled["bytecode"],
            label="KarmaToken",
        )
        addresses["karma_token"] = addr
    except FileNotFoundError as e:
        print(f"  ⚠️  Skipping KarmaToken: {e}")

    # --- AgentNFT ---
    try:
        compiled = load_compiled("AgentNFT")
        addr = deploy_contract(
            w3, account,
            compiled["abi"], compiled["bytecode"],
            label="AgentNFT",
        )
        addresses["agent_nft"] = addr
    except FileNotFoundError as e:
        print(f"  ⚠️  Skipping AgentNFT: {e}")

    # --- ArenaLeaderboard ---
    try:
        compiled = load_compiled("ArenaLeaderboard")
        addr = deploy_contract(
            w3, account,
            compiled["abi"], compiled["bytecode"],
            label="ArenaLeaderboard",
        )
        addresses["leaderboard"] = addr
    except FileNotFoundError as e:
        print(f"  ⚠️  Skipping ArenaLeaderboard: {e}")

    # --- Save config ---
    cfg = {
        **addresses,
        "network": args.network,
        "chain_id": net["chain_id"],
        "deployer": account.address,
        "deployed_at": datetime.now(timezone.utc).isoformat(),
        "explorer": net["explorer"],
    }
    cfg_path = Path("config/contracts.json")
    cfg_path.parent.mkdir(exist_ok=True)
    with open(cfg_path, "w") as f:
        json.dump(cfg, f, indent=2)

    print(f"\n📄 Contract addresses saved to {cfg_path}")
    print("\n🎉 Deployment complete!")
    for k, v in addresses.items():
        print(f"  {k:20s}: {net['explorer']}/address/{v}")


if __name__ == "__main__":
    asyncio.run(main())
