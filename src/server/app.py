from __future__ import annotations


def create_app() -> dict[str, str]:
    return {"name": "newbeebot-server", "status": "reserved"}


def get_health() -> dict[str, str]:
    return {"status": "ok", "service": "newbeebot-server"}


def get_startup_settings(*, host: str, port: int) -> dict[str, str | int]:
    return {"host": host, "port": port, "service": "newbeebot-server"}
