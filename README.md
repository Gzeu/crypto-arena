# 🏟️ CryptoArena

> **Fully autonomous, crypto-native AI agent game platform — launched 2026**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Chain: Base L2](https://img.shields.io/badge/Chain-Base%20L2-blue)](https://base.org)
[![Chain: MultiversX](https://img.shields.io/badge/Chain-MultiversX-green)](https://multiversx.com)
[![Mode: Simulation](https://img.shields.io/badge/Mode-Simulation-orange)](#execution-modes)

---

## 🎮 What is CryptoArena?

CryptoArena is a **real-time, live-data-driven competitive game** where **autonomous AI agents** battle it out across crypto markets. It is NOT a toy simulation — every price tick, regime shift, and narrative arc is anchored in real on-chain and market data.

Each agent starts with **10,000 USDC** (virtual) and competes to maximize:
- 📈 Portfolio returns (USDC-denominated P&L)
- 🎭 Narrative impact (epic wins, comebacks, legendary moments)

---

## 🧠 Architecture

```
ArenaCore (Orchestrator)
│
├── Market Scout Agent        — live prices, volumes, on-chain flows
├── Regime Detector Agent     — Bull / Bear / Sideways / Crisis
├── Strategy Analyst Agents   — 5 archetypes (Trend, Swing, Meme, DeFi, Prediction)
├── Trader Executor Agent     — paper or live order execution
├── Risk Guardian Agent       — hard veto, drawdown enforcement
├── Narrative Weaver Agent    — storylines, chronicles, social posts
└── Reflection Agent          — daily learning, memory updates
```

---

## 🤖 The 8 Agents (MVP)

| ID  | Name                        | Archetype                        | Focus                        |
|-----|-----------------------------|----------------------------------|------------------------------|
| A1  | BTC Trend Follower          | Trend / Momentum                 | BTC majors, macro            |
| A2  | ETH Swing Trader            | Swing / Mean-Reversion           | ETH cycles, oversold bounces |
| A3  | SOL Short / Hedge Specialist| Short / Hedger                   | SOL, hedging correlations    |
| A4  | Meme Sniper                 | High-velocity meme coins         | Top meme coins by 24h vol    |
| A5  | DeFi / Basis Trader         | Yield / Basis / LP               | Funding rates, LP strategies |
| A6  | Prediction Market Agent     | Polymarket & prediction markets  | Event-driven bets            |
| A7  | Risk-Adjusted Index Agent   | Diversified / Low-vol            | Balanced index approach      |
| A8  | Chaos / Exploration Agent   | Random exploration (small sizes) | Discovering alpha edges      |

---

## 🌐 Market Universe

- **Majors**: BTC, ETH, SOL
- **Dynamic meme coin slots**: top 3 by 24h volume (refreshed each cycle)
- **Data sources**: CoinGecko, Binance, DexScreener, Chainlink/Pyth, Polymarket, Dune/Flipside

---

## 📊 Market Regimes

| Regime       | Description                              | Agent Behavior                         |
|--------------|------------------------------------------|----------------------------------------|
| Bull / Trend | Uptrend, higher highs, rising volume     | Trend-follow, ride narratives, leverage |
| Bear / Crash | Downtrend, drawdowns, liquidity stress   | Risk-off, shorts, stablecoins          |
| Sideways     | Range-bound, high realized vol           | Mean-reversion, vol harvesting         |
| Crisis       | Extreme events, systemic risk            | Survival mode, max de-risk             |

---

## 🛡️ Safety Constraints

- No single position > **20%** of agent capital
- Hard max leverage: **5x** per position
- Daily max drawdown: **15%** (breach → de-risk only mode)
- Stop-loss and take-profit on EVERY directional trade
- **Always starts in paper / simulation mode**
- Cross-check all critical data with ≥ 2 independent sources

---

## ⛓️ On-Chain Infrastructure

- **Base L2**: leaderboard, karma token, agent NFTs, trade logs
- **MultiversX / Supernova**: special quests, cross-chain events, NFT seasons

---

## 📁 Project Structure

```
crypto-arena/
├── src/
│   ├── arenacore/          # Main orchestrator
│   ├── agents/             # All 8 agent modules
│   ├── regime/             # Regime detection engine
│   ├── market/             # Market Scout & data adapters
│   ├── risk/               # Risk Guardian logic
│   ├── narrative/          # Narrative Weaver
│   ├── reflection/         # Daily Reflection Agent
│   ├── execution/          # Trader Executor (paper + live)
│   └── state/              # Game State & Memory manager
├── config/
│   ├── agents.yaml         # Agent configs & risk profiles
│   └── game.yaml           # Global game settings
├── tests/
├── docs/
│   ├── GAME_RULES.md
│   ├── AGENTS.md
│   └── REGIME_MODEL.md
├── scripts/
│   └── start_arena.py      # Entry point
├── .github/
│   └── workflows/
│       └── ci.yml
├── requirements.txt
└── README.md
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/Gzeu/crypto-arena
cd crypto-arena
pip install -r requirements.txt
python scripts/start_arena.py --mode simulation
```

---

## 📜 License

MIT — see [LICENSE](LICENSE)
