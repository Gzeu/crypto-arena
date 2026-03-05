# 🏟️ CryptoArena

> **Fully autonomous, crypto-native AI agent game platform.**  
> Real-time data-driven multi-agent trading simulation with narrative engine,
> regime detection, on-chain leaderboard, and agent marketplace on Base L2.

[![Python CI](https://github.com/Gzeu/crypto-arena/actions/workflows/python_ci.yml/badge.svg)](https://github.com/Gzeu/crypto-arena/actions/workflows/python_ci.yml)
[![Contracts CI](https://github.com/Gzeu/crypto-arena/actions/workflows/contracts_ci.yml/badge.svg)](https://github.com/Gzeu/crypto-arena/actions/workflows/contracts_ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.3.0-blue)](docs/v1.3-RELEASE-NOTES.md)

---

## 📖 Overview

CryptoArena is a **live-data-driven AI game platform** where 8 specialised AI agents
compete in real-time crypto markets. Every cycle the platform:

1. **Senses** the market (prices, sentiment, whale flows, funding rates)
2. **Detects** the regime (bull / bear / sideways / volatile)
3. **Proposes** strategies via each agent's unique logic
4. **Filters** through risk constraints before execution
5. **Executes** trades in paper mode (or live with explicit flag)
6. **Publishes** narrative chronicles to Twitter/X and Discord
7. **Reflects** daily — agents learn from wins and losses
8. **Trades** agents on the marketplace using KARMA tokens

---

## 🤖 Agent Roster

| # | Agent | Strategy | Specialty |
|---|-------|----------|-----------|
| A1 | BTC Trend Follower | Momentum | Bitcoin long-only trend |
| A2 | ETH Swing Trader | Technical Analysis | Ethereum swing trades |
| A3 | SOL Short Specialist | Counter-trend | Solana bearish plays |
| A4 | Meme Coin Sniper | High-risk/reward | Viral token momentum |
| A5 | DeFi Basis Trader | Arbitrage | Funding rate capture |
| A6 | Prediction Market | Kelly Criterion | Polymarket edge plays |
| A7 | Crypto Index | Diversification | Weighted basket trades |
| A8 | Chaos Agent | Contrarian | Random/anti-consensus |

---

## 🏗️ Architecture

```
ArenaCoreV1.3
├── 📡  MarketScout          — CoinGecko / CMC / DEXScreener live feeds
├── 🌊  RegimeDetectorV2     — 6-signal composite (price, sentiment, vol,
│                               volume, funding, whale)
├── 🌡️  SentimentEngine      — Fear&Greed + CryptoPanic + Twitter + Funding
├── 🤖  AgentCrew × 8        — Independent strategy modules
├── 🛡️  RiskGuardian         — Position limits, correlation, stop-loss
├── ⚡  TraderExecutor       — Paper / live execution engine
├── 📖  NarrativeWeaver      — AI-generated story chronicles
├── 🧠  AgentMemory × 8      — Mem0 + ChromaDB persistent memory
├── 📢  ChroniclePublisher   — Twitter/X + Discord auto-posts
├── ⛓️  BaseChainClient      — Karma mint/burn + leaderboard sync
├── 🌐  MultiversXClient     — Quest NFT minting on Supernova
├── 🗺️  QuestManager         — 4 built-in quests (Bear Survivor, Alpha
│                               Hunter, Iron Hands, Volume King)
├── 🏆  TournamentManager   — Weekly cycles, entry fees, prize pool
├── 🏪  AgentMarketplace     — Buy/sell agent NFTs for KARMA (NEW v1.3)
├── 📊  ArenaMetrics         — 15 Prometheus metrics
├── 🪞  ReflectionAgent      — Daily self-improvement loop
└── 💾  StateManager         — SQLite persistence
```

---

## 📦 Module Map

```
src/
├── agents/          # 8 AI trading agents (A1–A8)
├── arenacore/       # Orchestrator v1.0 + v1.1
├── chain/           # Base L2 + MultiversX clients
├── execution/       # Trade execution engine
├── market/          # Market data feeds
├── marketplace/     # Agent Marketplace (v1.3) ✨
├── memory/          # Mem0 + ChromaDB agent memory
├── monitoring/      # Prometheus metrics + dashboard
├── narrative/       # Chronicle & story generation
├── quests/          # Quest system
├── reflection/      # Daily learning loop
├── regime/          # Regime detection (v1 + v2)
├── risk/            # Risk management
├── sentiment/       # Sentiment engine
├── social/          # Twitter + Discord publisher
├── state/           # Game state & persistence
└── tournament/      # Tournament manager

contracts/
├── KarmaToken.sol       # ERC-20 KARMA token
├── ArenaLeaderboard.sol # On-chain leaderboard
├── AgentNFT.sol         # ERC-721 agent identity
└── AgentMarketplace.sol # Agent marketplace escrow (v1.3) ✨
```

---

## ✅ Version History

| Version | Features | Status |
|---------|----------|--------|
| v1.0 MVP | 8 agents, orchestrator, regime detection, execution, state, narrative, reflection, Polymarket, deployment infra, health checks, web dashboard | ✅ Released |
| v1.1 | Persistent memory (Mem0 + ChromaDB), social media (Twitter/X + Discord), on-chain Base L2 (Karma + Leaderboard + AgentNFT), MultiversX quests, 4 quest types, tournament mode | ✅ Released |
| v1.2 | Hardhat pipeline, BaseScan verification, contract tests (16 total), Prometheus + Grafana monitoring stack, 15 metrics, SentimentEngine (4 sources), RegimeDetectorV2 (6 signals), GitHub Actions CI | ✅ Released |
| **v1.3** | **Agent Marketplace** (buy/sell NFTs for KARMA, REST API, WebSocket, AgentMarketplace.sol, price suggestion engine, 14 tests) | 🔄 In Progress |
| v1.4 | Next.js 14 frontend dashboard, backtesting engine | 🗓️ Planned |
| v1.5 | DEX execution (Uniswap v4), multi-chain (Arbitrum, Optimism) | 🗓️ Planned |
| v1.6 | Agent rental system, AI coach | 🗓️ Planned |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- Docker (for monitoring stack)

### 1. Setup
```bash
git clone https://github.com/Gzeu/crypto-arena.git
cd crypto-arena
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
```

### 2. Run Health Check
```bash
python scripts/health_check.py --verbose
```

### 3. Start Arena (Paper Mode)
```bash
python scripts/start_arena_v1_1.py --mode paper --tournament
```

### 4. Start Agent Marketplace API (v1.3)
```bash
pip install fastapi uvicorn[standard]
python scripts/start_marketplace.py --port 8001
# API docs → http://localhost:8001/docs
# Stats    → http://localhost:8001/marketplace/stats
```

### 5. Start Monitoring Stack
```bash
docker-compose -f monitoring/docker-compose.yml up -d
# Grafana    → http://localhost:3000  (admin / cryptoarena)
# Prometheus → http://localhost:9090
```

---

## ⛓️ Smart Contracts (Base L2)

| Contract | Description | Deployed |
|----------|-------------|----------|
| `KarmaToken.sol` | ERC-20 KARMA reward token | Base Sepolia |
| `ArenaLeaderboard.sol` | On-chain agent rankings | Base Sepolia |
| `AgentNFT.sol` | ERC-721 agent identity NFTs | Base Sepolia |
| `AgentMarketplace.sol` | Trustless NFT marketplace with KARMA escrow | Pending |

```bash
# Compile contracts
npm install && npm run compile

# Run contract tests (16 + 7 = 23 total)
npm run test:contracts

# Deploy to Base Sepolia
npx hardhat run scripts/hardhat_deploy.js --network base-sepolia
```

---

## 🏪 Agent Marketplace (v1.3)

Agents can list their NFTs for KARMA tokens. The marketplace provides:
- **Discovery** — filter by strategy, win rate, price, sort by PnL
- **Price Suggestions** — ML model based on win rate, PnL, tournament wins
- **WebSocket feed** — live updates every 10 seconds
- **On-chain settlement** — trustless escrow via `AgentMarketplace.sol`
- **2.5% fee** → Arena treasury for ecosystem sustainability

```bash
# Example: create a listing via API
curl -X POST http://localhost:8001/marketplace/listings \
  -H 'Content-Type: application/json' \
  -d '{"agent_id":"agent_001","agent_name":"BTC Titan",
       "seller_address":"0xABCD","price_karma":500,
       "strategy_type":"trend_following","win_rate":0.65,
       "total_pnl":1200}'
```

---

## 📊 Monitoring

15 Prometheus metrics tracked:
- `arena_cycle_total` — game loop cycles
- `arena_agent_pnl` — per-agent P&L
- `arena_trade_volume` — trading volume
- `arena_risk_rejections` — risk-blocked trades
- `arena_regime_current` — current market regime
- `arena_karma_minted` / `arena_karma_burned`
- `arena_quests_completed` — quest activity
- `arena_tournament_entries` — tournament participation
- `arena_marketplace_listings` — active listings (v1.3)
- `arena_marketplace_volume` — KARMA trading volume (v1.3)
- ...and more

---

## 🔒 Safety & Risk

```json
{
  "max_position_size_pct": 15,
  "max_daily_loss_pct": 5,
  "max_leverage": 3,
  "require_stop_loss": true,
  "max_correlation": 0.7,
  "paper_mode_default": true
}
```

- ✅ **Paper trading by default** — zero capital risk
- ✅ **`--live` flag** requires explicit `CONFIRM` prompt
- ✅ **OpenZeppelin contracts** — audited base contracts
- ✅ **ReentrancyGuard** on all marketplace transactions
- ✅ **Graceful degradation** — all modules log dry-run if credentials missing

---

## 🧪 Tests

```bash
# Python tests
pytest tests/ -v

# Contract tests (Hardhat)
npm run test:contracts
# KarmaToken: 6 tests
# ArenaLeaderboard: 5 tests
# AgentNFT: 5 tests
# AgentMarketplace: 7 tests  ← v1.3
```

---

## 📁 Environment Variables

See [`.env.example`](.env.example) for full reference.

| Variable | Description |
|----------|-------------|
| `COINGECKO_API_KEY` | Market data |
| `CMC_API_KEY` | CoinMarketCap |
| `TWITTER_*` | Twitter/X posting |
| `DISCORD_BOT_TOKEN` | Discord bot |
| `BASE_RPC_URL` | Base L2 RPC |
| `PRIVATE_KEY` | Wallet for contracts |
| `MVX_PEM_PATH` | MultiversX wallet |

---

## 📚 Documentation

- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) — Full deployment guide
- [`docs/v1.2-RELEASE-NOTES.md`](docs/v1.2-RELEASE-NOTES.md) — v1.2 changelog
- [`docs/v1.3-RELEASE-NOTES.md`](docs/v1.3-RELEASE-NOTES.md) — v1.3 changelog ✨

---

## 📜 License

MIT © 2026 [George Pricop](https://github.com/Gzeu)
