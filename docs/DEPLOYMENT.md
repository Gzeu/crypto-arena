# CryptoArena Deployment Guide

🚀 Complete guide for deploying CryptoArena to production.

## Prerequisites

### System Requirements

- **Python**: 3.9 or higher
- **OS**: Linux (Ubuntu 20.04+), macOS, or Windows with WSL2
- **RAM**: Minimum 2GB, recommended 4GB+
- **Disk**: 10GB free space
- **Network**: Stable internet connection

### Required API Keys

1. **CoinGecko API** (Free tier sufficient for MVP)
   - Sign up: https://www.coingecko.com/en/api
   - Set: `COINGECKO_API_KEY`

2. **CoinMarketCap API** (Free tier)
   - Sign up: https://coinmarketcap.com/api/
   - Set: `COINMARKETCAP_API_KEY`

3. **OpenAI API** (for narrative generation)
   - Sign up: https://platform.openai.com/
   - Set: `OPENAI_API_KEY`

### Optional API Keys

4. **Polymarket API** (for A6 prediction agent)
   - Set: `POLYMARKET_API_KEY`

5. **Alchemy/Infura** (for blockchain integration)
   - Alchemy: https://www.alchemy.com/
   - Infura: https://infura.io/
   - Set: `ALCHEMY_API_KEY` or `INFURA_API_KEY`

6. **Telegram Bot** (for notifications)
   - Create bot: https://t.me/BotFather
   - Set: `TELEGRAM_BOT_TOKEN`

7. **Discord Webhook** (for notifications)
   - Create webhook in Discord server settings
   - Set: `DISCORD_WEBHOOK_URL`

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/Gzeu/crypto-arena.git
cd crypto-arena
```

### 2. Set Up Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Minimum required `.env` content:**

```bash
# Required APIs
COINGECKO_API_KEY=your_coingecko_key_here
COINMARKETCAP_API_KEY=your_cmc_key_here
OPENAI_API_KEY=your_openai_key_here

# Game Configuration
GAME_MODE=paper  # Start in paper trading mode
STARTING_CAPITAL=100000
CYCLE_INTERVAL_MINUTES=60

# Optional: Blockchain (for leaderboard)
# BASE_RPC_URL=https://mainnet.base.org
# PRIVATE_KEY=your_private_key_here  # Never commit this!
```

### 4. Run Deployment Script

```bash
python scripts/deploy.py --mode production
```

This will:
- ✔️ Check system requirements
- ✔️ Validate API keys
- ✔️ Create necessary directories
- ✔️ Initialize database
- ✔️ Set up monitoring
- ✔️ Run health checks

### 5. Start CryptoArena

```bash
python scripts/start_arena.py
```

The arena will begin its autonomous operation:
- 🔍 Market data scanning every cycle
- 🧠 AI agents proposing trades
- 🛡️ Risk management filtering proposals
- 💰 Execution (paper trading by default)
- 📊 Performance tracking
- 📝 Daily narrative reports

## Deployment Modes

### Paper Trading (Default - Recommended for Launch)

```bash
python scripts/start_arena.py --mode paper
```

- **No real capital at risk**
- All trades simulated
- Full functionality testing
- Performance metrics tracked
- Perfect for:
  - Initial launch
  - Strategy validation
  - Agent performance evaluation
  - Public demonstration

### Live Trading (Use with Extreme Caution)

```bash
python scripts/start_arena.py --mode live --capital 1000
```

⚠️ **WARNING**: Only use live mode after:
1. Extensive paper trading validation (minimum 30 days)
2. Reviewing all agent strategies
3. Understanding all risks
4. Setting appropriate risk limits
5. Starting with minimal capital

**Additional requirements for live mode:**
- Exchange API keys (Binance, Coinbase, etc.)
- Sufficient account balance
- 2FA authentication configured
- Clear understanding of tax implications

## Monitoring

### Web Dashboard

Start the monitoring server:

```bash
python scripts/monitor.py
```

Access dashboard at: http://localhost:8000

**Dashboard features:**
- Real-time portfolio value
- Agent performance comparison
- Trade history
- Risk metrics
- Market regime detection
- System health status

### Logs

```bash
# Follow real-time logs
tail -f logs/arena.log

# View errors only
grep ERROR logs/arena.log

# View specific agent
grep "\[A1\]" logs/arena.log
```

### Metrics

Metrics are stored in:
- `data/arena.db` - SQLite database
- `state/game_state.json` - Current game state
- `reports/` - Daily narrative reports

## Configuration

### Game Parameters

Edit `config/deployment.json`:

```json
{
  "game": {
    "cycle_interval_minutes": 60,     // How often to run cycle
    "starting_capital": 100000,       // Starting portfolio value
    "mode": "paper",                  // paper or live
    "agents": {
      "enabled": ["A1", "A2", ...]    // Which agents to activate
    }
  }
}
```

### Risk Parameters

```json
{
  "risk": {
    "max_position_size_pct": 15,      // Max 15% per position
    "max_daily_loss_pct": 5,          // Stop if -5% in one day
    "max_leverage": 3,                // Maximum leverage allowed
    "require_stop_loss": true,        // Mandatory stop losses
    "max_correlation": 0.7            // Diversification requirement
  }
}
```

## Agent Configuration

### Enable/Disable Agents

Edit `config/deployment.json`:

```json
{
  "game": {
    "agents": {
      "enabled": [
        "A1",  // BTC Trend Follower
        "A2",  // ETH Swing Trader
        "A3",  // SOL Short Specialist
        "A4",  // Meme Coin Sniper
        "A5",  // DeFi Basis Trade
        "A6",  // Prediction Markets
        "A7",  // Crypto Index
        "A8"   // Chaos Agent
      ]
    }
  }
}
```

Remove agents you don't want to activate.

### Agent-Specific Settings

Each agent has configurable parameters in `src/agents/a*_*.py`:

```python
class A1BTCTrendFollower(BaseAgent):
    # Configurable parameters
    LOOKBACK_DAYS = 30
    CONFIDENCE_THRESHOLD = 0.7
    MAX_POSITION_SIZE = 0.2  # 20% of portfolio
```

## Blockchain Integration

### Deploy Smart Contracts

```bash
# Deploy to Base L2
python scripts/deploy_contracts.py --network base

# Verify deployment
python scripts/verify_contracts.py
```

### Update Contract Addresses

After deployment, update `config/deployment.json`:

```json
{
  "blockchain": {
    "contract_addresses": {
      "leaderboard": "0x...",
      "arena_token": "0x..."
    }
  }
}
```

## Maintenance

### Daily Checks

```bash
# Check system status
python scripts/health_check.py

# View performance summary
python scripts/summary.py --days 1

# Check for errors
grep ERROR logs/arena.log | tail -20
```

### Weekly Tasks

1. **Review Performance**
   ```bash
   python scripts/summary.py --days 7
   ```

2. **Backup Database**
   ```bash
   cp data/arena.db backups/arena_$(date +%Y%m%d).db
   ```

3. **Update Dependencies**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

4. **Check API Quotas**
   - CoinGecko: Check rate limit usage
   - OpenAI: Monitor token usage
   - Exchange: Verify API key validity

### Monthly Tasks

1. **Strategy Review**
   - Analyze agent performance
   - Identify underperforming agents
   - Adjust parameters if needed

2. **Risk Assessment**
   - Review maximum drawdown
   - Check correlation metrics
   - Validate risk limits

3. **System Updates**
   - Update Python packages
   - Review security advisories
   - Update API integrations

## Troubleshooting

### Common Issues

#### 1. API Rate Limits

**Symptom**: `RateLimitExceeded` errors in logs

**Solution**:
```python
# Reduce API call frequency in config/deployment.json
{
  "game": {
    "cycle_interval_minutes": 120  // Increase interval
  }
}
```

#### 2. Database Locked

**Symptom**: `database is locked` errors

**Solution**:
```bash
# Stop arena
pkill -f start_arena.py

# Check for lingering processes
ps aux | grep arena

# Restart
python scripts/start_arena.py
```

#### 3. Memory Issues

**Symptom**: Process killed by OS

**Solution**:
```bash
# Monitor memory usage
python scripts/monitor.py --check-memory

# Reduce agent count or increase system RAM
```

#### 4. Network Timeouts

**Symptom**: `TimeoutError` in logs

**Solution**:
```json
// Increase timeout in config/deployment.json
{
  "api": {
    "timeout_seconds": 30,
    "retry_attempts": 5
  }
}
```

### Getting Help

1. **Check Logs**:
   ```bash
   tail -100 logs/arena.log
   ```

2. **Run Diagnostics**:
   ```bash
   python scripts/diagnose.py
   ```

3. **GitHub Issues**:
   - Report bugs: https://github.com/Gzeu/crypto-arena/issues
   - Search existing issues first

4. **Community**:
   - Discord: [Join our server]
   - Telegram: [Join our group]

## Security Best Practices

### Environment Variables

- ⚠️ **NEVER** commit `.env` file
- ⚠️ **NEVER** share API keys
- ⚠️ **NEVER** commit private keys
- ✔️ Use environment variables for secrets
- ✔️ Rotate API keys regularly

### Access Control

```bash
# Restrict file permissions
chmod 600 .env
chmod 600 config/*.json

# Limit SSH access
# Use SSH keys instead of passwords
```

### Monitoring Access

If exposing monitoring dashboard:

```bash
# Use reverse proxy with authentication
# Example with nginx:

location /arena {
    auth_basic "CryptoArena";
    auth_basic_user_file /etc/nginx/.htpasswd;
    proxy_pass http://localhost:8000;
}
```

## Scaling

### Horizontal Scaling

```bash
# Run multiple instances with different agent subsets

# Instance 1: Trend followers (A1, A2, A7)
python scripts/start_arena.py --agents A1,A2,A7

# Instance 2: High-risk agents (A3, A4, A8)
python scripts/start_arena.py --agents A3,A4,A8

# Instance 3: Conservative agents (A5, A6)
python scripts/start_arena.py --agents A5,A6
```

### Resource Optimization

```python
# Reduce memory usage
import gc
gc.collect()  # Force garbage collection after each cycle

# Use connection pooling for APIs
# Configure in src/market/scout.py
```

## Production Checklist

Before going live:

- [ ] All API keys configured and tested
- [ ] Environment variables secured
- [ ] Database initialized and backed up
- [ ] Monitoring dashboard accessible
- [ ] Logs rotating properly
- [ ] Paper trading validated (30+ days)
- [ ] Risk limits configured appropriately
- [ ] Emergency stop procedures documented
- [ ] Team notified of deployment
- [ ] Rollback plan prepared

## Emergency Procedures

### Stop Everything Immediately

```bash
# Kill all arena processes
pkill -f start_arena.py
pkill -f monitor.py

# Close all positions (if in live mode)
python scripts/emergency_close.py
```

### Rollback

```bash
# Stop arena
pkill -f start_arena.py

# Restore previous database
cp backups/arena_YYYYMMDD.db data/arena.db

# Checkout previous code version
git checkout <previous-commit>

# Restart
python scripts/start_arena.py
```

## Support

- **Documentation**: https://github.com/Gzeu/crypto-arena/tree/main/docs
- **Issues**: https://github.com/Gzeu/crypto-arena/issues
- **Email**: support@cryptoarena.xyz

---

🏟️ **Welcome to CryptoArena!** May your agents trade wisely.
