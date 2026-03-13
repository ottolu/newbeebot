import asyncio
import json
from pathlib import Path

from core.types import UserMessageEvent
from storage.session_store import FileSessionStore


async def test_file_session_store_round_trip(tmp_path: Path) -> None:
    store = FileSessionStore(tmp_path)
    session = await store.create_session(channel="cli")

    event = UserMessageEvent.from_text(session_id=session.session_id, text="hello")
    await store.append_event(session.session_id, event)

    loaded = await store.get_session(session.session_id)

    assert loaded is not None
    assert loaded.channel == "cli"
    assert len(loaded.events) == 1
    assert loaded.events[0].payload["text"] == "hello"


async def test_file_session_store_lists_sessions_by_recent_update(tmp_path: Path) -> None:
    store = FileSessionStore(tmp_path)
    first = await store.create_session(channel="cli")
    second = await store.create_session(channel="cli")

    await store.append_event(
        first.session_id,
        UserMessageEvent.from_text(session_id=first.session_id, text="older"),
    )
    await store.append_event(
        second.session_id,
        UserMessageEvent.from_text(session_id=second.session_id, text="newer"),
    )

    sessions = await store.list_sessions()

    assert [session.session_id for session in sessions] == [second.session_id, first.session_id]


async def test_file_session_store_writes_schema_version(tmp_path: Path) -> None:
    store = FileSessionStore(tmp_path)
    session = await store.create_session(channel="cli")

    raw_data = json.loads((tmp_path / f"{session.session_id}.json").read_text(encoding="utf-8"))

    assert raw_data["schema_version"] == 1
    assert raw_data["session"]["session_id"] == session.session_id


async def test_file_session_store_skips_corrupted_sessions_when_listing(tmp_path: Path) -> None:
    store = FileSessionStore(tmp_path)
    session = await store.create_session(channel="cli")
    (tmp_path / "corrupted.json").write_text("{not valid json", encoding="utf-8")

    sessions = await store.list_sessions()

    assert [item.session_id for item in sessions] == [session.session_id]


async def test_file_session_store_handles_concurrent_appends(tmp_path: Path) -> None:
    store = FileSessionStore(tmp_path)
    session = await store.create_session(channel="cli")

    await asyncio.gather(
        *[
            store.append_event(
                session.session_id,
                UserMessageEvent.from_text(session_id=session.session_id, text=f"msg-{index}"),
            )
            for index in range(10)
        ]
    )

    loaded = await store.get_session(session.session_id)

    assert loaded is not None
    assert len(loaded.events) == 10
    assert sorted(event.payload["text"] for event in loaded.events) == [
        f"msg-{index}" for index in range(10)
    ]
