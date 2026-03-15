import json

from observability.logging import format_log_event
from observability.metrics import InMemoryMetricsSink
from observability.tracing import format_trace_span


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


def test_metrics_sink_records_counter_samples() -> None:
    sink = InMemoryMetricsSink()

    sink.increment("runtime.turns", value=2, attributes={"channel": "cli"})

    assert sink.samples == [
        {
            "name": "runtime.turns",
            "value": 2,
            "attributes": {"channel": "cli"},
        }
    ]


def test_format_trace_span_outputs_stable_json() -> None:
    payload = format_trace_span(
        name="runtime.turn",
        attributes={"provider": "fake"},
        status="ok",
    )

    assert json.loads(payload) == {
        "name": "runtime.turn",
        "attributes": {"provider": "fake"},
        "status": "ok",
    }
