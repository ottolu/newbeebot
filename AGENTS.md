# AGENTS

This repository is organized for parallel Codex execution.
The codebase is currently at MVP-complete baseline status; new work should be treated as
follow-on V1 or hardening work unless the execution docs say otherwise.

## Required reading before coding

1. `docs/system-design/`
2. `docs/blueprint/`
3. `docs/implementation/`
4. `docs/execution/`

## Coordination rules

- Do not change public contracts under `src/core/abstractions` or `src/core/types.py` without
  updating `docs/execution/03_interface_freeze_plan.md`.
- Do not mix orchestration, storage, adapters, and provider logic in the same module.
- Prefer adding new files inside your assigned module over editing shared files.
- If a task requires changing another module's contract, stop and document the conflict in
  `docs/execution/`.
- Start from a branch for normal development work; avoid direct `main` edits outside explicit
  coordination or release tasks.

## Ownership summary

- `src/core`: shared contracts and canonical types
- `src/storage`: persistence implementations only
- `src/providers`: LLM/provider adapters only
- `src/tools`: tool registration and safe tool implementations
- `src/runtime`: orchestration loop only
- `src/cli`: local developer entrypoint
- `src/server`: reserved API/server surface
- `services/*`: non-core support assets that must not introduce runtime coupling

## Default execution entrypoints

- one-shot CLI: `uv run python -m cli run --message "hello"`
- interactive CLI: `uv run python -m cli chat`
- diagnostics: `uv run python -m cli doctor`
- full verification: `./scripts/check.sh`
