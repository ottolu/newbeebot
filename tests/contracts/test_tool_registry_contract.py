from tools.echo import EchoTool
from tools.registry import SimpleToolRegistry


async def test_tool_registry_exports_schemas() -> None:
    registry = SimpleToolRegistry([EchoTool()])

    schemas = registry.get_schemas()

    assert schemas == [
        {
            "name": "echo",
            "description": "Return the provided text without modification.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        }
    ]
