# 📡 CryptoArena API Reference

## Core Modules

### `ArenaCore`

**Location:** `src/arenacore/orchestrator.py`

```python
from src.arenacore.orchestrator import ArenaCore

arena = ArenaCore(config)
await arena.run_micro_cycle()  # Returns decision cycle dict
await arena.run_meso_cycle()   # Hourly eval
await arena.run_macro_cycle()  # Daily reflection
```

---

### `GameState`

**Location:** `src/state/game_state.py`

```python
from src.state.game_state import GameState

state = GameState(config)
state.portfolios["A1"]  # AgentPortfolio object
state.current_regime    # Latest regime dict
state.leaderboard       # Sorted by score
```

**Key Methods:**

- `add_snapshot(snapshot: dict)` — Store market snapshot
- `update_regime(regime: dict)` — Update regime state
- `apply_executions(log: list)` — Record executed trades
- `compute_hourly_metrics()` — Recalculate PnL, drawdown
- `update_leaderboard()` — Rebuild leaderboard

---

### `MarketScout`

**Location:** `src/market/scout.py`

```python
from src.market.scout import MarketScout

scout = MarketScout(config)
snapshot = await scout.fetch_snapshot()
# Returns: { "timestamp", "prices", "volumes_24h", "price_changes_24h", "meme_coins", "anomalies" }
```

---

### `RegimeDetector`

**Location:** `src/regime/detector.py`

```python
from src.regime.detector import RegimeDetector

detector = RegimeDetector()
regime = detector.detect(snapshot)
# Returns: { "regime": str, "probabilities": dict, "explanation": str }
```

---

### `RiskGuardian`

**Location:** `src/risk/guardian.py`

```python
from src.risk.guardian import RiskGuardian

guardian = RiskGuardian(config)
approved, rejected = guardian.filter(proposals, portfolios)
```

---

### `TraderExecutor`

**Location:** `src/execution/executor.py`

```python
from src.execution.executor import TraderExecutor

executor = TraderExecutor(mode="simulation")
log = await executor.execute_batch(approved_proposals)
```

---

### `PolymarketClient`

**Location:** `src/market/polymarket.py`

```python
from src.market.polymarket import PolymarketClient

client = PolymarketClient()
markets = await client.get_crypto_markets()
odds = await client.get_market_odds(market_id)
```

---

### `OnChainSync`

**Location:** `src/state/onchain_sync.py`

```python
from src.state.onchain_sync import OnChainSync

sync = OnChainSync(config)
sync.sync_leaderboard(state.leaderboard)  # Push to Base L2
onchain_data = sync.read_leaderboard()     # Read from contract
```

---

## Data Schemas

### Market Snapshot

```python
{
  "timestamp": "2026-03-05T00:37:00Z",
  "prices": {"BTC": 73797.98, "ETH": 2000.0, "SOL": 85.8},
  "volumes_24h": {"BTC": 46.67e9, "ETH": 15.3e9, "SOL": 2.1e9},
  "price_changes_24h": {"BTC": +7.35, "ETH": -2.37, "SOL": -3.42},
  "meme_coins": [
    {"symbol": "DOGE", "price": 0.0896, "volume_24h": 1.37e9, "price_change_24h": +2.3},
    {"symbol": "PEPE", "price": 0.0000034, "volume_24h": 428e6, "price_change_24h": -5.1}
  ],
  "anomalies": ["BTC extreme 24h move: +7.35%"]
}
```

### Regime Detection

```python
{
  "regime": "Bear",
  "probabilities": {"Bull": 0.12, "Bear": 0.52, "Sideways": 0.31, "Crisis": 0.05},
  "avg_24h_change": -1.3,
  "anomalies_detected": [],
  "explanation": "Avg 24h change of -1.3% across majors. Mild Bear with Sideways overlay."
}
```

### Trade Proposal

```python
{
  "agent_id": "A2",
  "symbol": "ETH/USD",
  "side": "LONG",
  "size_usdc": 350.0,
  "leverage": 1.5,
  "entry_price_estimate": 2000.0,
  "stop_loss": 1860.0,
  "take_profit": 2200.0,
  "rationale": "ETH oversold dip entry at $2,000 support.",
  "entry_logic": "market now",
  "regime_alignment": "Bear bounce"
}
```

---

## Event-Driven Hooks

### Custom Agent Integration

To add a new agent:

1. Create `src/agents/a9_custom.py`
2. Inherit from `BaseAgent`
3. Implement `async def propose(regime, snapshot, portfolio) -> List[TradeProposal]`
4. Register in `src/agents/crew.py` → `AGENT_CLASSES`
5. Add config to `config/agents.yaml`

---

## WebSocket API (Future)

Planned for v2.0:

```python
# Subscribe to real-time game state
ws://localhost:8080/ws/game_state

# Messages:
{"type": "regime_update", "data": {...}}
{"type": "trade_executed", "data": {...}}
{"type": "leaderboard_update", "data": {...}}
```

---

## REST API Endpoints (Future)

Planned FastAPI server:

- `GET /leaderboard` — Current standings
- `GET /regime` — Current regime probabilities
- `GET /agents/{agent_id}` — Agent portfolio & stats
- `GET /history` — Historical snapshots
- `POST /admin/pause` — Emergency pause (admin only)
