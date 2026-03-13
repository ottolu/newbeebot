from __future__ import annotations


class CLIChannelAdapter:
    def __init__(self, channel_id: str = "cli") -> None:
        self.channel_id = channel_id

    def normalize_inbound(self, text: str) -> dict[str, str]:
        return {
            "channel_id": self.channel_id,
            "role": "user",
            "text": text,
        }

    def normalize_outbound(self, text: str) -> dict[str, str]:
        return {
            "channel_id": self.channel_id,
            "role": "assistant",
            "text": text,
        }
