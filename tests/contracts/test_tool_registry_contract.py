from tools.echo import EchoTool
from tools.registry import SimpleToolRegistry
from tools.upper import UpperTool
from tools.word_count import WordCountTool


async def test_tool_registry_exports_schemas() -> None:
    registry = SimpleToolRegistry([EchoTool(), UpperTool(), WordCountTool()])

    schemas = registry.get_schemas()

    assert [schema["name"] for schema in schemas] == ["echo", "upper", "word_count"]


async def test_safe_builtin_tools_execute_expected_transforms() -> None:
    upper_result = await UpperTool().run({"input": "hello world"})
    count_result = await WordCountTool().run({"input": "one two three"})

    assert upper_result.content == "HELLO WORLD"
    assert count_result.content == "3"
