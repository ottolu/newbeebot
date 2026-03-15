from pathlib import Path

from pytest import MonkeyPatch

from core.config import load_config


def test_load_config_applies_documented_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / "newbeebot.toml"
    config_path.write_text("[runtime]\nprovider = 'fake'\n", encoding="utf-8")

    config = load_config(config_path)

    assert config.runtime.provider == "fake"
    assert config.runtime.default_channel == "cli"
    assert config.provider.model == "gpt-4.1-mini"
    assert config.provider.base_url == "https://api.openai.com/v1"
    assert config.provider.api_key is None
    assert config.storage.backend == "memory"
    assert config.storage.base_path == ".newbeebot/state"


def test_load_config_applies_environment_overrides(
    tmp_path: Path,
    monkeypatch: MonkeyPatch,
) -> None:
    config_path = tmp_path / "newbeebot.toml"
    config_path.write_text(
        (
            "[runtime]\n"
            "provider = 'openai'\n"
            "[provider]\n"
            "model = 'gpt-4.1'\n"
            "[storage]\n"
            "base_path = './local-state'\n"
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("NEWBEEBOT_RUNTIME_PROVIDER", "env-provider")
    monkeypatch.setenv("NEWBEEBOT_PROVIDER_MODEL", "gpt-4.1-mini")
    monkeypatch.setenv("NEWBEEBOT_PROVIDER_API_KEY", "sk-test")
    monkeypatch.setenv("NEWBEEBOT_STORAGE_BASE_PATH", "/tmp/newbeebot-env-state")

    config = load_config(config_path)

    assert config.runtime.provider == "env-provider"
    assert config.provider.model == "gpt-4.1-mini"
    assert config.provider.api_key == "sk-test"
    assert config.storage.base_path == "/tmp/newbeebot-env-state"


def test_load_config_supports_policy_section(tmp_path: Path) -> None:
    config_path = tmp_path / "newbeebot.toml"
    config_path.write_text(
        (
            "[policy]\n"
            "allowed_tools = ['echo', 'upper']\n"
            "max_tool_input_chars = 12\n"
        ),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.policy.allowed_tools == ("echo", "upper")
    assert config.policy.max_tool_input_chars == 12
