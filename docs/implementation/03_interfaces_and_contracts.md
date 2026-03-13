# 接口与契约定义

## 概述

本文档定义系统中所有关键接口的详细契约，包括方法签名、参数说明、返回值、异常处理、并发安全性等。

---

## 1. Session Service

### 接口定义

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from agentos_core.types import Message, SessionMetadata

class SessionStore(ABC):
    """会话存储服务"""

    @abstractmethod
    async def create_session(
        self,
        session_id: str,
        user_id: str,
        channel: str,
        context_id: str,
        metadata: Optional[dict] = None
    ) -> None:
        """
        创建新会话

        Args:
            session_id: 会话唯一标识，格式 {channel}:{context_id}
            user_id: 用户标识
            channel: 渠道名称（telegram, slack, cli）
            context_id: 渠道内的上下文 ID（chat_id, channel_id）
            metadata: 额外元数据

        Raises:
            SessionAlreadyExistsError: 会话已存在
            StorageError: 存储失败
        """
        pass

    @abstractmethod
    async def save_message(
        self,
        session_id: str,
        message: Message
    ) -> None:
        """
        保存消息到会话历史（追加式）

        Args:
            session_id: 会话 ID
            message: 消息对象

        Raises:
            SessionNotFoundError: 会话不存在
            StorageError: 存储失败

        并发安全: 必须支持并发追加
        """
        pass

    @abstractmethod
    async def load_history(
        self,
        session_id: str,
        limit: Optional[int] = None,
        before: Optional[datetime] = None
    ) -> List[Message]:
        """
        加载会话历史

        Args:
            session_id: 会话 ID
            limit: 最多返回消息数（None = 全部）
            before: 只返回此时间之前的消息

        Returns:
            消息列表，按时间升序

        Raises:
            SessionNotFoundError: 会话不存在
            StorageError: 读取失败
        """
        pass

    @abstractmethod
    async def get_session_metadata(
        self,
        session_id: str
    ) -> SessionMetadata:
        """
        获取会话元数据

        Returns:
            SessionMetadata(
                session_id,
                user_id,
                channel,
                context_id,
                created_at,
                last_active,
                message_count,
                metadata
            )
        """
        pass

    @abstractmethod
    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        channel: Optional[str] = None,
        active_since: Optional[datetime] = None
    ) -> List[SessionMetadata]:
        """
        列出会话

        Args:
            user_id: 过滤用户
            channel: 过滤渠道
            active_since: 只返回此时间后活跃的会话

        Returns:
            会话元数据列表，按 last_active 降序
        """
        pass

    @abstractmethod
    async def delete_session(
        self,
        session_id: str
    ) -> None:
        """
        删除会话及其所有数据

        Args:
            session_id: 会话 ID

        Raises:
            SessionNotFoundError: 会话不存在
            StorageError: 删除失败
        """
        pass
```

### 数据模型

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

class Message(BaseModel):
    """消息模型"""
    role: Literal["user", "assistant", "system", "tool"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)

    # 工具调用相关
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None

class ToolCall(BaseModel):
    """工具调用"""
    id: str
    name: str
    arguments: dict

class SessionMetadata(BaseModel):
    """会话元数据"""
    session_id: str
    user_id: str
    channel: str
    context_id: str
    created_at: datetime
    last_active: datetime
    message_count: int
    metadata: dict = Field(default_factory=dict)
```

### 实现要点

**文件系统实现**:
```python
class FileSessionStore(SessionStore):
    """基于文件系统的实现"""

    def __init__(self, base_path: str = "~/.agentos/sessions"):
        self.base_path = Path(base_path).expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._locks = {}  # session_id -> asyncio.Lock

    def _get_session_path(self, session_id: str) -> Path:
        # 使用 session_id 的 hash 分片，避免单目录文件过多
        hash_prefix = hashlib.md5(session_id.encode()).hexdigest()[:2]
        return self.base_path / hash_prefix / f"{session_id}.jsonl"

    async def save_message(self, session_id: str, message: Message):
        path = self._get_session_path(session_id)

        # 获取会话级锁
        if session_id not in self._locks:
            self._locks[session_id] = asyncio.Lock()

        async with self._locks[session_id]:
            # 追加写入 JSONL
            async with aiofiles.open(path, 'a') as f:
                await f.write(message.model_dump_json() + '\n')
```

**为什么这样设计**:
- 追加式写入，避免读-改-写竞态
- 会话级锁，允许不同会话并发
- 文件分片，避免单目录性能问题

---

## 2. Routing Service

### 接口定义

```python
from abc import ABC, abstractmethod
from asyncio import Queue

class MessageBus(ABC):
    """消息总线"""

    @abstractmethod
    async def enqueue_inbound(
        self,
        message: InboundMessage
    ) -> None:
        """
        入队入站消息

        Args:
            message: 来自 channel 的消息

        并发安全: 必须支持多个 channel 并发入队
        """
        pass

    @abstractmethod
    async def dequeue_inbound(
        self,
        timeout: Optional[float] = None
    ) -> InboundMessage:
        """
        出队入站消息（阻塞）

        Args:
            timeout: 超时时间（秒），None = 永久等待

        Returns:
            入站消息

        Raises:
            asyncio.TimeoutError: 超时
        """
        pass

    @abstractmethod
    async def enqueue_outbound(
        self,
        message: OutboundMessage
    ) -> None:
        """
        入队出站消息

        Args:
            message: 发往 channel 的消息
        """
        pass

    @abstractmethod
    async def dequeue_outbound(
        self,
        timeout: Optional[float] = None
    ) -> OutboundMessage:
        """
        出队出站消息（阻塞）

        Returns:
            出站消息
        """
        pass

    @abstractmethod
    async def get_queue_size(self) -> dict:
        """
        获取队列大小

        Returns:
            {
                "inbound": int,
                "outbound": int
            }
        """
        pass
```

### 数据模型

```python
class InboundMessage(BaseModel):
    """入站消息"""
    session_id: str
    user_id: str
    channel: str
    content: str
    attachments: List[Attachment] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: dict = Field(default_factory=dict)

class OutboundMessage(BaseModel):
    """出站消息"""
    session_id: str
    channel: str
    content: str
    attachments: List[Attachment] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

class Attachment(BaseModel):
    """附件"""
    type: Literal["image", "file", "audio", "video"]
    url: Optional[str] = None
    data: Optional[bytes] = None
    filename: Optional[str] = None
```

### 实现要点

**内存队列实现**:
```python
class InMemoryMessageBus(MessageBus):
    """基于 asyncio.Queue 的实现"""

    def __init__(self, max_size: int = 1000):
        self.inbound_queue = Queue(maxsize=max_size)
        self.outbound_queue = Queue(maxsize=max_size)

    async def enqueue_inbound(self, message: InboundMessage):
        await self.inbound_queue.put(message)

    async def dequeue_inbound(self, timeout=None):
        if timeout:
            return await asyncio.wait_for(
                self.inbound_queue.get(),
                timeout=timeout
            )
        return await self.inbound_queue.get()
```

**为什么这样设计**:
- MVP 使用内存队列（简单、零依赖）
- 后期可替换为 Redis/RabbitMQ（持久化、分布式）
- 接口保持不变

---

## 3. Tool Registry

### 接口定义

```python
class ToolRegistry(ABC):
    """工具注册表"""

    @abstractmethod
    def register(
        self,
        tool: Tool
    ) -> None:
        """
        注册工具

        Args:
            tool: 工具实例

        Raises:
            ToolAlreadyExistsError: 工具名称已存在
        """
        pass

    @abstractmethod
    def unregister(
        self,
        tool_name: str
    ) -> None:
        """
        注销工具

        Args:
            tool_name: 工具名称

        Raises:
            ToolNotFoundError: 工具不存在
        """
        pass

    @abstractmethod
    def get(
        self,
        tool_name: str
    ) -> Tool:
        """
        获取工具

        Args:
            tool_name: 工具名称

        Returns:
            工具实例

        Raises:
            ToolNotFoundError: 工具不存在
        """
        pass

    @abstractmethod
    def list_tools(
        self,
        category: Optional[str] = None
    ) -> List[ToolMetadata]:
        """
        列出所有工具

        Args:
            category: 过滤分类

        Returns:
            工具元数据列表
        """
        pass

    @abstractmethod
    def get_schemas(self) -> List[dict]:
        """
        获取所有工具的 JSON Schema

        Returns:
            适合传给 LLM 的工具定义列表
        """
        pass
```

### 数据模型

```python
class Tool(ABC):
    """工具抽象基类"""
    name: str
    description: str
    parameters: dict  # JSON Schema
    category: str = "general"
    requires_confirmation: bool = False

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass

    def get_schema(self) -> dict:
        """返回 OpenAI function calling 格式的 schema"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

class ToolResult(BaseModel):
    """工具执行结果"""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: dict = Field(default_factory=dict)

class ToolMetadata(BaseModel):
    """工具元数据"""
    name: str
    description: str
    category: str
    requires_confirmation: bool
    parameters: dict
```

### 实现要点

```python
class SimpleToolRegistry(ToolRegistry):
    """简单的内存实现"""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool):
        if tool.name in self._tools:
            raise ToolAlreadyExistsError(f"Tool {tool.name} already exists")
        self._tools[tool.name] = tool

    def get_schemas(self) -> List[dict]:
        return [tool.get_schema() for tool in self._tools.values()]
```

**为什么这样设计**:
- 简单的字典存储足够 MVP
- 后期可扩展为支持动态加载（插件）
- Schema 格式与 OpenAI 兼容

---

## 4. Execution Runtime

### 接口定义

```python
class AgentLoop:
    """Agent 执行循环"""

    def __init__(
        self,
        llm: LLMProvider,
        tool_registry: ToolRegistry,
        policy_engine: PolicyEngine,
        max_iterations: int = 10
    ):
        self.llm = llm
        self.tool_registry = tool_registry
        self.policy = policy_engine
        self.max_iterations = max_iterations

    async def run(
        self,
        session_id: str,
        messages: List[Message],
        context: ExecutionContext
    ) -> AgentResponse:
        """
        执行一轮 Agent 循环

        Args:
            session_id: 会话 ID
            messages: 消息历史
            context: 执行上下文（用户信息、权限等）

        Returns:
            AgentResponse(
                messages: 新增的消息,
                final_response: 最终响应文本,
                tool_calls_made: 执行的工具调用,
                iterations: 迭代次数,
                metadata: 元数据（token 使用等）
            )

        Raises:
            MaxIterationsExceededError: 超过最大迭代次数
            ToolExecutionError: 工具执行失败
            PolicyViolationError: 违反策略
        """
        pass
```

### 数据模型

```python
class ExecutionContext(BaseModel):
    """执行上下文"""
    session_id: str
    user_id: str
    channel: str
    permissions: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

class AgentResponse(BaseModel):
    """Agent 响应"""
    messages: List[Message]
    final_response: str
    tool_calls_made: List[ToolCallRecord]
    iterations: int
    metadata: dict = Field(default_factory=dict)

class ToolCallRecord(BaseModel):
    """工具调用记录"""
    tool_name: str
    arguments: dict
    result: ToolResult
    timestamp: datetime
    duration_ms: float
```

### 执行流程

```python
async def run(self, session_id, messages, context):
    new_messages = []
    iterations = 0

    while iterations < self.max_iterations:
        iterations += 1

        # 1. 调用 LLM
        response = await self.llm.complete(
            messages + new_messages,
            tools=self.tool_registry.get_schemas()
        )

        # 2. 添加 assistant 消息
        new_messages.append(Message(
            role="assistant",
            content=response.content,
            tool_calls=response.tool_calls
        ))

        # 3. 如果没有工具调用，结束
        if not response.tool_calls:
            break

        # 4. 执行工具调用
        for tool_call in response.tool_calls:
            # 4.1 策略检查
            if not self.policy.check_tool_permission(
                tool_call.name,
                context
            ):
                raise PolicyViolationError(...)

            # 4.2 执行工具
            tool = self.tool_registry.get(tool_call.name)
            result = await tool.execute(**tool_call.arguments)

            # 4.3 添加工具结果消息
            new_messages.append(Message(
                role="tool",
                content=result.data,
                tool_call_id=tool_call.id
            ))

    return AgentResponse(
        messages=new_messages,
        final_response=new_messages[-1].content,
        ...
    )
```

**为什么这样设计**:
- 清晰的执行流程
- 策略检查在工具执行前
- 支持多轮工具调用
- 完整的执行记录

---

## 5. Policy Engine

### 接口定义

```python
class PolicyEngine(ABC):
    """策略引擎"""

    @abstractmethod
    def check_tool_permission(
        self,
        tool_name: str,
        context: ExecutionContext
    ) -> bool:
        """
        检查工具执行权限

        Args:
            tool_name: 工具名称
            context: 执行上下文

        Returns:
            True = 允许, False = 拒绝
        """
        pass

    @abstractmethod
    def check_resource_limit(
        self,
        resource_type: str,
        amount: float,
        context: ExecutionContext
    ) -> bool:
        """
        检查资源限制

        Args:
            resource_type: 资源类型（tokens, api_calls, file_size）
            amount: 请求数量
            context: 执行上下文

        Returns:
            True = 允许, False = 超限
        """
        pass

    @abstractmethod
    async def log_violation(
        self,
        violation_type: str,
        context: ExecutionContext,
        details: dict
    ) -> None:
        """
        记录策略违规

        Args:
            violation_type: 违规类型
            context: 执行上下文
            details: 详细信息
        """
        pass
```

### 实现要点

```python
class SimplePolicy...[truncated 5838 chars]