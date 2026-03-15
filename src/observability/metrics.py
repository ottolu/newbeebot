from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Protocol


class MetricsSink(Protocol):
    def increment(
        self,
        name: str,
        *,
        value: int = 1,
        attributes: Mapping[str, Any] | None = None,
    ) -> None: ...


class NullMetricsSink:
    def increment(
        self,
        name: str,
        *,
        value: int = 1,
        attributes: Mapping[str, Any] | None = None,
    ) -> None:
        del name, value, attributes


class InMemoryMetricsSink:
    def __init__(self) -> None:
        self.samples: list[dict[str, object]] = []

    def increment(
        self,
        name: str,
        *,
        value: int = 1,
        attributes: Mapping[str, Any] | None = None,
    ) -> None:
        self.samples.append(
            {
                "name": name,
                "value": value,
                "attributes": dict(attributes or {}),
            }
        )
