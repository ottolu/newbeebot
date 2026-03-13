# Module Ownership

## Ownership Model

This repository should be treated as a contract-first codebase with strict edit zones inside a
single root `src/` tree.

The goal is not bureaucracy. The goal is to make parallel Codex implementation safe.

---

## Directory Responsibilities

## `src/`

- Purpose:
  - all primary application and runtime code
  - explicit module-local ownership inside one repository root
- Allowed responsibilities:
  - `src/core`: contracts and canonical types
  - `src/storage`: persistence logic
  - `src/providers`: provider adapters
  - `src/tools`: tool registry and safe tools
  - `src/runtime`: orchestration
  - `src/cli`: CLI composition
  - `src/server`: server surface
- Forbidden responsibilities:
  - cross-module hidden coupling
  - mixing orchestration, storage, provider, and adapter logic in one module

## `services/`

- Purpose:
  - future process-extracted components only
  - long-running service boundaries such as orchestrator/router when extraction becomes necessary
- MVP rule:
  - reserve the directory now,
  - do not move runtime logic into `services/` during bootstrap

## `libs/`

- Purpose:
  - non-domain shared support code only
  - test utilities, dev tooling helpers, or thin reusable infrastructure shims
- MVP rule:
  - avoid putting business/domain contracts here
  - `libs/` is deliberately not the place for public runtime interfaces

---

## Public Base Layer

## `src/core/`

This is the shared public base layer.

It owns:

- abstractions/interfaces,
- shared events,
- shared schemas,
- shared models,
- shared exceptions,
- config contracts.

Changes here require higher scrutiny because they affect every parallel workstream.

### Edit rule

- Only the contract owner thread should modify `src/core/**` during a sprint unless an explicit
  interface-freeze update is approved in `docs/execution/03_interface_freeze_plan.md`.

---

## Module Ownership Table

| Directory | Owns | Must not own |
|---|---|---|
| `src/core/` | contracts, types, events, config schema, exceptions | runtime behavior, storage logic, app wiring |
| `src/storage/` | session/state persistence implementations, workspace access implementations | provider logic, channel logic, orchestration logic |
| `src/providers/` | provider adapters and fake providers | orchestration, session persistence |
| `src/tools/` | tool base implementation helpers, registry, built-in tools | runtime loop, session ownership |
| `src/channels/` | CLI and later external channel adapters | runtime orchestration internals, provider logic |
| `src/runtime/` | orchestration loop, policy hooks, routing handoff, context trimming | root config source of truth, channel SDK concerns |
| `src/cli/` | CLI commands and dependency composition | domain contracts, provider protocols |
| `src/server/` | HTTP/WebSocket app surface and health endpoints | core contracts, storage internals |
| `services/` | future extracted daemons | MVP logic during bootstrap |
| `libs/` | shared non-domain helper code | public runtime contracts |

---

## Shared Interface Placement

All shared contracts should live under:

- `src/core/abstractions/`
- `src/core/types.py`
- `src/core/events.py`
- `src/core/config.py`
- `src/core/exceptions.py`

Do **not** duplicate shared types in downstream modules.

## Source folder naming convention

- source package folders under `src/` should use short module names and should not carry a
  `newbeebot_` prefix
- preferred examples:
  - `core`
  - `storage`
  - `providers`
  - `tools`
  - `runtime`
  - `cli`
  - `server`
- keep this as the convention for all new structure changes

---

## Ownership Rules For Parallel Threads

## Safe to edit freely inside task scope

- files under the task's own `src/*` module directory
- that task's own tests
- its own README/TODO files

## Requires coordination

- `src/core/**`
- root `pyproject.toml`
- root workflow docs
- root CI files
- any file under `docs/execution/`

## Prefer adding over editing

Early-stage parallel work should:

- add new module files,
- add tests,
- add adapter implementations,
- avoid broad rewrites of shared files.

---

## Contract Change Policy

If a task discovers that a frozen contract is insufficient:

1. do not silently widen it in module code,
2. document the mismatch in `docs/execution/03_interface_freeze_plan.md`,
3. record impacted modules,
4. update ownership notes if needed,
5. then change the contract in a dedicated contract-change pass.

---

## Dependency Rules

- `src/core` depends on nothing in-repo.
- `src/storage`, `src/providers`, `src/tools`, `src/channels` may depend on `src/core`.
- `src/runtime` may depend on:
  - `src/core`
  - `src/storage`
  - `src/providers`
  - `src/tools`
- `src/cli` and `src/server` may depend on all required runtime modules.
- `services/*` should depend on contracts and service-safe modules only when introduced.

No runtime module may import from `src/cli` or `src/server`.

---

## Reserved Future Boundaries

These directories should remain intentionally light in the bootstrap:

- `src/server/`
- `services/orchestrator/`
- `services/router/`
- `libs/`

The point is to reserve clear landing zones without pulling future complexity into the MVP.
