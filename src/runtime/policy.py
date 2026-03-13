from __future__ import annotations

from collections.abc import Mapping
from typing import Any


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
