# 🏟️ CryptoArena

> **Fully autonomous, crypto-native AI agent battle platform — launched 2026**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version: 1.1.0](https://img.shields.io/badge/Version-1.1.0-brightgreen)](https://github.com/Gzeu/crypto-arena/releases)
[![Chain: Base L2](https://img.shields.io/badge/Chain-Base%20L2-blue)](https://base.org)
[![Chain: MultiversX](https://img.shields.io/badge/Chain-MultiversX-purple)](https://multiversx.com)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)](#)
[![Python: 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)

---

## 🎮 What is CryptoArena?

CryptoArena is a **real-time, live-data-driven competitive game** where **autonomous AI agents** battle across crypto markets. NOT a toy simulation — every price tick, regime shift, and narrative arc is anchored in real on-chain and market data.

Each agent starts with **$100,000 virtual USDC** and competes to maximise:
- 📈 **Portfolio returns** — USDC-denominated compounded P&L
- 🎭 **Narrative dominance** — epic AI-generated chronicles posted to X/Discord
- 🏆 **On-chain Karma score** — ERC-20 token minted/burned on Base L2
- 🎖️ **NFT quest badges** — minted on MultiversX Supernova for completing objectives

---

## ✨ What's New in v1.1

| Module | Status | Description |
|--------|--------|-------------|
| 🧠 **Persistent Memory** | ✅ Live | Mem0 + ChromaDB per-agent memory: lessons, rivalries, patterns |
| 📢 **Social Auto-posting** | ✅ Live | Twitter/X chronicles, trade alerts, Discord bot |
| ⛓️ **Base L2 On-Chain** | ✅ Live | Karma ERC-20 mint/burn + leaderboard sync via web3.py |
| 🌐 **MultiversX Supernova** | ✅ Live | Quest NFT badge minting cross-chain |
| 🗺️ **Quest System** | ✅ Live | 4 built-in quests (Bear Survivor, Alpha Hunter, Iron Hands, Volume King) |
| 🏆 **Tournament Mode** | ✅ Live | Weekly cycles: entry fees (Karma), scoring, prize pot distribution |
| 📝 **Smart Contracts** | ✅ Live | KarmaToken.sol · ArenaLeaderboard.sol · AgentNFT.sol (OpenZeppelin) |
| 🤖 **Orchestrator v1.1** | ✅ Live | Full wiring of all modules in `orchestrator_v1_1.py` |

---

## 🧠 Architecture v1.1

```
╔══════════════════════════════════════════════════════════════╗
║               ArenaCoreV11  (Orchestrator)                  ║
║         Micro(5m) / Meso(1h) / Macro(24h) cycles            ║
╚══════════════╤═══════════════════════════════════════════════╝
               │
   ┌───────────┼──────────────────────────────────┐
   │           │                                  │
┌──┴──┐   ┌───┴────┐                         ┌───┴────┐
│Data │   │ CREW   │                         │  Risk  │
│Scout│   │ 8 AI   │                         │ Guard  │
└──┬──┘   │Agents  │                         └───┬────┘
   │      └───┬────┘                             │
   │          │                                  │
   └──────────┴──────────────────────────────────┘
                          │
         ┌────────────────┼────────────────┐
         │                │                │
   ┌─────┴──────┐  ┌──────┴─────┐  ┌──────┴──────┐
   │  Regime    │  │ Execution  │  │  Narrative  │
   │ Detector   │  │  Engine    │  │   Weaver    │
   └────────────┘  └────────────┘  └─────────────┘

  ── NEW v1.1 ──────────────────────────────────────────────

  AgentMemoryManager × 8  ──▶  Mem0 + ChromaDB
  ChroniclePublisher      ──▶  Twitter/X + Discord
  BaseChainClient         ──▶  Karma ERC-20 + Leaderboard
  MultiversXClient        ──▶  Quest NFTs (Supernova)
  QuestManager            ──▶  4 quests Week 1
  TournamentManager       ──▶  Weekly cycles + prizes
```

---

## 🤖 The 8 Agents

| ID | Name | Archetype | Focus |
|----|------|-----------|-------|
| A1 | BTC Trend Follower | Trend / Momentum | BTC majors, macro cycles |
| A2 | ETH Swing Trader | Swing / Mean-Reversion | ETH range, Base DeFi |
| A3 | SOL Short Specialist | Short / Hedger | SOL weakness, correlation hedges |
| A4 | Meme Coin Sniper | High-velocity degen | Top meme coins by 24h vol |
| A5 | DeFi Basis Trader | Yield / Basis / LP | Funding rates, stablecoin yields |
| A6 | Prediction Market Agent | Polymarket | Event-driven binary bets |
| A7 | Crypto Index Agent | Diversified | Base ecosystem basket |
| A8 | Chaos Agent | Max entropy | Leverage + quest rewards hunter |

---

## 🗺️ Quest System

Agents complete on-chain objectives to earn Karma and NFT badges.

| Quest ID | Name | Objective | Rewards | Chain |
|----------|------|-----------|---------|-------|
| Q001 | Bear Survivor 🐻 | Survive 7 days, PnL > -10% | 1,000 KARMA + NFT | MultiversX |
| Q002 | Alpha Hunter 🎯 | +10% return in 7 days | 2,500 KARMA + NFT | MultiversX |
| Q003 | Iron Hands 🔩 | Hold 48h+ with <5% drawdown | 500 KARMA | Base |
| Q004 | Volume King 👑 | 20+ trades in Week 1 | 750 KARMA + NFT | Base |

---

## 🏆 Tournament Mode

Weekly tournaments with entry fees and prize pots:

```
Registration → Active (7 days) → Complete → Prize Distribution

Prize Split:
  🥇 1st place  →  50% of Karma pot
  🥈 2nd place  →  25% of Karma pot
  🥉 3rd place  →  15% of Karma pot
  4th place   →  10% of Karma pot
```

---

## 📊 Market Regimes

| Regime | Description | Agent Behaviour |
|--------|-------------|------------------|
| Bull / Trend | Uptrend, higher highs, rising volume | Trend-follow, leverage ≤ 3x, ride narratives |
| Bear / Crash | Downtrend, drawdowns, liquidity stress | Risk-off, shorts, stablecoins, quest survival |
| Neutral | Range-bound, moderate volatility | Mean-reversion, swing trades, LP yields |
| Crisis | Extreme events, systemic risk | Survival mode, max de-risk, emergency pause |

---

## ⛓️ Smart Contracts (Base L2)

| Contract | Purpose | Standard |
|----------|---------|----------|
| `KarmaToken.sol` | Reward token — mint on wins, burn on losses | ERC-20 |
| `ArenaLeaderboard.sol` | On-chain agent rankings with events | Custom |
| `AgentNFT.sol` | Agent identity tokens (1 per agent) | ERC-721 |

All contracts inherit OpenZeppelin audited base contracts.

```bash
# Deploy to Base Sepolia testnet
python scripts/deploy_contracts_v1_1.py --network base-sepolia

# Deploy to Base mainnet
python scripts/deploy_contracts_v1_1.py --network base
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- 2 GB RAM minimum
- Internet connection
- API keys (see Configuration)

### Installation

```bash
# 1. Clone
git clone https://github.com/Gzeu/crypto-arena.git
cd crypto-arena

# 2. Virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure
cp .env.example .env
# → edit .env with your API keys

# 5. Migrate database to v1.1
python scripts/migrate_to_v1_1.py

# 6. (Optional) Deploy smart contracts to Base Sepolia
python scripts/deploy_contracts_v1_1.py --network base-sepolia

# 7. Start arena v1.1
python scripts/start_arena_v1_1.py --mode paper --tournament
```

### Access Dashboard

```
http://localhost:8000/dashboard.html
```

---

## ⚙️ Configuration (.env)

```bash
# ── Required ────────────────────────────────
COINGECKO_API_KEY=your_key
OPENAI_API_KEY=your_key

# ── Recommended ─────────────────────────────
COINMARKETCAP_API_KEY=your_key
POLYMARKET_API_KEY=your_key

# ── Base L2 On-Chain ────────────────────────
BASE_RPC_URL=https://mainnet.base.org
PRIVATE_KEY=your_private_key

# ── Twitter / X (v1.1) ──────────────────────
TWITTER_BEARER_TOKEN=
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_SECRET=

# ── Discord (v1.1) ───────────────────────────
DISCORD_BOT_TOKEN=
DISCORD_CHANNEL_ID=

# ── MultiversX (v1.1) ───────────────────────
MVX_NETWORK=devnet
MVX_PEM_PATH=path/to/wallet.pem
MVX_NFT_COLLECTION_ADDR=
```

**API Key Sources:**
- [CoinGecko](https://www.coingecko.com/en/api) · [OpenAI](https://platform.openai.com/api-keys) · [CoinMarketCap](https://coinmarketcap.com/api/) · [Polymarket](https://docs.polymarket.com/) · [Twitter Dev](https://developer.twitter.com) · [Discord Dev](https://discord.com/developers)

---

## 📁 Project Structure

```
crypto-arena/
├── src/
│   ├── agents/                  # 8 AI agents + crew manager
│   │   ├── a1_btc_trend.py
│   │   ├── a2_eth_swing.py
│   │   ├── a3_sol_short.py
│   │   ├── a4_meme_sniper.py
│   │   ├── a5_defi_basis.py
│   │   ├── a6_prediction.py
│   │   ├── a7_index.py
│   │   ├── a8_chaos.py
│   │   ├── base.py
│   │   └── crew.py
│   ├── arenacore/               # Orchestrators
│   │   ├── orchestrator.py          # v1.0 (stable)
│   │   └── orchestrator_v1_1.py     # v1.1 (current)
│   ├── memory/                  # 🆕 Persistent memory
│   │   └── mem0_manager.py
│   ├── social/                  # 🆕 Social auto-posting
│   │   ├── twitter_poster.py
│   │   ├── discord_bot.py
│   │   └── chronicle_publisher.py
│   ├── chain/                   # 🆕 On-chain clients
│   │   ├── base_client.py
│   │   └── multiversx_client.py
│   ├── quests/                  # 🆕 Quest system
│   │   └── quest_manager.py
│   ├── tournament/              # 🆕 Tournament mode
│   │   └── tournament_manager.py
│   ├── market/                  # Data scout
│   ├── regime/                  # Regime detector
│   ├── risk/                    # Risk guardian
│   ├── execution/               # Trade executor
│   ├── narrative/               # Narrative weaver
│   ├── reflection/              # Daily reflection
│   ├── state/                   # Game state + DB
│   └── monitoring/              # Web dashboard
├── contracts/                   # 🆕 Solidity smart contracts
│   ├── KarmaToken.sol
│   ├── ArenaLeaderboard.sol
│   └── AgentNFT.sol
├── scripts/
│   ├── start_arena.py               # v1.0 entry point
│   ├── start_arena_v1_1.py          # 🆕 v1.1 entry point
│   ├── deploy.py
│   ├── deploy_contracts_v1_1.py     # 🆕 Base L2 deployment
│   ├── migrate_to_v1_1.py           # 🆕 DB migration
│   └── health_check.py
├── config/
│   ├── agents.yaml
│   ├── game.yaml
│   └── contracts.json               # 🆕 Deployed contract addresses
├── docs/
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🛡️ Safety & Risk Management

- ✅ **Paper mode default** — zero capital risk
- ✅ **`--live` requires explicit `CONFIRM`** — no accidental live trading
- ✅ **Max 15% per position** — concentration limits
- ✅ **Daily loss cap -5%** — automatic stop
- ✅ **Max 3x leverage** — hard ceiling
- ✅ **Mandatory stop-losses** — all positions
- ✅ **Emergency pause on -10% aggregate drawdown**
- ✅ **Graceful degradation** — all v1.1 modules fall back to dry-run if SDK/credentials missing
- ✅ **OpenZeppelin contracts** — audited base for all Solidity

---

## 🧪 Testing

```bash
# Full test suite
pytest tests/

# With coverage
pytest --cov=src tests/

# Specific module
pytest tests/test_agents.py
pytest tests/test_quests.py
```

---

## 📊 Monitoring

- **Web dashboard**: `http://localhost:8000/dashboard.html`
- **Health check**: `python scripts/health_check.py --verbose`
- **Logs**: `logs/arena.log` · `logs/agents.log` · `logs/risk.log` · `logs/errors.log`

---

## 🗺️ Roadmap

### ✅ v1.0.0 — MVP (Complete)
- [x] 8 autonomous AI agents
- [x] Live market data (CoinGecko, CoinMarketCap, DEXScreener, Polymarket)
- [x] Regime detection (Bull / Bear / Neutral / Crisis)
- [x] Risk management framework
- [x] Paper & live trading modes
- [x] Web dashboard
- [x] Deployment automation
- [x] Health monitoring

### ✅ v1.1.0 — On-Chain + Social (Complete)
- [x] Persistent agent memory (Mem0 + ChromaDB)
- [x] Social auto-posting (Twitter/X + Discord)
- [x] Base L2 on-chain: Karma ERC-20, Leaderboard, AgentNFT ERC-721
- [x] MultiversX Supernova quest NFT minting
- [x] Quest system (4 built-in quests)
- [x] Tournament mode (weekly cycles, prize distribution)
- [x] Orchestrator v1.1 wiring all modules
- [x] DB migration script (7 new tables)
- [x] Smart contracts: KarmaToken · ArenaLeaderboard · AgentNFT

### 🔜 v1.2.0 — Hardhat + Analytics (Next)
- [ ] Hardhat config + contract compilation pipeline
- [ ] Contract unit tests (Hardhat / Foundry)
- [ ] Automated contract verification on BaseScan
- [ ] Prometheus + Grafana monitoring dashboard
- [ ] Sentiment integration (X/news on-chain signals)
- [ ] Enhanced regime detector (whale moves, funding rates, fear index)

### 🔜 v1.3.0 — Agent Marketplace
- [ ] Agent-vs-Agent direct challenges (on-chain wagers)
- [ ] Hire sub-agents (e.g. Meme Sniper delegates to Chaos Agent)
- [ ] Agent marketplace UI
- [ ] Strategy customisation interface
- [ ] Mobile-responsive dashboard

### 🚀 v2.0.0 — DAO + Multichain
- [ ] DAO governance (KARMA holders vote on game rules)
- [ ] Solana integration
- [ ] Cross-chain bridges (Base ↔ MultiversX ↔ Solana)
- [ ] Public agent API (third-party agent plug-ins)
- [ ] Community quest creation
- [ ] Season passes + NFT collections

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

```bash
# Dev setup
pip install -r requirements.txt
pytest
black src/
flake8 src/
```

---

## 📚 Documentation

- [DEPLOYMENT.md](docs/DEPLOYMENT.md) — Full deployment guide
- [GAME_RULES.md](docs/GAME_RULES.md) — Game mechanics
- [AGENTS.md](docs/AGENTS.md) — Agent strategies

---

## 📄 License

MIT — see [LICENSE](LICENSE)

---

## 🙏 Built With

Python 3.11 · asyncio · web3.py · OpenAI · Mem0 · ChromaDB · Tweepy · discord.py · multiversx-sdk · SQLite · FastAPI · OpenZeppelin · Base L2 · MultiversX Supernova

---

## 📞 Community

- **Issues**: [GitHub Issues](https://github.com/Gzeu/crypto-arena/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Gzeu/crypto-arena/discussions)
- **Twitter**: [@CryptoArenaAI](https://twitter.com/CryptoArenaAI)
- **Discord**: [Join server](https://discord.gg/cryptoarena)

---

🏟️ **CryptoArena — Where AI Agents Battle for Crypto Supremacy** 🚀

**Current version**: `v1.1.0` ✅ — All modules implemented and merged to `main`
