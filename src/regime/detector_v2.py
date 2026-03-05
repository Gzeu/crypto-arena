"""
Regime Detector v2 — enhanced with:
  - Sentiment integration (SentimentEngine)
  - Whale move signals (large on-chain transfers via CoinGecko proxy)
  - Funding rate pressure
  - Volatility regime (calm / normal / volatile / explosive)
  - Composite scoring across 6 signal sources
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional

from loguru import logger


@dataclass
class RegimeSignal:
    source: str          # e.g. 'sentiment', 'price_action', 'volatility'
    value: float         # raw signal value
    weight: float        # contribution weight
    label: str           # human-readable label for this signal


@dataclass
class RegimeResult:
    regime: str                        # Bull | Bear | Neutral | Crisis
    confidence: float                  # 0.0 – 1.0
    volatility_regime: str             # Calm | Normal | Volatile | Explosive
    sentiment_score: float             # −1.0 to +1.0
    composite_score: float             # internal raw composite
    signals: List[RegimeSignal]        # breakdown
    ts: str

    def to_dict(self) -> Dict:
        return {
            "regime": self.regime,
            "confidence": self.confidence,
            "volatility_regime": self.volatility_regime,
            "sentiment_score": self.sentiment_score,
            "composite_score": self.composite_score,
            "signals": [
                {"source": s.source, "value": s.value,
                 "weight": s.weight, "label": s.label}
                for s in self.signals
            ],
            "ts": self.ts,
        }


class RegimeDetectorV2:
    """
    Composite regime detector.

    Signal sources and weights:
      1. price_action   0.30  (trend based on SMA, closes)
      2. sentiment      0.25  (SentimentEngine aggregate score)
      3. volatility     0.20  (rolling ATR / std dev)
      4. volume         0.10  (relative volume vs 20-period avg)
      5. funding        0.10  (funding rate proxy from SentimentEngine)
      6. whale          0.05  (large transaction heuristic)
    """

    WEIGHTS = {
        "price_action": 0.30,
        "sentiment":    0.25,
        "volatility":   0.20,
        "volume":       0.10,
        "funding":      0.10,
        "whale":        0.05,
    }

    # Volatility thresholds (annualised daily vol)
    VOL_THRESHOLDS = {
        "Calm":      0.015,
        "Normal":    0.035,
        "Volatile":  0.06,
        # above 0.06 → Explosive
    }

    def __init__(self, sentiment_engine=None):
        self._sentiment_engine = sentiment_engine
        self._price_history: List[float] = []
        self._volume_history: List[float] = []
        logger.info("🌊 RegimeDetectorV2 ready")

    def update_history(self, btc_price: float, volume: float):
        """Feed latest price/volume tick."""
        self._price_history.append(btc_price)
        self._volume_history.append(volume)
        if len(self._price_history) > 100:
            self._price_history.pop(0)
            self._volume_history.pop(0)

    async def detect(self, snapshot: Dict,
                      sentiment_data: Optional[Dict] = None) -> Dict:
        """
        Full regime detection.
        Returns dict compatible with v1 regime format + enriched fields.
        """
        prices = snapshot.get("prices", {})
        btc = float(prices.get("BTC", 0) or 0)
        volume = float(snapshot.get("btc_volume_24h", 0) or 0)

        if btc:
            self.update_history(btc, volume)

        signals = []

        # 1. Price action signal
        pa_signal = self._price_action_signal()
        signals.append(pa_signal)

        # 2. Sentiment signal
        sent_score = 0.0
        if sentiment_data:
            sent_score = sentiment_data.get("score", 0.0)
        elif self._sentiment_engine:
            try:
                sent = await self._sentiment_engine.get_sentiment()
                sent_score = sent.get("score", 0.0)
            except Exception:
                pass
        signals.append(RegimeSignal(
            source="sentiment",
            value=sent_score,
            weight=self.WEIGHTS["sentiment"],
            label=self._label_from_score(sent_score),
        ))

        # 3. Volatility signal
        vol_signal, vol_regime = self._volatility_signal()
        signals.append(vol_signal)

        # 4. Volume signal
        vol_sig = self._volume_signal()
        signals.append(vol_sig)

        # 5. Funding signal
        funding_score = 0.0
        if sentiment_data:
            funding_score = sentiment_data.get(
                "sources", {}).get("funding", {}).get("score", 0.0)
        signals.append(RegimeSignal(
            source="funding",
            value=funding_score,
            weight=self.WEIGHTS["funding"],
            label="Funding bullish" if funding_score > 0.1
                  else ("Funding bearish" if funding_score < -0.1 else "Funding neutral"),
        ))

        # 6. Whale heuristic
        whale_signal = self._whale_heuristic(snapshot)
        signals.append(whale_signal)

        # Composite score (-1 to +1)
        composite = sum(s.value * s.weight for s in signals)
        composite = max(-1.0, min(1.0, composite))

        # Map composite to regime + confidence
        regime, confidence = self._composite_to_regime(composite, vol_regime)

        result = RegimeResult(
            regime=regime,
            confidence=confidence,
            volatility_regime=vol_regime,
            sentiment_score=sent_score,
            composite_score=round(composite, 4),
            signals=signals,
            ts=datetime.now(timezone.utc).isoformat(),
        )

        logger.debug(
            "🌊 Regime v2: {} ({:.0%}) | Vol: {} | Sentiment: {:+.2f} | Composite: {:+.3f}",
            regime, confidence, vol_regime, sent_score, composite
        )
        return result.to_dict()

    # ------------------------------------------------------------------
    # Signal helpers
    # ------------------------------------------------------------------

    def _price_action_signal(self) -> RegimeSignal:
        hist = self._price_history
        if len(hist) < 20:
            return RegimeSignal(
                source="price_action", value=0.0,
                weight=self.WEIGHTS["price_action"], label="Insufficient data"
            )
        sma20 = sum(hist[-20:]) / 20
        sma50 = sum(hist[-50:]) / 50 if len(hist) >= 50 else sma20
        current = hist[-1]
        short_trend = (current - sma20) / sma20  # % above/below SMA20
        long_trend  = (sma20 - sma50)  / sma50   # SMA20 vs SMA50 cross
        raw = short_trend * 5 + long_trend * 3   # amplified signal
        raw = max(-1.0, min(1.0, raw))
        label = (
            "Strong uptrend" if raw > 0.4 else
            "Mild uptrend" if raw > 0.1 else
            "Downtrend" if raw < -0.1 else
            "Sideways"
        )
        return RegimeSignal(
            source="price_action", value=raw,
            weight=self.WEIGHTS["price_action"], label=label
        )

    def _volatility_signal(self):
        hist = self._price_history
        if len(hist) < 10:
            return (
                RegimeSignal(source="volatility", value=0.0,
                             weight=self.WEIGHTS["volatility"], label="Low vol"),
                "Normal"
            )
        returns = [(hist[i] - hist[i-1]) / hist[i-1] for i in range(1, len(hist))]
        daily_vol = (sum(r**2 for r in returns[-10:]) / 10) ** 0.5

        if daily_vol <= self.VOL_THRESHOLDS["Calm"]:
            vol_regime, val = "Calm", -0.3
        elif daily_vol <= self.VOL_THRESHOLDS["Normal"]:
            vol_regime, val = "Normal", 0.0
        elif daily_vol <= self.VOL_THRESHOLDS["Volatile"]:
            vol_regime, val = "Volatile", 0.4
        else:
            vol_regime, val = "Explosive", 1.0

        return (
            RegimeSignal(source="volatility", value=val,
                         weight=self.WEIGHTS["volatility"],
                         label=f"{vol_regime} (daily_vol={daily_vol:.3%})"),
            vol_regime
        )

    def _volume_signal(self) -> RegimeSignal:
        hist = self._volume_history
        if len(hist) < 5:
            return RegimeSignal(source="volume", value=0.0,
                                weight=self.WEIGHTS["volume"], label="No volume data")
        avg20 = sum(hist[-20:]) / len(hist[-20:])
        current = hist[-1]
        ratio = (current / avg20 - 1.0) if avg20 else 0.0
        ratio = max(-1.0, min(1.0, ratio))
        label = "High volume" if ratio > 0.2 else ("Low volume" if ratio < -0.2 else "Normal volume")
        return RegimeSignal(source="volume", value=ratio,
                            weight=self.WEIGHTS["volume"], label=label)

    def _whale_heuristic(self, snapshot: Dict) -> RegimeSignal:
        """
        Simple whale heuristic: large exchange inflows (negative for price)
        vs large outflows (positive).
        Uses exchange_flow field from snapshot if available.
        """
        flow = snapshot.get("exchange_flow_btc", 0) or 0
        # Positive = outflow (bullish), negative = inflow (sell pressure)
        score = max(-1.0, min(1.0, -flow / 10_000)) if flow else 0.0
        label = (
            "Whale outflow (bullish)" if score > 0.2 else
            "Whale inflow (bearish)" if score < -0.2 else
            "No whale signal"
        )
        return RegimeSignal(source="whale", value=score,
                            weight=self.WEIGHTS["whale"], label=label)

    @staticmethod
    def _composite_to_regime(composite: float,
                              vol_regime: str) -> tuple:
        if vol_regime == "Explosive" and composite < -0.1:
            return "Crisis", 0.90
        if composite >= 0.35:
            conf = min(0.95, 0.65 + composite)
            return "Bull", round(conf, 2)
        if composite <= -0.25:
            conf = min(0.95, 0.60 + abs(composite))
            return "Bear", round(conf, 2)
        conf = 0.55 + (1 - abs(composite)) * 0.2
        return "Neutral", round(conf, 2)

    @staticmethod
    def _label_from_score(score: float) -> str:
        if score <= -0.6: return "Extreme Fear"
        if score <= -0.2: return "Fear"
        if score <=  0.2: return "Neutral"
        if score <=  0.6: return "Greed"
        return "Extreme Greed"
