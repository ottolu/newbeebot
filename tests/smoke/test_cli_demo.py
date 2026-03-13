from pathlib import Path

from pytest import CaptureFixture

from cli.main import main


def test_cli_demo_runs_end_to_end(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    exit_code = main(
        [
            "demo",
            "--message",
            "hello bootstrap",
            "--data-dir",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "session_id=" in captured.out
    assert "assistant:" in captured.out
    assert "hello bootstrap" in captured.out


def test_cli_run_command_executes_one_shot(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    exit_code = main(
        [
            "run",
            "--message",
            "run bootstrap",
            "--data-dir",
            str(tmp_path),
        ]
    )

    captured = capsys.readouterr()

    assert exit_code == 0
    assert "session_id=" in captured.out
    assert "assistant: Echo: run bootstrap" in captured.out
