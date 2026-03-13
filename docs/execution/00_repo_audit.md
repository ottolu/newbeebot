# Repository Audit

## Executive Summary

`newbeebot` currently contains design-time documentation only. There is no application code, package layout, developer tooling, CI pipeline, or runnable MVP skeleton yet. The repository is therefore in a strong design state but a zero-implementation state.

The source-of-truth documents converge on a **Python 3.11+**, **async-first**, **single-process**, **monorepo**, **contract-first** AgentOS-style system with a **CLI-first MVP**, **file-based persistence**, **provider abstraction**, **tool registry**, and a later path toward multi-channel, memory, server, and orchestration services.

The immediate engineering goal is not feature breadth. It is to convert the existing design into:

1. frozen module boundaries,
2. frozen core interfaces,
3. a minimal runnable vertical slice,
4. a repository layout that multiple Codex agents can implement in parallel with minimal file collisions.

---

## System Goals

Based on `docs/system-design/*`, `docs/blueprint/*`, and `docs/implementation/*`, the project goals are:

- Build a lightweight AgentOS-inspired runtime guided by this repository's own design docs, not by copying OpenClaw or nanobot.
- Keep architecture layered and explicit:
  - access/channels
  - routing/message bus
  - orchestration/runtime
  - execution/providers/tools/policy
  - state/session/memory/workspace/config
- Prefer a simple, single-process, async runtime before any distributed architecture.
- Support extensibility through clear contracts rather than ad hoc coupling.
- Keep the MVP CLI-first and local-first.
- Make later expansion to server, more channels, memory consolidation, MCP, and service extraction possible without destabilizing the core.

---

## MVP Scope

The implementation documents are consistent on the MVP:

- One channel only: `CLI`
- One runnable agent loop
- Provider abstraction with a simple initial provider implementation
- Tool registry with a very small safe tool set
- Session persistence and session history inspection
- Simple config loading
- Basic policy boundary
- Local workspace assumptions
- Testable end-to-end local loop

MVP explicitly excludes:

- production multi-channel support,
- advanced memory consolidation,
- subagent orchestration,
- cron/heartbeat,
- multi-tenant auth,
- web UI,
- distributed deployment,
- advanced observability stack.

---

## V1 Scope

From `docs/system-design/15_reimplementation_plan.md` and `docs/implementation/04_mvp_build_plan.md`, the first expansion beyond MVP should add:

- message bus abstraction as a stable routing boundary,
- more tools,
- more channels such as Telegram/Slack,
- richer configuration,
- stronger error handling and retries,
- better runtime integration tests,
- optional server surface,
- early memory capability.

---

## V2 Scope

The V2 and later documents point to:

- MCP integration,
- skills system maturation,
- subagent support,
- cron/heartbeat/proactive behavior,
- stronger policy and auth boundaries,
- artifact-oriented workflows,
- better observability,
- optional server/service decomposition,
- enterprise/workflow capabilities only after the simpler stack is stable.

This means the near-term repository should reserve extension points, but it must not implement V2 complexity in the skeleton.

---

## Core Modules

The docs consistently imply these module boundaries:

- `src/core`
  - shared abstractions, events, types, schemas, exceptions
- `src/storage`
  - session store, state store, workspace access, later memory/persistence backends
- `src/providers`
  - LLM provider interface implementations and test fakes
- `src/tools`
  - tool base contract, registry, built-in tools
- `src/channels`
  - channel adapters, initially CLI only
- `src/runtime`
  - orchestration loop, policy checks, routing helpers, context handling
- `src/cli`
  - developer-facing and MVP-facing executable entrypoint
- `src/server`
  - reserved application surface for later HTTP/WebSocket support
- `services/*`
  - later extraction targets only, not an MVP requirement

---

## Key Interfaces To Preserve

The most important contracts repeated across docs are:

- session/state store
- message bus / routing
- tool interface and tool registry
- provider interface
- runtime/orchestration loop
- channel adapter
- execution context / policy engine
- config schema
- event types / event bus

These interfaces should live in `src/core` and be treated as public contracts for all parallel workstreams.

---

## Technical Assumptions

### Stable assumptions from docs

- Language: Python 3.11+
- Runtime: asyncio
- Data modeling: Pydantic-style schemas
- Architecture: modular monorepo
- Storage strategy: file-based first
- State model: session-centric
- Interaction model: CLI-first, channel-extensible
- Safety stance: explicit policy boundary, path restriction, command restrictions, auditable tool calls

### Tooling assumption conflict

There is one material document conflict worth recording:

- `docs/implementation/*` strongly assumes **Poetry workspace**
- current environment already has **`uv` installed** and does **not** have Poetry installed

### Recommended handling

To avoid blocking the bootstrap on package-manager mechanics, the repository should:

- preserve the **Python monorepo structure** mandated by the docs,
- use a **standards-based root `pyproject.toml`**,
- use **`uv` for developer commands and CI bootstrap** in the initial skeleton,
- document this as a tooling deviation, not a runtime architecture deviation.

This does **not** change the system architecture. It only changes the bootstrap tooling choice.

---

## Architectural Risks

High-priority risks distilled from the docs:

- Tool execution safety:
  - shell execution,
  - path traversal,
  - unbounded file access,
  - future web fetch SSRF
- Hidden coupling in runtime:
  - runtime can easily absorb storage/tools/provider/channel concerns if contracts are loose
- Interface churn:
  - parallel development will conflict immediately if `core` contracts are not frozen first
- Premature complexity:
  - subagents, memory consolidation, cron, multi-channel, and server concerns can destabilize MVP
- Observability debt:
  - logs and event records must be reserved early even if full metrics/tracing wait
- Session concurrency semantics:
  - docs discuss global-lock and session-lock tradeoffs; MVP should pick one and document it clearly

---

## Current Repository Gaps

The repository is currently missing:

- root `pyproject.toml`
- dependency/bootstrap workflow
- package directories
- source files
- tests
- scripts
- CI
- README / CONTRIBUTING / workflow docs
- module ownership guidance
- interface freeze document
- agent task prompts for parallel Codex threads

---

## Recommended Execution Strategy

1. Freeze contracts before broad implementation.
2. Build one runnable vertical slice:
   - CLI
   - fake provider
   - minimal runtime
   - session persistence
   - one safe built-in tool
3. Stub the rest behind interfaces.
4. Use `docs/execution/*` as the controlling artifact set for all parallel Codex work.
5. Keep `src/core` changes tightly controlled.

---

## Decisions For This Bootstrap Pass

- Treat the existing design docs as the approved architecture baseline.
- Preserve Python module boundaries while simplifying into one root `src/` tree.
- Use contract-first code placement in `src/core`.
- Reserve `src/server` and `services/*` with skeletal placeholders, not feature work.
- Build a minimal CLI-driven closure first.
- Prefer fake/stub provider and simple runtime behavior now; defer real provider breadth.

---

## Open Conflicts / Follow-ups

- Tooling:
  - Poetry workspace in docs vs `uv` in actual environment
- Scope:
  - docs place server later, but repository skeleton should still reserve it now
- Security:
  - docs call out strict safety needs, but MVP still needs a pragmatic starter policy model
- Concurrency:
  - documents leave room for global lock vs session lock; this must be frozen in the runtime contract before parallel implementation of richer routing
