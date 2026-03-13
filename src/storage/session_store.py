from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any

from core.types import Event, SessionRecord

SCHEMA_VERSION = 1


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}

    async def create_session(self, channel: str) -> SessionRecord:
        session = SessionRecord.create(channel=channel)
        self._sessions[session.session_id] = session
        return session

    async def get_session(self, session_id: str) -> SessionRecord | None:
        return self._sessions.get(session_id)

    async def append_event(self, session_id: str, event: Event) -> None:
        session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(f"Session '{session_id}' not found")
        session.append_event(event)

    async def list_sessions(self) -> list[SessionRecord]:
        return sorted(
            self._sessions.values(),
            key=lambda session: session.updated_at,
            reverse=True,
        )


class FileSessionStore:
    def __init__(self, base_path: Path) -> None:
        self._base_path = base_path
        self._base_path.mkdir(parents=True, exist_ok=True)
        self._locks: dict[str, asyncio.Lock] = {}

    async def create_session(self, channel: str) -> SessionRecord:
        session = SessionRecord.create(channel=channel)
        self._write_session(session)
        return session

    async def get_session(self, session_id: str) -> SessionRecord | None:
        session_path = self._session_path(session_id)
        if not session_path.exists():
            return None

        raw_data = json.loads(session_path.read_text(encoding="utf-8"))
        return self._decode_session(raw_data)

    async def append_event(self, session_id: str, event: Event) -> None:
        async with self._lock_for(session_id):
            session = await self.get_session(session_id)
            if session is None:
                raise KeyError(f"Session '{session_id}' not found")

            session.append_event(event)
            self._write_session(session)

    async def list_sessions(self) -> list[SessionRecord]:
        sessions: list[SessionRecord] = []
        for session_path in self._base_path.glob("*.json"):
            try:
                raw_data = json.loads(session_path.read_text(encoding="utf-8"))
                sessions.append(self._decode_session(raw_data))
            except (KeyError, TypeError, ValueError, json.JSONDecodeError):
                continue
        return sorted(sessions, key=lambda session: session.updated_at, reverse=True)

    def _session_path(self, session_id: str) -> Path:
        return self._base_path / f"{session_id}.json"

    def _write_session(self, session: SessionRecord) -> None:
        session_path = self._session_path(session.session_id)
        temp_path = session_path.with_suffix(".json.tmp")
        temp_path.write_text(
            json.dumps(
                {
                    "schema_version": SCHEMA_VERSION,
                    "session": session.to_dict(),
                },
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )
        temp_path.replace(session_path)

    def _decode_session(self, raw_data: dict[str, Any]) -> SessionRecord:
        if "schema_version" in raw_data:
            if raw_data["schema_version"] != SCHEMA_VERSION:
                raise ValueError(f"Unsupported schema version: {raw_data['schema_version']}")
            session_data = raw_data["session"]
        else:
            session_data = raw_data
        return SessionRecord.from_dict(session_data)

    def _lock_for(self, session_id: str) -> asyncio.Lock:
        if session_id not in self._locks:
            self._locks[session_id] = asyncio.Lock()
        return self._locks[session_id]
