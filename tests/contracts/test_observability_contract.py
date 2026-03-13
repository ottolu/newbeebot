import json

from observability.logging import format_log_event


def test_format_log_event_outputs_stable_json() -> None:
    payload = format_log_event(
        level="info",
        event="runtime.started",
        details={"provider": "fake", "channel": "cli"},
    )

    assert json.loads(payload) == {
        "level": "info",
        "event": "runtime.started",
        "details": {"provider": "fake", "channel": "cli"},
    }
