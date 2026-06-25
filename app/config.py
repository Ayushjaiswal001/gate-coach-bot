"""Typed settings. All env vars declared here — see .env.example."""

import re

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_bot_token: str = ""
    allowed_tg_user_ids: str = ""

    default_daily_hours: float = 4.5
    default_timezone: str = "Asia/Kolkata"
    reminder_hour: int = 7

    database_url: str = "sqlite+aiosqlite:///./data/gate.db"
    admin_token: str = ""

    @field_validator("telegram_bot_token", "allowed_tg_user_ids", "database_url", mode="before")
    @classmethod
    def clean_strings(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().replace("\r", "").replace("\n", "")
        return v

    @field_validator("database_url")
    @classmethod
    def normalize_db_url(cls, v: str) -> str:
        """Adapt a raw Neon/Heroku Postgres URL for SQLAlchemy + asyncpg."""
        if v.startswith("postgres://"):
            v = "postgresql://" + v[len("postgres://") :]
        if v.startswith("postgresql://"):
            v = "postgresql+asyncpg://" + v[len("postgresql://") :]
        if v.startswith("postgresql+asyncpg://"):
            v = v.replace("sslmode=", "ssl=")
            v = re.sub(r"channel_binding=[^&]*&?", "", v)
            v = v.replace("?&", "?").rstrip("?&")
        return v

    @property
    def allowed_ids(self) -> set[int]:
        return {int(x) for x in self.allowed_tg_user_ids.split(",") if x.strip()}


settings = Settings()
