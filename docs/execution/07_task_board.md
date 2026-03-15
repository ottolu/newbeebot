# Task Board

Updated: 2026-03-15

## Status Legend

- `[DONE]`: finished and verified
- `[SCAFFOLDED]`: skeleton exists, but the module is not MVP-complete
- `[READY]`: no work started yet, but interfaces and boundaries are ready for a parallel thread
- `[BLOCKED]`: should not start until an upstream dependency changes

## Completion Snapshot

- Execution bootstrap: `[DONE]`
- MVP engineering baseline: `[DONE]`
- Real MVP feature closure: `[DONE]`
- V1 expansion work: `[DONE]`

## 0. Program Coordination

Status: `[DONE]`

- [x] Audit source-of-truth docs and capture repository gaps
- [x] Define parallel task graph
- [x] Define module ownership and edit boundaries
- [x] Define interface freeze plan
- [x] Define MVP execution order
- [x] Generate subtask prompts for parallel Codex threads
- [x] Record bootstrap landing status

## 1. Repo Tooling And Workflow

Status: `[DONE]`

- [x] Create root `pyproject.toml`
- [x] Add `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `WORKFLOW.md`
- [x] Add `scripts/check.sh` and `scripts/run_cli.sh`
- [x] Add CI workflow for lint, typecheck, and tests
- [x] Establish root `src/` module skeleton
- [x] Add branch/PR templates if team workflow needs them
- [x] Add coverage reporting and failure thresholds

## 2. Core Contracts And Config

Status: `[DONE]`

- [x] Create shared config model
- [x] Create shared event/session types
- [x] Create provider/session/tool abstractions
- [x] Freeze initial contract plan in execution docs
- [x] Expand config validation and environment override support
- [x] Add contract tests for runtime, tools, and provider seams beyond current smoke level
- [x] Add explicit event bus/event envelope types if runtime requires them

## 3. Storage

Status: `[DONE]`

- [x] Create file-backed session store
- [x] Add storage round-trip contract test
- [x] Add session listing and metadata queries
- [x] Add durable state layout/versioning strategy
- [x] Add concurrent write safety rules
- [x] Add recovery behavior for corrupted session files

## 4. Providers

Status: `[DONE]`

- [x] Create deterministic fake provider
- [x] Define and implement first real provider adapter
- [x] Add provider config binding
- [x] Add provider failure/retry behavior
- [x] Add provider-specific tests beyond fake-path smoke coverage

## 5. Tools

Status: `[DONE]`

- [x] Create tool registry placeholder
- [x] Create one safe built-in tool placeholder
- [x] Define tool schema export and discovery behavior
- [x] Define tool execution result/error model
- [x] Add more safe built-in tools needed by MVP
- [x] Add tool-level tests

## 6. Runtime And Orchestration

Status: `[DONE]`

- [x] Create minimal one-turn runtime loop
- [x] Persist user and assistant events in the MVP smoke path
- [x] Add multi-turn session continuation
- [x] Add tool-call loop
- [x] Add routing/orchestration boundary beyond the current direct flow
- [x] Add policy hooks, limits, and failure handling
- [x] Add richer runtime tests

## 7. CLI

Status: `[DONE]`

- [x] Create `demo` command
- [x] Prove CLI smoke flow works end to end
- [x] Add `run` command for standard one-shot execution
- [x] Add session inspection commands
- [x] Add interactive `chat` flow
- [x] Add better config/path UX and help text

## 8. Server

Status: `[DONE]`

- [x] Reserve server package and importable placeholder
- [x] Add health endpoint or equivalent skeleton route
- [x] Add server startup path
- [x] Add server smoke/import tests

## 9. Policy / Auth / Permissions

Status: `[DONE]`

- [x] Confirm policy boundary from source-of-truth docs against frozen runtime seams
- [x] Define permission model for tools/channels/providers
- [x] Implement initial policy enforcement hook
- [x] Add tests for allowed/denied execution paths

## 10. Channels

Status: `[DONE]`

- [x] Create `src/channels/` boundary
- [x] Extract CLI-facing channel adapter seam from direct app composition
- [x] Define channel message normalization contract
- [x] Add at least one non-CLI adapter only if still inside MVP scope

## 11. Observability And Operability

Status: `[DONE]`

- [x] Add structured logging conventions
- [x] Define basic metrics/tracing seam
- [x] Add startup/runtime diagnostics
- [x] Add operator-facing troubleshooting notes

## 12. MVP Exit Criteria

Status: `[DONE]`

- [x] User can run one-shot CLI flow against a real provider
- [x] Session history persists and can be inspected
- [x] At least one safe tool can be invoked through runtime
- [x] Config can select provider/storage behavior cleanly
- [x] Main smoke path is covered by repeatable tests
- [x] README documents the MVP demo path end to end

## Post-Plan Backlog

- richer auth and external-channel policy models
- deeper tracing/metrics exporters
- broader built-in tool catalog
- server/API expansion beyond the current placeholder
