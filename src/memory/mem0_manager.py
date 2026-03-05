"""
Mem0 Manager — Persistent cross-run agent memory.
Each agent gets its own vector store + structured memory timeline.
"""

import asyncio
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from loguru import logger

try:
    from mem0 import Memory as Mem0Memory
    MEM0_AVAILABLE = True
except ImportError:
    MEM0_AVAILABLE = False
    logger.warning("mem0ai not installed — using fallback in-memory store")

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    logger.warning("chromadb not installed — vector search disabled")


class AgentMemoryManager:
    """
    Persistent memory for a single agent.
    Stores lessons, rivalries, market patterns, and strategy evolutions.
    Falls back gracefully if Mem0 / ChromaDB are not installed.
    """

    def __init__(self, agent_id: str, config: Optional[Dict] = None):
        self.agent_id = agent_id
        self.config = config or {}
        self._fallback: List[Dict] = []

        if MEM0_AVAILABLE:
            self._mem0 = Mem0Memory()
        else:
            self._mem0 = None

        if CHROMA_AVAILABLE:
            self._chroma = chromadb.Client()
            self._collection = self._chroma.get_or_create_collection(
                name=f"arena_{agent_id}"
            )
        else:
            self._chroma = None
            self._collection = None

        logger.debug("🧠 Memory initialised for agent {}", agent_id)

    # ------------------------------------------------------------------
    # Core write
    # ------------------------------------------------------------------

    async def store(self, memory_type: str, content: str,
                    metadata: Optional[Dict] = None,
                    importance: float = 0.5) -> str:
        """
        Persist a memory entry.
        memory_type: 'lesson' | 'market_pattern' | 'rivalry' | 'strategy'
        importance : 0.0 – 1.0  (higher = recalled first)
        """
        entry = {
            "agent_id": self.agent_id,
            "type": memory_type,
            "content": content,
            "importance": importance,
            "metadata": metadata or {},
            "ts": datetime.now(timezone.utc).isoformat(),
        }

        mem_id = f"{self.agent_id}_{memory_type}_{len(self._fallback)}"

        if self._mem0:
            result = self._mem0.add(
                messages=[{"role": "assistant", "content": content}],
                user_id=self.agent_id,
                metadata=entry,
            )
            mem_id = result.get("id", mem_id)

        if self._collection:
            self._collection.add(
                documents=[content],
                metadatas=[{"type": memory_type, "importance": importance,
                             "agent_id": self.agent_id}],
                ids=[mem_id],
            )

        self._fallback.append({"id": mem_id, **entry})
        logger.debug("💾 [{}] stored {} memory: {:.80s}", self.agent_id, memory_type, content)
        return mem_id

    # ------------------------------------------------------------------
    # Core read
    # ------------------------------------------------------------------

    async def recall(self, query: str, memory_type: Optional[str] = None,
                     limit: int = 5) -> List[Dict]:
        """Retrieve relevant memories via vector similarity (or fallback FIFO)."""

        if self._collection:
            where = {"type": memory_type} if memory_type else None
            results = self._collection.query(
                query_texts=[query],
                n_results=min(limit, max(1, self._collection.count())),
                where=where,
            )
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            return [{"content": d, **m} for d, m in zip(docs, metas)]

        # Fallback: return most recent entries
        filtered = [m for m in self._fallback
                    if not memory_type or m["type"] == memory_type]
        return sorted(filtered, key=lambda x: x["importance"], reverse=True)[:limit]

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    async def reflect_on_trade(self, trade: Dict) -> str:
        """Auto-generate and store a post-trade lesson."""
        pnl_pct = trade.get("pnl_pct", 0)
        symbol = trade.get("symbol", "?")
        strategy = trade.get("strategy", "?")
        regime = trade.get("regime", "?")

        if pnl_pct >= 0:
            content = (f"WIN +{pnl_pct:.2f}% on {symbol} using {strategy} "
                       f"during {regime}. Key: {trade.get('win_reason', 'N/A')}")
            importance = min(1.0, pnl_pct / 10)
        else:
            content = (f"LOSS {pnl_pct:.2f}% on {symbol} using {strategy} "
                       f"during {regime}. Lesson: {trade.get('loss_reason', 'N/A')}")
            importance = min(1.0, abs(pnl_pct) / 5)

        return await self.store("lesson", content, metadata=trade, importance=importance)

    async def record_rivalry(self, rival_agent: str, event: str) -> str:
        content = f"Rivalry vs {rival_agent}: {event} @ {datetime.now(timezone.utc).date()}"
        return await self.store("rivalry", content, importance=0.7)

    async def record_market_pattern(self, pattern: str, conditions: Dict) -> str:
        content = f"Pattern detected: {pattern} | Conditions: {json.dumps(conditions)}"
        return await self.store("market_pattern", content,
                                metadata=conditions, importance=0.6)

    def summary(self) -> Dict:
        """Return a quick stats summary for dashboards."""
        types: Dict[str, int] = {}
        for m in self._fallback:
            types[m["type"]] = types.get(m["type"], 0) + 1
        return {"agent_id": self.agent_id, "total_memories": len(self._fallback),
                "by_type": types}
