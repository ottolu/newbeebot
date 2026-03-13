from server.app import create_app, get_health, get_startup_settings


def test_server_placeholder_exposes_health_metadata() -> None:
    app = create_app()
    health = get_health()
    startup = get_startup_settings(host="127.0.0.1", port=8080)

    assert app == {"name": "newbeebot-server", "status": "reserved"}
    assert health == {"status": "ok", "service": "newbeebot-server"}
    assert startup == {"host": "127.0.0.1", "port": 8080, "service": "newbeebot-server"}
