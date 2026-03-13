import json
from email.message import Message
from typing import cast
from urllib.error import HTTPError
from urllib.request import Request

from pytest import raises

from core.abstractions import ProviderRequest
from core.config import ProviderConfig
from core.types import SessionRecord
from providers import build_provider
from providers.fake import FakeEchoProvider
from providers.openai_responses import OpenAIResponsesProvider


def test_build_provider_returns_fake_provider() -> None:
    provider = build_provider("fake", ProviderConfig())

    assert isinstance(provider, FakeEchoProvider)


def test_build_provider_rejects_unknown_provider() -> None:
    with raises(ValueError, match="Unknown provider"):
        build_provider("missing-provider", ProviderConfig())


def test_build_provider_returns_openai_provider() -> None:
    provider = build_provider(
        "openai",
        ProviderConfig(api_key="sk-test", model="gpt-4.1-mini"),
    )

    assert isinstance(provider, OpenAIResponsesProvider)


async def test_openai_provider_sends_responses_api_request() -> None:
    captured: dict[str, object] = {}

    class FakeHttpResponse:
        def __enter__(self) -> "FakeHttpResponse":
            return self

        def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
            del exc_type, exc, tb

        def read(self) -> bytes:
            return json.dumps({"output_text": "OpenAI says hi"}).encode("utf-8")

    def fake_urlopen(request: Request, timeout: float | None = 30) -> FakeHttpResponse:
        del timeout
        captured["url"] = request.full_url
        captured["authorization"] = request.headers["Authorization"]
        captured["content_type"] = request.get_header("Content-type")
        captured["body"] = json.loads(cast(bytes, request.data).decode("utf-8"))
        return FakeHttpResponse()

    provider = OpenAIResponsesProvider(
        api_key="sk-test",
        model="gpt-4.1-mini",
        base_url="https://api.openai.com/v1",
        urlopen=fake_urlopen,
    )

    session = SessionRecord.create(channel="cli")
    response = await provider.generate(
        ProviderRequest(session=session, message="hello responses api")
    )

    assert response.text == "OpenAI says hi"
    assert captured["url"] == "https://api.openai.com/v1/responses"
    assert captured["authorization"] == "Bearer sk-test"
    assert captured["content_type"] == "application/json"
    assert captured["body"] == {
        "model": "gpt-4.1-mini",
        "input": "hello responses api",
    }


async def test_openai_provider_retries_once_on_transient_http_error() -> None:
    attempts = 0

    class FakeHttpResponse:
        def __enter__(self) -> "FakeHttpResponse":
            return self

        def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
            del exc_type, exc, tb

        def read(self) -> bytes:
            return json.dumps({"output_text": "Recovered reply"}).encode("utf-8")

    def flaky_urlopen(request: Request, timeout: float | None = 30) -> FakeHttpResponse:
        del request, timeout
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise HTTPError(
                url="https://api.openai.com/v1/responses",
                code=500,
                msg="server error",
                hdrs=Message(),
                fp=None,
            )
        return FakeHttpResponse()

    provider = OpenAIResponsesProvider(
        api_key="sk-test",
        model="gpt-4.1-mini",
        base_url="https://api.openai.com/v1",
        urlopen=flaky_urlopen,
    )

    session = SessionRecord.create(channel="cli")
    response = await provider.generate(
        ProviderRequest(session=session, message="retry please")
    )

    assert attempts == 2
    assert response.text == "Recovered reply"
