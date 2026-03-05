"""
Tests for RegimeDetector
"""
import pytest
from src.regime.detector import RegimeDetector


def make_snapshot(btc_chg, eth_chg, sol_chg, anomalies=None):
    return {
        "price_changes_24h": {"BTC": btc_chg, "ETH": eth_chg, "SOL": sol_chg},
        "anomalies": anomalies or [],
    }


def test_bull_regime():
    detector = RegimeDetector()
    snapshot = make_snapshot(5.0, 6.0, 7.0)
    result = detector.detect(snapshot)
    assert result["regime"] == "Bull"
    assert result["probabilities"]["Bull"] > 0.5


def test_bear_regime():
    detector = RegimeDetector()
    snapshot = make_snapshot(-5.0, -6.0, -7.0)
    result = detector.detect(snapshot)
    assert result["regime"] == "Bear"
    assert result["probabilities"]["Bear"] > 0.5


def test_sideways_regime():
    detector = RegimeDetector()
    snapshot = make_snapshot(0.2, -0.3, 0.5)
    result = detector.detect(snapshot)
    assert result["regime"] == "Sideways"


def test_crisis_regime():
    detector = RegimeDetector()
    snapshot = make_snapshot(-25.0, -18.0, -22.0, anomalies=["BTC extreme 24h move: -25.0%"])
    result = detector.detect(snapshot)
    assert result["regime"] == "Crisis"
    assert result["probabilities"]["Crisis"] > 0.5


def test_probabilities_sum_to_one():
    detector = RegimeDetector()
    snapshot = make_snapshot(2.0, 1.5, 3.0)
    result = detector.detect(snapshot)
    total = sum(result["probabilities"].values())
    assert abs(total - 1.0) < 0.01
