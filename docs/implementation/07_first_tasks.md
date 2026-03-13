# 首批开发任务

## 概述

本文档提供可直接执行的开发任务清单，每个任务都有明确的背景、目标、依赖、输入输出和完成标准。任务粒度适合 1-2 天完成。

---

## Phase 1: 项目初始化 (Week 1, Day 1-2)

### Task 1.1: 创建 Monorepo 结构

**背景**:
- 需要建立项目的基础目录结构
- 使用 Poetry workspace 管理多个包

**目标**:
- 创建完整的目录结构
- 配置 Poetry workspace
- 配置开发工具

**依赖**: 无

**输入**: 无

**输出**:
- 完整的目录结构
- `pyproject.toml` (根)
- 各包的 `pyproject.toml`

**步骤**:

1. 创建根目录结构
```bash
mkdir -p agentos/{packages,apps,services,examples,docs,scripts,tests}
cd agentos
```

2. 创建根 `pyproject.toml`
```toml
[tool.poetry]
name = "agentos"
version = "0.1.0"
description = "A lightweight AgentOS framework"
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.10"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"
pytest-asyncio = "^0.21.0"
pytest-cov = "^4.1.0"
black = "^23.7.0"
ruff = "^0.0.285"
mypy = "^1.5.0"
pre-commit = "^3.3.3"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

3. 创建包结构
```bash
# Core package
mkdir -p packages/core/src/agentos_core/{abstractions,types,exceptions}
mkdir -p packages/core/tests

# Storage package
mkdir -p packages/storage/src/agentos_storage
mkdir -p packages/storage/tests

# Providers package
mkdir -p packages/providers/src/agentos_providers
mkdir -p packages/providers/tests

# Tools package
mkdir -p packages/tools/src/agentos_tools
mkdir -p packages/tools/tests

# Channels package
mkdir -p packages/channels/src/agentos_channels
mkdir -p packages/channels/tests

# Runtime package
mkdir -p packages/runtime/src/agentos_runtime
mkdir -p packages/runtime/tests

# CLI app
mkdir -p apps/cli/src/agentos_cli
mkdir -p apps/cli/tests
```

4. 创建各包的 `pyproject.toml`
```bash
# 为每个包创建配置文件
# 示例: packages/core/pyproject.toml
```

5. 配置 pre-commit
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.0.285
    hooks:
      - id: ruff
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.0
    hooks:
      - id: mypy
```

6. 初始化 Git
```bash
git init
git add .
git commit -m "Initial project structure"
```

**完成标准**:
- [ ] 目录结构完整
- [ ] Poetry 可以识别所有包
- [ ] `poetry install` 成功
- [ ] Pre-commit hooks 安装成功

**验收命令**:
```bash
poetry install
poetry run pre-commit install
poetry run pre-commit run --all-files
```

---

### Task 1.2: 配置 CI/CD

**背景**:
- 需要自动化测试和代码质量检查
- 使用 GitHub Actions

**目标**:
- 配置自动化测试
- 配置代码质量检查
- 配置发布流程

**依赖**: Task 1.1

**输入**: 项目结构

**输出**: GitHub Actions workflows

**步骤**:

1. 创建测试 workflow
```yaml
# .github/workflows/test.yml
name: Test

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
      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
      - name: Install dependencies
        run: poetry install
      - name: Run tests
        run: poetry run pytest --cov
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

2. 创建 lint workflow
```yaml
# .github/workflows/lint.yml
name: Lint

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"
      - name: Install Poetry
        run: |
          curl -sSL https://install.python-poetry.org | python3 -
      - name: Install dependencies
        run: poetry install
      - name: Run black
        run: poetry run black --check .
      - name: Run ruff
        run: poetry run ruff check .
      - name: Run mypy
        run: poetry run mypy packages apps
```

**完成标准**:
- [ ] GitHub Actions 配置完成
- [ ] 测试 workflow 可以运行
- [ ] Lint workflow 可以运行

---

## Phase 2: Core 包实现 (Week 1, Day 3-4)

### Task 2.1: 定义核心抽象类

**背景**:
- 所有其他模块都依赖 core 包
- 需要定义清晰的接口

**目标**:
- 定义 Session, Agent, Tool, Channel, LLMProvider 抽象

**依赖**: Task 1.1

**输入**: 无

**输出**: `packages/core/src/agentos_core/abstractions/`

**步骤**:

1. 定义 Tool 抽象
```python
# packages/core/src/agentos_core/abstractions/tool.py
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from pydantic import BaseModel

class ToolResult(BaseModel):
    """工具执行结果"""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}

class Tool(ABC):
    """工具抽象基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """工具描述"""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, Any]:
        """参数 JSON Schema"""
        pass

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具"""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """转换为 LLM 工具定义格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
```

2. 定义 LLMProvider 抽象
```python
# packages/core/src/agentos_core/abstractions/llm.py
from abc import ABC, abstractmethod
from typing import List, Optional
from ..types import Message, Response

class LLMProvider(ABC):
    """LLM 提供者抽象"""

    @abstractmethod
    async def complete(
        self,
        messages: List[Message],
        tools: Optional[List[Dict]] = None,
        **kwargs
    ) -> Response:
        """完成对话"""
        pass

    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """估算 token 数量"""
        pass
```

3. 定义 Session 抽象
```python
# packages/core/src/agentos_core/abstractions/session.py
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from ..types import Message, SessionMetadata

class SessionStore(ABC):
    """会话存储抽象"""

    @abstractmethod
    async def create_session(
        self,
        session_id: str,
        user_id: str,
        channel: str,
        context_id: str,
        metadata: Optional[dict] = None
    ) -> None:
        pass

    @abstractmethod
    async def save_message(
        self,
        session_id: str,
        message: Message
    ) -> None:
        pass

    @abstractmethod
    async def load_history(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> List[Message]:
        pass

    @abstractmethod
    async def get_session_metadata(
        self,
        session_id: str
    ) -> SessionMetadata:
        pass
```

4. 定义 Channel 抽象
```python
# packages/core/src/agentos_core/abstractions/channel.py
from abc import ABC, abstractmethod
from ..types import InboundMessage, OutboundMessage

class Channel(ABC):
    """渠道抽象"""

    @property
    @abstractmethod
    def channel_id(self) -> str:
        pass

    @property
    @abstractmethod
    def channel_type(self) -> str:
        pass

    @abstractmethod
    async def start(self) -> None:
        """启动渠道"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """停止渠道"""
        pass

    @abstractmethod
    async def send(self, message: OutboundMessage) -> None:
        """发送消息"""
        pass

    @abstractmethod
    def is_authorized(self, user_id: str) -> bool:
        """检查用户授权"""
        pass
```

**完成标准**:
- [ ] 所有抽象类定义完成
- [ ] 有完整的 docstring
- [ ] 通过 mypy 类型检查
- [ ] 有基础的单元测试

**验收命令**:
```bash
poetry run mypy packages/core
poetry run pytest packages/core/tests
```

---

### Task 2.2: 定义数据模型

**背景**:
- 需要统一的数据模型
- 使用 Pydantic 进行验证

**目标**:
- 定义 Message, ToolCall, Config 等模型

**依赖**: Task 2.1

**输入**: 抽象类定义

**输出**: `packages/core/src/agentos_core/types/`

**步骤**:

1. 定义 Message 模型
```python
# packages/core/src/agentos_core/types/message.py
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

class ToolCall(BaseModel):
    """工具调用"""
    id: str
    name: str
    arguments: dict

class Message(BaseModel):
    """消息模型"""
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)

    # 工具调用相关
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class InboundMessage(BaseModel):
    """入站消息"""
    session_id: str
    user_id: str
    channel: str
    content: str
    metadata: dict = Field(default_factory=dict)

class OutboundMessage(BaseModel):
    """出站消息"""
    session_id: str
    channel: str
    content: str
    metadata: dict = Field(default_factory=dict)
```

2. 定义 Response 模型
```python
# packages/core/src/agentos_core/types/response.py
from pydantic import BaseModel
from typing import Optional, List
from .message import ToolCall

class Response(BaseModel):
    """LLM 响应"""
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    finish_reason: str
    usage: dict = Field(default_factory=dict)
```

3. 定义 Config 模型
```python
# packages/core/src/agentos_core/types/config.py
from pydantic import BaseModel, Field
from typing import Optional, List

class LLMConfig(BaseModel):
    """LLM 配置"""
    provider: str = "litellm"
    model: str = "gpt-4"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None

class ChannelConfig(BaseModel):
    """渠道配置"""
    channel_type: str
    enabled: bool = True
    config: dict = Field(default_factory=dict)

class AgentConfig(BaseModel):
    """Agent 配置"""
    max_iterations: int = 10
    max_tokens: int = 4000
    timeout: int = 300

class Config(BaseModel):
    """全局配置"""
    llm: LLMConfig
    agent: AgentConfig = Field(default_factory=AgentConfig)
    channels: List[ChannelConfig] = Field(default_factory=list)
    storage_path: str = "~/.agentos"
```

**完成标准**:
- [ ] 所有数据模型定义完成
- [ ] Pydantic 验证正确
- [ ] 有序列化/反序列化测试

**验收命令**:
```bash
poetry run pytest packages/core/tests/test_types.py -v
```

---

### Task 2.3: 定义异常体系

**背景**:
- 需要统一的异常处理
- 便于错误追踪和处理

**目标**:
- 定义异常类层次结构

**依赖**: Task 2.1

**输入**: 无

**输出**: `packages/core/src/agentos_core/exceptions.py`

**步骤**:

```python
# packages/core/src/agentos_core/exceptions.py

class AgentOSError(Exception):
    """AgentOS 基础异常"""
    pass

# Storage 相关
class StorageError(AgentOSError):
    """存储错误"""
    pass

class SessionNotFoundError(StorageError):
    """会话不存在"""
    pass

class SessionAlreadyExistsError(StorageError):
    """会话已存在"""
    pass

# Tool 相关
class ToolError(AgentOSError):
    """工具错误"""
    pass

class ToolExecutionError(ToolError):
    """工具执行失败"""
    pass

class ToolNotFoundError(ToolError):
    """工具不存在"""
    pass

class ToolValidationError(ToolError):
    """工具参数验证失败"""
    pass

# LLM 相关
class LLMError(AgentOSError):
    """LLM 错误"""
    pass

class LLMTimeoutError(LLMError):
    """LLM 调用超时"""
    pass

class LLMRateLimitError(LLMError):
    """LLM 速率限制"""
    pass

# Channel 相关
class ChannelError(AgentOSError):
    """渠道错误"""
    pass

class ChannelNotFoundError(ChannelError):
    """渠道不存在"""
    pass

class UnauthorizedError(ChannelError):
    """未授权"""
    pass

# Runtime 相关
class RuntimeError(AgentOSError):
    """运行时错误"""
    pass

class MaxIterationsExceededError(RuntimeError):
    """超过最大迭代次数"""
    pass

class ContextTooLongError(RuntimeError):
    """上下文过长"""
    pass
```

**完成标准**:
- [ ] 异常类定义完成
- [ ] 有继承关系
- [ ] 有 docstring

---

## Phase 3: Storage 包实现 (Week 1, Day 5)

### Task 3.1: 实现 FileSessionStore

**背景**:
- 需要持久化会话历史
- 使用 JSONL 格式

**目标**:
- 实现基于文件系统的会话存储

**依赖**: Task 2.1, Task 2.2

**输入**: SessionStore 抽象

**输出**: `packages/storage/src/agentos_storage/session.py`

**步骤**:

```python
# packages/storage/src/agentos_storage/session.py
import asyncio
import hashlib
import json
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
import aiofiles

from agentos_core.abstractions import SessionStore
from agentos_core.types import Message, SessionMetadata
from agentos_core.exceptions import (
    SessionNotFoundError,
    SessionAlreadyExistsError,
    StorageError
)

class FileSessionStore(SessionStore):
    """基于文件系统的会话存储"""

    def __init__(self, base_path: str = "~/.agentos/sessions"):
        self.base_path = Path(base_path).expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._locks: Dict[str, asyncio.Lock] = {}

    def _get_session_path(self, session_id: str) -> Path:
        """获取会话文件路径（使用哈希分片）"""
        hash_prefix = hashlib.md5(session_id.encode()).hexdigest()[:2]
        session_dir = self.base_path / hash_prefix
        session_dir.mkdir(parents=True, exist_ok=True)
        return session_dir / f"{session_id}.jsonl"

    def _get_metadata_path(self, session_id: str) -> Path:
        """获取元数据文件路径"""
        return self._get_session_path(session_id).with_suffix(".meta.json")

    def _get_lock(self, session_id: str) -> asyncio.Lock:
        """获取会话锁"""
        if session_id not in self._locks:
            self._locks[session_id] = asyncio.Lock()
        return self._locks[session_id]

    async def create_session(
        self,
        session_id: str,
        user_id: str,
        channel: str,
        context_id: str,
        metadata: Optional[dict] = None
    ) -> None:
        """创建新会话"""
        meta_path = self._get_metadata_path(session_id)

        if meta_path.exists():
            raise SessionAlreadyExistsError(f"Session {session_id} already exists")

        session_meta = SessionMetadata(
            session_id=session_id,
            user_id=user_id,
            channel=channel,
            context_id=context_id,
            created_at=datetime.utcnow(),
            last_active=datetime.utcnow(),
            message_count=0,
            metadata=metadata or {}
        )

        async with aiofiles.open(meta_path, 'w') as f:
            await f.write(session_meta.model_dump_json())

        # 创建空的消息文件
        session_path = self._get_session_path(session_id)
        session_path.touch()

    async def save_message(
        self,
        session_id: str,
        message: Message
    ) -> None:
        """保存消息（追加式）"""
        session_path = self._get_session_path(session_id)

        if not session_path.exists():
            raise SessionNotFoundError(f"Session {session_id} not found")

        lock = self._get_lock(session_id)

        async with lock:
            # 追加消息
            async with aiofiles.open(session_path, 'a') as f:
                await f.write(message.model_dump_json() + '\n')

            # 更新元数据
            await self._update_metadata(session_id)

    async def _update_metadata(self, session_id: str) -> None:
        """更新会话元数据"""
        meta_path = self._get_metadata_path(session_id)
        session_path = self._get_session_path(session_id)

        # 读取现有元数据
        async with aiofiles.open(meta_path, 'r') as f:
            content = await f.read()
            meta = SessionMetadata.model_validate_json(content)

        # 更新
        meta.last_active = datetime.utcnow()
        meta.message_count = sum(1 for _ in open(session_path))

        # 写回
        async with aiofiles.open(meta_path, 'w') as f:
            await f.write(meta.model_dump_json())

    async def load_history(
        self,
        session_id: str,
        limit: Optional[int] = None,
        before: Optional[datetime] = None
    ) -> List[Message]:
        """加载会话历史"""
        session_path = self._get_session_path(session_id)

        if not session_path.exists():
            raise SessionNotFoundError(f"Session {session_id} not found")

        messages = []

        async with aiofiles.open(session_path, 'r') as f:
            async for line in f:
                if line.strip():
                    msg = Message.model_validate_json(line)

                    if before and msg.timestamp >= before:
                        continue

                    messages.append(msg)

        # 应用 limit
        if limit:
            messages = messages[-limit:]

        return messages

    async def get_session_metadata(
        self,
        session_id: str
    ) -> SessionMetadata:
        """获取会话元数据"""
        meta_path = self._get_metadata_path(session_id)

        if not meta_path.exists():
            raise SessionNotFoundError(f"Session {session_id} not found")

        async with aiofiles.open(meta_path, 'r') as f:
            content = await f.read()
            return SessionMetadata.model_validate_json(content)

    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        channel: Optional[str] = None,
        active_since: Optional[datetime] = None
    ) -> List[SessionMetadata]:
        """列出会话"""
        sessions = []

        # 遍历所有分片目录
        for shard_dir in self.base_path.iterdir():
            if not shard_dir.is_dir():
                continue

            # 遍历元数据文件
            for meta_file in shard_dir.glob("*.meta.json"):
                async with aiofiles.open(meta_file, 'r') as f:
                    content = await f.read()
                    meta = SessionMetadata.model_validate_json(content)

                    # 应用过滤
                    if user_id and meta.user_id != user_id:
                        continue
                    if channel and meta.channel != channel:
                        continue
                    if active_since and meta.last_active < active_since:
                        continue

                    sessions.append(meta)

        # 按 last_active 降序排序
        sessions.sort(key=lambda x: x.last_active, reverse=True)

        return sessions

    async def delete_session(self, session_id: str) -> None:
        """删除会话"""
        session_path = self._get_session_path(session_id)
        meta_path = self._get_metadata_path(session_id)

        if not session_path.exists():
            raise SessionNotFoundError(f"Session {session_id} not found")

        session_path.unlink()
        meta_path.unlink()

        # 清理锁
        if session_id in self._locks:
            del self._locks[session_id]
```

**完成标准**:
- [ ] 所有方法实现完成
- [ ] 支持并发写入
- [ ] 有完整的单元测试
- [ ] 测试覆盖率 > 80%

**验收命令**:
```bash
poetry run pytest packages/storage/tests/test_session.py -v --cov
```

---

## 后续任务预览

由于篇幅限制，后续任务包括：

**Week 2**:
- Task 4.1-4.3: 实现 LiteLLMProvider
- Task 5.1-5.3: 实现核心工具 (FileRead, FileWrite, Shell)

**Week 3**:
- Task 6.1-6.3: 实现 AgentLoop
- Task 7.1-7.2: 集成测试

**Week 4**:
- Task 8.1-8.3: 实现 CLI Channel 和应用

**Week 5-6**:
- Bug 修复、优化、文档、发布

每个任务都遵循相同的格式：背景、目标、依赖、输入输出、步骤、完成标准。

---

## 任务执行建议

**对于 AI 辅助开发**:
1. 按顺序执行任务
2. 每个任务完成后运行验收命令
3. 提交代码前运行完整测试套件
4. 保持小步快跑，频繁提交

**对于团队协作**:
1. 可以并行执行不同 Phase 的任务
2. 使用 Git 分支管理
3. Code Review 检查完成标准
4. 定期同步进度

**风险控制**:
1. 每天结束时确保代码可运行
2. 遇到阻塞及时调整计划
3. 优先完成核心功能
4. 文档可以后补但不能缺失
