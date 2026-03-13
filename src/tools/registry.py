from __future__ import annotations

from collections.abc import Iterable

from core.abstractions import Tool, ToolSpec


class SimpleToolRegistry:
    def __init__(self, tools: Iterable[Tool] | None = None) -> None:
        self._tools: dict[str, Tool] = {}
        if tools is not None:
            for tool in tools:
                self.register(tool)

    def register(self, tool: Tool) -> None:
        self._tools[tool.spec.name] = tool

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def list_tools(self) -> list[ToolSpec]:
        return [tool.spec for tool in self._tools.values()]

    def get_schemas(self) -> list[dict[str, object]]:
        return [tool.spec.to_dict() for tool in self._tools.values()]
