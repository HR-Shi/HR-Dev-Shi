"""Centralized configuration for the backend service.

All deployment-critical settings live here so they can be modified in **one place**.
Values are read from environment variables (recommended for production) and fall back
to reasonable defaults – the same defaults provided in the shared .env examples.

Usage
-----
>>> from config import settings
>>> print(settings.SUPABASE_URL)

Because this module executes at import time and sets `os.environ.setdefault`,
legacy code that still calls `os.getenv` will continue to work, even if it
hasn't been refactored to import `settings` directly.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pydantic import BaseSettings, Field

# ---------------------------------------------------------------------------
# Load .env file (if present)
# ---------------------------------------------------------------------------
BACKEND_DIR = Path(__file__).resolve().parent
load_dotenv(dotenv_path=BACKEND_DIR / ".env", override=False)


class Settings(BaseSettings):
    """Application settings with environment-variable overrides."""

    # General ---------------------------------------------------------------
    ENVIRONMENT: str = Field("development", description="Environment name e.g. development / production")
    SECRET_KEY: str = Field("uEHzXpsFzB-fFA4YDjLBf09W9QHVD__jby8W42eI9UI", description="FastAPI/JWT secret key")
    SQL_DEBUG: bool = Field(False, description="If True SQLAlchemy will echo SQL")

    # Frontend / Backend URLs ---------------------------------------------
    FRONTEND_URL: str = Field("https://hr-dev-shi.vercel.app", description="Allowed CORS origin for frontend")
    BACKEND_URL: str = Field("https://hr-dev-shi.onrender.com", description="Public URL of the backend when deployed")

    # Supabase -------------------------------------------------------------
    SUPABASE_URL: str = "https://udaulvygaczcsrgybdqw.supabase.co"
    SUPABASE_ANON_KEY: str = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkYXVsdnlnYWN6Y3NyZ3liZHF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDk4MzMyOTMsImV4cCI6MjA2NTQwOTI5M30."
        "a9_SJERhQL_UAMWmvSrBdrZbDgFnPHaRpLWoOD-P33o"
    )
    SUPABASE_SERVICE_ROLE_KEY: str = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkYXVsdnlnYWN6Y3NyZ3liZHF3Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0OTgzMzI5MywiZXhwIjoyMDY1NDA5MjkzfQ."
        "7mRyHdf6WSa7XGO6pxRU0gsJiMSvWXUfQyUI7xnhAfw"
    )
    SUPABASE_DATABASE_URL: str = (
        "postgresql://postgres.udaulvygaczcsrgybdqw:6wjSo5aCUjkCLMHZ@aws-0-ap-south-1.pooler.supabase.com:6543/postgres"
    )

    # Optional – alternative DB URL for tools expecting DATABASE_URL
    DATABASE_URL: str | None = None

    # Third-party APIs ------------------------------------------------------
    CEREBRAS_API_KEY: str | None = Field(
        "csk-yfykk3992ntf239vynnktnyftt5ppnyp4pcrrp3cdcr6rcpd", 
        description="API key for Cerebras inference or similar service"
    )

    class Config:
        env_file: str | Path = ".env"  # secondary fallback (project root)
        case_sensitive = False
        # For security, don't show secrets in repr()
        secrets_dir = None

    # ---------------------------------------------------------------------
    # Helpers / derived properties
    # ---------------------------------------------------------------------

    @property
    def sqlalchemy_database_uri(self) -> str:
        """Return the database URI that SQLAlchemy should use."""
        return self.DATABASE_URL or self.SUPABASE_DATABASE_URL


# Instantiate settings ------------------------------------------------------
settings = Settings()

# ---------------------------------------------------------------------------
# Ensure downstream `os.getenv` calls still work by setting defaults.
# This allows gradual refactor of legacy code without breaking anything.
# ---------------------------------------------------------------------------
_defaults: dict[str, Any] = {
    "ENVIRONMENT": settings.ENVIRONMENT,
    "SECRET_KEY": settings.SECRET_KEY,
    "SQL_DEBUG": str(settings.SQL_DEBUG).lower(),
    "FRONTEND_URL": settings.FRONTEND_URL,
    "BACKEND_URL": settings.BACKEND_URL,
    "SUPABASE_URL": settings.SUPABASE_URL,
    "SUPABASE_ANON_KEY": settings.SUPABASE_ANON_KEY,
    "SUPABASE_SERVICE_ROLE_KEY": settings.SUPABASE_SERVICE_ROLE_KEY,
    "SUPABASE_DATABASE_URL": settings.SUPABASE_DATABASE_URL,
    "DATABASE_URL": settings.DATABASE_URL or "",
    "CEREBRAS_API_KEY": settings.CEREBRAS_API_KEY or "",
}

for _key, _val in _defaults.items():
    os.environ.setdefault(_key, str(_val)) 