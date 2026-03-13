from pathlib import Path

from pytest import CaptureFixture

from cli.main import main


def test_cli_sessions_list_and_show(tmp_path: Path, capsys: CaptureFixture[str]) -> None:
    demo_exit_code = main(
        [
            "demo",
            "--message",
            "remember me",
            "--data-dir",
            str(tmp_path),
        ]
    )
    demo_output = capsys.readouterr().out
    session_line = next(line for line in demo_output.splitlines() if line.startswith("session_id="))
    session_id = session_line.split("=", maxsplit=1)[1]

    list_exit_code = main(["sessions", "list", "--data-dir", str(tmp_path)])
    list_output = capsys.readouterr().out

    show_exit_code = main(["sessions", "show", session_id, "--data-dir", str(tmp_path)])
    show_output = capsys.readouterr().out

    assert demo_exit_code == 0
    assert list_exit_code == 0
    assert show_exit_code == 0
    assert session_id in list_output
    assert "channel=cli" in list_output
    assert "user_message: remember me" in show_output
    assert "assistant_message: Echo: remember me" in show_output
