from pathlib import Path

from pytest import CaptureFixture

from cli.main import main


def test_cli_doctor_reports_runtime_configuration(
    tmp_path: Path,
    capsys: CaptureFixture[str],
) -> None:
    config_path = tmp_path / "newbeebot.toml"
    config_path.write_text(
        (
            "[runtime]\n"
            "provider = 'fake'\n"
            "[storage]\n"
            f"base_path = '{tmp_path / 'state'}'\n"
        ),
        encoding="utf-8",
    )

    exit_code = main(["doctor", "--config", str(config_path)])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert "provider=fake" in captured.out
    assert f"storage_base_path={tmp_path / 'state'}" in captured.out
    assert "tools=echo" in captured.out
    assert "server_status=ok" in captured.out
