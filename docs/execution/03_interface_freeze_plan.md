# Interface Freeze Plan

## Goal

Freeze the contracts that multiple implementation threads must share before broad coding starts.

The contracts below are intentionally small. MVP needs stable seams more than feature-rich APIs.

---

## Freeze Priority

## Freeze Now

- session/state service
- tool registry and tool execution contracts
- provider contract
- runtime/orchestration handoff contract
- channel adapter contract
- config schema
- core event types

## Freeze After First Runnable Slice

- richer routing/event bus behavior
- memory consolidation contract
- server APIs
- extracted services

---

## 1. Session / State Service

### Proposed contract

- `SessionStore.create_session(...) -> SessionMetadata`
- `SessionStore.save_message(session_id, message) -> None`
- `SessionStore.load_history(session_id, limit=None) -> list[Message]`
- `SessionStore.get_session_metadata(session_id) -> SessionMetadata`
- `SessionStore.list_sessions(...) -> list[SessionMetadata]`

### Why freeze early

- storage, runtime, CLI, and future server all depend on it
- message model shape and persistence semantics should not drift per module

### Risk level

High

### First implementation guidance

- implement in-memory and file-backed versions behind the same contract
- write contract tests first

---

## 2. Tool Registry / Execution Interface

### Proposed contract

- `Tool.name`
- `Tool.description`
- `Tool.parameters`
- `Tool.execute(**kwargs) -> ToolResult`
- `ToolRegistry.register(tool) -> None`
- `ToolRegistry.get(name) -> Tool`
- `ToolRegistry.list_tools(...) -> list[ToolMetadata]`
- `ToolRegistry.get_schemas() -> list[dict]`

### Why freeze early

- runtime, provider tool-calling, policy, and future MCP/tool plugins all depend on it

### Risk level

High

### First implementation guidance

- freeze schema output format now
- treat destructive tools as opt-in later
- use contract tests and one smoke-tested built-in tool

---

## 3. Routing / Orchestration Interface

### Proposed contract

- `AgentLoop.run(session_id, inbound_message, context) -> AgentResponse`
- `AgentResponse.messages`
- `AgentResponse.final_response`
- `AgentResponse.tool_calls_made`
- `AgentResponse.iterations`

### Why freeze early

- CLI and future server should integrate with runtime without owning loop internals

### Risk level

High

### First implementation guidance

- keep runtime surface narrow
- defer advanced task scheduling and subagents
- begin with synchronous-within-session semantics

---

## 4. Channel Adapter Interface

### Proposed contract

- `Channel.channel_id`
- `Channel.start()`
- `Channel.stop()`
- `Channel.send(outbound_message)`
- `Channel.is_authorized(user_id) -> bool`

### Why freeze early

- CLI channel starts now; more channels come later
- without a frozen channel contract, every channel thread will invent a different message boundary

### Risk level

Medium

### First implementation guidance

- start with CLI adapter only
- keep channel adapters thin
- forbid runtime logic in channel modules

---

## 5. Event Bus / Event Types

### Proposed contract

- `InboundMessage`
- `OutboundMessage`
- `Attachment`
- `SystemEvent`
- `EventType`

Optional early message bus contract:

- `MessageBus.enqueue_inbound`
- `MessageBus.dequeue_inbound`
- `MessageBus.enqueue_outbound`
- `MessageBus.dequeue_outbound`

### Why freeze early

- even if the full bus implementation waits, event shapes should not

### Risk level

Medium

### First implementation guidance

- freeze event payload schema now
- allow message bus implementation to remain in-memory

---

## 6. Config Schema

### Proposed MVP sections

- `system`
- `agent`
- `provider`
- `storage`
- `tools`
- `cli`

### Why freeze early

- CLI wiring, provider selection, storage roots, policy defaults, and tests all need the same config shape

### Risk level

High

### First implementation guidance

- keep schema small
- reserve optional sections for future channels/server
- allow environment-variable override strategy from day one

---

## 7. Persistence Abstraction

### Proposed contract

- `SessionStore`
- `WorkspaceStore` or workspace access boundary
- file path safety helpers behind a policy-aware abstraction

### Why freeze early

- storage implementation may evolve from file-only to richer backends later

### Risk level

Medium

### First implementation guidance

- freeze logical behavior, not backend choice
- keep filesystem-first but backend-agnostic contracts

---

## 8. Policy / Auth / Permission Boundary

### Proposed contract

- `PolicyEngine.check_tool_permission(tool_name, context) -> bool`
- `PolicyEngine.check_path_access(path, context) -> bool`
- `PolicyEngine.check_resource_limit(resource_type, amount, context) -> bool`

### Why freeze early

- tools and runtime need a single safety gate
- channel auth and execution auth must not become the same thing

### Risk level

High

### First implementation guidance

- CLI MVP can use a simple allow-all or restricted-local policy implementation
- keep richer auth out of MVP, but keep the boundary explicit

---

## High-Risk Interfaces

These need the highest change discipline:

- `SessionStore`
- `Tool` / `ToolRegistry`
- `AgentLoop.run`
- config schema
- `PolicyEngine`

If these shift late, multiple downstream tasks will churn.

---

## Stub / Contract-Test First Candidates

These should be written as contracts + tests before full implementation:

- `SessionStore`
- `ToolRegistry`
- `AgentLoop`
- `Channel`
- config loading/validation

Recommended first test shape:

- contract smoke test for in-memory implementation,
- regression test for file-backed persistence,
- tool loop smoke test using fake provider,
- CLI smoke test calling the same runtime facade.

---

## Freeze Change Process

If a frozen interface must change:

1. add the mismatch to this document,
2. list impacted tasks/modules,
3. update tests first,
4. update the contract,
5. then update implementations.

No silent contract widening in downstream modules.
