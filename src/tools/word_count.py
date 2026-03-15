from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.abstractions import ToolResult, ToolSpec


class WordCountTool:
    @property
    def spec(self) -> ToolSpec:
        return ToolSpec(
            name="word_count",
            description="Count the number of whitespace-delimited words in the input.",
            parameters={
                "type": "object",
                "properties": {"input": {"type": "string"}},
                "required": ["input"],
            },
        )

    async def run(self, arguments: Mapping[str, Any]) -> ToolResult:
        text = str(arguments.get("input", "")).strip()
        word_count = len(text.split()) if text else 0
        return ToolResult.ok(str(word_count))
