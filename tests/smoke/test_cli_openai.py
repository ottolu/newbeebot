import json
from pathlib import Path
from urllib.request import Request

from pytest import CaptureFixture, MonkeyPatch

from cli.main import main


def test_cli_run_uses_openai_provider_path(
    tmp_path: Path,
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    config_path = tmp_path / "newbeebot.toml"
    config_path.write_text(
        (
            "[runtime]\n"
            "provider = 'openai'\n"
            "[provider]\n"
            "model = 'gpt-4.1-mini'\n"
            "base_url = 'https://api.openai.com/v1'\n"
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("NEWBEEBOT_PROVIDER_API_KEY", "sk-test")

    class FakeHttpResponse:
        def __enter__(self) -> "FakeHttpResponse":
            return self

        def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
            del exc_type, exc, tb

        def read(self) -> bytes:
            return json.dumps({"output_text": "OpenAI CLI reply"}).encode("utf-8")

    def fake_urlopen(request: Request, timeout: float | None = 30) -> FakeHttpResponse:
        del request, timeout
        return FakeHttpResponse()

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    exit_code = main(
        [
            "run",
            "--config",
            str(config_path),
            "--data-dir",
            str(tmp_path / "state"),
            "--message",
            "hello openai",
        ]
    )
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "session_id=" in captured.out
    assert "assistant: OpenAI CLI reply" in captured.out
