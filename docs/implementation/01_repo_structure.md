# 仓库结构设计

## 推荐方案：Monorepo

### 为什么选择 Monorepo

**优势**:
- ✅ 统一版本管理，避免依赖地狱
- ✅ 代码共享容易，重构方便
- ✅ 原子性提交（跨模块修改一次提交）
- ✅ 统一的 CI/CD 和工具链
- ✅ 适合早期快速迭代

**劣势**:
- ⚠️ 仓库体积会增长（但早期不是问题）
- ⚠️ 需要好的工具支持（如 pnpm workspace / poetry workspace）

**何时考虑拆分**:
- 团队规模 > 10 人
- 某个模块需要独立发布周期
- 性能成为瓶颈（CI 时间过长）

---

## 推荐目录结构

```
agentos/
├── README.md
├── pyproject.toml              # 根项目配置
├── .github/
│   └── workflows/              # CI/CD
│       ├── test.yml
│       ├── lint.yml
│       └── release.yml
│
├── packages/                   # 核心库（可独立发布）
│   ├── core/                   # 核心抽象和接口
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── agentos_core/
│   │   │       ├── __init__.py
│   │   │       ├── abstractions/    # Session, Agent, Tool 等抽象
│   │   │       ├── types/           # 类型定义
│   │   │       └── exceptions/      # 异常定义
│   │   └── tests/
│   │
│   ├── runtime/                # Agent 执行运行时
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── agentos_runtime/
│   │   │       ├── __init__.py
│   │   │       ├── loop.py          # Agent Loop
│   │   │       ├── executor.py      # Tool Executor
│   │   │       └── policy.py        # Policy Engine
│   │   └── tests/
│   │
│   ├── storage/                # 状态存储
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── agentos_storage/
│   │   │       ├── __init__.py
│   │   │       ├── session.py       # Session Store
│   │   │       ├── memory.py        # Memory Store
│   │   │       └── workspace.py     # Workspace
│   │   └── tests/
│   │
│   ├── channels/               # Channel 适配器
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── agentos_channels/
│   │   │       ├── __init__.py
│   │   │       ├── base.py          # BaseChannel
│   │   │       ├── telegram.py
│   │   │       ├── slack.py
│   │   │       └── cli.py           # CLI Channel（开发用）
│   │   └── tests/
│   │
│   ├── tools/                  # 内置工具
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── agentos_tools/
│   │   │       ├── __init__.py
│   │   │       ├── base.py          # BaseTool
│   │   │       ├── filesystem.py
│   │   │       ├── shell.py
│   │   │       ├── web.py
│   │   │       └── registry.py      # Tool Registry
│   │   └── tests/
│   │
│   └── providers/              # LLM Provider 抽象
│       ├── pyproject.toml
│       ├── src/
│       │   └── agentos_providers/
│       │       ├── __init__.py
│       │       ├── base.py          # BaseLLMProvider
│       │       ├── litellm.py       # LiteLLM 适配器
│       │       └── openai.py        # OpenAI 直接适配器
│       └── tests/
│
├── apps/                       # 可执行应用
│   ├── server/                 # HTTP/WebSocket 服务器
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── agentos_server/
│   │   │       ├── __init__.py
│   │   │       ├── main.py          # FastAPI 入口
│   │   │       ├── api/             # REST API
│   │   │       ├── websocket/       # WebSocket
│   │   │       └── config.py
│   │   └── tests/
│   │
│   └── cli/                    # 命令行工具
│       ├── pyproject.toml
│       ├── src/
│       │   └── agentos_cli/
│       │       ├── __init__.py
│       │       ├── main.py          # Click 入口
│       │       └── commands/
│       └── tests/
│
├── services/                   # 独立服务（可选，后期）
│   ├── orchestrator/           # Agent 编排服务
│   └── router/                 # 消息路由服务
│
├── examples/                   # 示例和教程
│   ├── quickstart/
│   ├── custom_tool/
│   └── custom_channel/
│
├── docs/                       # 文档
│   ├── system-design/
│   ├── blueprint/
│   ├── implementation/         # 当前文档
│   └── api/                    # API 文档
│
└── scripts/                    # 开发脚本
    ├── setup_dev.sh
    ├── run_tests.sh
    └── build.sh
```

---

## 各 Package 职责说明

### packages/core

**职责**: 定义核心抽象和类型

**包含**:
- `Session`, `Agent`, `Tool`, `Channel` 等抽象基类
- 消息类型 (`Message`, `InboundMessage`, `OutboundMessage`)
- 配置类型 (`Config`, `ChannelConfig`, `ToolConfig`)
- 异常类型 (`AgentOSError`, `ToolExecutionError`)

**依赖**: 无（纯抽象）

**为什么独立**:
- 所有其他包都依赖它
- 变化频率低，稳定
- 可以独立发布给第三方开发者

**示例代码**:
```python
# packages/core/src/agentos_core/abstractions/tool.py
from abc import ABC, abstractmethod
from typing import Any, Dict
from pydantic import BaseModel

class ToolResult(BaseModel):
    success: bool
    data: Any
    error: Optional[str] = None

class Tool(ABC):
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON Schema

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass
```

---

### packages/runtime

**职责**: Agent 执行运行时

**包含**:
- `AgentLoop`: 主执行循环
- `ToolExecutor`: 工具执行器
- `PolicyEngine`: 策略引擎（权限检查、资源限制）
- `ContextManager`: 上下文管理（token 计数、历史管理）

**依赖**: `core`, `providers`, `tools`

**为什么独立**:
- 核心业务逻辑
- 可能有多种实现（单 agent、多 agent）
- 便于测试和优化

**示例代码**:
```python
# packages/runtime/src/agentos_runtime/loop.py
from agentos_core.abstractions import Agent, Tool
from agentos_providers.base import LLMProvider

class AgentLoop:
    def __init__(
        self,
        llm: LLMProvider,
        tools: List[Tool],
        max_iterations: int = 10
    ):
        self.llm = llm
        self.tools = {t.name: t for t in tools}
        self.max_iterations = max_iterations

    async def run(self, messages: List[Message]) -> Response:
        for i in range(self.max_iterations):
            response = await self.llm.complete(messages, self.tools)
            if not response.tool_calls:
                return response
            # 执行工具调用...
```

---

### packages/storage

**职责**: 状态持久化

**包含**:
- `SessionStore`: 会话存储（JSONL 实现）
- `MemoryStore`: 记忆存储（Markdown 实现）
- `WorkspaceManager`: 工作空间管理
- `ConfigStore`: 配置存储

**依赖**: `core`

**为什么独立**:
- 存储实现可能变化（文件 → 数据库）
- 便于测试（可以 mock）
- 可以独立优化性能

**实现策略**:
- **MVP**: 文件系统实现（简单、零依赖）
- **后期**: 可选的数据库实现（PostgreSQL、SQLite）

---

### packages/channels

**职责**: 多渠道接入

**包含**:
- `BaseChannel`: 抽象基类
- 各平台实现: `TelegramChannel`, `SlackChannel`, `CLIChannel`
- `ChannelManager`: 管理多个 channel

**依赖**: `core`

**为什么独立**:
- 每个 channel 相对独立
- 便于增加新 channel
- 可以按需加载（减少依赖）

**实现策略**:
- **MVP**: 只实现 `CLIChannel`（开发测试用）
- **Week 2**: 添加 `TelegramChannel`（最常用）
- **后期**: 按需添加其他 channel

---

### packages/tools

**职责**: 内置工具集

**包含**:
- `BaseTool`: 抽象基类
- 核心工具: `FileReadTool`, `FileWriteTool`, `ShellTool`, `WebSearchTool`
- `ToolRegistry`: 工具注册和发现

**依赖**: `core`

**为什么独立**:
- 工具集可以独立扩展
- 便于第三方贡献工具
- 可以按需加载

**实现策略**:
- **MVP**: 3-5 个核心工具
- **后期**: 支持插件工具（MCP 协议）

---

### packages/providers

**职责**: LLM Provider 抽象

**包含**:
- `BaseLLMProvider`: 抽象基类
- `LiteLLMProvider`: LiteLLM 适配器（推荐）
- `OpenAIProvider`: OpenAI 直接适配器（备选）

**依赖**: `core`

**为什么独立**:
- Provider 实现可能变化
- 便于测试（可以 mock）
- 可以支持多种 provider

**实现策略**:
- **MVP**: 只实现 `LiteLLMProvider`（支持 20+ providers）
- **后期**: 按需添加直接适配器

---

### apps/server

**职责**: HTTP/WebSocket 服务器

**包含**:
- FastAPI 应用
- REST API 端点
- WebSocket 端点
- 认证中间件

**依赖**: 所有 `packages/*`

**为什么独立**:
- 部署单元
- 可以独立扩展（如添加 GraphQL）
- 便于容器化

**实现策略**:
- **MVP**: 不实现（先用 CLI）
- **Week 4**: 实现基础 HTTP API
- **后期**: 添加 WebSocket 支持

---

### apps/cli

**职责**: 命令行工具

**包含**:
- Click 命令行应用
- 交互式 REPL
- 配置管理命令

**依赖**: 所有 `packages/*`

**为什么独立**:
- 部署单元
- 开发和测试的主要入口
- 便于打包分发

**实现策略**:
- **Week 1**: 实现基础 CLI
- **MVP**: 完整的交互式体验

---

## 依赖关系图

```
apps/cli ────────┐
apps/server ─────┼──→ packages/runtime ──→ packages/core
                 │         ↓
                 ├──→ packages/channels ──→ packages/core
                 │         ↓
                 ├──→ packages/tools ────→ packages/core
                 │         ↓
                 ├──→ packages/providers ─→ packages/core
                 │         ↓
                 └──→ packages/storage ───→ packages/core
```

**关键原则**:
- `core` 无依赖
- 其他 `packages` 只依赖 `core`
- `apps` 依赖所有 `packages`
- `packages` 之间不互相依赖（除了 `core`）

---

## 技术栈选择

### 语言和框架

**Python 3.11+**
- 为什么: 丰富的 AI/ML 生态，asyncio 成熟
- 类型检查: mypy
- 代码格式: ruff

**依赖管理**:
- **推荐**: Poetry（支持 workspace）
- 备选: PDM, Hatch

**Web 框架**:
- FastAPI（异步、类型安全、自动文档）

**CLI 框架**:
- Click（简单、强大）

### 关键依赖

**必需**:
- `pydantic` (v2): 数据验证和配置
- `litellm`: LLM provider 抽象
- `aiofiles`: 异步文件操作
- `structlog`: 结构化日志

**可选**:
- `redis`: 消息队列（后期）
- `sqlalchemy`: 数据库（后期）
- `prometheus-client`: 监控（后期）

---

## 开发工具链

### 代码质量

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

### CI/CD

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install poetry
      - run: poetry install
      - run: poetry run pytest
      - run: poetry run mypy .
      - run: poetry run ruff check .
```

---

## Monorepo 管理

### Poetry Workspace 配置

```toml
# 根 pyproject.toml
[tool.poetry]
name = "agentos"
version = "0.1.0"
description = "AgentOS - A modular agent operating system"

[tool.poetry.dependencies]
python = "^3.11"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0"
pytest-asyncio = "^0.21"
mypy = "^1.0"
ruff = "^0.1"

# Workspace 配置
[tool.poetry.workspace]
packages = [
    "packages/core",
    "packages/runtime",
    "packages/storage",
    "packages/channels",
    "packages/tools",
    "packages/providers",
    "apps/cli",
    "apps/server",
]
```

### 各 Package 配置示例

```toml
# packages/core/pyproject.toml
[tool.poetry]
name = "agentos-core"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.11"
pydantic = "^2.0"
```

```toml
# packages/runtime/pyproject.toml
[tool.poetry]
name = "agentos-runtime"
version = "0.1.0"

[tool.poetry.dependencies]
python = "^3.11"
agentos-core = { path = "../core", develop = true }
agentos-providers = { path = "../providers", develop = true }
agentos-tools = { path = "../tools", develop = true }
```

---

## 版本管理策略

### 语义化版本

- `0.1.0`: MVP
- `0.2.0`: 添加主要功能
- `0.x.y`: 迭代开发
- `1.0.0`: 生产就绪

### 发布策略

**开发阶段** (0.x):
- 所有 packages 统一版本号
- 一起发布

**成熟阶段** (1.x+):
- 核心 packages (`core`, `runtime`) 独立版本
- 其他 packages 可以独立迭代

---

## 迁移到 Polyrepo 的时机

**何时考虑**:
1. 团队规模 > 10 人
2. 某些 packages 需要独立发布周期
3. CI 时间 > 30 分钟
4. 不同 packages 有不同的技术栈

**如何拆分**:
1. `core` → 独立仓库（最稳定）
2. `runtime` → 独立仓库
3. 其他按需拆分

**保持 Monorepo 的部分**:
- `apps/*` 可以保持在一起
- `examples/` 和 `docs/` 保持在一起

---

## 总结

**推荐方案**: Monorepo + Poetry Workspace

**核心原则**:
1. 清晰的模块边界
2. 单向依赖（避免循环）
3. 核心抽象稳定（`core` 包）
4. 应用层灵活（`apps/*`）

**演进路径**:
- Week 1-4: Monorepo 快速迭代
- Month 2-6: 稳定核心 packages
- Month 6+: 按需拆分到 Polyrepo
