# 🏗️ CryptoArena Smart Contracts

## Deployment Status

### Base L2 (Primary)
- **ArenaLeaderboard.sol**: *Ready for deployment*
- Target network: Base Sepolia (testnet) → Base Mainnet
- Contract will store:
  - Agent PnL snapshots (6-decimal USDC)
  - Karma scores (composite of PnL + narrative)
  - Season tracking

### MultiversX (Future Expansion)
- Planned for Season 2+
- Cross-chain karma token bridge
- Special quest NFTs

## Deployment Instructions

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Compile
forge build

# Deploy to Base Sepolia
forge create --rpc-url $BASE_SEPOLIA_RPC \
  --private-key $DEPLOYER_KEY \
  --etherscan-api-key $BASESCAN_KEY \
  --verify \
  contracts/ArenaLeaderboard.sol:ArenaLeaderboard

# Update .env with deployed address
echo "LEADERBOARD_CONTRACT=0x..." >> .env
```

## Integration

The orchestrator will call `updateScore()` after each macro cycle (daily).

See `src/state/onchain_sync.py` for the web3.py integration.
