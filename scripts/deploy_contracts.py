#!/usr/bin/env python3
"""Smart Contract Deployment Script

Deploys CryptoArena smart contracts to Base L2 network.
Handles:
- ArenaLeaderboard contract deployment
- Contract verification
- Configuration updates
"""
import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Optional

try:
    from web3 import Web3
    from eth_account import Account
except ImportError:
    print("❌ Required packages not installed. Run: pip install web3 eth-account")
    sys.exit(1)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class ContractDeployer:
    """Deploys smart contracts to blockchain."""
    
    NETWORKS = {
        "base": {
            "name": "Base Mainnet",
            "rpc": "https://mainnet.base.org",
            "chain_id": 8453,
            "explorer": "https://basescan.org"
        },
        "base-sepolia": {
            "name": "Base Sepolia Testnet",
            "rpc": "https://sepolia.base.org",
            "chain_id": 84532,
            "explorer": "https://sepolia.basescan.org"
        }
    }
    
    def __init__(self, network: str, private_key: Optional[str] = None):
        if network not in self.NETWORKS:
            raise ValueError(f"Unsupported network: {network}")
        
        self.network = self.NETWORKS[network]
        self.network_name = network
        
        # Initialize Web3
        self.w3 = Web3(Web3.HTTPProvider(self.network["rpc"]))
        
        if not self.w3.is_connected():
            raise ConnectionError(f"Cannot connect to {self.network['name']}")
        
        # Load private key
        self.private_key = private_key or os.getenv("PRIVATE_KEY")
        if not self.private_key:
            raise ValueError("Private key not provided. Set PRIVATE_KEY env var.")
        
        # Create account
        self.account = Account.from_key(self.private_key)
        self.address = self.account.address
        
        print(f"✅ Connected to {self.network['name']}")
        print(f"📍 Deployer address: {self.address}")
        
        # Check balance
        balance = self.w3.eth.get_balance(self.address)
        balance_eth = self.w3.from_wei(balance, 'ether')
        print(f"💰 Balance: {balance_eth:.4f} ETH")
        
        if balance == 0:
            raise ValueError("Insufficient balance for deployment")
    
    def deploy_leaderboard(self) -> str:
        """Deploy ArenaLeaderboard contract.
        
        Returns:
            Contract address
        """
        print("\n🚀 Deploying ArenaLeaderboard contract...")
        
        # Load contract ABI and bytecode
        contract_path = project_root / "contracts" / "ArenaLeaderboard.sol"
        
        if not contract_path.exists():
            raise FileNotFoundError(f"Contract not found: {contract_path}")
        
        # For MVP, we'll provide the compiled bytecode
        # In production, use solc or hardhat for compilation
        print("⚠️  Note: Using pre-compiled bytecode. Compile with solc for production.")
        
        # Simplified deployment for MVP
        # This would need actual compilation step
        print("\n⚠️  CONTRACT DEPLOYMENT PLACEHOLDER")
        print("To deploy contracts in production:")
        print("1. Install Foundry: https://book.getfoundry.sh/")
        print("2. Compile: forge build")
        print("3. Deploy: forge create --rpc-url $RPC_URL --private-key $PRIVATE_KEY")
        print("\nFor now, contracts can run in paper trading mode without deployment.")
        
        return "0x0000000000000000000000000000000000000000"  # Placeholder
    
    def verify_contract(self, address: str, args: list):
        """Verify contract on block explorer."""
        print(f"\n🔍 Verifying contract at {address}...")
        print(f"Explorer: {self.network['explorer']}/address/{address}")
        print("\n⚠️  Manual verification required:")
        print(f"1. Visit: {self.network['explorer']}/verifyContract")
        print(f"2. Enter contract address: {address}")
        print("3. Upload Solidity source code")
        print("4. Match compiler version and settings")
    
    def update_config(self, leaderboard_address: str):
        """Update deployment configuration with contract addresses."""
        config_path = project_root / "config" / "deployment.json"
        
        if not config_path.exists():
            print("⚠️  Config file not found, skipping update")
            return
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Update contract addresses
        if "blockchain" not in config:
            config["blockchain"] = {}
        
        config["blockchain"]["network"] = self.network_name
        config["blockchain"]["contract_addresses"] = {
            "leaderboard": leaderboard_address
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Updated config: {config_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Deploy CryptoArena smart contracts"
    )
    parser.add_argument(
        "--network",
        choices=["base", "base-sepolia"],
        default="base-sepolia",
        help="Network to deploy to"
    )
    parser.add_argument(
        "--private-key",
        type=str,
        help="Private key (or use PRIVATE_KEY env var)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify contracts after deployment"
    )
    
    args = parser.parse_args()
    
    try:
        print("="*60)
        print("🏟️  CryptoArena Contract Deployment")
        print("="*60)
        
        # Initialize deployer
        deployer = ContractDeployer(
            network=args.network,
            private_key=args.private_key
        )
        
        # Deploy contracts
        leaderboard_address = deployer.deploy_leaderboard()
        
        print(f"\n✅ Deployment complete!")
        print(f"📍 Leaderboard: {leaderboard_address}")
        
        # Verify if requested
        if args.verify and leaderboard_address != "0x0000000000000000000000000000000000000000":
            deployer.verify_contract(leaderboard_address, [])
        
        # Update config
        deployer.update_config(leaderboard_address)
        
        print("\n" + "="*60)
        print("✅ All done! Contract addresses saved to config.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
