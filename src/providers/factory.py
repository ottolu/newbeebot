from __future__ import annotations

from core.abstractions import ModelProvider
from core.config import ProviderConfig
from providers.fake import FakeEchoProvider
from providers.openai_responses import OpenAIResponsesProvider


def build_provider(name: str, config: ProviderConfig) -> ModelProvider:
    if name == "fake":
        return FakeEchoProvider()
    if name == "openai":
        if config.api_key is None:
            raise ValueError("OpenAI provider requires provider.api_key")
        return OpenAIResponsesProvider(
            api_key=config.api_key,
            model=config.model,
            base_url=config.base_url,
        )
    raise ValueError(f"Unknown provider: {name}")
