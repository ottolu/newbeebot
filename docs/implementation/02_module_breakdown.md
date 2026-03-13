# 模块拆解与依赖

## 概述

本文档将系统拆解为可独立开发的模块，明确每个模块的输入输出、依赖关系、优先级和并行开发可能性。

---

## 模块依赖图

```
                    ┌─────────────┐
                    │    core     │ (L0: 基础层)
                    └─────────────┘
                           ↑
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────────┐         ┌─────────┐       ┌──────────┐
   │providers│         │ storage │       │ channels │ (L1: 适配层)
   └────────┘         └─────────┘       └──────────┘
        ↑                  ↑                  ↑
        │                  │                  │
        └──────────┬───────┴──────────────────┘
                   │
              ┌─────────┐
              │  tools  │ (L1: 适配层)
              └─────────┘
                   ↑
                   │
              ┌─────────┐
              │ runtime │ (L2: 业务层)
              └─────────┘
                   ↑
        ┌──────────┴──────────┐
        │                     │
   ┌─────────┐           ┌─────────┐
   │   cli   │           │ server  │ (L3: 应用层)
   └─────────┘           └─────────┘
```

---

## 模块详细拆解

### M1: core (核心抽象)

**优先级**: P0 (最高，所有模块依赖)

**职责**:
- 定义核心抽象类和接口
- 定义数据类型和模型
- 定义异常体系

**输入**: 无

**输出**:
- `Session`, `Agent`, `Tool`, `Channel` 等抽象基类
- `Message`, `ToolResult`, `Config` 等数据模型
- `AgentOSError` 等异常类

**依赖**: 无

**关键接口**:
```python
# abstractions/session.py
class Session(ABC):
    session_id: str
    user_id: str
    channel: str
    context_id: str

# abstractions/tool.py
class Tool(ABC):
    name: str
    description: str
    parameters: JSONSchema

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass

# abstractions/channel.py
class Channel(ABC):
    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def send(self, message: OutboundMessage) -> None:
        pass

# abstractions/llm.py
class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: List[Message],
        tools: Optional[List[Tool]] = None
    ) -> Response:
        pass
```

**完成标准**:
- [ ] 所有抽象类定义完成
- [ ] 类型定义完整（使用 Pydantic）
- [ ] 有完整的 docstring
- [ ] 通过 mypy 类型检查

**工作量估算**: 2-3 天

**可并行**: 无（必须最先完成）

---

### M2: storage (存储层)

**优先级**: P0 (核心功能)

**职责**:
- 会话历史持久化
- 记忆管理
- 工作空间文件管理

**输入**:
- Session 对象
- Message 对象
- Memory 对象

**输出**:
- 持久化的会话数据
- 可查询的历史记录
- 文件系统操作

**依赖**: `core`

**关键接口**:
```python
# session_store.py
class SessionStore(ABC):
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
    async def list_sessions(
        self,
        user_id: str
    ) -> List[SessionMetadata]:
        pass

# memory_store.py
class MemoryStore(ABC):
    @abstractmethod
    async def save_memory(
        self,
        session_id: str,
        memory: Memory
    ) -> None:
        pass

    @abstractmethod
    async def search_memories(
        self,
        query: str,
        limit: int = 10
    ) -> List[Memory]:
        pass

# workspace.py
class WorkspaceManager(ABC):
    @abstractmethod
    async def read_file(
        self,
        session_id: str,
        path: str
    ) -> bytes:
        pass

    @abstractmethod
    async def write_file(
        self,
        session_id: str,
        path: str,
        content: bytes
    ) -> None:
        pass
```

**实现策略**:
- **MVP**: 文件系统实现
  - Session: JSONL 文件 (`~/.agentos/sessions/{session_id}.jsonl`)
  - Memory: Markdown 文件 (`~/.agentos/memory/{session_id}/`)
  - Workspace: 目录 (`~/.agentos/workspace/{session_id}/`)
- **后期**: 可选数据库实现

**完成标准**:
- [ ] 文件系统实现完成
- [ ] 支持并发读写（文件锁）
- [ ] 单元测试覆盖率 > 80%
- [ ] 性能测试（1000 条消息读写 < 1s）

**工作量估算**: 3-4 天

**可并行**: 与 M3, M4 并行

---

### M3: providers (LLM 提供者)

**优先级**: P0 (核心功能)

**职责**:
- 统一 LLM 调用接口
- 支持多种 LLM provider
- 处理重试和错误

**输入**:
- 消息历史
- 工具定义
- 配置参数

**输出**:
- LLM 响应
- 工具调用请求

**依赖**: `core`

**关键接口**:
```python
# base.py
class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: List[Message],
        tools: Optional[List[Tool]] = None,
        **kwargs
    ) -> Response:
        pass

# litellm_provider.py
class LiteLLMProvider(LLMProvider):
    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    async def complete(self, messages, tools, **kwargs):
        # 使用 LiteLLM 调用
        pass

# openai_provider.py
class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def complete(self, messages, tools, **kwargs):
        # 直接调用 OpenAI API
        pass
```

**实现策略**:
- **MVP**: 只实现 LiteLLM 适配器（支持 20+ providers）
- **后期**: 按需添加直接适配器（性能优化）

**完成标准**:
- [ ] LiteLLM 适配器完成
- [ ] 支持工具调用
- [ ] 支持流式响应
- [ ] 错误处理和重试
- [ ] 单元测试（使用 mock）

**工作量估算**: 2-3 天

**可并行**: 与 M2, M4 并行

---

### M4: channels (渠道适配器)

**优先级**: P1 (MVP 只需 CLI)

**职责**:
- 多平台消息接入
- 消息格式转换
- 用户身份验证

**输入**:
- 平台原始消息

**输出**:
- 标准化的 InboundMessage
- 发送到平台的消息

**依赖**: `core`

**关键接口**:
```python
# base.py
class Channel(ABC):
    channel_id: str
    channel_type: str

    @abstractmethod
    async def start(self) -> None:
        """启动 channel 监听"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """停止 channel"""
        pass

    @abstractmethod
    async def send(self, message: OutboundMessage) -> None:
        """发送消息"""
        pass

    @abstractmethod
    def is_authorized(self, user_id: str) -> bool:
        """检查用户授权"""
        pass

# cli_channel.py
class CLIChannel(Channel):
    """命令行 channel，用于开发和测试"""

    async def start(self):
        # 启动交互式 CLI
        pass

    async def send(self, message):
        # 打印到终端
        print(f"Agent: {message.content}")
```

**实现策略**:
- **MVP**: 只实现 CLI Channel
- **Phase 2**: Telegram, Slack
- **Phase 3**: 其他平台

**完成标准**:
- [ ] CLI Channel 完成
- [ ] 支持多轮对话
- [ ] 支持文件附件显示
- [ ] 单元测试

**工作量估算**:
- CLI: 1-2 天
- Telegram: 2-3 天
- Slack: 2-3 天

**可并行**: 与 M2, M3 并行

---

### M5: tools (工具系统)

**优先级**: P0 (核心功能)

**职责**:
- 提供内置工具
- 工具注册和发现
- 工具执行和沙箱

**输入**:
- 工具调用请求
- 参数

**输出**:
- 工具执行结果

**依赖**: `core`

**关键接口**:
```python
# registry.py
class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        """注册工具"""
        self.tools[tool.name] = tool

    def get(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self.tools.get(name)

    def list(self) -> List[Tool]:
        """列出所有工具"""
        return list(self.tools.values())

# filesystem.py
class FileReadTool(Tool):
    name = "file_read"
    description = "读取文件内容"
    parameters = {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件路径"}
        },
        "required": ["path"]
    }

    async def execute(self, path: str) -> ToolResult:
        try:
            # 路径验证
            # 读取文件
            # 返回结果
            pass
        except Exception as e:
            return ToolResult(success=False, error=str(e))
```

**MVP 工具清单**:
1. `file_read` - 读取文件
2. `file_write` - 写入文件
3. `file_list` - 列出文件
4. `shell_execute` - 执行 shell 命令（需要安全策略）
5. `web_search` - 网页搜索（可选）

**实现策略**:
- **MVP**: 5 个基础工具
- **Phase 2**: 添加更多工具
- **Phase 3**: 支持 MCP 协议

**完成标准**:
- [ ] 5 个基础工具实现
- [ ] 工具注册系统
- [ ] 参数验证
- [ ] 安全检查（路径遍历、命令注入）
- [ ] 单元测试覆盖率 > 90%

**工作量估算**: 3-4 天

**可并行**: 与 M2, M3, M4 并行

---

### M6: runtime (执行运行时)

**优先级**: P0 (核心功能)

**职责**:
- Agent 执行循环
- 工具调用编排
- 策略控制
- 上下文管理

**输入**:
- 用户消息
- 会话历史
- 可用工具

**输出**:
- Agent 响应
- 工具调用记录
- 更新的会话状态

**依赖**: `core`, `providers`, `tools`, `storage`

**关键接口**:
```python
# loop.py
class AgentLoop:
    def __init__(
        self,
        llm: LLMProvider,
        tools: ToolRegistry,
        policy: PolicyEngine,
        max_iterations: int = 10
    ):
        self.llm = llm
        self.tools = tools
        self.policy = policy
        self.max_iterations = max_iterations

    async def run(
        self,
        session: Session,
        message: InboundMessage
    ) -> Response:
        """执行一轮对话"""
        # 1. 加载历史
        # 2. 添加新消息
        # 3. 循环调用 LLM
        # 4. 执行工具
        # 5. 返回响应
        pass

# policy.py
class PolicyEngine:
    def check_tool_permission(
        self,
        tool_name: str,
        session: Session
    ) -> bool:
        """检查工具权限"""
        pass

    def check_resource_limit(
        self,
        resource: str,
        session: Session
    ) -> bool:
        """检查资源限制"""
        pass

# context.py
class ContextManager:
    def estimate_tokens(self, messages: List[Message]) -> int:
        """估算 token 数"""
        pass

    def should_consolidate(
        self,
        messages: List[Message],
        max_tokens: int
    ) -> bool:
        """是否需要整合历史"""
        pass
```

**实现策略**:
- **MVP**: 简单的执行循环 + 基础策略
- **Phase 2**: 添加记忆整合
- **Phase 3**: 添加子任务支持

**完成标准**:
- [ ] Agent Loop 实现
- [ ] 工具调用编排
- [ ] 基础策略引擎
- [ ] Token 计数和限制
- [ ] 集成测试

**工作量估算**: 4-5 天

**可并行**: 不可（依赖 M2-M5）

---

### M7: cli (命令行应用)

**优先级**: P0 (MVP 交付物)

**职责**:
- 提供命令行界面
- 配置管理
- 开发和测试工具

**输入**:
- 命令行参数
- 配置文件

**输出**:
- 交互式对话
- 命令执行结果

**依赖**: `core`, `runtime`, `storage`, `channels`, `tools`, `providers`

**关键命令**:
```bash
# 启动交互式对话
agentos chat

# 单次执行
agentos run "帮我创建一个 Python 项目"

# 配置管理
agentos config set llm.provider openai
agentos config set llm.model gpt-4

# 会话管理
agentos sessions list
agentos sessions show <session_id>
agentos sessions delete <session_id>

# 工具管理
agentos tools list
agentos tools info <tool_name>
```

**实现策略**:
- 使用 Click 或 Typer 框架
- 配置文件: `~/.agentos/config.yaml`
- 交互式 UI: Rich 库

**完成标准**:
- [ ] 基础命令实现
- [ ] 配置管理
- [ ] 交互式对话
- [ ] 帮助文档
- [ ] E2E 测试

**工作量估算**: 3-4 天

**可并行**: 不可（依赖 M6）

---

### M8: server (HTTP 服务)

**优先级**: P2 (后期)

**职责**:
- 提供 REST API
- WebSocket 支持
- 多用户管理

**输入**:
- HTTP 请求
- WebSocket 消息

**输出**:
- API 响应
- WebSocket 推送

**依赖**: `core`, `runtime`, `storage`, `channels`, `tools`, `providers`

**关键 API**:
```
POST   /api/v1/sessions              # 创建会话
GET    /api/v1/sessions              # 列出会话
GET    /api/v1/sessions/{id}         # 获取会话
DELETE /api/v1/sessions/{id}         # 删除会话

POST   /api/v1/sessions/{id}/messages  # 发送消息
GET    /api/v1/sessions/{id}/messages  # 获取历史

WS     /api/v1/ws/{session_id}       # WebSocket 连接

GET    /api/v1/tools                 # 列出工具
POST   /api/v1/tools/{name}/execute  # 执行工具
```

**实现策略**:
- 使用 FastAPI
- 认证: API Key 或 JWT
- 限流: slowapi

**完成标准**:
- [ ] REST API 实现
- [ ] WebSocket 支持
- [ ] API 文档（OpenAPI）
- [ ] 认证和授权
- [ ] API 测试

**工作量估算**: 5-6 天

**可并行**: 与 M7 并行（都依赖 M6）

---

## 模块优先级总结

### P0 (MVP 必需)
- M1: core
- M2: storage
- M3: providers
- M4: channels (只需 CLI)
- M5: tools
- M6: runtime
- M7: cli

### P1 (Phase 2)
- M4: channels (Telegram, Slack)
- M5: tools (更多工具)
- 记忆整合功能

### P2 (Phase 3)
- M8: server
- 子任务支持
- MCP 协议支持

---

## 并行开发计划

### Week 1: 基础层
**并行组 A**: M1 (core)
- 必须先完成，其他模块依赖

### Week 2-3: 适配层
**并行组 B**:
- M2 (storage) - 开发者 A
- M3 (providers) - 开发者 B
- M4 (channels/CLI) - 开发者 C
- M5 (tools) - 开发者 D

这 4 个模块互不依赖，可以完全并行

### Week 4: 业务层
**串行**: M6 (runtime)
- 依赖 M2-M5 完成
- 需要集成测试

### Week 5: 应用层
**并行组 C**:
- M7 (cli) - 开发者 A
- M8 (server) - 开发者 B (可选)

---

## 模块间接口契约

### Storage → Runtime
```python
# Runtime 调用 Storage
history = await session_store.load_history(session_id, limit=100)
await session_store.save_message(session_id, message)
```

### Providers → Runtime
```python
# Runtime 调用 Providers
response = await llm.complete(messages, tools)
```

### Tools → Runtime
```python
# Runtime 调用 Tools
tool = tool_registry.get(tool_name)
result = await tool.execute(**params)
```

### Runtime → CLI
```python
# CLI 调用 Runtime
agent = AgentLoop(llm, tools, policy)
response = await agent.run(session, message)
```

---

## 风险与依赖

### 关键路径
```
M1 → M2,M3,M4,M5 → M6 → M7
```

**瓶颈**: M6 (runtime) 是关键路径，必须等待 M2-M5 完成

**缓解策略**:
- M2-M5 尽早完成接口定义
- M6 可以先用 mock 开始开发
- 提前编写集成测试

### 依赖风险

**外部依赖**:
- LiteLLM: 如果有 bug，可能阻塞 M3
  - 缓解: 准备 OpenAI 直接适配器作为备选
- 平台 API: Telegram/Slack API 变化
  - 缓解: 先完成 CLI，平台 channel 后期添加

**内部依赖**:
- M6 依赖 M2-M5: 如果任何一个延期，M6 无法开始
  - 缓解: M2-M5 并行开发，定期同步进度

---

## 总结

**总模块数**: 8 个

**MVP 模块**: 7 个 (M1-M7)

**可并行模块**: 4 个 (M2-M5)

**关键路径**: M1 → M2-M5 → M6 → M7

**总工作量**: 约 20-25 天（单人）或 4-5 周（4 人并行）
