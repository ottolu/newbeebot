# 测试策略

## 概述

本文档定义 AgentOS 的完整测试策略，包括单元测试、集成测试、端到端测试，以及针对 Agent 系统的特殊测试方法。

---

## 测试金字塔

```
           /\
          /  \     E2E Tests (5%)
         /    \    - 完整用户流程
        /------\   - 真实环境
       /        \
      /          \  Integration Tests (25%)
     /            \ - 模块间集成
    /--------------\ - 部分 mock
   /                \
  /------------------\ Unit Tests (70%)
 /____________________\ - 单个函数/类
                        - 完全隔离
```

**为什么这样分配**:
- 单元测试快速、稳定、易维护
- 集成测试覆盖关键路径
- E2E 测试覆盖核心用户场景

---

## 1. 单元测试 (Unit Tests)

### 目标

测试单个函数或类的行为，完全隔离外部依赖。

### 覆盖范围

**packages/core**:
- 数据模型验证
- 异常类行为
- 工具类函数

**packages/storage**:
- 文件读写逻辑
- 路径处理
- 数据序列化

**packages/tools**:
- 工具执行逻辑
- 参数验证
- 错误处理

**packages/providers**:
- 消息格式转换
- 错误处理
- 重试逻辑

**packages/runtime**:
- Agent Loop 状态机
- Context 管理
- Token 计数

### 示例

**测试数据模型**:
```python
# tests/unit/core/test_models.py
import pytest
from agentos_core.types import Message, ToolCall

def test_message_creation():
    """测试消息创建"""
    msg = Message(
        role="user",
        content="Hello"
    )
    assert msg.role == "user"
    assert msg.content == "Hello"
    assert msg.timestamp is not None

def test_message_validation():
    """测试消息验证"""
    with pytest.raises(ValueError):
        Message(role="invalid", content="test")

def test_tool_call_serialization():
    """测试工具调用序列化"""
    call = ToolCall(
        id="call_123",
        name="file_read",
        arguments={"path": "/tmp/test.txt"}
    )
    json_str = call.model_dump_json()
    restored = ToolCall.model_validate_json(json_str)
    assert restored == call
```

**测试工具执行**:
```python
# tests/unit/tools/test_file_tools.py
import pytest
from pathlib import Path
from agentos_tools import FileReadTool, FileWriteTool

@pytest.fixture
def temp_file(tmp_path):
    """创建临时文件"""
    file = tmp_path / "test.txt"
    file.write_text("Hello World")
    return file

@pytest.mark.asyncio
async def test_file_read_success(temp_file):
    """测试文件读取成功"""
    tool = FileReadTool()
    result = await tool.execute(path=str(temp_file))

    assert result.success
    assert result.data["content"] == "Hello World"

@pytest.mark.asyncio
async def test_file_read_not_found():
    """测试文件不存在"""
    tool = FileReadTool()
    result = await tool.execute(path="/nonexistent/file.txt")

    assert not result.success
    assert "not found" in result.error.lower()

@pytest.mark.asyncio
async def test_file_write_success(tmp_path):
    """测试文件写入"""
    tool = FileWriteTool()
    target = tmp_path / "output.txt"

    result = await tool.execute(
        path=str(target),
        content="Test content"
    )

    assert result.success
    assert target.read_text() == "Test content"

@pytest.mark.asyncio
async def test_file_write_path_traversal():
    """测试路径遍历攻击防护"""
    tool = FileWriteTool()

    result = await tool.execute(
        path="../../../etc/passwd",
        content="malicious"
    )

    assert not result.success
    assert "path" in result.error.lower()
```

**测试存储层**:
```python
# tests/unit/storage/test_session_store.py
import pytest
from agentos_storage import FileSessionStore
from agentos_core.types import Message

@pytest.fixture
def store(tmp_path):
    """创建临时存储"""
    return FileSessionStore(base_path=str(tmp_path))

@pytest.mark.asyncio
async def test_create_session(store):
    """测试创建会话"""
    await store.create_session(
        session_id="test:123",
        user_id="user1",
        channel="cli",
        context_id="123"
    )

    metadata = await store.get_session_metadata("test:123")
    assert metadata.session_id == "test:123"
    assert metadata.user_id == "user1"

@pytest.mark.asyncio
async def test_save_and_load_messages(store):
    """测试保存和加载消息"""
    await store.create_session(
        session_id="test:123",
        user_id="user1",
        channel="cli",
        context_id="123"
    )

    # 保存消息
    msg1 = Message(role="user", content="Hello")
    msg2 = Message(role="assistant", content="Hi")

    await store.save_message("test:123", msg1)
    await store.save_message("test:123", msg2)

    # 加载历史
    history = await store.load_history("test:123")

    assert len(history) == 2
    assert history[0].content == "Hello"
    assert history[1].content == "Hi"

@pytest.mark.asyncio
async def test_concurrent_writes(store):
    """测试并发写入"""
    await store.create_session(
        session_id="test:123",
        user_id="user1",
        channel="cli",
        context_id="123"
    )

    # 并发写入 100 条消息
    tasks = []
    for i in range(100):
        msg = Message(role="user", content=f"Message {i}")
        tasks.append(store.save_message("test:123", msg))

    await asyncio.gather(*tasks)

    # 验证所有消息都保存了
    history = await store.load_history("test:123")
    assert len(history) == 100
```

### 工具和配置

**pytest 配置**:
```ini
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--cov=packages",
    "--cov-report=html",
    "--cov-report=term-missing",
    "-v"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow tests"
]
```

**运行单元测试**:
```bash
# 运行所有单元测试
pytest -m unit

# 运行特定模块
pytest tests/unit/tools/

# 带覆盖率
pytest -m unit --cov

# 并行运行
pytest -m unit -n auto
```

---

## 2. 集成测试 (Integration Tests)

### 目标

测试多个模块协同工作，部分使用真实依赖，部分使用 mock。

### 覆盖范围

**Storage + Runtime**:
- Agent Loop 使用真实存储
- 会话历史持久化

**Runtime + Tools**:
- Agent 调用真实工具
- 工具结果处理

**Providers + Runtime**:
- LLM 调用（使用 mock）
- 工具调用流程

### 示例

**测试 Agent + Storage 集成**:
```python
# tests/integration/test_agent_storage.py
import pytest
from agentos_runtime import AgentLoop
from agentos_storage import FileSessionStore
from agentos_providers import MockLLMProvider
from agentos_tools import FileReadTool

@pytest.fixture
def agent_with_storage(tmp_path):
    """创建带存储的 Agent"""
    store = FileSessionStore(base_path=str(tmp_path))

    # Mock LLM 返回工具调用
    llm = MockLLMProvider(responses=[
        {
            "role": "assistant",
            "content": "",
            "tool_calls": [{
                "id": "call_1",
                "name": "file_read",
                "arguments": {"path": "/tmp/test.txt"}
            }]
        },
        {
            "role": "assistant",
            "content": "文件内容是: Hello World"
        }
    ])

    agent = AgentLoop(
        llm=llm,
        tools=[FileReadTool()],
        session_store=store
    )

    return agent, store

@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_persists_history(agent_with_storage, tmp_path):
    """测试 Agent 持久化历史"""
    agent, store = agent_with_storage

    # 创建测试文件
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello World")

    # 运行 Agent
    session_id = "test:123"
    await store.create_session(
        session_id=session_id,
        user_id="user1",
        channel="cli",
        context_id="123"
    )

    messages = [
        Message(role="user", content="读取 /tmp/test.txt")
    ]

    response = await agent.run(session_id, messages)

    # 验证历史被保存
    history = await store.load_history(session_id)

    assert len(history) >= 3  # user + assistant + tool
    assert any(msg.role == "tool" for msg in history)
    assert history[-1].content == "文件内容是: Hello World"
```

**测试 Agent + Tools 集成**:
```python
# tests/integration/test_agent_tools.py
import pytest
from agentos_runtime import AgentLoop
from agentos_providers import MockLLMProvider
from agentos_tools import FileWriteTool, FileReadTool

@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_multi_tool_workflow(tmp_path):
    """测试 Agent 多工具工作流"""

    # Mock LLM 返回多个工具调用
    llm = MockLLMProvider(responses=[
        # 第一轮：写文件
        {
            "role": "assistant",
            "tool_calls": [{
                "id": "call_1",
                "name": "file_write",
                "arguments": {
                    "path": str(tmp_path / "test.txt"),
                    "content": "Hello"
                }
            }]
        },
        # 第二轮：读文件
        {
            "role": "assistant",
            "tool_calls": [{
                "id": "call_2",
                "name": "file_read",
                "arguments": {
                    "path": str(tmp_path / "test.txt")
                }
            }]
        },
        # 第三轮：返回结果
        {
            "role": "assistant",
            "content": "文件已创建并读取，内容是: Hello"
        }
    ])

    agent = AgentLoop(
        llm=llm,
        tools=[FileWriteTool(), FileReadTool()],
        max_iterations=10
    )

    messages = [
        Message(role="user", content="创建文件并读取")
    ]

    response = await agent.run("test:123", messages)

    # 验证文件被创建
    assert (tmp_path / "test.txt").exists()
    assert (tmp_path / "test.txt").read_text() == "Hello"

    # 验证最终响应
    assert "Hello" in response.content
```

**测试错误恢复**:
```python
# tests/integration/test_error_recovery.py
import pytest
from agentos_runtime import AgentLoop
from agentos_providers import MockLLMProvider
from agentos_tools import FileReadTool

@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_handles_tool_error():
    """测试 Agent 处理工具错误"""

    llm = MockLLMProvider(responses=[
        # 第一轮：调用不存在的文件
        {
            "role": "assistant",
            "tool_calls": [{
                "id": "call_1",
                "name": "file_read",
                "arguments": {"path": "/nonexistent.txt"}
            }]
        },
        # 第二轮：处理错误
        {
            "role": "assistant",
            "content": "抱歉，文件不存在"
        }
    ])

    agent = AgentLoop(
        llm=llm,
        tools=[FileReadTool()]
    )

    messages = [
        Message(role="user", content="读取文件")
    ]

    response = await agent.run("test:123", messages)

    # 验证 Agent 优雅处理错误
    assert "不存在" in response.content
    assert response.success
```

### 运行集成测试

```bash
# 运行所有集成测试
pytest -m integration

# 运行特定集成测试
pytest tests/integration/test_agent_storage.py

# 带详细输出
pytest -m integration -v -s
```

---

## 3. 端到端测试 (E2E Tests)

### 目标

测试完整的用户流程，使用真实环境（除了 LLM）。

### 覆盖范围

**核心用户场景**:
- 启动 CLI 并进行对话
- 多轮对话
- 工具调用
- 会话恢复

### 示例

**测试 CLI 交互**:
```python
# tests/e2e/test_cli.py
import pytest
from click.testing import CliRunner
from agentos_cli.main import cli

@pytest.fixture
def runner():
    return CliRunner()

@pytest.mark.e2e
def test_cli_chat_session(runner, tmp_path, monkeypatch):
    """测试 CLI 对话会话"""

    # 设置临时配置
    config_dir = tmp_path / ".agentos"
    monkeypatch.setenv("AGENTOS_HOME", str(config_dir))

    # 配置 LLM（使用 mock）
    result = runner.invoke(cli, [
        "config", "set",
        "llm.provider", "mock"
    ])
    assert result.exit_code == 0

    # 启动对话（模拟输入）
    result = runner.invoke(cli, ["chat"], input="你好\n退出\n")

    assert result.exit_code == 0
    assert "你好" in result.output

@pytest.mark.e2e
def test_cli_session_persistence(runner, tmp_path, monkeypatch):
    """测试会话持久化"""

    config_dir = tmp_path / ".agentos"
    monkeypatch.setenv("AGENTOS_HOME", str(config_dir))

    # 第一次对话
    result = runner.invoke(cli, ["chat"], input="创建文件 test.txt\n退出\n")
    assert result.exit_code == 0

    # 列出会话
    result = runner.invoke(cli, ["session", "list"])
    assert result.exit_code == 0
    assert "cli:" in result.output

    # 查看会话历史
    result = runner.invoke(cli, ["session", "show", "cli:default"])
    assert result.exit_code == 0
    assert "创建文件" in result.output
```

**测试完整工作流**:
```python
# tests/e2e/test_workflows.py
import pytest
from agentos_cli.main import cli
from click.testing import CliRunner

@pytest.mark.e2e
@pytest.mark.slow
def test_file_manipulation_workflow(runner, tmp_path, monkeypatch):
    """测试文件操作工作流"""

    config_dir = tmp_path / ".agentos"
    workspace = tmp_path / "workspace"
    monkeypatch.setenv("AGENTOS_HOME", str(config_dir))
    monkeypatch.setenv("AGENTOS_WORKSPACE", str(workspace))

    # 配置
    runner.invoke(cli, ["config", "set", "llm.provider", "mock"])

    # 执行工作流
    commands = [
        "创建文件 notes.txt，内容是 'Meeting notes'",
        "读取 notes.txt",
        "在 notes.txt 末尾添加 '- Action item 1'",
        "退出"
    ]

    result = runner.invoke(cli, ["chat"], input="\n".join(commands))

    assert result.exit_code == 0

    # 验证文件被创建和修改
    notes_file = workspace / "notes.txt"
    assert notes_file.exists()
    content = notes_file.read_text()
    assert "Meeting notes" in content
    assert "Action item 1" in content
```

### 运行 E2E 测试

```bash
# 运行所有 E2E 测试
pytest -m e2e

# 跳过慢速测试
pytest -m "e2e and not slow"

# 带详细日志
pytest -m e2e -v -s --log-cli-level=DEBUG
```

---

## 4. Agent/Tool 模拟测试

### Mock LLM Provider

**为什么需要**:
- 真实 LLM 调用慢且昂贵
- 不确定性导致测试不稳定
- 需要测试特定场景（错误、边界情况）

**实现**:
```python
# packages/providers/src/agentos_providers/mock.py
from agentos_core.abstractions import LLMProvider
from typing import List, Dict, Any

class MockLLMProvider(LLMProvider):
    """Mock LLM Provider for testing"""

    def __init__(self, responses: List[Dict[str, Any]]):
        """
        Args:
            responses: 预定义的响应列表
        """
        self.responses = responses
        self.call_count = 0

    async def complete(
        self,
        messages: List[Message],
        tools: Optional[List[Tool]] = None,
        **kwargs
    ) -> Response:
        if self.call_count >= len(self.responses):
            raise ValueError("No more mock responses")

        response = self.responses[self.call_count]
        self.call_count += 1

        return Response(**response)

    def reset(self):
        """重置调用计数"""
        self.call_count = 0
```

**使用示例**:
```python
# 测试工具调用
llm = MockLLMProvider(responses=[
    {
        "role": "assistant",
        "content": "",
        "tool_calls": [{
            "id": "call_1",
            "name": "file_read",
            "arguments": {"path": "/tmp/test.txt"}
        }]
    },
    {
        "role": "assistant",
        "content": "文件内容是: ..."
    }
])

# 测试错误处理
llm = MockLLMProvider(responses=[
    {
        "role": "assistant",
        "content": "抱歉，我遇到了错误",
        "error": "rate_limit_exceeded"
    }
])
```

### Mock Tools

**为什么需要**:
- 隔离工具实现
- 测试 Agent 逻辑
- 避免副作用（文件操作、网络请求）

**实现**:
```python
# tests/mocks/tools.py
from agentos_core.abstractions import Tool, ToolResult

class MockTool(Tool):
    """Mock Tool for testing"""

    def __init__(
        self,
        name: str,
        description: str,
        result: ToolResult
    ):
        self.name = name
        self.description = description
        self.parameters = {}
        self._result = result
        self.call_count = 0
        self.last_args = None

    async def execute(self, **kwargs) -> ToolResult:
        self.call_count += 1
        self.last_args = kwargs
        return self._result
```

**使用示例**:
```python
# 测试 Agent 调用工具
mock_tool = MockTool(
    name="test_tool",
    description="A test tool",
    result=ToolResult(success=True, data={"result": "ok"})
)

agent = AgentLoop(llm=llm, tools=[mock_tool])
await agent.run("test:123", messages)

# 验证工具被调用
assert mock_tool.call_count == 1
assert mock_tool.last_args == {"param": "value"}
```

---

## 5. Sandbox/Policy/Routing 测试

### Policy Engine 测试

**测试权限检查**:
```python
# tests/unit/runtime/test_policy.py
import pytest
from agentos_runtime import PolicyEngine

def test_policy_allows_safe_tool():
    """测试允许安全工具"""
    policy = PolicyEngine(config={
        "allowed_tools": ["file_read", "web_search"]
    })

    assert policy.check_tool_permission("file_read", context={})
    assert not policy.check_tool_permission("shell_execute", context={})

def test_policy_path_restriction():
    """测试路径限制"""
    policy = PolicyEngine(config={
        "workspace_root": "/home/user/workspace"
    })

    assert policy.check_path_access("/home/user/workspace/file.txt")
    assert not policy.check_path_access("/etc/passwd")
    assert not policy.check_path_access("../../../etc/passwd")

def test_policy_rate_limiting():
    """测试速率限制"""
    policy = PolicyEngine(config={
        "rate_limit": {"max_requests": 10, "window": 60}
    })

    # 前 10 次应该通过
    for i in range(10):
        assert policy.check_rate_limit("user1")

    # 第 11 次应该被拒绝
    assert not policy.check_rate_limit("user1")
```

### Routing 测试

**测试消息路由**:
```python
# tests/unit/routing/test_message_bus.py
import pytest
from agentos_routing import MessageBus

@pytest.mark.asyncio
async def test_message_bus_fifo():
    """测试消息按 FIFO 顺序"""
    bus = MessageBus()

    # 入队 3 条消息
    await bus.enqueue_inbound(msg1)
    await bus.enqueue_inbound(msg2)
    await bus.enqueue_inbound(msg3)

    # 出队应该按顺序
    assert await bus.dequeue_inbound() == msg1
    assert await bus.dequeue_inbound() == msg2
    assert await bus.dequeue_inbound() == msg3

@pytest.mark.asyncio
async def test_message_bus_concurrent():
    """测试并发入队"""
    bus = MessageBus()

    # 并发入队 100 条消息
    tasks = [
        bus.enqueue_inbound(Message(role="user", content=f"msg{i}"))
        for i in range(100)
    ]
    await asyncio.gather(*tasks)

    # 验证所有消息都入队了
    count = 0
    while not bus.is_empty():
        await bus.dequeue_inbound()
        count += 1

    assert count == 100
```

---

## 6. 回归测试

### 目标

确保新代码不破坏现有功能。

### 策略

**自动化回归测试**:
```bash
# 每次提交前运行
pre-commit run --all-files

# CI 中运行完整测试套件
pytest --cov --cov-fail-under=70
```

**快照测试**:
```python
# tests/snapshots/test_agent_responses.py
import pytest
from syrupy import SnapshotAssertion

@pytest.mark.snapshot
def test_agent_response_format(snapshot: SnapshotAssertion):
    """测试 Agent 响应格式不变"""
    agent = create_test_agent()
    response = await agent.run("test:123", [
        Message(role="user", content="Hello")
    ])

    # 第一次运行会创建快照
    # 后续运行会对比快照
    assert response.model_dump() == snapshot
```

**性能回归测试**:
```python
# tests/performance/test_benchmarks.py
import pytest

@pytest.mark.benchmark
def test_session_load_performance(benchmark):
    """测试会话加载性能"""
    store = create_test_store_with_1000_messages()

    result = benchmark(
        lambda: asyncio.run(store.load_history("test:123"))
    )

    # 确保性能不退化
    assert result.stats.mean < 1.0  # 平均 < 1 秒
```

---

## 测试覆盖率目标

| 模块 | 目标覆盖率 | 原因 |
|-----|-----------|------|
| core | 90% | 基础抽象，必须稳定 |
| storage | 85% | 数据持久化，关键 |
| tools | 80% | 工具多样，部分难测 |
| providers | 75% | 外部依赖多 |
| runtime | 85% | 核心逻辑 |
| channels | 70% | 平台特定代码 |
| cli | 60% | UI 代码，难测 |

**总体目标**: 70%+

---

## CI/CD 集成

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install poetry
          poetry install

      - name: Run linters
        run: |
          poetry run ruff check .
          poetry run mypy packages

      - name: Run unit tests
        run: |
          poetry run pytest -m unit --cov

      - name: Run integration tests
        run: |
          poetry run pytest -m integration

      - name: Run E2E tests
        run: |
          poetry run pytest -m "e2e and not slow"

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 总结

**测试优先级**:
1. 单元测试（快速反馈）
2. 集成测试（关键路径）
3. E2E 测试（核心场景）

**测试原则**:
- 快速：单元测试 < 1s，集成测试 < 10s
- 稳定：避免 flaky tests
- 隔离：测试间互不影响
- 可维护：清晰的测试代码

**持续改进**:
- 定期审查测试覆盖率
- 修复 flaky tests
- 添加回归测试
- 优化慢速测试
