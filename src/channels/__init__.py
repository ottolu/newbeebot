"""Channel adapters for newbeebot."""

from channels.cli import CLIChannelAdapter
from channels.memory import MemoryChannelAdapter

__all__ = ["CLIChannelAdapter", "MemoryChannelAdapter"]
