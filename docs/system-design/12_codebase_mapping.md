# Codebase Mapping

## 架构到代码的映射

**[FACT]** 从目录结构到架构组件的映射：

### 核心模块映射表

| 架构组件 | 代码位置 | 关键文件 | 行数 |
|---------|---------|---------|------|
| Message Bus | `nanobot/bus/` | `queue.py`, `events.py` | ~80 |
| Agent Loop | `nanobot/agent/` | `loop.py` | ~495 |
| Context Builder | `nanobot/agent/` | `context.py` | ~192 |
| Tool Registry | `nanobot/agent/tools/` | `registry.py`, `base.py` | ~250 |
| Session Manager | `nanobot/session/` | `manager.py` | ~214 |
| Memory System | `nanobot/agent/` | `memory.py` | ~270 |
| Skills System | `nanobot/agent/` | `skills.py` | ~260 |
| Provider Layer | `nanobot/providers/` | `base.py`, `registry.py` | ~350 |
| Channel Adapters | `nanobot/channels/` | 11 个实现文件 | ~3000 |
| Config System | `nanobot/config/` | `schema.py`, `loader.py` | ~550 |
| CLI | `nanobot/cli/` | `commands.py` | ~925 |
| Cron Service | `nanobot/cron/` | `service.py` | ~150 |
| Heartbeat | `nanobot/heartbeat/` | `service.py` | ~120 |

## 最值得先读的 20 个文件

**[FACT]** 按理解顺序推荐：

### 第一阶段：理解数据流

1. **`bus/events.py`** (39 行)
   - 定义 InboundMessage 和 OutboundMessage
   - 理解消息结构

2. **`bus/queue.py`** (45 行)
   - 简单的 asyncio 队列封装
   - 理解消息路由

3. **`session/manager.py`** (214 行)
   - Session 数据结构
   - JSONL 持久化
   - 理解会话管理

### 第二阶段：理解核心逻辑

4. **`agent/loop.py`** (495 行) ⭐ 最重要
   - 核心处理循环
   - 工具调用逻辑
   - 消息处理流程

5. **`agent/context.py`** (192 行)
   - System prompt 构建
   - 消息列表组装
   - 理解上下文管理

6. **`agent/tools/base.py`** (182 行)
   - Tool 抽象接口
   - 参数验证逻辑
   - 理解工具系统

7. **`agent/tools/registry.py`** (68 行)
   - 工具注册和执行
   - 理解工具调度

### 第三阶段：理解扩展机制

8. **`agent/memory.py`** (270 行)
   - Memory 整合逻辑
   - Token 估算
   - 理解长期记忆

9. **`agent/skills.py`** (260 行)
   - Skills 加载
   - Metadata 解析
   - 理解技能系统

10. **`agent/subagent.py`** (228 行)
    - 子代理生成
    - 并行任务执行
    - 理解任务分发

### 第四阶段：理解 Provider 层

11. **`providers/base.py`** (271 行)
    - LLMProvider 抽象
    - 重试逻辑
    - 理解 LLM 集成

12. **`providers/registry.py`** (120 行)
    - Provider 规范定义
    - 匹配逻辑
    - 理解多 provider 支持

13. **`providers/litellm_provider.py`** (150 行)
    - LiteLLM 集成
    - 大多数 provider 的实现

### 第五阶段：理解 Channel 层

14. **`channels/base.py`** (135 行)
    - Channel 抽象接口
    - Allowlist 检查
    - 理解 channel 模式

15. **`channels/telegram.py`** (305 行)
    - 完整的 channel 实现示例
    - 媒体处理
    - 理解平台集成

16. **`channels/manager.py`** (80 行)
    - Channel 生命周期管理
    - 理解多 channel 协调

### 第六阶段：理解配置和工具

17. **`config/schema.py`** (450 行)
    - 完整配置结构
    - Pydantic 模型
    - 理解配置系统

18. **`agent/tools/filesystem.py`** (200 行)
    - 文件操作工具
    - Workspace 限制
    - 理解工具实现

19. **`agent/tools/mcp.py`** (180 行)
    - MCP 集成
    - 动态工具注册
    - 理解扩展机制

20. **`cli/commands.py`** (925 行)
    - CLI 入口
    - Gateway 启动
    - 理解部署模式

## 目录结构详解

**[FACT]** 完整目录树：

```
nanobot/
├── __init__.py              # 版本信息
├── __main__.py              # 入口点
├── agent/                   # 核心 Agent 逻辑
│   ├── __init__.py
│   ├── context.py          # 上下文构建
│   ├── loop.py             # 主循环 ⭐
│   ├── memory.py           # 内存整合
│   ├── skills.py           # 技能加载
│   ├── subagent.py         # 子代理
│   └── tools/              # 工具实现
│       ├── base.py         # 工具基类
│       ├── registry.py     # 工具注册表
│       ├── filesystem.py   # 文件操作
│       ├── shell.py        # Shell 执行
│       ├── web.py          # Web 搜索/抓取
│       ├── message.py      # 消息发送
│       ├── spawn.py        # 子代理生成
│       ├── cron.py         # Cron 任务
│       └── mcp.py          # MCP 集成
├── bus/                     # 消息总线
│   ├── events.py           # 消息定义
│   └── queue.py            # 队列实现
├── channels/                # Channel 适配器
│   ├── base.py             # Channel 基类
│   ├── manager.py          # Channel 管理
│   ├── registry.py         # Channel 发现
│   ├── telegram.py         # Telegram
│   ├── discord.py          # Discord
│   ├── slack.py            # Slack
│   ├── whatsapp.py         # WhatsApp
│   ├── feishu.py           # Feishu
│   ├── dingtalk.py         # DingTalk
│   ├── email.py            # Email
│   ├── matrix.py           # Matrix
│   ├── mochat.py           # Mochat
│   ├── qq.py               # QQ
│   └── wecom.py            # WeCom
├── cli/                     # 命令行接口
│   └── commands.py         # CLI 命令
├── config/                  # 配置系统
│   ├── __init__.py
│   ├── loader.py           # 配置加载
│   ├── paths.py            # 路径解析
│   └── schema.py           # 配置模型 ⭐
├── cron/                    # Cron 服务
│   ├── service.py          # Cron 调度
│   └── types.py            # 数据类型
├── heartbeat/               # Heartbeat 服务
│   └── service.py          # 心跳逻辑
├── providers/               # LLM Provider
│   ├── base.py             # Provider 基类
│   ├── registry.py         # Provider 注册
│   ├── litellm_provider.py # LiteLLM 实现
│   ├── custom_provider.py  # 自定义 Provider
│   ├── azure_openai_provider.py
│   ├── openai_codex_provider.py
│   └── transcription.py    # 音频转录
├── session/                 # 会话管理
│   └── manager.py          # Session 管理
├── templates/               # 模板文件
│   ├── AGENTS.md
│   ├── SOUL.md
│   ├── USER.md
│   ├── TOOLS.md
│   ├── HEARTBEAT.md
│   └── memory/
│       └── MEMORY.md
├── skills/                  # 内置技能
│   ├── memory/
│   ├── github/
│   ├── weather/
│   └── ...
└── utils/                   # 工具函数
    └── helpers.py
```

## 关键接口定义位置

**[FACT]** 重要接口的定义位置：

| 接口 | 文件 | 行号范围 |
|-----|------|---------|
| `Tool` | `agent/tools/base.py` | 7-182 |
| `LLMProvider` | `providers/base.py` | 69-271 |
| `BaseChannel` | `channels/base.py` | 15-135 |
| `Session` | `session/manager.py` | 16-71 |
| `InboundMessage` | `bus/events.py` | 9-25 |
| `OutboundMessage` | `bus/events.py` | 28-37 |
| `Config` | `config/schema.py` | 351-450 |

## 数据流追踪

**[FACT]** 关键数据流的代码路径：

### 用户消息处理

```
channels/telegram.py:_handle_message()
  → bus/queue.py:publish_inbound()
  → agent/loop.py:consume_inbound()
  → agent/loop.py:_dispatch()
  → agent/loop.py:_process_message()
  → agent/context.py:build_messages()
  → agent/loop.py:_run_agent_loop()
  → providers/base.py:chat_with_retry()
  → agent/tools/registry.py:execute()
  → session/manager.py:save()
  → bus/queue.py:publish_outbound()
  → channels/telegram.py:send()
```

### Memory 整合

```
agent/loop.py:_process_message()
  → agent/memory.py:maybe_consolidate_by_tokens()
  → session/manager.py:get_history()
  → providers/base.py:chat()
  → agent/memory.py:_consolidate()
  → agent/memory.py:MemoryStore.append()
  → session/manager.py:save()
```
