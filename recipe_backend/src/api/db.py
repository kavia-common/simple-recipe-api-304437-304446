import os
from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional

import psycopg2
import psycopg2.extras


def _get_database_url() -> str:
    """
    Returns the PostgreSQL DSN from environment.

    Canonical format (per recipe_database/db_connection.txt):
      postgresql://appuser:dbuser123@localhost:5000/myapp

    NOTE: This function intentionally does not read db_connection.txt at runtime.
    In production/deployment, the orchestrator should set DATABASE_URL in .env.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL environment variable is required. "
            "Set it to the canonical DSN format from recipe_database/db_connection.txt, "
            "e.g. postgresql://user:pass@host:port/dbname"
        )
    return database_url


@contextmanager
def get_connection() -> Iterator[psycopg2.extensions.connection]:
    """
    Context manager that yields a PostgreSQL connection.

    Uses RealDictCursor so rows come back as dicts.
    """
    conn = psycopg2.connect(_get_database_url())
    try:
        yield conn
    finally:
        conn.close()


def fetch_all(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """Execute a SELECT and return all rows as dicts."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]


def fetch_one(query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
    """Execute a SELECT and return a single row as a dict, or None."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None


def execute_returning_one(query: str, params: Optional[tuple] = None) -> Dict[str, Any]:
    """
    Execute INSERT/UPDATE/DELETE ... RETURNING and return the returned row as dict.

    Commits the transaction.
    """
    with get_connection() as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(query, params)
            row = cur.fetchone()
            if not row:
                raise RuntimeError("Query did not return a row; expected RETURNING clause.")
            conn.commit()
            return dict(row)
