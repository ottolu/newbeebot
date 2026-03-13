# AgentOS 参考架构

## 概述

本文档定义了一个通用的 AgentOS 参考架构，适用于构建各类 AI Agent 操作系统。该架构从 nanobot 等实际项目中提炼，但不局限于特定实现。

## 核心理念

**AgentOS 不是单一 Agent，而是一个支持 Agent 运行的操作系统层**

- 提供 Agent 运行的基础设施
- 管理 Agent 与外部世界的交互
- 处理状态、权限、资源、并发
- 像 OS 管理进程一样管理 Agent 会话

## 五层参考架构

```
┌─────────────────────────────────────────────────┐
│  Layer 5: 接入层 (Access Layer)                  │
│  职责: 多渠道接入、协议适配、消息归一化            │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Layer 4: 路由层 (Routing Layer)                 │
│  职责: 消息队列、会话路由、负载均衡                │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Layer 3: 编排层 (Orchestration Layer)          │
│  职责: Agent 生命周期、任务调度、子任务分发        │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Layer 2: 执行层 (Execution Layer)               │
│  职责: LLM 调用、工具执行、策略控制                │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│  Layer 1: 状态层 (State Layer)                   │
│  职责: 会话存储、记忆管理、工作空间                │
└─────────────────────────────────────────────────┘
```

---

## Layer 5: 接入层 (Access Layer)

### 职责

- **多渠道接入**: 支持多种通信协议（HTTP、WebSocket、消息平台 API）
- **协议适配**: 将不同平台的消息格式转换为统一内部格式
- **身份验证**: 验证用户身份和权限
- **消息归一化**: 统一消息结构（文本、附件、元数据）

### 核心抽象

```python
class Channel(ABC):
    """渠道抽象"""

    @abstractmethod
    async def start(self) -> None:
        """启动渠道监听"""

    @abstractmethod
    async def stop(self) -> None:
        """停止渠道"""

    @abstractmethod
    async def send(self, message: Message) -> None:
        """发送消息到渠道"""

    @abstractmethod
    def is_authorized(self, user_id: str) -> bool:
        """检查用户授权"""
```

### 设计要点

1. **解耦性**: 每个 Channel 独立实现，互不影响
2. **可插拔**: 新增渠道不影响核心逻辑
3. **容错性**: 单个渠道故障不影响其他渠道
4. **归一化**: 内部只处理统一的 Message 对象

### 边界

**输入边界**: 外部平台的原始消息
**输出边界**: 标准化的 `InboundMessage` 对象

**不应包含**:
- 业务逻辑
- 会话管理
- Agent 调用

---

## Layer 4: 路由层 (Routing Layer)

### 职责

- **消息队列**: 异步解耦接入层和编排层
- **会话路由**: 根据 session_id 路由到正确的 Agent 实例
- **优先级管理**: 处理消息优先级
- **流量控制**: 限流、背压处理

### 核心抽象

```python
class MessageBus:
    """消息总线"""

    async def enqueue_inbound(self, message: InboundMessage) -> None:
        """入队入站消息"""

    async def dequeue_inbound(self) -> InboundMessage:
        """出队入站消息"""

    async def enqueue_outbound(self, message: OutboundMessage) -> None:
        """入队出站消息"""

    async def dequeue_outbound(self) -> OutboundMessage:
        """出队出站消息"""
```

### 设计要点

1. **异步解耦**: 接入层和编排层通过队列解耦
2. **背压处理**: 队列满时的处理策略
3. **持久化**: 是否需要持久化队列（取决于可靠性要求）
4. **监控**: 队列长度、延迟等指标

### 边界

**输入边界**: 来自接入层的 `InboundMessage`
**输出边界**: 路由到编排层的消息

**不应包含**:
- Agent 逻辑
- 工具执行
- 状态管理

---

## Layer 3: 编排层 (Orchestration Layer)

### 职责

- **Agent 生命周期**: 创建、运行、暂停、恢复、销毁 Agent
- **任务调度**: 决定何时处理哪个任务
- **子任务分发**: 将复杂任务分解并分发给子 Agent
- **并发控制**: 管理并发执行的 Agent 数量
- **超时管理**: 处理长时间运行的任务

### 核心抽象

```python
class AgentOrchestrator:
    """Agent 编排器"""

    async def create_session(self, session_id: str) -> AgentSession:
        """创建新会话"""

    async def get_session(self, session_id: str) -> AgentSession:
        """获取现有会话"""

    async def execute_turn(self, session: AgentSession, message: InboundMessage) -> None:
        """执行一轮对话"""

    async def spawn_subagent(self, parent_session: str, task: Task) -> AgentSession:
        """派生子 Agent"""
```

### 设计要点

1. **会话隔离**: 每个会话独立状态
2. **并发策略**: 串行 vs 并行执行
3. **资源限制**: CPU、内存、并发数限制
4. **错误恢复**: 失败重试、降级策略

### 边界

**输入边界**: 路由层的消息 + 会话上下文
**输出边界**: 调用执行层 + 更新状态层

**不应包含**:
- 具体的 LLM 调用逻辑
- 工具的实现细节
- 存储的实现细节

---

## Layer 2: 执行层 (Execution Layer)

### 职责

- **LLM 调用**: 与各种 LLM Provider 交互
- **工具执行**: 执行 Agent 请求的工具调用
- **策略控制**: 安全策略、权限检查、资源限制
- **结果处理**: 处理 LLM 和工具的返回结果

### 核心抽象

```python
class LLMProvider(ABC):
    """LLM 提供者抽象"""

    @abstractmethod
    async def complete(self, messages: List[Message], tools: List[Tool]) -> Response:
        """完成对话"""

class Tool(ABC):
    """工具抽象"""

    name: str
    description: str
    parameters: JSONSchema

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具"""

class PolicyEngine:
    """策略引擎"""

    def check_tool_permission(self, tool: str, context: Context) -> bool:
        """检查工具权限"""

    def check_resource_limit(self, resource: str, context: Context) -> bool:
        """检查资源限制"""
```

### 设计要点

1. **Provider 抽象**: 统一不同 LLM 的接口
2. **工具注册**: 动态注册和发现工具
3. **安全沙箱**: 工具执行的隔离环境
4. **超时控制**: LLM 和工具调用的超时

### 边界

**输入边界**: 编排层的执行请求
**输出边界**: LLM 响应 + 工具结果

**不应包含**:
- 会话管理
- 消息路由
- 长期状态存储

---

## Layer 1: 状态层 (State Layer)

### 职责

- **会话存储**: 持久化会话历史和状态
- **记忆管理**: 长期记忆的存储和检索
- **工作空间**: 文件系统或对象存储
- **配置管理**: 系统和用户配置

### 核心抽象

```python
class SessionStore(ABC):
    """会话存储抽象"""

    @abstractmethod
    async def save_message(self, session_id: str, message: Message) -> None:
        """保存消息"""

    @abstractmethod
    async def load_history(self, session_id: str, limit: int) -> List[Message]:
        """加载历史"""

class MemoryStore(ABC):
    """记忆存储抽象"""

    @abstractmethod
    async def save_memory(self, session_id: str, memory: Memory) -> None:
        """保存记忆"""

    @abstractmethod
    async def search_memory(self, query: str) -> List[Memory]:
        """搜索记忆"""

class Workspace(ABC):
    """工作空间抽象"""

    @abstractmethod
    async def read_file(self, path: str) -> bytes:
        """读取文件"""

    @abstractmethod
    async def write_file(self, path: str, content: bytes) -> None:
        """写入文件"""
```

### 设计要点

1. **存储选择**: 文件系统 vs 数据库 vs 对象存储
2. **一致性**: 事务支持的必要性
3. **性能**: 缓存策略、索引设计
4. **备份**: 数据备份和恢复机制

### 边界

**输入边界**: 来自编排层和执行层的存储请求
**输出边界**: 持久化的数据

**不应包含**:
- 业务逻辑
- Agent 调度
- 消息路由

---

## 层次间交互规则

### 单向依赖原则

```
Layer 5 → Layer 4 → Layer 3 → Layer 2 → Layer 1
```

- 上层可以调用下层
- 下层不应依赖上层
- 跨层调用应通过接口抽象

### 事件驱动原则

某些场景下，下层可以通过事件通知上层：

```python
class Event:
    """系统事件"""
    type: EventType
    payload: Dict[str, Any]
    timestamp: datetime

# 例如：状态层可以发出 "storage_full" 事件
# 编排层订阅该事件并采取行动
```

---

## 可选层次

### 可观测层 (Observability Layer)

跨越所有层，提供：
- 日志聚合
- 指标收集
- 分布式追踪
- 告警

### 安全层 (Security Layer)

跨越所有层，提供：
- 认证授权
- 审计日志
- 加密
- 威胁检测

---

## 推荐解耦方式

### 1. 接口抽象

每层定义清晰的接口，实现与接口分离：

```python
# 定义接口
class ISessionStore(Protocol):
    async def save(self, session: Session) -> None: ...

# 多种实现
class FileSessionStore(ISessionStore): ...
class PostgresSessionStore(ISessionStore): ...
class RedisSessionStore(ISessionStore): ...
```

### 2. 依赖注入

通过依赖注入解耦具体实现：

```python
class AgentOrchestrator:
    def __init__(
        self,
        session_store: ISessionStore,
        llm_provider: ILLMProvider,
        tool_registry: IToolRegistry
    ):
        self.session_store = session_store
        self.llm_provider = llm_provider
        self.tool_registry = tool_registry
```

### 3. 事件总线

使用事件总线解耦模块间通信：

```python
class EventBus:
    def publish(self, event: Event) -> None: ...
    def subscribe(self, event_type: str, handler: Callable) -> None: ...

# 模块 A 发布事件
event_bus.publish(Event(type="session_created", payload={...}))

# 模块 B 订阅事件
event_bus.subscribe("session_created", on_session_created)
```

### 4. 配置驱动

通过配置文件控制实现选择：

```yaml
session_store:
  type: postgres
  connection: postgresql://...

llm_provider:
  type: openai
  api_key: sk-...
```

---

## 架构演进路径

### 阶段 1: 单体架构

所有层在一个进程中：

```
┌─────────────────────┐
│   Single Process    │
│  ┌───────────────┐  │
│  │  All Layers   │  │
│  └───────────────┘  │
└─────────────────────┘
```

**适用场景**: MVP、个人使用、低并发

### 阶段 2: 模块化单体

层次清晰但仍在一个进程：

```
┌─────────────────────┐
│   Single Process    │
│  ┌───────────────┐  │
│  │  Layer 5      │  │
│  ├───────────────┤  │
│  │  Layer 4      │  │
│  ├───────────────┤  │
│  │  Layer 3      │  │
│  ├───────────────┤  │
│  │  Layer 2      │  │
│  ├───────────────┤  │
│  │  Layer 1      │  │
│  └───────────────┘  │
└─────────────────────┘
```

**适用场景**: 小团队、中等并发、需要清晰架构

### 阶段 3: 分布式架构

层次分离到不同服务：

```
┌──────────┐  ┌──────────┐  ┌──────────┐
│ Layer 5  │→ │ Layer 4  │→ │ Layer 3  │
│ (多实例) │  │ (队列)   │  │ (多实例) │
└──────────┘  └──────────┘  └──────────┘
                                ↓
                    ┌──────────┐  ┌──────────┐
                    │ Layer 2  │→ │ Layer 1  │
                    │ (多实例) │  │ (数据库) │
                    └──────────┘  └──────────┘
```

**适用场景**: 大规模、高并发、多租户

---

## 架构决策检查清单

在设计 AgentOS 时，每层都应回答以下问题：

### 接入层
- [ ] 需要支持哪些渠道？
- [ ] 如何处理渠道故障？
- [ ] 如何验证用户身份？
- [ ] 消息格式如何归一化？

### 路由层
- [ ] 需要持久化队列吗？
- [ ] 如何处理队列积压？
- [ ] 需要优先级队列吗？
- [ ] 如何监控队列健康？

### 编排层
- [ ] 串行还是并行处理？
- [ ] 如何限制并发数？
- [ ] 如何处理超时？
- [ ] 如何支持子任务？

### 执行层
- [ ] 支持哪些 LLM Provider？
- [ ] 工具如何注册和发现？
- [ ] 如何隔离工具执行？
- [ ] 如何实施安全策略？

### 状态层
- [ ] 使用什么存储？
- [ ] 需要事务支持吗？
- [ ] 如何备份数据？
- [ ] 如何处理存储故障？

---

## 总结

这个五层参考架构提供了构建 AgentOS 的通用框架：

1. **接入层**: 多渠道接入和协议适配
2. **路由层**: 消息队列和会话路由
3. **编排层**: Agent 生命周期和任务调度
4. **执行层**: LLM 调用和工具执行
5. **状态层**: 会话存储和记忆管理

每层职责清晰、边界明确，通过接口抽象和依赖注入实现解耦。架构可以从单体逐步演进到分布式，适应不同规模的需求。
