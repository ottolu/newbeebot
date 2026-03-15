from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.abstractions import (
    ModelProvider,
    PolicyEngine,
    ProviderRequest,
    SessionStore,
    ToolRegistry,
)
from core.types import AssistantMessageEvent, Event, SessionRecord, UserMessageEvent
from observability.metrics import MetricsSink, NullMetricsSink
from runtime.policy import AllowAllPolicy


@dataclass(frozen=True, slots=True)
class TurnResult:
    session: SessionRecord
    assistant_text: str


class AgentLoop:
    def __init__(
        self,
        provider: ModelProvider,
        session_store: SessionStore,
        tool_registry: ToolRegistry,
        policy_engine: PolicyEngine | None = None,
        metrics_sink: MetricsSink | None = None,
    ) -> None:
        self._provider = provider
        self._session_store = session_store
        self._tool_registry = tool_registry
        self._policy_engine = policy_engine or AllowAllPolicy()
        self._metrics_sink = metrics_sink or NullMetricsSink()

    async def run_once(self, *, channel: str, user_text: str) -> TurnResult:
        session = await self._session_store.create_session(channel=channel)
        return await self._run_turn(session=session, user_text=user_text)

    async def continue_session(self, *, session_id: str, user_text: str) -> TurnResult:
        session = await self._session_store.get_session(session_id)
        if session is None:
            raise KeyError(f"Session '{session_id}' not found")
        return await self._run_turn(session=session, user_text=user_text)

    async def _run_turn(self, *, session: SessionRecord, user_text: str) -> TurnResult:
        self._metrics_sink.increment(
            "runtime.turns",
            attributes={"channel": session.channel},
        )
        user_event = UserMessageEvent.from_text(session.session_id, user_text)
        await self._session_store.append_event(session.session_id, user_event)

        tool_request = self._parse_tool_request(user_text)
        if tool_request is not None:
            return await self._run_tool_turn(session=session, tool_request=tool_request)

        refreshed_session = await self._session_store.get_session(session.session_id)
        if refreshed_session is None:
            raise RuntimeError("Session disappeared before provider request")

        provider_response = await self._provider.generate(
            ProviderRequest(session=refreshed_session, message=user_text)
        )
        assistant_event = AssistantMessageEvent.from_text(
            session.session_id,
            provider_response.text,
        )
        await self._session_store.append_event(session.session_id, assistant_event)

        stored_session = await self._session_store.get_session(session.session_id)
        if stored_session is None:
            raise RuntimeError("Session disappeared after persistence round trip")

        return TurnResult(session=stored_session, assistant_text=provider_response.text)

    async def _run_tool_turn(
        self,
        *,
        session: SessionRecord,
        tool_request: tuple[str, dict[str, Any]],
    ) -> TurnResult:
        tool_name, arguments = tool_request
        tool_context = {"session_id": session.session_id, "channel": session.channel}
        if not self._policy_engine.check_tool_permission(tool_name, tool_context):
            self._metrics_sink.increment(
                "runtime.tool_permission_denied",
                attributes={"tool_name": tool_name, "channel": session.channel},
            )
            assistant_text = f"Tool blocked by policy: {tool_name}"
            assistant_event = AssistantMessageEvent.from_text(session.session_id, assistant_text)
            await self._session_store.append_event(session.session_id, assistant_event)
            stored_session = await self._session_store.get_session(session.session_id)
            if stored_session is None:
                raise RuntimeError("Session disappeared after policy denial")
            return TurnResult(session=stored_session, assistant_text=assistant_text)

        tool_input_chars = sum(len(str(value)) for value in arguments.values())
        if not self._policy_engine.check_resource_limit(
            "tool_input_chars",
            tool_input_chars,
            tool_context,
        ):
            self._metrics_sink.increment(
                "runtime.tool_limit_denied",
                attributes={"tool_name": tool_name, "channel": session.channel},
            )
            assistant_text = "Tool blocked by policy limit: tool_input_chars"
            assistant_event = AssistantMessageEvent.from_text(session.session_id, assistant_text)
            await self._session_store.append_event(session.session_id, assistant_event)
            stored_session = await self._session_store.get_session(session.session_id)
            if stored_session is None:
                raise RuntimeError("Session disappeared after policy limit denial")
            return TurnResult(session=stored_session, assistant_text=assistant_text)

        tool = self._tool_registry.get(tool_name)
        if tool is None:
            assistant_text = f"Tool not found: {tool_name}"
            assistant_event = AssistantMessageEvent.from_text(session.session_id, assistant_text)
            await self._session_store.append_event(session.session_id, assistant_event)
            stored_session = await self._session_store.get_session(session.session_id)
            if stored_session is None:
                raise RuntimeError("Session disappeared after missing tool handling")
            return TurnResult(session=stored_session, assistant_text=assistant_text)

        tool_call_event = Event.create(
            session.session_id,
            "tool_call",
            {"tool_name": tool_name, "arguments": arguments},
        )
        await self._session_store.append_event(session.session_id, tool_call_event)
        self._metrics_sink.increment(
            "runtime.tool_calls",
            attributes={"tool_name": tool_name, "channel": session.channel},
        )

        try:
            tool_result = await tool.run(arguments)
        except Exception as exc:
            error_text = str(exc)
            tool_result_event = Event.create(
                session.session_id,
                "tool_result",
                {"tool_name": tool_name, "error": error_text},
            )
            await self._session_store.append_event(session.session_id, tool_result_event)
            assistant_text = f"Tool {tool_name} failed: {error_text}"
            assistant_event = AssistantMessageEvent.from_text(session.session_id, assistant_text)
            await self._session_store.append_event(session.session_id, assistant_event)

            stored_session = await self._session_store.get_session(session.session_id)
            if stored_session is None:
                raise RuntimeError("Session disappeared after tool failure") from exc
            return TurnResult(session=stored_session, assistant_text=assistant_text)

        tool_result_event = Event.create(
            session.session_id,
            "tool_result",
            (
                {"tool_name": tool_name, "content": tool_result.content}
                if tool_result.success
                else {"tool_name": tool_name, "error": tool_result.error or "tool failed"}
            ),
        )
        await self._session_store.append_event(session.session_id, tool_result_event)

        if tool_result.success:
            assistant_text = f"Tool {tool_name}: {tool_result.content}"
        else:
            assistant_text = f"Tool {tool_name} failed: {tool_result.error or 'tool failed'}"
        assistant_event = AssistantMessageEvent.from_text(session.session_id, assistant_text)
        await self._session_store.append_event(session.session_id, assistant_event)

        stored_session = await self._session_store.get_session(session.session_id)
        if stored_session is None:
            raise RuntimeError("Session disappeared after tool execution")
        return TurnResult(session=stored_session, assistant_text=assistant_text)

    def _parse_tool_request(self, user_text: str) -> tuple[str, dict[str, Any]] | None:
        prefix = "/tool "
        if not user_text.startswith(prefix):
            return None

        remainder = user_text[len(prefix) :].strip()
        if not remainder:
            return None

        tool_name, _, raw_args = remainder.partition(" ")
        arguments = self._tool_arguments(tool_name=tool_name, raw_args=raw_args.strip())
        return tool_name, arguments

    def _tool_arguments(self, *, tool_name: str, raw_args: str) -> dict[str, Any]:
        if tool_name == "echo":
            return {"text": raw_args}
        return {"input": raw_args}
