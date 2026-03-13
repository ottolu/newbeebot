from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": self.name,
            "description": self.description,
        }
        if self.parameters is not None:
            payload["parameters"] = self.parameters
        return payload


@dataclass(frozen=True, slots=True)
class ToolResult:
    success: bool
    content: str | None = None
    error: str | None = None

    @classmethod
    def ok_result(cls, content: str) -> ToolResult:
        return cls(success=True, content=content)

    @classmethod
    def ok(cls, content: str) -> ToolResult:
        return cls.ok_result(content)

    @classmethod
    def failure(cls, error: str) -> ToolResult:
        return cls(success=False, error=error)


class Tool(Protocol):
    @property
    def spec(self) -> ToolSpec: ...

    async def run(self, arguments: Mapping[str, Any]) -> ToolResult: ...


class ToolRegistry(Protocol):
    def register(self, tool: Tool) -> None: ...

    def get(self, name: str) -> Tool | None: ...

    def list_tools(self) -> list[ToolSpec]: ...

    def get_schemas(self) -> list[dict[str, Any]]: ...
