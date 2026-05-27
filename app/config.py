"""Typed application settings, loaded from environment / .env via pydantic-settings."""
from __future__ import annotations

import os

from pydantic_settings import BaseSettings, SettingsConfigDict

# Absolute path so the MCP server and Streamlit (which may run from a different
# working directory) always point at the same SQLite file.
_DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "onpreo_poc.db")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Required: a missing token raises ValidationError at startup (fail closed).
    mcp_bearer_token: str

    # SQLite by default; overridable via DATABASE_URL.
    database_url: str = f"sqlite:///{_DEFAULT_DB_PATH}"


settings = Settings()
