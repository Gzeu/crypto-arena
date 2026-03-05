# 📊 CryptoArena — Regime Model

## Regimes

### 1. Bull / Trend
- Strong uptrend: higher highs, higher lows, rising volume
- Allowed behavior: trend-following, leverage up to config max, ride narratives
- Heuristic trigger: avg 24h change > +3% across BTC/ETH/SOL

### 2. Bear / Crash
- Persistent downtrend, large drawdowns, liquidity stress
- Allowed behavior: risk-off, shorts, stablecoins, capital preservation
- Heuristic trigger: avg 24h change < -3%

### 3. Sideways / High Vol
- Range-bound chop, high realized volatility, no clear trend
- Allowed behavior: mean-reversion, volatility harvesting, LP/arbitrage
- Heuristic trigger: avg 24h change between -1% and +1%

### 4. Crisis
- Extreme events: exchange failures, massive liquidations, systemic risk
- Allowed behavior: survival mode, max risk reduction, mostly stablecoins
- Heuristic trigger: any asset with |24h change| > 20% OR DATA_FETCH_FAILED

## Detection Method (MVP)
Simple heuristic based on:
- Average 24h price change of BTC, ETH, SOL
- Maximum single-asset 24h absolute change
- Anomaly flags from Market Scout

## Planned Upgrade
- Hidden Markov Model (HMM) with Markov Regime Switching
- Feature set: returns, volatility, volume z-scores, funding rates, open interest
- Emit regime probabilities per cycle as posterior distribution
