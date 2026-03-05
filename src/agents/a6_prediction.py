"""A6 — Prediction Market Agent

Scans Polymarket for mispriced crypto-related prediction markets.
Looks for discrepancies between market odds and expected outcomes.
Places strategic bets when edge is detected.
"""
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

from src.agents.base import BaseAgent, TradeProposal

logger = logging.getLogger(__name__)


class A6PredictionMarketAgent(BaseAgent):
    """Agent specializing in crypto prediction markets on Polymarket."""
    
    AGENT_ID = "A6"
    ARCHETYPE = "prediction_market"
    
    # Prediction market configuration
    MIN_EDGE = 0.05  # 5% minimum edge to place bet
    MIN_LIQUIDITY = 10000  # $10k minimum liquidity
    MAX_BET_SIZE = 0.03  # 3% of portfolio per bet
    
    # Crypto-related market keywords
    CRYPTO_KEYWORDS = [
        "bitcoin", "btc", "ethereum", "eth", "crypto", "cryptocurrency",
        "defi", "nft", "blockchain", "web3", "solana", "sol",
        "price", "all-time high", "ath", "market cap"
    ]
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.cycle_count = 0
        self.active_bets: List[Dict] = []
        self.market_cache: Dict[str, Any] = {}
        self.last_scan_time = None
    
    async def propose(self, regime: Dict, snapshot: Dict, portfolio: Dict) -> List[TradeProposal]:
        """Generate prediction market bet proposals.
        
        Args:
            regime: Current market regime detection
            snapshot: Latest market data snapshot
            portfolio: Current portfolio state
            
        Returns:
            List of trade proposals for prediction markets
        """
        self.cycle_count += 1
        proposals = []
        
        try:
            # First cycle: observe only
            if self.cycle_count == 1:
                logger.info(f"[{self.AGENT_ID}] First cycle - observing markets only")
                return []
            
            # Get current market prices for context
            btc_price = snapshot.get("btc_price", 0)
            eth_price = snapshot.get("eth_price", 0)
            
            # Check for mispriced markets
            markets = await self._scan_prediction_markets(snapshot)
            
            for market in markets:
                edge = self._calculate_edge(market, snapshot, regime)
                
                if edge >= self.MIN_EDGE:
                    # Found mispriced market
                    proposal = self._create_bet_proposal(
                        market=market,
                        edge=edge,
                        portfolio=portfolio,
                        regime=regime
                    )
                    
                    if proposal:
                        proposals.append(proposal)
                        logger.info(
                            f"[{self.AGENT_ID}] Found edge: {market['title'][:50]}... "
                            f"Edge: {edge:.2%}, Bet: ${proposal.size}"
                        )
            
            return proposals
            
        except Exception as e:
            logger.error(f"[{self.AGENT_ID}] Error generating proposals: {e}", exc_info=True)
            return []
    
    async def _scan_prediction_markets(self, snapshot: Dict) -> List[Dict]:
        """Scan Polymarket for relevant crypto prediction markets.
        
        Args:
            snapshot: Latest market data
            
        Returns:
            List of relevant prediction markets
        """
        # Check if we need to refresh cache (every 5 minutes)
        now = datetime.now()
        if (self.last_scan_time is None or 
            (now - self.last_scan_time) > timedelta(minutes=5)):
            
            try:
                # Import here to avoid circular dependency
                from src.market.polymarket import PolymarketClient
                
                client = PolymarketClient()
                all_markets = await client.get_active_markets()
                
                # Filter for crypto-related markets
                crypto_markets = []
                for market in all_markets:
                    title_lower = market.get("title", "").lower()
                    description_lower = market.get("description", "").lower()
                    
                    is_crypto = any(
                        keyword in title_lower or keyword in description_lower
                        for keyword in self.CRYPTO_KEYWORDS
                    )
                    
                    # Check liquidity
                    liquidity = market.get("liquidity", 0)
                    
                    if is_crypto and liquidity >= self.MIN_LIQUIDITY:
                        crypto_markets.append(market)
                
                self.market_cache = {m["id"]: m for m in crypto_markets}
                self.last_scan_time = now
                
                logger.info(
                    f"[{self.AGENT_ID}] Scanned {len(all_markets)} markets, "
                    f"found {len(crypto_markets)} relevant crypto markets"
                )
                
            except Exception as e:
                logger.error(f"[{self.AGENT_ID}] Error scanning Polymarket: {e}")
                return []
        
        return list(self.market_cache.values())
    
    def _calculate_edge(self, market: Dict, snapshot: Dict, regime: Dict) -> float:
        """Calculate expected edge for a prediction market.
        
        Args:
            market: Prediction market data
            snapshot: Current market snapshot
            regime: Current regime
            
        Returns:
            Estimated edge (0.0 to 1.0)
        """
        try:
            # Get market odds
            yes_price = market.get("yes_price", 0.5)  # Probability of YES outcome
            no_price = market.get("no_price", 0.5)   # Probability of NO outcome
            
            # Get market details
            title = market.get("title", "").lower()
            end_date = market.get("end_date")
            
            # Simple heuristic-based edge calculation
            # In production, this would use sophisticated models
            
            # Example: "BTC to reach $100k by end of 2026"
            if "btc" in title or "bitcoin" in title:
                btc_price = snapshot.get("btc_price", 0)
                
                if "100k" in title and btc_price < 80000:
                    # Market might be underpricing this event
                    fair_prob = 0.60  # Our model's estimate
                    edge = abs(fair_prob - yes_price)
                    return edge if fair_prob > yes_price else 0.0
            
            # Example: "ETH to flip BTC in market cap"
            if "eth" in title and "flip" in title:
                # Very unlikely event
                fair_prob = 0.05
                edge = abs(fair_prob - yes_price)
                return edge if yes_price > fair_prob else 0.0
            
            # Regime-based adjustments
            regime_type = regime.get("type", "neutral")
            
            if regime_type == "bull":
                # In bull markets, positive crypto events more likely
                if "bullish" in title or "rise" in title or "up" in title:
                    return 0.03  # Small edge
            
            elif regime_type == "bear":
                # In bear markets, negative events more likely
                if "bearish" in title or "fall" in title or "down" in title:
                    return 0.03
            
            # No clear edge detected
            return 0.0
            
        except Exception as e:
            logger.error(f"[{self.AGENT_ID}] Error calculating edge: {e}")
            return 0.0
    
    def _create_bet_proposal(
        self,
        market: Dict,
        edge: float,
        portfolio: Dict,
        regime: Dict
    ) -> TradeProposal:
        """Create a bet proposal for a mispriced market.
        
        Args:
            market: Prediction market data
            edge: Calculated edge
            portfolio: Current portfolio
            regime: Current regime
            
        Returns:
            TradeProposal or None
        """
        try:
            portfolio_value = portfolio.get("total_value", 100000)
            
            # Position sizing based on Kelly Criterion (simplified)
            # kelly = edge / odds
            # Use fractional Kelly for safety
            yes_price = market.get("yes_price", 0.5)
            
            if yes_price > 0:
                kelly_fraction = edge / yes_price
                position_size = min(kelly_fraction * 0.25, self.MAX_BET_SIZE)  # 25% Kelly
            else:
                position_size = self.MAX_BET_SIZE
            
            bet_amount = portfolio_value * position_size
            
            # Minimum bet threshold
            if bet_amount < 100:
                return None
            
            # Create proposal
            return TradeProposal(
                agent_id=self.AGENT_ID,
                action="BET",
                symbol=f"POLY_{market['id']}",
                size=round(bet_amount, 2),
                rationale=(
                    f"Prediction market edge detected: {market['title'][:100]}. "
                    f"Edge: {edge:.2%}, Market odds: {yes_price:.2%}, "
                    f"Regime: {regime.get('type', 'neutral')}"
                ),
                confidence=min(0.5 + edge, 0.85),  # Confidence based on edge
                metadata={
                    "market_id": market["id"],
                    "market_title": market["title"],
                    "yes_price": yes_price,
                    "edge": edge,
                    "liquidity": market.get("liquidity", 0)
                }
            )
            
        except Exception as e:
            logger.error(f"[{self.AGENT_ID}] Error creating bet proposal: {e}")
            return None
    
    def _update_active_bets(self, executed_proposals: List[TradeProposal]):
        """Track active prediction market bets.
        
        Args:
            executed_proposals: List of executed trade proposals
        """
        for proposal in executed_proposals:
            if proposal.action == "BET":
                self.active_bets.append({
                    "market_id": proposal.metadata.get("market_id"),
                    "amount": proposal.size,
                    "entry_price": proposal.metadata.get("yes_price"),
                    "timestamp": datetime.now().isoformat(),
                    "status": "active"
                })
