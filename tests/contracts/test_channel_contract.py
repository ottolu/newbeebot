from channels.cli import CLIChannelAdapter


def test_cli_channel_normalizes_inbound_and_outbound_messages() -> None:
    channel = CLIChannelAdapter(channel_id="cli")

    inbound = channel.normalize_inbound("hello channel")
    outbound = channel.normalize_outbound("assistant reply")

    assert inbound == {
        "channel_id": "cli",
        "role": "user",
        "text": "hello channel",
    }
    assert outbound == {
        "channel_id": "cli",
        "role": "assistant",
        "text": "assistant reply",
    }
