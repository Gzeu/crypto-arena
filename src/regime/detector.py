"""
Regime Detector Agent
======================
Classifies the current market regime into one of:
  Bull | Bear | Sideways | Crisis
with probability estimates.
"""

from typing import Dict
from loguru import logger


REGIMES = ["Bull", "Bear", "Sideways", "Crisis"]


class RegimeDetector:
    """
    Heuristic regime detector.
    Uses 24h price changes, volume trends, and anomaly flags.
    Future: replace with Markov Regime Switching (HMM).
    """

    def detect(self, snapshot: dict) -> dict:
        prices_change = snapshot.get("price_changes_24h", {})
        anomalies = snapshot.get("anomalies", [])

        btc_chg = prices_change.get("BTC", 0) or 0
        eth_chg = prices_change.get("ETH", 0) or 0
        sol_chg = prices_change.get("SOL", 0) or 0

        avg_chg = (btc_chg + eth_chg + sol_chg) / 3
        max_abs = max(abs(btc_chg), abs(eth_chg), abs(sol_chg))
        has_extreme = max_abs > 15 or "DATA_FETCH_FAILED" in anomalies

        probs = self._compute_probs(avg_chg, max_abs, has_extreme)
        regime = max(probs, key=probs.get)

        result = {
            "regime": regime,
            "probabilities": probs,
            "avg_24h_change": round(avg_chg, 2),
            "anomalies_detected": anomalies,
            "explanation": self._explain(regime, avg_chg, max_abs, anomalies),
        }
        logger.info("🎯 Regime: {} | probs: {}", regime, probs)
        return result

    def _compute_probs(self, avg_chg: float, max_abs: float, has_extreme: bool) -> Dict[str, float]:
        if has_extreme and max_abs > 20:
            return {"Bull": 0.05, "Bear": 0.20, "Sideways": 0.10, "Crisis": 0.65}
        elif has_extreme:
            return {"Bull": 0.10, "Bear": 0.45, "Sideways": 0.25, "Crisis": 0.20}
        elif avg_chg > 3:
            return {"Bull": 0.65, "Bear": 0.10, "Sideways": 0.20, "Crisis": 0.05}
        elif avg_chg > 1:
            return {"Bull": 0.45, "Bear": 0.20, "Sideways": 0.30, "Crisis": 0.05}
        elif avg_chg > -1:
            return {"Bull": 0.20, "Bear": 0.20, "Sideways": 0.55, "Crisis": 0.05}
        elif avg_chg > -3:
            return {"Bull": 0.10, "Bear": 0.50, "Sideways": 0.35, "Crisis": 0.05}
        else:
            return {"Bull": 0.05, "Bear": 0.65, "Sideways": 0.20, "Crisis": 0.10}

    def _explain(self, regime: str, avg_chg: float, max_abs: float, anomalies: list) -> str:
        base = f"Avg 24h change across BTC/ETH/SOL: {avg_chg:+.2f}%. Max individual move: {max_abs:.1f}%."
        if anomalies:
            base += f" Anomalies detected: {', '.join(anomalies)}."
        explanations = {
            "Bull": " Positive momentum across majors suggests trending upward conditions.",
            "Bear": " Negative pressure across majors — risk-off stance warranted.",
            "Sideways": " Mixed signals with no clear directional bias — range-trading conditions.",
            "Crisis": " Extreme moves detected — survival mode activated, max de-risk.",
        }
        return base + explanations.get(regime, "")
