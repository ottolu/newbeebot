# Runtime Scenarios

## Scenario 1: User Message Processing

**[FACT]** 完整的消息处理流程，从 `channels/telegram.py` 和 `agent/loop.py` 分析：

### Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant Telegram
    participant Channel
    participant Bus
    participant AgentLoop
    participant Provider
    participant Tool
    participant Session

    User->>Telegram: Send message
    Telegram->>Channel: on_message event
    Channel->>Channel: Check allowlist
    Channel->>Bus: publish_inbound(msg)
    Bus->>AgentLoop: consume_inbound()
    AgentLoop->>Session: get_or_create(session_key)
    AgentLoop->>Session: get_history()
    AgentLoop->>AgentLoop: build_messages(history + current)

    loop Tool Call Iteration (max 40)
        AgentLoop->>Provider: chat(messages, tools)
        Provider-->>AgentLoop: LLMResponse

        alt Has tool calls
            AgentLoop->>Tool: execute(tool_call)
            Tool-->>AgentLoop: result
            AgentLoop->>AgentLoop: add_tool_result to messages
        else Has text response
            AgentLoop->>Session: save messages
            AgentLoop->>Bus: publish_outbound(response)
        end
    end

    Bus->>Channel: consume_outbound()
    Channel->>Telegram: send_message
    Telegram->>User: Display response
```

### 关键步骤

**[FACT]** 从代码追踪：

1. **接收阶段** (`channels/telegram.py:_handle_message`)
   - 平台 SDK 触发事件
   - 提取 sender_id, chat_id, content
   - 检查 allowlist
   - 创建 InboundMessage

2. **路由阶段** (`bus/queue.py`)
   - 消息放入 inbound 队列
   - AgentLoop 消费消息
   - 创建 asyncio.Task 处理

3. **上下文构建** (`agent/context.py`)
   - 加载 session history
   - 构建 system prompt (identity + memory + skills)
   - 添加 runtime context (时间、channel)
   - 合并为完整 messages 列表

4. **LLM 调用** (`agent/loop.py:_run_agent_loop`)
   - 调用 provider.chat_with_retry()
   - 获取响应（文本或工具调用）
   - 如有工具调用，执行并循环

5. **工具执行** (`agent/tools/registry.py`)
   - 验证参数
   - 执行工具
   - 返回字符串结果

6. **保存状态** (`session/manager.py`)
   - 追加消息到 session
   - 保存到 JSONL 文件
   - 检查是否需要 consolidation

7. **响应发送** (`channels/telegram.py:send`)
   - 从 outbound 队列消费
   - 调用平台 API 发送
   - 处理错误和重试

## Scenario 2: Tool Call Chain

**[FACT]** 工具调用链示例，从 `agent/loop.py` 分析：

### Example Flow

```
User: "Read the README and summarize it"

Iteration 1:
  LLM → tool_call: read_file("README.md")
  Tool → result: "# nanobot\n\nA lightweight..."

Iteration 2:
  LLM → text: "The README describes nanobot as..."
  → Return to user
```

### Sequence Diagram

```mermaid
sequenceDiagram
    participant Agent
    participant LLM
    participant ToolRegistry
    participant ReadFileTool

    Agent->>LLM: chat(messages, tools)
    LLM-->>Agent: tool_call: read_file("README.md")
    Agent->>ToolRegistry: execute("read_file", args)
    ToolRegistry->>ReadFileTool: execute(file_path="README.md")
    ReadFileTool-->>ToolRegistry: file content
    ToolRegistry-->>Agent: result string
    Agent->>Agent: add tool_result to messages
    Agent->>LLM: chat(messages + tool_result, tools)
    LLM-->>Agent: text response
    Agent-->>User: final answer
```

### 关键机制

**[FACT]** 从 `agent/loop.py:_run_agent_loop`:

- **迭代限制**: 最多 40 次（防止无限循环）
- **工具结果截断**: 超过 16,000 字符会被截断
- **错误处理**: 工具失败返回错误信息，LLM 可以重试
- **进度流式**: 可选的工具调用提示发送到用户

## Scenario 3: Memory Consolidation

**[FACT]** 内存整合流程，从 `agent/memory.py` 分析：

### Trigger Condition

```python
estimated_tokens = len(messages) * 100  # 粗略估算
if estimated_tokens > context_window_tokens * 0.8:
    consolidate()
```

### Consolidation Process

```mermaid
sequenceDiagram
    participant AgentLoop
    participant MemoryConsolidator
    participant Session
    participant LLM
    participant MemoryStore

    AgentLoop->>MemoryConsolidator: maybe_consolidate_by_tokens(session)
    MemoryConsolidator->>Session: get unconsolidated messages
    MemoryConsolidator->>MemoryConsolidator: estimate tokens

    alt Exceeds threshold
        MemoryConsolidator->>LLM: summarize(messages)
        LLM-->>MemoryConsolidator: summary
        MemoryConsolidator->>MemoryStore: append to MEMORY.md
        MemoryConsolidator->>MemoryStore: append to HISTORY.md
        MemoryConsolidator->>Session: update last_consolidated
        MemoryConsolidator->>Session: save()
    end
```

### 输出格式

**[FACT]** 从 `agent/memory.py`:

**MEMORY.md** (事实提取):
```markdown
- User prefers Python over JavaScript
- Working on nanobot documentation project
- Uses macOS with Python 3.11
```

**HISTORY.md** (时间线):
```markdown
[2026-03-12 08:30] User asked about nanobot architecture
[2026-03-12 08:35] Created system design documentation
```

## Scenario 4: Subagent Spawning

**[FACT]** 子代理生成流程，从 `agent/subagent.py` 分析：

### Use Case

```
User: "Spawn a task to research Python async patterns"
```

### Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant MainAgent
    participant SpawnTool
    participant SubagentManager
    participant Subagent
    participant LLM

    User->>MainAgent: "spawn task to research..."
    MainAgent->>LLM: chat with spawn tool
    LLM-->>MainAgent: tool_call: spawn(prompt="research...")
    MainAgent->>SpawnTool: execute(prompt)
    SpawnTool->>SubagentManager: spawn(prompt, session_key)
    SubagentManager->>Subagent: create_task(process)
    Subagent->>LLM: independent chat loop
    LLM-->>Subagent: responses
    Subagent-->>SubagentManager: result
    SubagentManager-->>SpawnTool: task_id + result
    SpawnTool-->>MainAgent: "Spawned task {id}: {result}"
    MainAgent-->>User: "Task completed: ..."
```

### 关键特性

**[FACT]**:
- 独立的消息历史
- 并行执行（asyncio.Task）
- 可通过 /stop 取消
- 结果返回给父代理

## Scenario 5: Cron Job Execution

**[FACT]** 定时任务执行，从 `cron/service.py` 和 `agent/loop.py` 分析：

### Creation

```
User: "Schedule a daily reminder at 9am"
LLM: tool_call: cron(schedule="0 9 * * *", message="Daily reminder")
```

### Execution Flow

```mermaid
sequenceDiagram
    participant CronService
    participant AgentLoop
    participant LLM
    participant Channel

    loop Every second
        CronService->>CronService: check due jobs
    end

    CronService->>CronService: job is due
    CronService->>AgentLoop: on_job(job)
    AgentLoop->>AgentLoop: process_direct(job.message)
    AgentLoop->>LLM: chat with job instruction
    LLM-->>AgentLoop: response

    alt job.deliver == true
        AgentLoop->>Channel: send to job.channel:job.to
    end

    AgentLoop-->>CronService: result
```

### 持久化

**[FACT]** 存储在 `~/.nanobot/cron/jobs.json`:
```json
{
  "jobs": [
    {
      "id": "uuid",
      "name": "daily-reminder",
      "schedule": "0 9 * * *",
      "payload": {
        "message": "Check daily tasks",
        "channel": "telegram",
        "to": "123456",
        "deliver": true
      },
      "enabled": true
    }
  ]
}
```

## Scenario 6: Session Restart (/new)

**[FACT]** 会话重启流程，从 `agent/loop.py:_process_message`:

### Sequence

```mermaid
sequenceDiagram
    participant User
    participant AgentLoop
    participant MemoryConsolidator
    participant Session
    participant MemoryStore

    User->>AgentLoop: "/new"
    AgentLoop->>MemoryConsolidator: archive_unconsolidated(session)
    MemoryConsolidator->>Session: get unconsolidated messages
    MemoryConsolidator->>MemoryStore: consolidate to MEMORY.md/HISTORY.md
    MemoryConsolidator-->>AgentLoop: success
    AgentLoop->>Session: clear()
    AgentLoop->>Session: save()
    AgentLoop->>Session: invalidate cache
    AgentLoop-->>User: "New session started."
```

### 关键点

**[FACT]**:
- 未整合的消息先归档到 memory
- Session 清空但保留 key
- 缓存失效，下次重新加载
- 失败时不清空（保护数据）
