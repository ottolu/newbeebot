from __future__ import annotations

import json
from typing import Any


def format_log_event(*, level: str, event: str, details: dict[str, Any]) -> str:
    return json.dumps(
        {
            "level": level,
            "event": event,
            "details": details,
        },
        sort_keys=True,
    )
