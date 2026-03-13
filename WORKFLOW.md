# WORKFLOW

## Execution sequence

1. Freeze contracts in `src/core`
2. Land module-local implementations behind those contracts
3. Keep cross-module changes small and reviewable
4. Verify with lint, typecheck, and tests
5. Merge through a development branch unless a direct `main` integration is explicitly approved

## Parallel development guidance

- Start with tasks marked immediately parallel in `docs/execution/01_parallel_task_graph.md`.
- Reserve shared files for the coordination thread when possible.
- Use `docs/execution/05_agent_task_prompts.md` as the default handoff input for new Codex threads.
- Prefer `dev/<topic>` branches for parallel implementation threads.
- Keep `main` as the integration branch, not the default coding surface.

## Minimum verification

```bash
./scripts/check.sh
```
