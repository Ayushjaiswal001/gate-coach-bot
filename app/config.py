"""Typed settings. All env vars declared here — see .env.example."""

import hashlib
import os
import re
from typing import Any

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")
TELEGRAM_TOKEN = re.compile(r"^\d+:[A-Za-z0-9_-]{30,}$")


def _clean_string(value: str) -> str:
    """Remove characters that commonly sneak in through copied env values."""
    return CONTROL_CHARS.sub("", value.strip().lstrip("\ufeff"))


def _env_debug(name: str) -> dict[str, object]:
    raw = os.environ.get(name)
    if raw is None:
        return {"set": False}
    cleaned = _clean_string(raw)
    controls = [f"0x{ord(ch):02x}" for ch in raw if CONTROL_CHARS.match(ch)]
    return {
        "set": True,
        "raw_len": len(raw),
        "clean_len": len(cleaned),
        "changed_by_cleaning": raw != cleaned,
        "control_chars": controls,
        "starts_or_ends_with_space": raw != raw.strip(),
        "sha256_8": hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:8],
    }


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    telegram_bot_token: str = ""
    allowed_tg_user_ids: str = ""

    default_daily_hours: float = 4.5
    default_timezone: str = "Asia/Kolkata"
    reminder_hour: int = 7

    database_url: str = "sqlite+aiosqlite:///./data/gate.db"
    admin_token: str = ""

    @field_validator("*", mode="before")
    @classmethod
    def clean_strings(cls, v: Any) -> Any:
        if isinstance(v, str):
            return _clean_string(v)
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

    @model_validator(mode="after")
    def validate_settings(self) -> "Settings":
        if not self.telegram_bot_token:
            return self
        if CONTROL_CHARS.search(self.telegram_bot_token):
            raise ValueError("TELEGRAM_BOT_TOKEN contains non-printable control characters")
        if not TELEGRAM_TOKEN.match(self.telegram_bot_token):
            raise ValueError("TELEGRAM_BOT_TOKEN does not look like a valid Telegram bot token")
        return self

    @property
    def allowed_ids(self) -> set[int]:
        return {int(x) for x in self.allowed_tg_user_ids.split(",") if x.strip()}

    def safe_startup_summary(self) -> dict[str, object]:
        return {
            "telegram_bot_token": _env_debug("TELEGRAM_BOT_TOKEN"),
            "allowed_tg_user_ids": _env_debug("ALLOWED_TG_USER_IDS"),
            "database_url": _env_debug("DATABASE_URL"),
            "admin_token": _env_debug("ADMIN_TOKEN"),
            "reminder_hour": self.reminder_hour,
            "default_timezone": self.default_timezone,
            "allowed_user_count": len(self.allowed_ids),
            "render": bool(os.environ.get("RENDER")),
        }

    def require_bot_token(self) -> None:
        if not self.telegram_bot_token:
            raise ValueError("TELEGRAM_BOT_TOKEN is required")


settings = Settings()
