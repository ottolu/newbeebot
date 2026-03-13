# Newbeebot Execution Bootstrap Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Convert the design-only repository into an executable, contract-first monorepo skeleton with a runnable CLI vertical slice and parallel-safe module boundaries.

**Architecture:** Preserve the documented Python monorepo and layer boundaries, freeze contracts in `packages/core`, implement a tiny local runtime closure using a fake provider and safe tool registry, and reserve future server/service boundaries without premature feature work.

**Tech Stack:** Python 3.11+, asyncio, Pydantic, pytest, mypy, ruff, `uv` bootstrap on top of a standards-based `pyproject.toml`

---

### Task 1: Execution Documents

**Files:**
- Create: `docs/execution/00_repo_audit.md`
- Create: `docs/execution/01_parallel_task_graph.md`
- Create: `docs/execution/02_module_ownership.md`
- Create: `docs/execution/03_interface_freeze_plan.md`
- Create: `docs/execution/04_mvp_execution_order.md`
- Create: `docs/execution/05_agent_task_prompts.md`

**Step 1: Capture current repository/design constraints**

- Summarize architecture, MVP/V1/V2 scope, risks, and repo gaps from the source docs.

**Step 2: Define parallel-safe module boundaries**

- Freeze ownership rules and identify which modules can start immediately.

**Step 3: Save execution artifacts**

- Ensure all future implementation threads can treat these docs as governing references.

### Task 2: Root Tooling Bootstrap

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `.github/workflows/ci.yml`
- Create: `scripts/*.sh`
- Create: `README.md`
- Create: `AGENTS.md`
- Create: `CONTRIBUTING.md`
- Create: `WORKFLOW.md`

**Step 1: Write the minimal root tooling**

- Bootstrap lint/typecheck/test commands and CI.

**Step 2: Document developer workflow**

- Make the repo operable for multiple Codex threads.

### Task 3: Contract-First Vertical Slice

**Files:**
- Create: `packages/core/**`
- Create: `packages/storage/**`
- Create: `packages/providers/**`
- Create: `packages/tools/**`
- Create: `packages/runtime/**`
- Create: `apps/cli/**`
- Create: `apps/server/**`

**Step 1: Write failing smoke tests**

- Prove the intended CLI/runtime/session flow does not exist yet.

**Step 2: Implement the minimal code to pass**

- Add frozen contracts, a fake provider, a safe tool, a runtime loop, and a CLI surface.

**Step 3: Keep future boundaries skeletal**

- Server and services stay placeholder-only in this pass.

### Task 4: Verification

**Files:**
- Verify all created files

**Step 1: Run lint, typecheck, and tests**

- Use fresh commands only.

**Step 2: Record next parallel threads**

- Point future Codex work at the new execution docs and package boundaries.
