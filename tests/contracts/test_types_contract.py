from core.types import Event, EventEnvelope, SessionRecord


def test_event_envelope_wraps_event_with_session_context() -> None:
    session = SessionRecord.create(channel="cli")
    event = Event.create(session.session_id, "tool_result", {"tool_name": "echo", "content": "ok"})

    envelope = EventEnvelope.from_session_event(session=session, event=event)

    assert envelope.session_id == session.session_id
    assert envelope.channel == "cli"
    assert envelope.event is event
