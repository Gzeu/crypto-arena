"""
Tests for RiskGuardian
"""
import pytest
from unittest.mock import MagicMock
from src.risk.guardian import RiskGuardian
from src.agents.base import TradeProposal


DEFAULT_CONFIG = {
    "risk": {
        "max_position_pct": 0.20,
        "max_leverage": 5.0,
        "daily_max_drawdown_pct": 0.15,
    }
}


def make_portfolio(equity=10000, de_risk=False):
    p = MagicMock()
    p.total_equity = equity
    p.de_risk_mode = de_risk
    return p


def make_proposal(agent_id="A1", size=500, leverage=2.0):
    return TradeProposal(
        agent_id=agent_id,
        symbol="BTC/USD",
        side="LONG",
        size_usdc=size,
        leverage=leverage,
        entry_price_estimate=50000,
        stop_loss=46500,
        take_profit=56000,
        rationale="Test",
    )


def test_approve_valid_proposal():
    guardian = RiskGuardian(DEFAULT_CONFIG)
    proposal = make_proposal(size=500, leverage=2.0)
    portfolio = make_portfolio(equity=10000)
    approved, rejected = guardian.filter([proposal], {"A1": portfolio})
    assert len(approved) == 1
    assert len(rejected) == 0


def test_reject_oversized_leverage():
    guardian = RiskGuardian(DEFAULT_CONFIG)
    proposal = make_proposal(size=500, leverage=6.0)  # exceeds 5x cap
    portfolio = make_portfolio(equity=10000)
    approved, rejected = guardian.filter([proposal], {"A1": portfolio})
    assert len(rejected) == 1


def test_reject_de_risk_mode():
    guardian = RiskGuardian(DEFAULT_CONFIG)
    proposal = make_proposal(size=200, leverage=1.0)
    portfolio = make_portfolio(de_risk=True)
    approved, rejected = guardian.filter([proposal], {"A1": portfolio})
    assert len(rejected) == 1


def test_downsize_oversized_position():
    guardian = RiskGuardian(DEFAULT_CONFIG)
    proposal = make_proposal(size=2500, leverage=2.0)  # >20% of 10k
    portfolio = make_portfolio(equity=10000)
    approved, rejected = guardian.filter([proposal], {"A1": portfolio})
    assert len(approved) == 1
    assert approved[0].size_usdc == 1250  # downsized by 50%
