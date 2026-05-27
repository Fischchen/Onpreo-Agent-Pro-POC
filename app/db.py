"""Database engine, session factory, and SQLite tuning.

DATABASE_URL is resolved independently of the full Settings model so that Alembic
migrations can run without requiring MCP_BEARER_TOKEN to be set.
"""
from __future__ import annotations

import os
from contextlib import contextmanager

from sqlalchemy import event
from sqlmodel import Session, create_engine

_DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "onpreo_poc.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{_DEFAULT_DB_PATH}")

# check_same_thread=False: the MCP server serves requests across threads.
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


@event.listens_for(engine, "connect")
def _enable_wal(dbapi_connection, _connection_record):
    """WAL mode lets Streamlit and the MCP server read/write the same file
    concurrently without tripping 'database is locked'."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.close()


@contextmanager
def get_session():
    with Session(engine) as session:
        yield session
