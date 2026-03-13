# nanobot System Design Documentation

## Navigation & Reading Order

This documentation package provides a complete reverse-engineered system design analysis of nanobot, an ultra-lightweight personal AI assistant framework.

### Recommended Reading Order

**Phase 1: Understanding the System**
1. [01_system_scope_and_goals.md](01_system_scope_and_goals.md) - What nanobot is and why it exists
2. [02_context_view.md](02_context_view.md) - External dependencies and boundaries
3. [03_container_view.md](03_container_view.md) - Runtime architecture

**Phase 2: Internal Architecture**
4. [04_component_view.md](04_component_view.md) - Core subsystems breakdown
5. [05_domain_model.md](05_domain_model.md) - Key concepts and entities
6. [06_runtime_scenarios.md](06_runtime_scenarios.md) - How the system behaves

**Phase 3: Deep Dive**
7. [07_state_and_session_model.md](07_state_and_session_model.md) - Session lifecycle
8. [08_tool_and_extension_model.md](08_tool_and_extension_model.md) - Extensibility mechanisms
9. [09_security_and_trust_boundaries.md](09_security_and_trust_boundaries.md) - Security model
10. [10_configuration_and_operability.md](10_configuration_and_operability.md) - Configuration system

**Phase 4: Implementation Details**
11. [11_deployment_view.md](11_deployment_view.md) - Deployment options
12. [12_codebase_mapping.md](12_codebase_mapping.md) - Code navigation guide
13. [13_architectural_decisions_and_tradeoffs.md](13_architectural_decisions_and_tradeoffs.md) - Design rationale

**Phase 5: Learning & Reuse**
14. [14_reusable_agentos_blueprint.md](14_reusable_agentos_blueprint.md) - Generic AgentOS patterns
15. [15_reimplementation_plan.md](15_reimplementation_plan.md) - How to build similar systems
16. [16_open_questions.md](16_open_questions.md) - Unresolved items

## One-Page Summary

**nanobot** is a lightweight personal AI assistant framework (v0.1.4) that delivers core agent functionality with 99% fewer lines of code than OpenClaw.

### Core Architecture Pattern
```
Channels → MessageBus → AgentLoop → LLM Provider
                ↓           ↓
            Sessions    Tool Registry
```

### Key Characteristics
- **Minimalist Design**: ~64 Python files, ~6K core lines
- **Multi-Channel**: Telegram, Discord, Slack, WhatsApp, Email, Matrix, Feishu, DingTalk, QQ, WeCom
- **Async-First**: Built on asyncio for concurrent message handling
- **Provider-Agnostic**: Supports 20+ LLM providers via LiteLLM
- **Tool-Extensible**: Built-in tools + MCP server integration
- **Session-Persistent**: JSONL-based conversation history with memory consolidation

### Primary Use Cases
1. Personal AI assistant accessible via multiple chat platforms
2. Autonomous task execution with tool calling
3. Long-running conversations with memory
4. Scheduled/cron-based automation
5. Multi-user deployment with per-channel isolation

### Technology Stack
- **Language**: Python 3.11+
- **Async Runtime**: asyncio
- **LLM Integration**: LiteLLM (unified API), direct providers (OpenAI, Anthropic, Azure)
- **Channels**: Platform-specific SDKs (python-telegram-bot, discord.py, slack-sdk, etc.)
- **Storage**: File-based (JSONL sessions, Markdown memory)
- **Bridge**: Node.js/TypeScript (WhatsApp only)

### Distinguishing Features
1. **Ultra-lightweight**: Minimal dependencies, simple architecture
2. **File-based state**: No database required
3. **Memory consolidation**: Automatic summarization to extend context
4. **Skills system**: Markdown-based capability extensions
5. **Heartbeat service**: Proactive agent behavior
6. **Subagent spawning**: Parallel task execution

## Document Conventions

### Evidence Tags
- **[FACT]**: Directly verified from code/config/docs
- **[INFERENCE]**: Reasonable deduction from implementation patterns
- **[OPEN QUESTION]**: Requires further investigation

### Diagram Format
All diagrams use Mermaid syntax for portability and version control.

### File References
References to code use format: `module.file:line` or `directory/file.py`

## Project Context

- **Repository**: https://github.com/HKUDS/nanobot
- **Version Analyzed**: v0.1.4.post4
- **Analysis Date**: 2026-03-12
- **License**: MIT
- **Primary Language**: Python
- **Inspiration**: OpenClaw (but 99% smaller)
