from __future__ import annotations

from typing import Protocol

from core.types import Event, SessionRecord


class SessionStore(Protocol):
    async def create_session(self, channel: str) -> SessionRecord: ...

    async def get_session(self, session_id: str) -> SessionRecord | None: ...

    async def append_event(self, session_id: str, event: Event) -> None: ...

    async def list_sessions(self) -> list[SessionRecord]: ...
