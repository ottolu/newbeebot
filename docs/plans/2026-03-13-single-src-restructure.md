# Single Root Src Restructure Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Collapse the current multi-root `apps/*/src` and `packages/*/src` layout into a single repository-level `src/` tree without changing runtime behavior.

**Architecture:** Keep the existing logical module split (`core`, `storage`, `providers`, `tools`, `runtime`, `cli`, `server`) but move those modules into one top-level `src/` directory. Update imports, tooling, scripts, tests, and execution docs to treat `src/` as the single main code root. Remove the old `apps/` and `packages/` trees from the active execution path.

**Tech Stack:** Python 3.11+, `uv`, `pytest`, `ruff`, `mypy`, setuptools `pyproject.toml`

---

### Task 1: Write the failing expectations for the new layout

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `WORKFLOW.md`
- Modify: `tests/contracts/test_config_contract.py`
- Modify: `tests/contracts/test_session_store_contract.py`
- Modify: `tests/smoke/test_cli_demo.py`
- Modify: `scripts/run_cli.sh`
- Modify: `pyproject.toml`

**Step 1: Write the failing test/config expectation**

- Change test imports and developer tooling references from old multi-root paths to `src/...`
- Change `pythonpath` / `mypy_path` to only include `src`
- Change CLI module invocation to `python -m cli.main`

**Step 2: Run test to verify it fails**

Run: `uv run pytest`
Expected: FAIL with import errors because `src/` has not been populated yet

**Step 3: Write minimal implementation**

- Create the repository-level `src/` directory
- Leave old code in place until the next task migrates it

**Step 4: Run test to verify expected failure remains import-related**

Run: `uv run pytest`
Expected: FAIL due to missing modules under `src`

### Task 2: Migrate source modules into root `src/`

**Files:**
- Create: `src/core/**`
- Create: `src/storage/**`
- Create: `src/providers/**`
- Create: `src/tools/**`
- Create: `src/runtime/**`
- Create: `src/cli/**`
- Create: `src/server/**`
- Remove from active path: `apps/cli/src/cli/**`
- Remove from active path: `apps/server/src/server/**`
- Remove from active path: `packages/core/src/core/**`
- Remove from active path: `packages/storage/src/storage/**`
- Remove from active path: `packages/providers/src/providers/**`
- Remove from active path: `packages/tools/src/tools/**`
- Remove from active path: `packages/runtime/src/runtime/**`

**Step 1: Move code**

- Move each active module directory into `src/`
- Preserve module names and file contents

**Step 2: Fix imports**

- Update all in-repo imports to point at the modules under `src/`
- Ensure no import still depends on `apps/*/src` or `packages/*/src`

**Step 3: Run focused tests**

Run: `uv run pytest tests/contracts/test_config_contract.py tests/contracts/test_session_store_contract.py tests/smoke/test_cli_demo.py -v`
Expected: PASS

### Task 3: Update documentation and execution references

**Files:**
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `CONTRIBUTING.md`
- Modify: `WORKFLOW.md`
- Modify: `docs/execution/01_parallel_task_graph.md`
- Modify: `docs/execution/02_module_ownership.md`
- Modify: `docs/execution/06_bootstrap_status.md`
- Modify: `docs/execution/07_task_board.md`

**Step 1: Replace old structure references**

- Update execution docs so the canonical layout is `src/*`
- Keep ownership and task boundaries, but point them at the new tree

**Step 2: Run grep validation**

Run: `rg -n "apps/.*/src|packages/.*/src|packages/core/src/core|apps/cli/src/cli|apps/server/src/server" docs README.md AGENTS.md CONTRIBUTING.md WORKFLOW.md scripts tests pyproject.toml`
Expected: no matches for active structure references

### Task 4: Verify and clean up

**Files:**
- Modify: `.gitignore` if needed
- Review: repository tree

**Step 1: Run full verification**

Run: `./scripts/check.sh`
Expected: PASS

Run: `./scripts/run_cli.sh`
Expected: PASS and print a `session_id=...` line plus assistant output

**Step 2: Review resulting structure**

Run: `find src -maxdepth 2 -type d | sort`
Expected:
- `src/core`
- `src/storage`
- `src/providers`
- `src/tools`
- `src/runtime`
- `src/cli`
- `src/server`

**Step 3: Commit**

```bash
git add src README.md AGENTS.md CONTRIBUTING.md WORKFLOW.md docs/execution docs/plans pyproject.toml scripts tests .gitignore
git commit -m "refactor: collapse code into root src tree"
```
