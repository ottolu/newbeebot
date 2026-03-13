from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol


class PolicyEngine(Protocol):
    def check_tool_permission(self, tool_name: str, context: Mapping[str, Any]) -> bool: ...

    def check_path_access(self, path: str, context: Mapping[str, Any]) -> bool: ...

    def check_resource_limit(
        self,
        resource_type: str,
        amount: int,
        context: Mapping[str, Any],
    ) -> bool: ...
