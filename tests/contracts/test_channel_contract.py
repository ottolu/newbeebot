from channels.cli import CLIChannelAdapter
from channels.memory import MemoryChannelAdapter


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


def test_memory_channel_normalizes_inbound_and_outbound_messages() -> None:
    channel = MemoryChannelAdapter(channel_id="memory")

    inbound = channel.normalize_inbound("loopback in")
    outbound = channel.normalize_outbound("loopback out")

    assert inbound == {
        "channel_id": "memory",
        "role": "user",
        "text": "loopback in",
    }
    assert outbound == {
        "channel_id": "memory",
        "role": "assistant",
        "text": "loopback out",
    }
