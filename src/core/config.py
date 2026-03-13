from __future__ import annotations

import os
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    provider: str = "fake"
    default_channel: str = "cli"


@dataclass(frozen=True, slots=True)
class StorageConfig:
    backend: str = "memory"
    base_path: str = ".newbeebot/state"


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    api_key: str | None = None
    base_url: str = "https://api.openai.com/v1"
    model: str = "gpt-4.1-mini"


@dataclass(frozen=True, slots=True)
class AppConfig:
    runtime: RuntimeConfig = RuntimeConfig()
    provider: ProviderConfig = ProviderConfig()
    storage: StorageConfig = StorageConfig()


def load_config(path: Path | str | None = None) -> AppConfig:
    raw_data: Mapping[str, Any] = {}
    if path is not None:
        config_path = Path(path)
        if config_path.exists():
            with config_path.open("rb") as handle:
                raw_data = tomllib.load(handle)

    runtime = _section(raw_data, "runtime")
    provider = _section(raw_data, "provider")
    storage = _section(raw_data, "storage")

    return AppConfig(
        runtime=RuntimeConfig(
            provider=_env_or_value("NEWBEEBOT_RUNTIME_PROVIDER", runtime.get("provider", "fake")),
            default_channel=_env_or_value(
                "NEWBEEBOT_RUNTIME_DEFAULT_CHANNEL",
                runtime.get("default_channel", "cli"),
            ),
        ),
        provider=ProviderConfig(
            api_key=_env_or_optional("NEWBEEBOT_PROVIDER_API_KEY", provider.get("api_key")),
            base_url=_env_or_value(
                "NEWBEEBOT_PROVIDER_BASE_URL",
                provider.get("base_url", "https://api.openai.com/v1"),
            ),
            model=_env_or_value("NEWBEEBOT_PROVIDER_MODEL", provider.get("model", "gpt-4.1-mini")),
        ),
        storage=StorageConfig(
            backend=_env_or_value("NEWBEEBOT_STORAGE_BACKEND", storage.get("backend", "memory")),
            base_path=_env_or_value(
                "NEWBEEBOT_STORAGE_BASE_PATH",
                storage.get("base_path", ".newbeebot/state"),
            ),
        ),
    )


def _section(raw_data: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = raw_data.get(key, {})
    if isinstance(value, Mapping):
        return value
    return {}


def _env_or_value(env_name: str, default: Any) -> str:
    return os.environ.get(env_name, str(default))


def _env_or_optional(env_name: str, default: Any) -> str | None:
    if env_name in os.environ:
        return os.environ[env_name]
    if default is None:
        return None
    return str(default)
