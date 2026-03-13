from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.abstractions import ToolResult, ToolSpec


class EchoTool:
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="echo",
            description="Return the provided text without modification.",
            parameters={
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        )

    async def run(self, arguments: Mapping[str, Any]) -> ToolResult:
        text = str(arguments.get("text", ""))
        return ToolResult.ok(text)
