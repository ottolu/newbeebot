# System Scope and Goals

## Purpose

**[FACT]** nanobot is an ultra-lightweight personal AI assistant framework designed to provide core agent functionality with minimal code complexity.

**[FACT]** Explicitly inspired by OpenClaw but delivers "99% fewer lines of code" while maintaining essential features.

## Target Users

**[FACT]** Based on configuration and channel support:
1. **Individual developers** - Personal AI assistant for daily tasks
2. **Small teams** - Shared assistant via group chats
3. **Power users** - Multi-platform access to same agent
4. **Hobbyists** - Self-hosted AI assistant experimentation

**[INFERENCE]** Not designed for:
- Enterprise-scale deployments (no multi-tenancy, no database)
- High-throughput production services (single-process, file-based state)
- Complex workflow orchestration (basic subagent support only)

## System Boundaries

### In Scope
**[FACT]** From codebase analysis:
- Multi-channel chat interface (11 platforms)
- LLM provider abstraction (20+ providers)
- Tool execution (filesystem, shell, web, MCP)
- Session management with memory
- Scheduled tasks (cron)
- Subagent spawning
- OAuth authentication (OpenAI Codex, GitHub Copilot)

### Out of Scope
**[INFERENCE]** Based on architecture:
- Database-backed persistence
- Horizontal scaling / load balancing
- Complex workflow DAGs
- Built-in UI/web interface
- Multi-tenant isolation
- Real-time collaboration between users
- Advanced observability (metrics, tracing)

## Core Goals

### 1. Simplicity
**[FACT]** Primary design goal from README:
- Minimal codebase (~64 Python files)
- No database required
- File-based configuration
- Single-process deployment

### 2. Accessibility
**[FACT]** Multi-channel support enables:
- Use existing chat apps (no new UI to learn)
- Platform flexibility (mobile, desktop, web)
- Consistent experience across channels

### 3. Extensibility
**[FACT]** Extension mechanisms:
- Skills system (Markdown-based)
- MCP server integration
- Custom tool registration
- Provider plugins

### 4. Autonomy
**[FACT]** Agent capabilities:
- Tool calling with iteration loop
- Memory consolidation
- Proactive heartbeat service
- Scheduled task execution

## Non-Goals

**[INFERENCE]** Based on implementation choices:

1. **Not a production-grade service**
   - No health checks, metrics, or monitoring
   - Single point of failure (one process)
   - No graceful degradation

2. **Not a workflow engine**
   - Basic subagent support, not complex orchestration
   - No workflow visualization or debugging
   - No retry policies or error recovery strategies

3. **Not a multi-user platform**
   - No user management or RBAC
   - Simple allowlist-based access control
   - No usage quotas or rate limiting

4. **Not a data processing system**
   - No batch processing
   - No data pipelines
   - No analytics or reporting

## Differentiation

### vs. OpenClaw
**[FACT]** From README:
- 99% fewer lines of code
- Same core functionality
- Simpler architecture

**[INFERENCE]** Trade-offs:
- Less feature-rich
- Fewer abstractions
- More direct implementation

### vs. Generic Chatbot
**[FACT]** Key differences:
- Tool execution capability
- Multi-turn conversation memory
- Workspace-aware (filesystem access)
- Scheduled/proactive behavior
- Subagent spawning

### vs. LangChain/LlamaIndex
**[FACT]** Architectural differences:
- Integrated multi-channel support
- Session management built-in
- Simpler tool abstraction
- No complex chains/graphs

**[INFERENCE]** nanobot is:
- More opinionated (fewer choices)
- More integrated (batteries included)
- Less flexible (harder to customize deeply)

## Success Criteria

**[INFERENCE]** Based on design:
1. **Ease of setup**: < 5 minutes from install to first chat
2. **Code simplicity**: Readable by intermediate Python developers
3. **Feature completeness**: Core agent loop + tools + memory
4. **Reliability**: Handles common errors gracefully
5. **Extensibility**: Users can add skills/tools without forking

## System Context

### What nanobot IS
- Personal AI assistant framework
- Multi-channel chat interface
- Tool-calling agent runtime
- Conversation memory system
- Task scheduler

### What nanobot IS NOT
- Production SaaS platform
- Workflow orchestration engine
- Data processing pipeline
- Multi-tenant service
- Enterprise integration hub

## Key Constraints

**[FACT]** From implementation:
1. **Single-process**: No distributed architecture
2. **File-based**: No database dependency
3. **Python 3.11+**: Modern Python features required
4. **Async-first**: Built on asyncio
5. **LLM-dependent**: Requires external LLM API access

**[INFERENCE]** Implications:
- Limited scalability (vertical only)
- State persistence via filesystem
- Concurrent message handling within single process
- Network latency to LLM providers
