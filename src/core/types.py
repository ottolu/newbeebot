from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any, Literal, cast
from uuid import uuid4

EventKind = Literal["user_message", "assistant_message", "tool_call", "tool_result"]


def utc_now() -> str:
    return datetime.now(tz=UTC).isoformat()


@dataclass(frozen=True, slots=True)
class Event:
    event_id: str
    session_id: str
    kind: EventKind
    timestamp: str
    payload: dict[str, Any]

    @classmethod
    def create(cls, session_id: str, kind: EventKind, payload: Mapping[str, Any]) -> Event:
        return cls(
            event_id=f"evt_{uuid4().hex}",
            session_id=session_id,
            kind=kind,
            timestamp=utc_now(),
            payload=dict(payload),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "session_id": self.session_id,
            "kind": self.kind,
            "timestamp": self.timestamp,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, raw_data: Mapping[str, Any]) -> Event:
        return cls(
            event_id=str(raw_data["event_id"]),
            session_id=str(raw_data["session_id"]),
            kind=cast(EventKind, raw_data["kind"]),
            timestamp=str(raw_data["timestamp"]),
            payload=dict(cast(Mapping[str, Any], raw_data["payload"])),
        )


@dataclass(frozen=True, slots=True)
class UserMessageEvent(Event):
    @classmethod
    def from_text(cls, session_id: str, text: str) -> UserMessageEvent:
        return cls(
            event_id=f"evt_{uuid4().hex}",
            session_id=session_id,
            kind="user_message",
            timestamp=utc_now(),
            payload={"text": text},
        )


@dataclass(frozen=True, slots=True)
class AssistantMessageEvent(Event):
    @classmethod
    def from_text(cls, session_id: str, text: str) -> AssistantMessageEvent:
        return cls(
            event_id=f"evt_{uuid4().hex}",
            session_id=session_id,
            kind="assistant_message",
            timestamp=utc_now(),
            payload={"text": text},
        )


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    session_id: str
    channel: str
    event: Event

    @classmethod
    def from_session_event(cls, *, session: SessionRecord, event: Event) -> EventEnvelope:
        return cls(
            session_id=session.session_id,
            channel=session.channel,
            event=event,
        )


@dataclass(slots=True)
class SessionRecord:
    session_id: str
    channel: str
    created_at: str
    updated_at: str
    events: list[Event] = field(default_factory=list)

    @classmethod
    def create(cls, channel: str) -> SessionRecord:
        timestamp = utc_now()
        return cls(
            session_id=f"session_{uuid4().hex}",
            channel=channel,
            created_at=timestamp,
            updated_at=timestamp,
            events=[],
        )

    def append_event(self, event: Event) -> None:
        self.events.append(event)
        self.updated_at = utc_now()

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "channel": self.channel,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "events": [event.to_dict() for event in self.events],
        }

    @classmethod
    def from_dict(cls, raw_data: Mapping[str, Any]) -> SessionRecord:
        raw_events = cast(list[Mapping[str, Any]], raw_data.get("events", []))
        return cls(
            session_id=str(raw_data["session_id"]),
            channel=str(raw_data["channel"]),
            created_at=str(raw_data["created_at"]),
            updated_at=str(raw_data["updated_at"]),
            events=[Event.from_dict(raw_event) for raw_event in raw_events],
        )
