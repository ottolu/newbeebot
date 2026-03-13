# Parallel Task Graph

## Principles

- Split by **module boundary**, not by feature narrative.
- Freeze `src/core` contracts first.
- Prefer tasks that create new files over tasks that edit shared files.
- Avoid simultaneous edits to:
  - `src/core/**`
  - root `pyproject.toml`
  - root workflow docs

---

## Task Graph

## T0. Contract Freeze Baseline

- Goal: finalize core contracts and public type locations.
- Dependencies: none
- Input: `docs/system-design/*`, `docs/implementation/03_interfaces_and_contracts.md`
- Output:
  - `src/core/**`
  - contract tests for public interfaces
- Involved directories:
  - `src/core/`
  - `docs/execution/`
- Must not modify:
  - `src/storage/`
  - `src/providers/`
  - `src/tools/`
  - `src/runtime/`
  - `src/cli/`
  - `src/server/`
- Acceptance:
  - public interface modules exist,
  - all downstream modules can import contracts without circular imports,
  - contract smoke tests pass.
- Parallel status: must happen first

## T1. Developer Tooling And CI

- Goal: bootstrap the root developer workflow.
- Dependencies: none
- Input: repo audit and execution docs
- Output:
  - root `pyproject.toml`
  - `.github/workflows/ci.yml`
  - scripts and check commands
- Involved directories:
  - repository root
  - `.github/`
  - `scripts/`
- Must not modify:
  - `src/core/**` contracts
- Acceptance:
  - `uv` bootstrap works,
  - lint/typecheck/test commands are documented and runnable.
- Parallel status: can start immediately in parallel with T0, but must avoid root-file collisions

## T2. Session And Persistence Layer

- Goal: implement session metadata/history persistence against frozen contracts.
- Dependencies: T0
- Input:
  - session abstractions
  - config path conventions
- Output:
  - `src/storage/**`
  - storage tests
- Involved directories:
  - `src/storage/`
- Must not modify:
  - `src/providers/`
  - `src/tools/`
  - `src/cli/`
  - `src/server/`
- Acceptance:
  - session create/save/load/list works,
  - persistence tests pass,
  - no runtime logic leaks into storage.
- Parallel status: immediate after T0

## T3. Provider Layer

- Goal: implement fake/mock provider first, then real provider adapters behind the same contract.
- Dependencies: T0
- Input:
  - provider abstractions
  - execution response models
- Output:
  - `src/providers/**`
  - provider tests
- Involved directories:
  - `src/providers/`
- Must not modify:
  - `src/storage/`
  - `src/tools/`
  - `src/cli/`
  - `src/server/`
- Acceptance:
  - fake provider supports runtime contract tests,
  - provider module does not own orchestration or session logic.
- Parallel status: immediate after T0

## T4. Tool Registry And Safe Built-ins

- Goal: implement tool registry and the smallest safe built-in tool set.
- Dependencies: T0
- Input:
  - tool contracts
  - policy boundary assumptions
- Output:
  - `src/tools/**`
  - tool tests
- Involved directories:
  - `src/tools/`
- Must not modify:
  - `src/storage/`
  - `src/providers/`
  - `src/cli/`
  - `src/server/`
- Acceptance:
  - registry registration/lookup/schema export works,
  - at least one safe built-in tool is executable,
  - destructive shell/web behavior remains stubbed or guarded.
- Parallel status: immediate after T0

## T5. Runtime Loop

- Goal: implement the minimal orchestration loop using frozen contracts and test doubles.
- Dependencies: T2, T3, T4
- Input:
  - session store,
  - provider,
  - tool registry,
  - policy interfaces
- Output:
  - `src/runtime/**`
  - runtime tests
- Involved directories:
  - `src/runtime/`
- Must not modify:
  - root tooling files
  - `src/cli/`
  - `src/server/`
- Acceptance:
  - one-turn and tool-call loop works,
  - session history persists,
  - runtime owns orchestration only.
- Parallel status: after T2/T3/T4 contract readiness

## T6. CLI Application

- Goal: ship the MVP entrypoint and local demo surface.
- Dependencies: T5
- Input:
  - runtime facade,
  - config loader,
  - safe tools,
  - fake or real provider wiring
- Output:
  - `src/cli/**`
  - CLI tests
- Involved directories:
  - `src/cli/`
- Must not modify:
  - `src/core/`
  - `src/storage/`
  - `src/runtime/` except explicitly approved integration seams
- Acceptance:
  - `run`, `chat`, `sessions list`, `sessions show` work,
  - README demo path is valid.
- Parallel status: after T5

## T7. Server Skeleton

- Goal: reserve the future API surface without implementing V1 server scope.
- Dependencies: T0
- Input: app boundary docs
- Output:
  - `src/server/**`
  - health endpoint or placeholder app
- Involved directories:
  - `src/server/`
- Must not modify:
  - runtime orchestration internals
  - provider implementations
- Acceptance:
  - skeleton imports cleanly,
  - clear TODOs mark deferred V1 work.
- Parallel status: after T0, low coupling

## T8. Routing/Event Bus Package

- Goal: implement message bus and event bus behind frozen contracts.
- Dependencies: T0
- Input:
  - event models
  - routing interfaces
- Output:
  - runtime-local or future extracted routing modules
  - routing tests
- Involved directories:
  - `src/runtime/` or future `services/router/`
- Must not modify:
  - CLI UX files
  - storage implementation files
- Acceptance:
  - in-memory queue behavior validated,
  - session-safe routing semantics documented.
- Parallel status: after interface freeze; should wait until T5 integration points are stable

## T9. Channels Expansion

- Goal: implement non-CLI channel adapters.
- Dependencies: T0, T5
- Input:
  - channel contract
  - routing boundary
  - policy/auth boundary
- Output:
  - `src/channels/**`
- Involved directories:
  - `src/channels/`
- Must not modify:
  - `src/core/`
  - `src/runtime/` orchestration internals
- Acceptance:
  - adapter lifecycle methods implemented,
  - contract tests pass with fake routing endpoints.
- Parallel status: should wait until channel interface and runtime handoff are frozen

---

## Immediate Parallel Work

These can begin as soon as T0 produces frozen contracts:

- T2 Session And Persistence Layer
- T3 Provider Layer
- T4 Tool Registry And Safe Built-ins
- T7 Server Skeleton

T1 can run in parallel from the start, but only one thread should own root tooling files.

---

## Tasks That Must Wait For Interface Freeze

- T5 Runtime Loop
- T8 Routing/Event Bus Package
- T9 Channels Expansion
- any future service extraction from `src/` to `services/`

---

## Low-Conflict File Ownership Guidance

- One owner only for root files:
  - `pyproject.toml`
  - `.github/workflows/ci.yml`
  - `README.md`
- One owner only for public contracts:
  - `src/core/**`
- All other tasks should prefer new files inside their own module.
