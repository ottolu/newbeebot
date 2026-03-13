# Agent Task Prompts

These prompts are written for separate Codex threads. Each task assumes `docs/execution/*` and
`src/core` contracts are the governing baseline.

---

## Task 1: Session Storage

- Task name: Session Store Implementation
- Background: `newbeebot` already has source-of-truth docs and a frozen contract layer. The
  storage task must implement session persistence without introducing runtime or CLI logic.
- Goal: implement session persistence behind the existing `SessionStore` contract, including
  tests.
- Boundaries:
  - only own persistence logic and filesystem-safe behavior,
  - do not add orchestration, provider, or CLI behavior.
- Allowed directories:
  - `src/storage/`
  - storage-specific tests
- Forbidden directories:
  - `src/core/`
  - `src/runtime/`
  - `src/cli/`
  - `src/server/`
- Dependencies:
  - requires frozen contracts in `src/core`
- Completion standard:
  - session create/save/load/list metadata works,
  - tests cover persistence and isolation,
  - no circular import into runtime or apps.
- Self-test:
  - run storage unit tests,
  - run repository smoke tests if they include storage.

## Task 2: Provider Fake And Adapter Boundary

- Task name: Provider Layer
- Background: runtime and CLI need a deterministic provider before real network integrations.
- Goal: implement fake/mock provider behavior and prepare one provider adapter seam.
- Boundaries:
  - no CLI UX,
  - no session persistence,
  - no orchestration policy decisions.
- Allowed directories:
  - `src/providers/`
- Forbidden directories:
  - `src/core/`
  - `src/runtime/`
  - `src/cli/`
  - `src/server/`
- Dependencies:
  - frozen provider contracts
- Completion standard:
  - fake provider supports deterministic tests,
  - adapter boundary is importable,
  - provider tests pass.
- Self-test:
  - provider tests,
  - any runtime contract smoke tests that use fake provider.

## Task 3: Tool Registry And Safe Tool

- Task name: Tool Registry Bootstrap
- Background: runtime needs tool schemas and execution hooks, but early work must avoid unsafe
  shell/web breadth.
- Goal: implement tool registry and at least one safe built-in tool.
- Boundaries:
  - do not implement shell execution or network fetch unless explicitly stubbed,
  - do not edit runtime orchestration.
- Allowed directories:
  - `src/tools/`
- Forbidden directories:
  - `src/core/`
  - `src/runtime/`
  - `src/cli/`
  - `src/server/`
- Dependencies:
  - frozen tool contracts
- Completion standard:
  - registry registration/lookup/schema export works,
  - built-in tool executes successfully,
  - tool tests pass.
- Self-test:
  - tool unit tests,
  - runtime smoke test if available.

## Task 4: Runtime Loop

- Task name: Runtime Vertical Slice
- Background: storage, provider, and tools are available behind contracts.
- Goal: implement the minimal orchestration loop for one-turn and tool-call execution.
- Boundaries:
  - runtime owns orchestration only,
  - do not add CLI parsing or server endpoints,
  - do not mutate core contracts without documenting it.
- Allowed directories:
  - `src/runtime/`
  - runtime tests
- Forbidden directories:
  - `src/core/`
  - `src/cli/`
  - `src/server/`
- Dependencies:
  - storage, provider, and tool modules ready
- Completion standard:
  - one-turn flow works,
  - tool-call loop works,
  - session history integration works.
- Self-test:
  - runtime tests,
  - repository smoke test.

## Task 5: CLI MVP

- Task name: CLI Entry Surface
- Background: the runtime vertical slice exists and needs a developer-facing executable.
- Goal: implement one-shot and interactive CLI commands plus session inspection commands.
- Boundaries:
  - only compose existing modules,
  - do not move business logic into CLI handlers.
- Allowed directories:
  - `src/cli/`
  - CLI tests
  - README sections directly related to CLI usage
- Forbidden directories:
  - `src/core/`
  - `src/storage/`
  - `src/runtime/` except approved integration seam fixes
- Dependencies:
  - runtime ready
- Completion standard:
  - `run`, `chat`, `sessions list`, `sessions show` work,
  - CLI tests pass.
- Self-test:
  - CLI tests,
  - manual smoke path documented in README.

## Task 6: Config System

- Task name: Config Schema And Loader
- Background: multiple modules need one consistent source of runtime configuration.
- Goal: implement config schema, defaults, and environment overrides.
- Boundaries:
  - config owns validation and loading only,
  - no provider networking,
  - no CLI command behavior.
- Allowed directories:
  - `src/core/` only if task is explicitly assigned contract ownership
  - otherwise `src/runtime/` or dedicated config implementation location already defined by core
    contracts
- Forbidden directories:
  - `src/cli/`
  - `src/server/`
  - `src/storage/`
  - `src/providers/`
- Dependencies:
  - config contract freeze
- Completion standard:
  - valid config loads,
  - invalid config fails clearly,
  - environment overrides work.
- Self-test:
  - config tests,
  - smoke command using config path override.

## Task 7: Server Skeleton

- Task name: Server Placeholder
- Background: server is not MVP business scope, but the repo should reserve the surface cleanly.
- Goal: create a minimal importable server app with health endpoint or equivalent placeholder.
- Boundaries:
  - no rich API design,
  - no session business endpoints beyond skeleton.
- Allowed directories:
  - `src/server/`
- Forbidden directories:
  - `src/core/`
  - `src/runtime/`
  - `src/storage/`
- Dependencies:
  - none beyond frozen contracts
- Completion standard:
  - skeleton app imports,
  - health check works,
  - TODOs clearly mark deferred work.
- Self-test:
  - server smoke test or import test.

## Task 8: Developer Workflow Docs

- Task name: Contributor Workflow
- Background: multiple Codex threads will touch the repo and need consistent rules.
- Goal: tighten developer-facing docs without changing runtime code.
- Boundaries:
  - documentation and scripts only,
  - no domain code changes.
- Allowed directories:
  - `README.md`
  - `AGENTS.md`
  - `CONTRIBUTING.md`
  - `WORKFLOW.md`
  - `scripts/`
- Forbidden directories:
  - `src/*`
- Dependencies:
  - execution docs
- Completion standard:
  - developer onboarding path is clear,
  - scripts map to documented commands,
  - file ownership and workflow rules are reflected.
- Self-test:
  - run documented commands exactly as written.

## Task 9: CI And Quality Gates

- Task name: CI Bootstrap
- Background: parallel development is unsafe without a shared verification path.
- Goal: implement CI for lint, typecheck, and tests.
- Boundaries:
  - CI/workflow only,
  - do not redesign runtime logic.
- Allowed directories:
  - `.github/workflows/`
  - root tooling config
  - scripts
- Forbidden directories:
  - `src/core/`
  - feature modules unless fixing command wiring
- Dependencies:
  - root developer commands documented
- Completion standard:
  - CI runs lint, typecheck, and test commands,
  - repository bootstrap works in CI.
- Self-test:
  - run the same commands locally before finalizing.
