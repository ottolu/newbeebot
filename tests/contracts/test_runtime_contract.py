from collections.abc import Mapping
from typing import Any

from core.abstractions import ToolResult, ToolSpec
from core.types import SessionRecord
from providers.fake import FakeEchoProvider
from runtime.agent_loop import AgentLoop
from storage.session_store import InMemorySessionStore
from tools.echo import EchoTool
from tools.registry import SimpleToolRegistry


async def test_agent_loop_continues_existing_session() -> None:
    store = InMemorySessionStore()
    loop = AgentLoop(
        provider=FakeEchoProvider(),
        session_store=store,
        tool_registry=SimpleToolRegistry([EchoTool()]),
    )

    first = await loop.run_once(channel="cli", user_text="first message")
    continued = await loop.continue_session(
        session_id=first.session.session_id,
        user_text="second message",
    )

    assert isinstance(continued.session, SessionRecord)
    assert continued.session.session_id == first.session.session_id
    assert len(continued.session.events) == 4
    assert continued.session.events[-2].payload["text"] == "second message"
    assert continued.session.events[-1].payload["text"] == "Echo: second message"


async def test_agent_loop_executes_echo_tool_calls() -> None:
    store = InMemorySessionStore()
    loop = AgentLoop(
        provider=FakeEchoProvider(),
        session_store=store,
        tool_registry=SimpleToolRegistry([EchoTool()]),
    )

    result = await loop.run_once(channel="cli", user_text="/tool echo hello tool")

    assert result.assistant_text == "Tool echo: hello tool"
    assert [event.kind for event in result.session.events] == [
        "user_message",
        "tool_call",
        "tool_result",
        "assistant_message",
    ]
    assert result.session.events[1].payload == {
        "tool_name": "echo",
        "arguments": {"text": "hello tool"},
    }
    assert result.session.events[2].payload == {"tool_name": "echo", "content": "hello tool"}


class FailingTool:
    @property
    def spec(self) -> ToolSpec:
        return EchoTool().spec

    async def run(self, arguments: Mapping[str, Any]) -> ToolResult:
        del arguments
        raise RuntimeError("boom")


async def test_agent_loop_surfaces_tool_failures() -> None:
    store = InMemorySessionStore()
    loop = AgentLoop(
        provider=FakeEchoProvider(),
        session_store=store,
        tool_registry=SimpleToolRegistry([FailingTool()]),
    )

    result = await loop.run_once(channel="cli", user_text="/tool echo bad tool")

    assert result.assistant_text == "Tool echo failed: boom"
    assert result.session.events[2].payload == {
        "tool_name": "echo",
        "error": "boom",
    }
