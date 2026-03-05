# 🚀 CryptoArena Deployment Guide

## Prerequisites

- Python 3.11+
- Node.js 18+ (for Foundry)
- Redis (optional, for distributed state)
- Base L2 RPC endpoint
- (Optional) Binance API keys for live mode

---

## 1. Local Development Setup

```bash
git clone https://github.com/Gzeu/crypto-arena
cd crypto-arena

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your settings
```

---

## 2. Smart Contract Deployment (Base L2)

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Compile contracts
forge build

# Deploy to Base Sepolia (testnet)
forge create --rpc-url https://sepolia.base.org \
  --private-key $DEPLOYER_KEY \
  --etherscan-api-key $BASESCAN_KEY \
  --verify \
  contracts/ArenaLeaderboard.sol:ArenaLeaderboard

# Save deployed address to .env
echo "LEADERBOARD_CONTRACT=0xYourContractAddress" >> .env
```

---

## 3. Run CryptoArena (Simulation Mode)

```bash
python scripts/start_arena.py --mode simulation
```

This starts the autonomous game loop:
- Micro cycles every 5 minutes
- Hourly performance evaluation
- Daily reflection & chronicle

---

## 4. Monitoring Dashboard

In a separate terminal:

```bash
python scripts/monitor.py
```

This launches a Rich terminal UI showing:
- Live leaderboard
- Current regime probabilities
- Recent trades
- System status

---

## 5. Production Deployment (Live Mode)

⚠️ **CRITICAL SAFETY CHECKLIST:**

- [ ] Smart contracts audited
- [ ] MPC or hardware wallet signing implemented
- [ ] Position size limits enforced (max 20% per position)
- [ ] Daily drawdown monitoring active (15% hard stop)
- [ ] Real-time kill-switch enabled
- [ ] Legal compliance verified for jurisdiction
- [ ] Insurance / risk management in place

```bash
# Set live mode in config/game.yaml
execution_mode: "live"

# Or override via CLI
python scripts/start_arena.py --mode live
```

⚠️ Live mode requires:
- `BINANCE_API_KEY` and `BINANCE_API_SECRET` in `.env`
- Sufficient account balance and margin
- 24/7 monitoring infrastructure

---

## 6. Cloud Deployment (AWS / GCP / Azure)

### Docker Container

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "scripts/start_arena.py", "--mode", "simulation"]
```

```bash
docker build -t crypto-arena .
docker run -d --env-file .env --name arena crypto-arena
```

### systemd Service (Linux)

```ini
# /etc/systemd/system/crypto-arena.service
[Unit]
Description=CryptoArena Autonomous Game
After=network.target

[Service]
Type=simple
User=arena
WorkingDirectory=/opt/crypto-arena
Environment="PATH=/opt/crypto-arena/venv/bin"
ExecStart=/opt/crypto-arena/venv/bin/python scripts/start_arena.py --mode simulation
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable crypto-arena
sudo systemctl start crypto-arena
sudo journalctl -u crypto-arena -f
```

---

## 7. Backup & Recovery

```bash
# Backup game state (SQLite)
cp state.db state.backup.$(date +%Y%m%d).db

# Backup agent memory
tar -czf memory_backup.tar.gz memory/
```

---

## 8. Monitoring & Alerts

- **Logs**: `logs/arena.log` (via Loguru)
- **Metrics**: Export to Prometheus/Grafana (future)
- **Alerts**: Set up PagerDuty / Slack webhooks for:
  - Daily drawdown > 12%
  - API failures
  - Regime shifts to Crisis
  - On-chain sync failures

---

## 9. Maintenance

```bash
# Pull latest code
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart crypto-arena
```

---

## Support

- GitHub Issues: [https://github.com/Gzeu/crypto-arena/issues](https://github.com/Gzeu/crypto-arena/issues)
- Docs: [https://github.com/Gzeu/crypto-arena/tree/main/docs](https://github.com/Gzeu/crypto-arena/tree/main/docs)
