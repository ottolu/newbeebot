from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any


def format_trace_span(
    *,
    name: str,
    attributes: Mapping[str, Any],
    status: str,
) -> str:
    return json.dumps(
        {
            "name": name,
            "attributes": dict(attributes),
            "status": status,
        },
        sort_keys=True,
    )
