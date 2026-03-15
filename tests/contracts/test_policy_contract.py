from collections.abc import Mapping
from typing import Any

from core.abstractions import ToolResult, ToolSpec
from core.config import PolicyConfig
from providers.fake import FakeEchoProvider
from runtime.agent_loop import AgentLoop
from runtime.policy import ConfigurablePolicy
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


def test_configurable_policy_allows_only_configured_tools() -> None:
    policy = ConfigurablePolicy(
        PolicyConfig(allowed_tools=("echo", "upper"), max_tool_input_chars=16)
    )

    assert policy.check_tool_permission("echo", {"channel": "cli"}) is True
    assert policy.check_tool_permission("upper", {"channel": "cli"}) is True
    assert policy.check_tool_permission("word_count", {"channel": "cli"}) is False


async def test_agent_loop_blocks_tool_when_input_exceeds_policy_limit() -> None:
    loop = AgentLoop(
        provider=FakeEchoProvider(),
        session_store=InMemorySessionStore(),
        tool_registry=SimpleToolRegistry([EchoTool()]),
        policy_engine=ConfigurablePolicy(
            PolicyConfig(allowed_tools=("echo",), max_tool_input_chars=4)
        ),
    )

    result = await loop.run_once(channel="cli", user_text="/tool echo too-long")

    assert result.assistant_text == "Tool blocked by policy limit: tool_input_chars"
    assert [event.kind for event in result.session.events] == [
        "user_message",
        "assistant_message",
    ]
