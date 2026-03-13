# AgentOS 核心抽象

## 概述

本文档定义 AgentOS 中的核心抽象概念，给出每个抽象的推荐定义、职责边界、设计原则。这些抽象是构建任何 AgentOS 的基础词汇表。

---

## 1. Session (会话)

### 定义

**Session 是 Agent 与用户/系统交互的独立上下文单元**

一个 Session 封装了：
- 对话历史
- 上下文状态
- 工作空间
- 元数据

### 职责边界

**应该包含**:
- ✅ 消息历史记录
- ✅ 当前对话状态
- ✅ 临时工作文件
- ✅ 会话级配置

**不应该包含**:
- ❌ 跨会话的长期记忆（应该在 Memory）
- ❌ 用户全局配置（应该在 User Profile）
- ❌ Agent 执行逻辑（应该在 Agent）

### 关键属性

```python
@dataclass
class Session:
    session_id: str           # 唯一标识
    user_id: str              # 所属用户
    channel: str              # 来源渠道
    context_id: str           # 渠道内的上下文（如聊天 ID）
    created_at: datetime      # 创建时间
    last_active: datetime     # 最后活跃时间
    state: SessionState       # 当前状态
    metadata: Dict[str, Any]  # 扩展元数据
```

### 生命周期

```
Created → Active → Idle → Archived → Deleted
```

- **Created**: 首次消息到达时创建
- **Active**: 正在处理消息
- **Idle**: 一段时间无活动
- **Archived**: 长期无活动，压缩存储
- **Deleted**: 用户主动删除或过期清理

### 设计原则

1. **隔离性**: 不同 Session 之间完全隔离
2. **可恢复性**: Session 可以从持久化状态恢复
3. **轻量性**: Session 创建和销毁应该低成本
4. **可追溯性**: Session 的所有操作应该可审计

### 常见模式

**模式 1: 单用户多会话**
```
User A
  ├── Session 1 (Telegram)
  ├── Session 2 (Slack)
  └── Session 3 (Web)
```

**模式 2: 多用户共享会话**
```
Group Chat
  └── Session (shared by User A, B, C)
```

**模式 3: 层次化会话**
```
Parent Session
  ├── Child Session 1 (subtask)
  └── Child Session 2 (subtask)
```

### 来自 nanobot 的实现

- Session Key = `{channel}:{context_id}`
- 每个 Session 独立的 JSONL 文件存储历史
- 每个 Session 独立的工作空间目录

---

## 2. Agent (智能体)

### 定义

**Agent 是执行任务的智能实体，能够感知、推理、行动**

一个 Agent 包含：
- 推理引擎（通常是 LLM）
- 工具集
- 策略/规则
- 执行循环

### 职责边界

**应该包含**:
- ✅ 理解用户意图
- ✅ 规划执行步骤
- ✅ 调用工具完成任务
- ✅ 生成响应

**不应该包含**:
- ❌ 消息路由（应该在 Router）
- ❌ 状态持久化（应该在 Store）
- ❌ 渠道通信（应该在 Channel）

### 关键属性

```python
@dataclass
class Agent:
    agent_id: str                    # 唯一标识
    session_id: str                  # 所属会话
    llm_provider: LLMProvider        # LLM 提供者
    tools: List[Tool]                # 可用工具
    system_prompt: str               # 系统提示
    max_iterations: int              # 最大迭代次数
    state: AgentState                # 当前状态
```

### 执行循环

```
1. Perceive (感知)
   ↓
2. Think (推理)
   ↓
3. Act (行动)
   ↓
4. Observe (观察结果)
   ↓
5. Decide (决定是否继续)
   ↓
   └──→ 回到步骤 2 或结束
```

### 设计原则

1. **自主性**: Agent 应该能够自主决策
2. **目标导向**: Agent 应该朝着明确目标工作
3. **适应性**: Agent 应该能够根据反馈调整策略
4. **透明性**: Agent 的推理过程应该可解释

### Agent 类型

**类型 1: 单轮 Agent**
- 接收输入 → 生成输出 → 结束
- 适用于简单问答

**类型 2: 多轮 Agent**
- 多次与用户交互
- 适用于复杂对话

**类型 3: 任务型 Agent**
- 自主执行多步骤任务
- 适用于工作流自动化

**类型 4: 协作型 Agent**
- 与其他 Agent 协作
- 适用于复杂系统

### 来自 nanobot 的实现

- AgentLoop 类实现执行循环
- 支持工具调用和多轮迭代
- 支持子 Agent 派发

---

## 3. Channel (渠道)

### 定义

**Channel 是 Agent 与外部世界交互的通道**

一个 Channel 负责：
- 接收外部消息
- 发送响应消息
- 协议转换
- 身份验证

### 职责边界

**应该包含**:
- ✅ 平台特定的通信协议
- ✅ 消息格式转换
- ✅ 用户身份验证
- ✅ 错误处理和重试

**不应该包含**:
- ❌ Agent 逻辑
- ❌ 业务规则
- ❌ 状态管理

### 关键属性

```python
@dataclass
class Channel:
    channel_id: str              # 唯一标识
    channel_type: str            # 类型（telegram, slack, etc.）
    config: ChannelConfig        # 配置（API key, webhook, etc.）
    authorized_users: List[str]  # 授权用户列表
    status: ChannelStatus        # 当前状态
```

### 消息流

```
External Platform
    ↓ (raw message)
Channel Adapter
    ↓ (normalized message)
Message Bus
    ↓
Agent
    ↓ (response)
Message Bus
    ↓
Channel Adapter
    ↓ (platform-specific format)
External Platform
```

### 设计原则

1. **解耦性**: Channel 与 Agent 完全解耦
2. **可插拔性**: 新增 Channel 不影响核心逻辑
3. **容错性**: Channel 故障不影响其他 Channel
4. **一致性**: 所有 Channel 提供统一的消息格式

### Channel 类型

**类型 1: 推送型 (Push)**
- 平台主动推送消息（Webhook）
- 例如: Telegram Bot, Slack Bot

**类型 2: 拉取型 (Pull)**
- 定期轮询获取消息
- 例如: Email, RSS

**类型 3: 双向型 (Bidirectional)**
- WebSocket 长连接
- 例如: Web Chat

### 来自 nanobot 的实现

- 11 个 Channel 实现（Telegram, Slack, Discord 等）
- 统一的 BaseChannel 抽象
- 每个 Channel 独立运行

---

## 4. Tool (工具)

### 定义

**Tool 是 Agent 可以调用的原子能力单元**

一个 Tool 包含：
- 名称和描述
- 参数定义
- 执行逻辑
- 返回结果

### 职责边界

**应该包含**:
- ✅ 单一、明确的功能
- ✅ 清晰的参数定义
- ✅ 错误处理
- ✅ 执行日志

**不应该包含**:
- ❌ 复杂的业务逻辑（应该拆分为多个 Tool）
- ❌ 状态管理（应该无状态）
- ❌ Agent 决策逻辑

### 关键属性

```python
@dataclass
class Tool:
    name: str                    # 工具名称
    description: str             # 功能描述
    parameters: JSONSchema       # 参数定义
    returns: JSONSchema          # 返回值定义
    category: str                # 分类
    requires_confirmation: bool  # 是否需要用户确认
```

### 执行模式

```python
class Tool(ABC):
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """执行工具"""
        pass

    def validate_params(self, **kwargs) -> bool:
        """验证参数"""
        pass

    def get_schema(self) -> Dict:
        """获取 JSON Schema"""
        pass
```

### 设计原则

1. **单一职责**: 每个 Tool 只做一件事
2. **幂等性**: 相同输入应该产生相同输出（如果可能）
3. **安全性**: 危险操作应该有确认机制
4. **可组合性**: Tool 应该可以组合使用

### Tool 分类

**按功能分类**:
- **信息获取**: web_search, read_file, database_query
- **信息处理**: text_analysis, data_transform
- **执行操作**: write_file, send_email, api_call
- **系统控制**: shell_execute, process_manage

**按风险分类**:
- **只读**: 无副作用，安全
- **可逆**: 有副作用但可撤销
- **不可逆**: 危险操作，需要确认

### 来自 nanobot 的实现

- 9 个内置工具
- 每个工具有 JSON Schema 定义
- 支持 MCP 协议扩展工具

---

## 5. Task (任务)

### 定义

**Task 是 Agent 需要完成的工作单元**

一个 Task 包含：
- 目标描述
- 输入数据
- 执行状态
- 输出结果

### 职责边界

**应该包含**:
- ✅ 明确的目标
- ✅ 可验证的完成条件
- ✅ 执行进度跟踪
- ✅ 结果记录

**不应该包含**:
- ❌ 执行逻辑（应该在 Agent）
- ❌ 工具实现（应该在 Tool）

### 关键属性

```python
@dataclass
class Task:
    task_id: str                 # 唯一标识
    session_id: str              # 所属会话
    description: str             # 任务描述
    status: TaskStatus           # 状态
    priority: int                # 优先级
    created_at: datetime         # 创建时间
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[TaskResult]
    parent_task_id: Optional[str]  # 父任务
```

### 状态机

```
Pending → Running → Completed
            ↓
          Failed
            ↓
          Retrying → Running
```

### 设计原则

1. **可分解性**: 复杂任务应该可以分解为子任务
2. **可追踪性**: 任务状态应该可以查询
3. **可恢复性**: 失败的任务应该可以重试
4. **可取消性**: 运行中的任务应该可以取消

### Task 类型

**类型 1: 同步任务**
- 立即执行，阻塞等待结果
- 适用于快速操作

**类型 2: 异步任务**
- 后台执行，轮询查询状态
- 适用于长时间操作

**类型 3: 定时任务**
- 按计划执行
- 适用于周期性操作

**类型 4: 事件驱动任务**
- 由事件触发
- 适用于响应式操作

### 来自 nanobot 的实现

- 支持子任务派发（subagent）
- 支持定时任务（cron）
- 支持心跳任务（heartbeat）

---

## 6. Skill (技能)

### 定义

**Skill 是 Agent 的高级能力模板，封装了特定领域的知识和流程**

一个 Skill 包含：
- 领域知识
- 执行流程
- 最佳实践
- 示例

### 职责边界

**应该包含**:
- ✅ 领域特定的提示词
- ✅ 推荐的工具组合
- ✅ 执行步骤指导
- ✅ 常见问题处理

**不应该包含**:
- ❌ 工具的具体实现
- ❌ 硬编码的业务逻辑

### 关键属性

```python
@dataclass
class Skill:
    skill_id: str                # 唯一标识
    name: str                    # 技能名称
    description: str             # 功能描述
    prompt_template: str         # 提示词模板
    required_tools: List[str]    # 需要的工具
    examples: List[Example]      # 示例
    category: str                # 分类
```

### 使用模式

```
User Request
    ↓
Skill Matching (根据描述匹配技能)
    ↓
Skill Loading (加载技能提示词)
    ↓
Agent Execution (使用技能指导执行)
    ↓
Result
```

### 设计原则

1. **可复用性**: Skill 应该适用于多个场景
2. **可组合性**: Skill 可以组合使用
3. **可定制性**: Skill 应该支持参数化
4. **可演化性**: Skill 应该易于更新

### Skill 类型

**类型 1: 流程型 Skill**
- 定义执行步骤
- 例如: "代码审查流程"

**类型 2: 知识型 Skill**
- 提供领域知识
- 例如: "Python 最佳实践"

**类型 3: 模板型 Skill**
- 提供输出模板
- 例如: "技术文档模板"

### 来自 nanobot 的实现

- Markdown 格式的 Skill 文件
- 通过 frontmatter 定义元数据
- 动态加载和应用

---

## 7. Workspace (工作空间)

### 定义

**Workspace 是 Agent 操作文件和数据的隔离环境**

一个 Workspace 包含：
- 文件系统
- 临时数据
- 配置文件
- 输出结果

### 职责边界

**应该包含**:
- ✅ Session 相关的文件
- ✅ 临时工作文件
- ✅ 生成的输出
- ✅ 缓存数据

**不应该包含**:
- ❌ 系统文件
- ❌ 用户全局数据
- ❌ 其他 Session 的数据

### 关键属性

```python
@dataclass
class Workspace:
    workspace_id: str            # 唯一标识
    session_id: str              # 所属会话
    root_path: Path              # 根目录
    quota: int                   # 空间配额
    created_at: datetime
```

### 文件组织

```
workspace/
├── sessions/
│   └── {session_id}/
│       └── history.jsonl
├── memory/
│   ├── MEMORY.md
│   └── memories/
├── files/
│   └── {session_id}/
└── cache/
```

### 设计原则

1. **隔离性**: 不同 Workspace 完全隔离
2. **安全性**: 限制访问范围，防止路径遍历
3. **配额管理**: 限制空间使用
4. **清理机制**: 自动清理过期数据

### 来自 nanobot 的实现

- 默认在 `~/.nanobot/workspace/`
- 每个 Session 独立子目录
- 文件工具限制在 Workspace 内操作

---

## 8. Policy (策略)

### 定义

**Policy 是控制 Agent 行为的规则集合**

一个 Policy 定义：
- 允许/禁止的操作
- 资源限制
- 安全规则
- 审批流程

### 职责边界

**应该包含**:
- ✅ 权限控制规则
- ✅ 资源配额规则
- ✅ 安全策略
- ✅ 合规要求

**不应该包含**:
- ❌ 业务逻辑
- ❌ 执行细节

### 关键属性

```python
@dataclass
class Policy:
    policy_id: str               # 唯一标识
    name: str                    # 策略名称
    rules: List[Rule]            # 规则列表
    scope: PolicyScope           # 作用范围
    priority: int                # 优先级
```

### 策略类型

**类型 1: 权限策略**
```python
{
    "tool": "shell_execute",
    "action": "deny",
    "condition": "command.startswith('rm -rf')"
}
```

**类型 2: 配额策略**
```python
{
    "resource": "llm_tokens",
    "limit": 100000,
    "period": "daily"
}
```

**类型 3: 审批策略**
```python
{
    "tool": "send_email",
    "requires_approval": true,
    "approver": "user"
}
```

### 设计原则

1. **最小权限**: 默认拒绝，显式允许
2. **分层控制**: 全局 → 用户 → 会话
3. **可审计**: 所有策略决策应该记录
4. **可配置**: 策略应该易于修改

### 来自 nanobot 的实现

- Channel 级别的用户白名单
- 工作空间路径限制
- 部分工具的权限检查（待完善）

---

## 9. Memory (记忆)

### 定义

**Memory 是 Agent 的长期知识存储，跨越单次对话**

Memory 包含：
- 事实知识
- 用户偏好
- 历史经验
- 学习内容

### 职责边界

**应该包含**:
- ✅ 跨会话的持久信息
- ✅ 用户个人信息
- ✅ 重要的历史决策
- ✅ 学到的知识

**不应该包含**:
- ❌ 当前对话的临时状态（应该在 Session）
- ❌ 原始消息历史（应该在 Session History）

### 关键属性

```python
@dataclass
class Memory:
    memory_id: str               # 唯一标识
    user_id: str                 # 所属用户
    content: str                 # 记忆内容
    type: MemoryType             # 类型
    importance: float            # 重要性评分
    created_at: datetime
    last_accessed: datetime
    access_count: int
```

### Memory 类型

**类型 1: 事实记忆 (Semantic)**
- "用户是 Python 开发者"
- "项目使用 PostgreSQL"

**类型 2: 情景记忆 (Episodic)**
- "上周修复了登录 bug"
- "用户偏好简洁的回复"

**类型 3: 程序记忆 (Procedural)**
- "部署流程是..."
- "代码审查标准是..."

### 整合机制

```
Session History (长)
    ↓ (达到阈值)
LLM Summarization
    ↓
Memory Extraction
    ↓
Memory Store (短)
```

### 设计原则

1. **选择性**: 不是所有信息都值得记忆
2. **可检索性**: Memory 应该易于搜索和召回
3. **可遗忘性**: 过时的 Memory 应该被清理
4. **可验证性**: Memory 应该可以追溯来源

### 来自 nanobot 的实现

- LLM 驱动的自动整合
- Markdown 格式存储
- 分类存储（user, feedback, project, reference）

---

## 10. Event (事件)

### 定义

**Event 是系统中发生的重要事情的记录**

Event 用于：
- 触发响应
- 审计追踪
- 系统监控
- 异步通信

### 职责边界

**应该包含**:
- ✅ 事件类型
- ✅ 发生时间
- ✅ 相关实体
- ✅ 事件数据

**不应该包含**:
- ❌ 处理逻辑（应该在 Handler）
- ❌ 业务规则（应该在 Policy）

### 关键属性

```python
@dataclass
class Event:
    event_id: str                # 唯一标识
    event_type: str              # 事件类型
    source: str                  # 事件来源
    timestamp: datetime          # 发生时间
    data: Dict[str, Any]         # 事件数据
    metadata: Dict[str, Any]     # 元数据
```

### Event 类型

**系统事件**:
- `session.created`
- `session.closed`
- `agent.started`
- `agent.completed`

**用户事件**:
- `message.received`
- `message.sent`
- `tool.executed`

**定时事件**:
- `cron.triggered`
- `heartbeat.tick`

### 事件驱动模式

```
Event Source
    ↓
Event Bus
    ↓
Event Handlers (多个)
    ↓
Actions
```

### 设计原则

1. **不可变性**: Event 一旦产生不可修改
2. **完整性**: Event 应该包含足够的上下文
3. **时序性**: Event 应该有明确的时间戳
4. **可追溯性**: Event 应该可以追溯到源头

### 来自 nanobot 的实现

- 定时事件（cron, heartbeat）
- 消息事件（inbound, outbound）
- 缺少统一的事件系统（可改进）

---

## 抽象关系图

```
User
  ├── Session (1:N)
  │     ├── Agent (1:1)
  │     │     ├── Tool (N:M)
  │     │     └── Skill (N:M)
  │     ├── Task (1:N)
  │     └── Workspace (1:1)
  ├── Memory (1:N)
  └── Policy (1:N)

Channel (N:M) ←→ Session
Event (N:M) ←→ All Entities
```

---

## 设计检查清单

在设计 AgentOS 时，确保每个抽象都回答了以下问题：

- [ ] **边界清晰**: 职责是否明确？
- [ ] **可测试**: 是否易于单元测试？
- [ ] **可扩展**: 是否易于添加新功能？
- [ ] **可维护**: 是否易于理解和修改？
- [ ] **性能**: 是否有性能瓶颈？
- [ ] **安全**: 是否有安全风险？
- [ ] **可观测**: 是否易于监控和调试？
