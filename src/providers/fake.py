from __future__ import annotations

from core.abstractions import ModelProvider, ProviderRequest, ProviderResponse


class FakeEchoProvider(ModelProvider):
    name = "fake"

    async def generate(self, request: ProviderRequest) -> ProviderResponse:
        return ProviderResponse(text=f"Echo: {request.message}")
