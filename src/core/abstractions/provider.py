from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from core.types import SessionRecord


@dataclass(frozen=True, slots=True)
class ProviderRequest:
    session: SessionRecord
    message: str


@dataclass(frozen=True, slots=True)
class ProviderResponse:
    text: str


class ModelProvider(Protocol):
    name: str

    async def generate(self, request: ProviderRequest) -> ProviderResponse: ...
