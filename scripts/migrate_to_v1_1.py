"""
Migration script: upgrades the CryptoArena database to v1.1 schema.
Safe to run multiple times (idempotent — CREATE IF NOT EXISTS).

Usage:
  python scripts/migrate_to_v1_1.py
"""

import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("data/arena.db")

MIGRATIONS = [
    # Agent persistent memory
    """
    CREATE TABLE IF NOT EXISTS agent_memory (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id     TEXT    NOT NULL,
        memory_type  TEXT    NOT NULL,
        content      TEXT    NOT NULL,
        metadata     TEXT    DEFAULT '{}',
        importance   REAL    DEFAULT 0.5,
        created_at   TEXT    NOT NULL,
        accessed_cnt INTEGER DEFAULT 0,
        last_accessed TEXT
    );
    """,
    "CREATE INDEX IF NOT EXISTS idx_mem_agent ON agent_memory(agent_id);",
    "CREATE INDEX IF NOT EXISTS idx_mem_type  ON agent_memory(memory_type);",

    # On-chain leaderboard cache
    """
    CREATE TABLE IF NOT EXISTS onchain_leaderboard (
        agent_id       TEXT PRIMARY KEY,
        wallet_address TEXT,
        nft_token_id   INTEGER,
        karma_balance  REAL    DEFAULT 0,
        total_pnl      REAL    DEFAULT 0,
        win_rate       REAL    DEFAULT 0,
        rank           INTEGER,
        last_sync      TEXT,
        tx_hash        TEXT
    );
    """,

    # Quest definitions
    """
    CREATE TABLE IF NOT EXISTS quests (
        quest_id     TEXT PRIMARY KEY,
        name         TEXT NOT NULL,
        description  TEXT,
        quest_type   TEXT NOT NULL,
        requirements TEXT DEFAULT '{}',
        rewards      TEXT DEFAULT '{}',
        chain        TEXT DEFAULT 'multiversx',
        active       INTEGER DEFAULT 1,
        created_at   TEXT NOT NULL
    );
    """,

    # Per-agent quest progress
    """
    CREATE TABLE IF NOT EXISTS quest_progress (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id      TEXT NOT NULL,
        quest_id      TEXT NOT NULL,
        status        TEXT DEFAULT 'active',
        started_at    TEXT NOT NULL,
        completed_at  TEXT,
        nft_tx_hash   TEXT,
        progress_pct  REAL DEFAULT 0,
        metadata      TEXT DEFAULT '{}',
        UNIQUE(agent_id, quest_id)
    );
    """,

    # Social post log
    """
    CREATE TABLE IF NOT EXISTS social_posts (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        platform    TEXT NOT NULL,
        post_type   TEXT NOT NULL,
        content     TEXT NOT NULL,
        media_url   TEXT,
        posted_at   TEXT NOT NULL,
        post_id     TEXT,
        engagement  TEXT DEFAULT '{}'
    );
    """,

    # Tournament records
    """
    CREATE TABLE IF NOT EXISTS tournaments (
        tournament_id TEXT PRIMARY KEY,
        week_number   INTEGER NOT NULL,
        name          TEXT NOT NULL,
        start_time    TEXT NOT NULL,
        end_time      TEXT NOT NULL,
        entry_karma   INTEGER DEFAULT 500,
        status        TEXT    DEFAULT 'registration',
        karma_pot     INTEGER DEFAULT 0,
        winner_id     TEXT,
        winner_karma  INTEGER DEFAULT 0,
        created_at    TEXT NOT NULL
    );
    """,

    # Tournament entries
    """
    CREATE TABLE IF NOT EXISTS tournament_entries (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        tournament_id   TEXT NOT NULL,
        agent_id        TEXT NOT NULL,
        entry_karma     INTEGER DEFAULT 500,
        registered_at   TEXT NOT NULL,
        final_pnl_pct   REAL,
        final_rank      INTEGER,
        karma_won       INTEGER DEFAULT 0,
        UNIQUE(tournament_id, agent_id)
    );
    """,

    # Schema version tracking
    """
    CREATE TABLE IF NOT EXISTS schema_version (
        version    TEXT PRIMARY KEY,
        applied_at TEXT NOT NULL
    );
    """,
]


def run_migration():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    print(f"📦 Migrating database: {DB_PATH}")

    for i, sql in enumerate(MIGRATIONS, 1):
        try:
            cur.executescript(sql)
            print(f"  ✅ Step {i:02d} OK")
        except sqlite3.Error as exc:
            print(f"  ❌ Step {i:02d} FAILED: {exc}")
            con.rollback()
            sys.exit(1)

    cur.execute(
        "INSERT OR REPLACE INTO schema_version VALUES (?, ?)",
        ("1.1.0", datetime.now(timezone.utc).isoformat()),
    )
    con.commit()
    con.close()

    print("\n🎉 Migration to v1.1 complete!")
    print("New tables: agent_memory, onchain_leaderboard, quests,")
    print("            quest_progress, social_posts, tournaments, tournament_entries")


if __name__ == "__main__":
    run_migration()
