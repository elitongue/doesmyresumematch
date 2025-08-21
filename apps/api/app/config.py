import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Settings:
    database_url: Optional[str]
    openai_api_key: Optional[str]
    embedding_provider: Optional[str]
    embedding_dim: Optional[int]
    lambda_decay: Optional[float]
    dev_mode: bool
    analytics_enabled: bool


def _parse_int(name: str, value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Invalid integer for {name}: {value}") from exc


def _parse_float(name: str, value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError as exc:  # pragma: no cover - defensive
        raise RuntimeError(f"Invalid float for {name}: {value}") from exc


def load_settings() -> Settings:
    env = os.environ
    dev_mode = env.get("DEV_MODE") == "1"
    required = [
        "DATABASE_URL",
        "OPENAI_API_KEY",
        "EMBEDDING_PROVIDER",
        "EMBEDDING_DIM",
        "LAMBDA_DECAY",
    ]
    missing = [name for name in required if env.get(name) is None]
    if missing and not dev_mode:
        raise RuntimeError(
            "Missing required environment variables: " + ", ".join(missing)
        )

    return Settings(
        database_url=env.get("DATABASE_URL"),
        openai_api_key=env.get("OPENAI_API_KEY"),
        embedding_provider=(env.get("EMBEDDING_PROVIDER") or "").lower() or None,
        embedding_dim=_parse_int("EMBEDDING_DIM", env.get("EMBEDDING_DIM")),
        lambda_decay=_parse_float("LAMBDA_DECAY", env.get("LAMBDA_DECAY")),
        dev_mode=dev_mode,
        analytics_enabled=env.get("ANALYTICS_ENABLED") == "1",
    )


settings = load_settings()
