#!/usr/bin/env python3
# agents/agent_ghl/scripts/ghl_rate_guard.py
# Forge Stack Engine — GoHighLevel API rate limiter
# Version: 1.0
#
# Enforces GHL API v2 rate limit: 100 requests per 10 seconds per location.
# State is persisted in SQLite (forge.db) — NOT in memory.
# This ensures rate limiting survives process restarts and is
# visible across all agents.
#
# Called by agent_ghl before every API operation.
#
# Usage (as library):
#   from agents.agent_ghl.scripts.ghl_rate_guard import RateGuard
#   guard = RateGuard()
#   guard.acquire()           # blocks until a slot is available
#   guard.acquire(timeout=30) # raises TimeoutError if no slot in 30s
#
# Usage (as CLI for testing):
#   python ghl_rate_guard.py --status
#   python ghl_rate_guard.py --reset
#
# Rate limit reference:
#   https://highlevel.stoplight.io/docs/integrations/a3a25fd547d78-rate-limiting
#   100 requests / 10 seconds / location

import argparse
import os
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path


# ── Constants ─────────────────────────────────────────────────────────────────

RATE_LIMIT      = 100     # max requests per window
WINDOW_SECONDS  = 10      # window size in seconds
POLL_INTERVAL   = 0.25    # seconds between retry checks
DEFAULT_TIMEOUT = 60      # seconds before giving up on acquire

# SQLite table for rate guard state
TABLE_NAME = "ghl_rate_guard"

# Default DB path — reads from SQLITE_PATH env var or falls back to project default
def _get_db_path() -> str:
    default = str(Path(__file__).parent.parent.parent.parent / "db" / "forge.db")
    return os.getenv("SQLITE_PATH", default)


# ── Database ──────────────────────────────────────────────────────────────────

def _connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def _ensure_table(conn: sqlite3.Connection) -> None:
    """Creates ghl_rate_guard table if it doesn't exist."""
    conn.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            ts          REAL NOT NULL,
            location_id TEXT NOT NULL DEFAULT 'default'
        )
    """)
    conn.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_ghl_rate_ts
        ON {TABLE_NAME}(ts, location_id)
    """)
    conn.commit()


def _now_ts() -> float:
    """Returns current UTC timestamp as float."""
    return datetime.now(timezone.utc).timestamp()


def _count_in_window(conn: sqlite3.Connection,
                     location_id: str,
                     window_start: float) -> int:
    """Returns number of requests in the current window."""
    row = conn.execute(
        f"SELECT COUNT(*) as n FROM {TABLE_NAME} "
        f"WHERE ts >= ? AND location_id = ?",
        (window_start, location_id)
    ).fetchone()
    return row["n"] if row else 0


def _record_request(conn: sqlite3.Connection,
                    location_id: str,
                    ts: float) -> None:
    """Records a new request timestamp."""
    conn.execute(
        f"INSERT INTO {TABLE_NAME} (ts, location_id) VALUES (?, ?)",
        (ts, location_id)
    )
    conn.commit()


def _cleanup_old_records(conn: sqlite3.Connection,
                          location_id: str,
                          cutoff: float) -> int:
    """Deletes records older than cutoff. Returns number deleted."""
    cursor = conn.execute(
        f"DELETE FROM {TABLE_NAME} WHERE ts < ? AND location_id = ?",
        (cutoff, location_id)
    )
    conn.commit()
    return cursor.rowcount


# ── RateGuard class ───────────────────────────────────────────────────────────

class RateGuard:
    """
    SQLite-backed rate limiter for GHL API v2.

    Thread-safe via SQLite WAL mode.
    Survives process restarts — state is in DB, not memory.

    Usage:
        guard = RateGuard()
        guard.acquire()  # blocks until a request slot is available

    With custom location:
        guard = RateGuard(location_id="loc_abc123")
        guard.acquire()
    """

    def __init__(self,
                 location_id: str = "default",
                 db_path: str | None = None,
                 rate_limit: int = RATE_LIMIT,
                 window_seconds: int = WINDOW_SECONDS):
        self.location_id    = location_id
        self.db_path        = db_path or _get_db_path()
        self.rate_limit     = rate_limit
        self.window_seconds = window_seconds
        self._init_db()

    def _init_db(self) -> None:
        """Ensures DB and table exist."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with _connect(self.db_path) as conn:
            _ensure_table(conn)

    def status(self) -> dict:
        """
        Returns current rate guard status without consuming a slot.

        Returns:
            {
                "requests_in_window": int,
                "slots_available":    int,
                "window_start":       float,
                "window_end":         float,
                "rate_limit":         int,
                "window_seconds":     int,
            }
        """
        now          = _now_ts()
        window_start = now - self.window_seconds
        with _connect(self.db_path) as conn:
            _ensure_table(conn)
            count = _count_in_window(conn, self.location_id, window_start)
        return {
            "requests_in_window": count,
            "slots_available":    max(0, self.rate_limit - count),
            "window_start":       window_start,
            "window_end":         now,
            "rate_limit":         self.rate_limit,
            "window_seconds":     self.window_seconds,
            "location_id":        self.location_id,
        }

    def acquire(self, timeout: float = DEFAULT_TIMEOUT) -> float:
        """
        Blocks until a rate limit slot is available, then records the request.

        Args:
            timeout: seconds to wait before raising TimeoutError.
                     Set to 0 for non-blocking (raises immediately if no slot).

        Returns:
            timestamp when slot was acquired.

        Raises:
            TimeoutError: if no slot available within timeout seconds.
        """
        deadline = _now_ts() + timeout

        while True:
            now          = _now_ts()
            window_start = now - self.window_seconds

            with _connect(self.db_path) as conn:
                _ensure_table(conn)

                # Clean up records outside the window (housekeeping)
                _cleanup_old_records(conn, self.location_id,
                                     now - self.window_seconds * 2)

                count = _count_in_window(conn, self.location_id, window_start)

                if count < self.rate_limit:
                    # Slot available — record and return
                    _record_request(conn, self.location_id, now)
                    return now

            # No slot available
            if timeout == 0 or _now_ts() >= deadline:
                status = self.status()
                raise TimeoutError(
                    f"GHL rate limit reached: {status['requests_in_window']}/"
                    f"{self.rate_limit} requests in last {self.window_seconds}s. "
                    f"Timeout after {timeout}s."
                )

            # Wait and retry
            time.sleep(POLL_INTERVAL)

    def reset(self, confirm: bool = False) -> int:
        """
        Clears all rate guard records for this location.
        Requires confirm=True to prevent accidental resets.

        Returns number of records deleted.
        """
        if not confirm:
            raise ValueError("reset() requires confirm=True")
        with _connect(self.db_path) as conn:
            _ensure_table(conn)
            cursor = conn.execute(
                f"DELETE FROM {TABLE_NAME} WHERE location_id = ?",
                (self.location_id,)
            )
            conn.commit()
            return cursor.rowcount


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Forge Stack Engine — GHL API rate guard"
    )
    parser.add_argument(
        "--status", action="store_true",
        help="Show current rate guard status"
    )
    parser.add_argument(
        "--reset", action="store_true",
        help="Reset rate guard records (use with --confirm)"
    )
    parser.add_argument(
        "--confirm", action="store_true",
        help="Required for --reset"
    )
    parser.add_argument(
        "--location_id", default="default",
        help="GHL Location ID (default: 'default')"
    )
    parser.add_argument(
        "--db_path", default=None,
        help="Path to SQLite DB (default: reads SQLITE_PATH env var)"
    )
    args = parser.parse_args()

    guard = RateGuard(
        location_id=args.location_id,
        db_path=args.db_path,
    )

    if args.status:
        s = guard.status()
        print(f"\n[ GHL Rate Guard Status ]\n")
        print(f"  Location:           {s['location_id']}")
        print(f"  Requests in window: {s['requests_in_window']}/{s['rate_limit']}")
        print(f"  Slots available:    {s['slots_available']}")
        print(f"  Window:             {s['window_seconds']}s")
        print()
        sys.exit(0)

    if args.reset:
        if not args.confirm:
            print("ERROR: --reset requires --confirm", file=sys.stderr)
            sys.exit(1)
        deleted = guard.reset(confirm=True)
        print(f"Reset complete. Deleted {deleted} records.")
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()
