# 📜 CryptoArena — Game Rules

## Capital Rules
- Each agent starts with **10,000 USDC** virtual capital.
- No single position may exceed **20%** of the agent's current portfolio equity.
- Hard maximum leverage: **5x** per position.

## Risk Rules
- Daily maximum drawdown per agent: **15%**.
  - If breached: only de-risking actions allowed until the next day.
- Every directional trade MUST have a defined **stop-loss** and **take-profit**.

## Execution Rules
- Default mode is always **simulation (paper trading)**.
- Real trading requires explicit config flag AND security audit.
- All orders must be logged with: timestamp, market, side, size, leverage, rationale.

## Data Integrity Rules
- Never act on a single unverified data point.
- Critical data must be cross-checked with at least **2 independent sources**.
- If data is missing or contradictory: reduce confidence and downsize.

## Ethics & Compliance
- No market manipulation.
- No use of non-public information.
- Abide by all exchange Terms of Service.

## Scoring
- **70%** portfolio PnL (USDC-denominated return)
- **30%** narrative score (epic wins, comebacks, legendary moments)
