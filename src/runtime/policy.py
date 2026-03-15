from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.config import PolicyConfig


class AllowAllPolicy:
    def check_tool_permission(self, tool_name: str, context: Mapping[str, Any]) -> bool:
        del tool_name, context
        return True

    def check_path_access(self, path: str, context: Mapping[str, Any]) -> bool:
        del path, context
        return True

    def check_resource_limit(
        self,
        resource_type: str,
        amount: int,
        context: Mapping[str, Any],
    ) -> bool:
        del resource_type, amount, context
        return True


class ConfigurablePolicy:
    def __init__(self, config: PolicyConfig) -> None:
        self._allowed_tools = set(config.allowed_tools)
        self._max_tool_input_chars = config.max_tool_input_chars

    def check_tool_permission(self, tool_name: str, context: Mapping[str, Any]) -> bool:
        del context
        if not self._allowed_tools:
            return True
        return tool_name in self._allowed_tools

    def check_path_access(self, path: str, context: Mapping[str, Any]) -> bool:
        del path, context
        return True

    def check_resource_limit(
        self,
        resource_type: str,
        amount: int,
        context: Mapping[str, Any],
    ) -> bool:
        del context
        if resource_type == "tool_input_chars":
            return amount <= self._max_tool_input_chars
        return True
