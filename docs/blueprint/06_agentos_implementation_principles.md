# AgentOS 实现原则

## 概述

本文档总结实现 AgentOS 时必须遵守的工程原则、应该避免的陷阱、以及推荐的实践方法。这些原则来自实际项目经验和软件工程最佳实践。

---

## 原则 1: 先抽象，后实现

### 核心思想

在写具体实现之前，先定义清晰的抽象接口。

### 为什么重要

- ✅ 避免过早绑定到特定实现
- ✅ 便于测试（可以 mock）
- ✅ 便于替换实现
- ✅ 强制思考边界

### 必须先抽象的接口

**1. LLM Provider**
```python
class LLMProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: List[Message],
        tools: Optional[List[Tool]] = None,
        **kwargs
    ) -> Response:
        """完成对话"""
        pass
```

**为什么**: LLM 技术快速演进，provider 频繁变化

**2. Storage**
```python
class SessionStore(ABC):
    @abstractmethod
    async def save_message(self, session_id: str, message: Message) -> None:
        pass

    @abstractmethod
    async def load_history(self, session_id: str, limit: int) -> List[Message]:
        pass
```

**为什么**: 存储方案可能从文件系统迁移到数据库

**3. Channel**
```python
class Channel(ABC):
    @abstractmethod
    async def start(self) -> None:
        pass

    @abstractmethod
    async def send(self, message: Message) -> None:
        pass
```

**为什么**: 需要支持多种通信平台

**4. Tool**
```python
class Tool(ABC):
    name: str
    description: str
    parameters: JSONSchema

    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        pass
```

**为什么**: 工具集需要可扩展

### 反面案例

❌ **直接依赖具体实现**
```python
# 不好
from openai import OpenAI

class Agent:
    def __init__(self):
        self.client = OpenAI()  # 硬编码依赖
```

✅ **依赖抽象**
```python
# 好
class Agent:
    def __init__(self, llm_provider: LLMProvider):
        self.llm = llm_provider  # 依赖注入
```

---

## 原则 2: 控制复杂度增长

### 核心思想

复杂度是 AgentOS 的最大敌人，必须从一开始就控制。

### 复杂度来源

**1. 状态管理**
- 会话状态
- 对话历史
- 工作空间
- 缓存

**控制方法**:
- 明确状态的生命周期
- 追加式而非可变式
- 定期清理过期状态

**2. 并发控制**
- 多个请求同时到达
- 资源竞争
- 死锁风险

**控制方法**:
- 从简单的全局锁开始
- 只在性能瓶颈时才优化
- 避免过早的细粒度锁

**3. 错误处理**
- LLM 调用失败
- 工具执行失败
- 网络错误
- 超时

**控制方法**:
- 统一的错误处理机制
- 明确的重试策略
- 优雅降级

**4. 配置管理**
- 系统配置
- 用户配置
- Channel 配置
- Tool 配置

**控制方法**:
- 使用配置模式（如 Pydantic）
- 配置验证
- 合理的默认值

### 复杂度预算

为每个模块设定复杂度预算：

| 模块 | 最大代码行数 | 最大依赖数 | 最大嵌套层级 |
|-----|------------|-----------|------------|
| Channel | 300 | 5 | 3 |
| Agent Loop | 500 | 8 | 4 |
| Tool | 200 | 3 | 3 |
| Storage | 300 | 5 | 3 |

超过预算时，必须重构或拆分。

---

## 原则 3: 不要过早实现的功能

### 核心思想

很多功能看起来有用，但实际上可能永远不需要。推迟实现直到真正需要。

### 不要过早实现的功能清单

#### ❌ 分布式部署

**为什么不急**:
- 单机足够支撑早期用户
- 分布式增加巨大复杂度
- 状态同步、一致性问题

**何时实现**:
- 单机性能瓶颈
- 需要高可用
- 用户规模达到阈值

#### ❌ 实时协作

**为什么不急**:
- 异步协作足够大多数场景
- 实时协作需要复杂的冲突解决
- WebSocket 连接管理复杂

**何时实现**:
- 用户明确需求
- 异步协作成为瓶颈

#### ❌ 细粒度权限

**为什么不急**:
- 简单的白名单足够早期
- 细粒度权限管理复杂
- 可能过度设计

**何时实现**:
- 多租户需求
- 合规要求
- 用户明确需求

#### ❌ 多语言支持

**为什么不急**:
- 增加维护负担
- 翻译质量难保证
- 可能没有国际用户

**何时实现**:
- 有明确的国际用户
- 有专业翻译资源

#### ❌ 插件市场

**为什么不急**:
- 需要审核机制
- 需要版本管理
- 需要支付系统

**何时实现**:
- 有活跃的插件开发者社区
- 有运营资源

#### ❌ 高级分析

**为什么不急**:
- 早期用户少，数据不足
- 分析系统复杂
- 可能分析错方向

**何时实现**:
- 有足够数据
- 有明确的分析目标

### 推荐的 MVP 功能集

**Phase 1: 核心功能**
- ✅ 单 Channel（选一个最重要的）
- ✅ 基础 Agent Loop
- ✅ 3-5 个核心工具
- ✅ 简单的文件存储
- ✅ 基础错误处理

**Phase 2: 可用性**
- ✅ 多 Channel 支持
- ✅ 更多工具
- ✅ 配置系统
- ✅ 日志和监控

**Phase 3: 扩展性**
- ✅ 插件系统
- ✅ 子任务支持
- ✅ 记忆系统

**Phase 4: 企业级**
- ✅ 权限系统
- ✅ 审计日志
- ✅ 高可用

---

## 原则 4: 测试策略

### 核心思想

AgentOS 的测试比传统软件更困难（LLM 不确定性），需要特殊策略。

### 测试金字塔

```
        /\
       /  \  E2E Tests (少量)
      /    \
     /------\  Integration Tests (适量)
    /        \
   /----------\  Unit Tests (大量)
  /______________\
```

### 单元测试

**测什么**:
- 工具的执行逻辑
- 配置解析
- 消息格式转换
- 状态管理

**不测什么**:
- LLM 的输出（不确定）
- 外部 API（用 mock）

**示例**:
```python
def test_file_read_tool():
    tool = FileReadTool()
    result = await tool.execute(path="/tmp/test.txt")
    assert result.success
    assert "content" in result.data

def test_session_isolation():
    store = SessionStore()
    await store.save_message("session1", msg1)
    await store.save_message("session2", msg2)

    history1 = await store.load_history("session1")
    assert len(history1) == 1
    assert msg2 not in history1
```

### 集成测试

**测什么**:
- Channel 与 Message Bus 的集成
- Agent 与 Tool 的集成
- Storage 的读写

**示例**:
```python
async def test_agent_tool_integration():
    agent = Agent(llm_provider=MockLLM())
    agent.register_tool(FileReadTool())

    response = await agent.process("读取 /tmp/test.txt")

    assert response.tool_calls
    assert response.tool_calls[0].name == "file_read"
```

### E2E 测试

**测什么**:
- 完整的用户流程
- 多轮对话
- 错误恢复

**示例**:
```python
async def test_multi_turn_conversation():
    client = TestClient()

    # 第一轮
    response1 = await client.send("创建文件 test.txt")
    assert "创建成功" in response1.text

    # 第二轮
    response2 = await client.send("读取刚才的文件")
    assert "test.txt" in response2.text
```

### LLM 测试策略

**策略 1: Mock LLM**
```python
class MockLLM(LLMProvider):
    def __init__(self, responses: List[str]):
        self.responses = responses
        self.call_count = 0

    async def complete(self, messages, tools):
        response = self.responses[self.call_count]
        self.call_count += 1
        return response
```

**策略 2: 快照测试**
- 记录 LLM 的输出
- 后续测试对比快照
- 快照变化时人工审查

**策略 3: 属性测试**
- 不测具体输出
- 测输出的属性（如格式、长度）

```python
def test_llm_output_format():
    response = await agent.process("...")
    assert isinstance(response, dict)
    assert "content" in response
    assert len(response["content"]) > 0
```

---

## 原则 5: 可观测性优先

### 核心思想

AgentOS 的调试非常困难，必须从一开始就内建可观测性。

### 三大支柱

**1. Logs (日志)**

**结构化日志**:
```python
import structlog

logger = structlog.get_logger()

logger.info(
    "agent_turn_completed",
    session_id=session_id,
    turn_id=turn_id,
    tool_calls=len(tool_calls),
    duration_ms=duration,
    tokens_used=tokens
)
```

**日志级别**:
- DEBUG: 详细的执行流程
- INFO: 关键事件（会话创建、工具调用）
- WARNING: 异常但可恢复的情况
- ERROR: 错误和失败

**2. Metrics (指标)**

**关键指标**:
```python
# 请求指标
requests_total = Counter("requests_total", ["channel", "status"])
request_duration = Histogram("request_duration_seconds", ["channel"])

# Agent 指标
agent_turns = Counter("agent_turns_total", ["session_id"])
tool_calls = Counter("tool_calls_total", ["tool_name", "status"])

# LLM 指标
llm_calls = Counter("llm_calls_total", ["provider", "model"])
llm_tokens = Counter("llm_tokens_total", ["provider", "type"])  # type: prompt/completion
llm_latency = Histogram("llm_latency_seconds", ["provider"])

# 系统指标
active_sessions = Gauge("active_sessions")
queue_size = Gauge("message_queue_size", ["direction"])  # direction: inbound/outbound
```

**3. Traces (追踪)**

**分布式追踪**:
```python
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

async def process_message(message):
    with tracer.start_as_current_span("process_message") as span:
        span.set_attribute("session_id", message.session_id)
        span.set_attribute("channel", message.channel)

        with tracer.start_as_current_span("agent_turn"):
            response = await agent.process(message)

        with tracer.start_as_current_span("send_response"):
            await channel.send(response)
```

### 调试友好的设计

**1. 请求 ID**
- 每个请求分配唯一 ID
- 在所有日志中包含
- 便于追踪完整流程

**2. 上下文传递**
```python
@dataclass
class Context:
    request_id: str
    session_id: str
    user_id: str
    channel: str
    start_time: datetime

# 在整个调用链中传递
async def process(context: Context, message: Message):
    logger.info("processing", **asdict(context))
    ...
```

**3. 错误上下文**
```python
try:
    result = await tool.execute(**params)
except Exception as e:
    logger.error(
        "tool_execution_failed",
        tool_name=tool.name,
        params=params,
        session_id=context.session_id,
        error=str(e),
        traceback=traceback.format_exc()
    )
    raise
```

---

## 原则 6: 安全性内建

### 核心思想

安全不是事后添加的，必须从设计阶段就考虑。

### 必须实现的安全措施

**1. 输入验证**

```python
def validate_file_path(path: str, workspace: str) -> str:
    """验证文件路径，防止路径遍历"""
    # 解析为绝对路径
    abs_path = Path(path).resolve()
    workspace_path = Path(workspace).resolve()

    # 检查是否在 workspace 内
    if not abs_path.is_relative_to(workspace_path):
        raise SecurityError(f"Path {path} is outside workspace")

    return str(abs_path)
```

**2. 命令注入防护**

```python
def execute_shell_command(command: str, allowed_commands: List[str]):
    """执行 shell 命令，防止注入"""
    # 解析命令
    parts = shlex.split(command)
    cmd = parts[0]

    # 检查白名单
    if cmd not in allowed_commands:
        raise SecurityError(f"Command {cmd} not allowed")

    # 使用 subprocess 安全执行
    result = subprocess.run(
        parts,
        capture_output=True,
        timeout=30,
        check=False
    )
    return result
```

**3. 敏感信息脱敏**

```python
def sanitize_log(data: Dict) -> Dict:
    """脱敏日志数据"""
    sensitive_keys = ["password", "api_key", "token", "secret"]

    def _sanitize(obj):
        if isinstance(obj, dict):
            return {
                k: "***REDACTED***" if k.lower() in sensitive_keys else _sanitize(v)
                for k, v in obj.items()
            }
        elif isinstance(obj, list):
            return [_sanitize(item) for item in obj]
        else:
            return obj

    return _sanitize(data)
```

**4. 速率限制**

```python
class RateLimiter:
    """速率限制器"""

    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window = window_seconds
        self.requests: Dict[str, List[datetime]] = {}

    async def check_limit(self, user_id: str) -> bool:
        """检查是否超过速率限制"""
        now = datetime.now()
        cutoff = now - timedelta(seconds=self.window)

        # 清理过期记录
        if user_id in self.requests:
            self.requests[user_id] = [
                t for t in self.requests[user_id] if t > cutoff
            ]
        else:
            self.requests[user_id] = []

        # 检查限制
        if len(self.requests[user_id]) >= self.max_requests:
            return False

        # 记录请求
        self.requests[user_id].append(now)
        return True
```

### 安全检查清单

在发布前必须检查：

- [ ] 所有用户输入都经过验证
- [ ] 文件操作限制在 workspace 内
- [ ] Shell 命令使用白名单
- [ ] API key 不出现在日志中
- [ ] 实现了速率限制
- [ ] 实现了超时控制
- [ ] 危险操作需要确认
- [ ] 错误消息不泄露敏感信息

---

## 原则 7: 配置优于硬编码

### 核心思想

所有可能变化的值都应该可配置，而不是硬编码。

### 应该可配置的内容

**1. LLM 配置**
```yaml
llm:
  provider: openai
  model: gpt-4
  temperature: 0.7
  max_tokens: 4000
  timeout: 60
```

**2. Channel 配置**
```yaml
channels:
  telegram:
    enabled: true
    token: ${TELEGRAM_TOKEN}
    authorized_users:
      - user123
      - user456

  slack:
    enabled: false
    token: ${SLACK_TOKEN}
```

**3. 工具配置**
```yaml
tools:
  file_read:
    enabled: true
    max_file_size: 10485760  # 10MB

  shell_execute:
    enabled: true
    allowed_commands:
      - ls
      - cat
      - grep
    timeout: 30
```

**4. 系统配置**
```yaml
system:
  workspace_dir: ~/.agentos/workspace
  log_level: INFO
  max_concurrent_sessions: 10
  session_timeout: 3600
```

### 配置管理最佳实践

**1. 使用配置模式**
```python
from pydantic import BaseSettings

class Config(BaseSettings):
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"
    workspace_dir: Path = Path.home() / ".agentos" / "workspace"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_prefix = "AGENTOS_"
```

**2. 环境变量覆盖**
```bash
# 配置文件中的默认值
llm_model: gpt-4

# 环境变量覆盖
export AGENTOS_LLM_MODEL=gpt-3.5-turbo
```

**3. 配置验证**
```python
def validate_config(config: Config):
    """验证配置"""
    if config.workspace_dir.exists() and not config.workspace_dir.is_dir():
        raise ValueError(f"{config.workspace_dir} is not a directory")

    if config.max_concurrent_sessions < 1:
        raise ValueError("max_concurrent_sessions must be >= 1")
```

---

## 总结：实现检查清单

在开始实现 AgentOS 之前，确保：

### 架构设计
- [ ] 定义了清晰的层次架构
- [ ] 每层的职责明确
- [ ] 层间依赖单向
- [ ] 核心抽象已定义

### 复杂度控制
- [ ] 设定了复杂度预算
- [ ] 识别了复杂度来源
- [ ] 有控制复杂度的策略

### 功能范围
- [ ] 明确了 MVP 功能
- [ ] 列出了不做的功能
- [ ] 有功能优先级

### 测试策略
- [ ] 定义了测试金字塔
- [ ] 有 LLM 测试策略
- [ ] 有 E2E 测试计划

### 可观测性
- [ ] 设计了日志策略
- [ ] 定义了关键指标
- [ ] 有追踪方案

### 安全性
- [ ] 识别了安全风险
- [ ] 有输入验证
- [ ] 有权限控制
- [ ] 有审计日志

### 配置管理
- [ ] 定义了配置结构
- [ ] 有配置验证
- [ ] 支持环境变量

完成这个检查清单后，就可以开始实现了。
