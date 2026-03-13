from pathlib import Path

from pytest import CaptureFixture, MonkeyPatch

from cli.main import main


def test_cli_chat_runs_interactive_loop(
    tmp_path: Path,
    capsys: CaptureFixture[str],
    monkeypatch: MonkeyPatch,
) -> None:
    inputs = iter(["hello chat", "/tool echo chat tool", "/exit"])
    monkeypatch.setattr("builtins.input", lambda _prompt: next(inputs))

    exit_code = main(["chat", "--data-dir", str(tmp_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "session_id=" in captured.out
    assert "assistant: Echo: hello chat" in captured.out
    assert "assistant: Tool echo: chat tool" in captured.out
