from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Protocol, cast
from urllib import error, request

from core.abstractions import ModelProvider, ProviderRequest, ProviderResponse


class HttpResponse(Protocol):
    def __enter__(self) -> HttpResponse: ...

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None: ...

    def read(self) -> bytes: ...


class UrlopenCallable(Protocol):
    def __call__(self, request: request.Request, timeout: float | None = None) -> HttpResponse: ...


class OpenAIResponsesProvider(ModelProvider):
    name = "openai"

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        base_url: str = "https://api.openai.com/v1",
        urlopen: UrlopenCallable | None = None,
        max_retries: int = 1,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._urlopen = cast(UrlopenCallable, request.urlopen) if urlopen is None else urlopen
        self._max_retries = max_retries

    async def generate(self, request_data: ProviderRequest) -> ProviderResponse:
        payload = json.dumps(
            {
                "model": self._model,
                "input": request_data.message,
            }
        ).encode("utf-8")
        http_request = request.Request(
            url=f"{self._base_url}/responses",
            data=payload,
            method="POST",
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
        )
        raw_data: Mapping[str, object] | None = None
        for attempt in range(self._max_retries + 1):
            try:
                with self._urlopen(http_request, timeout=30) as response:
                    raw_data = json.loads(response.read().decode("utf-8"))
                break
            except error.HTTPError as exc:
                if attempt >= self._max_retries or exc.code < 500:
                    raise
        if raw_data is None:
            raise RuntimeError("Provider request completed without a response payload")
        return ProviderResponse(text=_extract_output_text(raw_data))


def _extract_output_text(raw_data: Mapping[str, object]) -> str:
    output_text = raw_data.get("output_text")
    if isinstance(output_text, str):
        return output_text

    output = raw_data.get("output")
    if not isinstance(output, list):
        return ""

    parts: list[str] = []
    for item in output:
        if not isinstance(item, Mapping):
            continue
        content = item.get("content")
        if not isinstance(content, list):
            continue
        for content_item in content:
            if not isinstance(content_item, Mapping):
                continue
            text_value = content_item.get("text")
            if isinstance(text_value, str):
                parts.append(text_value)
    return "".join(parts)
