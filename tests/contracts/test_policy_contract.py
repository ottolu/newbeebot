from collections.abc import Mapping
from typing import Any

from core.abstractions import ToolResult, ToolSpec
from providers.fake import FakeEchoProvider
from runtime.agent_loop import AgentLoop
from storage.session_store import InMemorySessionStore
from tools.registry import SimpleToolRegistry


class DenyAllPolicy:
    def check_tool_permission(self, tool_name: str, context: Mapping[str, Any]) -> bool:
        return False

    def check_path_access(self, path: str, context: Mapping[str, Any]) -> bool:
        return False

    def check_resource_limit(
        self,
        resource_type: str,
        amount: int,
        context: Mapping[str, Any],
    ) -> bool:
        return False


class EchoTool:
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(name="echo", description="Echo tool")

    async def run(self, arguments: Mapping[str, Any]) -> ToolResult:
        return ToolResult.ok(str(arguments.get("text", "")))


async def test_agent_loop_blocks_tool_when_policy_denies() -> None:
    loop = AgentLoop(
        provider=FakeEchoProvider(),
        session_store=InMemorySessionStore(),
        tool_registry=SimpleToolRegistry([EchoTool()]),
        policy_engine=DenyAllPolicy(),
    )

    result = await loop.run_once(channel="cli", user_text="/tool echo blocked")

    assert result.assistant_text == "Tool blocked by policy: echo"
    assert [event.kind for event in result.session.events] == [
        "user_message",
        "assistant_message",
    ]
