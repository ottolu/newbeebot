# Reimplementation Plan

## 分阶段实现策略

**[INFERENCE]** 基于 nanobot 架构，提供同类项目的实现路线图。

## MVP 阶段 (2-3 周)

### 目标
最小可用的 Agent 系统，单 channel，基础工具。

### 核心功能
- ✅ 单个 channel (CLI 或 Telegram)
- ✅ LLM 集成 (单个 provider)
- ✅ 基础工具 (文件读写、shell)
- ✅ 简单 session 管理
- ✅ 配置系统

### 技术栈
- Python 3.11+
- asyncio
- LiteLLM 或直接 OpenAI SDK
- JSONL 存储

### 模块清单
```
mvp/
├── main.py              # 入口
├── agent.py             # Agent loop (200 行)
├── llm.py               # LLM 调用 (100 行)
├── tools.py             # 工具实现 (200 行)
├── session.py           # Session 管理 (100 行)
└── config.py            # 配置 (50 行)
```

### 实现顺序
1. **Day 1-2**: LLM 集成 + 基础对话
2. **Day 3-4**: Tool 系统 + 工具调用循环
3. **Day 5-7**: Session 持久化
4. **Day 8-10**: CLI 或 Telegram channel
5. **Day 11-14**: 测试和优化

### 不做的事
- ❌ 多 channel
- ❌ Memory 整合
- ❌ 子任务
- ❌ Cron
- ❌ 复杂配置

---

## V1 阶段 (4-6 周)

### 目标
生产可用，多 channel，完整工具集。

### 新增功能
- ✅ 3-5 个 channel
- ✅ Message bus 解耦
- ✅ 完整工具集 (web, message, etc.)
- ✅ Memory 整合
- ✅ 配置系统增强
- ✅ 错误处理和重试

### 架构升级
```
v1/
├── channels/           # Channel 适配器
│   ├── base.py
│   ├── telegram.py
│   ├── discord.py
│   └── slack.py
├── bus/                # Message bus
│   ├── queue.py
│   └── events.py
├── agent/              # Agent 核心
│   ├── loop.py
│   ├── context.py
│   └── memory.py
├── tools/              # 工具系统
│   ├── base.py
│   ├── registry.py
│   └── implementations/
├── providers/          # LLM providers
├── session/            # Session 管理
└── config/             # 配置系统
```

### 实现顺序
1. **Week 1**: Message bus + Channel 抽象
2. **Week 2**: 实现 3 个 channel
3. **Week 3**: 工具系统重构
4. **Week 4**: Memory 整合
5. **Week 5-6**: 测试、文档、部署

### 风险点
- Channel SDK 学习曲线
- Memory 整合效果
- 并发处理正确性

---

## V2 阶段 (2-3 月)

### 目标
企业级特性，高级功能。

### 新增功能
- ✅ 所有主流 channel (10+)
- ✅ MCP 集成
- ✅ Skills 系统
- ✅ Subagent 支持
- ✅ Cron 任务
- ✅ Heartbeat 服务
- ✅ OAuth providers
- ✅ 多 workspace 支持

### 架构完善
- 更好的错误处理
- 日志和监控
- 性能优化
- 文档完善

### 实现顺序
1. **Month 1**: 剩余 channel + MCP
2. **Month 2**: Skills + Subagent + Cron
3. **Month 3**: 优化 + 文档 + 测试

---

## 未来增强 (可选)

### 高级特性
- 多租户支持
- 数据库存储
- 分布式架构
- 工作流引擎
- Web UI
- API 网关
- 监控和告警
- 审计日志

### 技术债偿还
- 细粒度锁
- 结构化日志
- Metrics 和 tracing
- 自动化测试
- CI/CD

---

## 技术选型建议

### 核心依赖
```toml
[dependencies]
# LLM
litellm = "^1.82"          # 或 openai, anthropic

# Async
asyncio = "built-in"

# 数据验证
pydantic = "^2.12"

# 日志
loguru = "^0.7"

# HTTP
httpx = "^0.28"
```

### Channel 依赖
```toml
# 按需添加
python-telegram-bot = "^22.6"
discord.py = "^2.3"
slack-sdk = "^3.39"
```

### 可选依赖
```toml
# MCP
mcp = "^1.26"

# 数据库 (如果需要)
sqlalchemy = "^2.0"
asyncpg = "^0.29"
```

---

## 关键实现建议

### 1. Agent Loop 设计

```python
async def agent_loop(message, session):
    # 1. 构建上下文
    messages = build_context(session, message)

    # 2. 迭代调用
    for i in range(MAX_ITERATIONS):
        response = await llm.chat(messages, tools)

        if response.tool_calls:
            for tc in response.tool_calls:
                result = await execute_tool(tc)
                messages.append(tool_result)
        else:
            return response.text

    return "Max iterations reached"
```

### 2. Tool 系统设计

```python
class Tool(ABC):
    @abstractmethod
    async def execute(self, **kwargs) -> str:
        pass

class ToolRegistry:
    def register(self, tool: Tool):
        self.tools[tool.name] = tool

    async def execute(self, name: str, args: dict) -> str:
        tool = self.tools[name]
        return await tool.execute(**args)
```

### 3. Session 管理设计

```python
class Session:
    key: str
    messages: list[dict]

    def add_message(self, role, content):
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": now()
        })

    def save(self):
        with open(f"{self.key}.jsonl", "w") as f:
            for msg in self.messages:
                f.write(json.dumps(msg) + "\n")
```

---

## 避免的陷阱

### 1. 过早优化
- ❌ 不要一开始就做分布式
- ✅ 先单进程，需要时再扩展

### 2. 过度抽象
- ❌ 不要设计复杂的插件系统
- ✅ 简单的接口 + 直接实现

### 3. 功能蔓延
- ❌ 不要添加"可能有用"的功能
- ✅ 只做明确需要的

### 4. 忽视错误处理
- ❌ 不要假设一切正常
- ✅ 每个外部调用都要处理错误

### 5. 配置复杂化
- ❌ 不要支持过多配置选项
- ✅ 合理的默认值 + 少量配置

---

## 测试策略

### MVP 阶段
- 手动测试
- 基础单元测试

### V1 阶段
- 单元测试 (70% 覆盖)
- 集成测试 (关键流程)
- Channel 模拟测试

### V2 阶段
- 完整测试套件
- E2E 测试
- 性能测试
- 负载测试
