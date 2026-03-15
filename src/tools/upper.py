from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.abstractions import ToolResult, ToolSpec


class UpperTool:
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="upper",
            description="Convert the provided input to uppercase.",
            parameters={
                "type": "object",
                "properties": {"input": {"type": "string"}},
                "required": ["input"],
            },
        )

    async def run(self, arguments: Mapping[str, Any]) -> ToolResult:
        return ToolResult.ok(str(arguments.get("input", "")).upper())
