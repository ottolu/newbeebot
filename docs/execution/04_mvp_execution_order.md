# MVP Execution Order

## Smallest Runnable Closure

The first runnable closure is:

- a CLI entrypoint,
- a config loader,
- a session store,
- a fake provider,
- a tool registry with one safe tool,
- a runtime loop that can:
  - accept a user message,
  - persist it,
  - optionally execute a tool call,
  - persist the assistant response,
  - show the response in the terminal.

This is the minimum loop that proves the repository has moved from design-only to executable architecture.

---

## Demo Path

The first demo path should be:

1. bootstrap dependencies,
2. run a one-shot CLI prompt,
3. run an interactive CLI chat,
4. list saved sessions,
5. show session history.

Optional second demo:

- issue a message that triggers the fake provider to request a safe tool,
- verify tool execution appears in session history.

---

## What Must Be Real In MVP-0

- config schema and loading
- core contracts
- CLI entrypoint
- runtime loop
- session persistence
- session history inspection
- tool registry
- at least one safe built-in tool

---

## What Can Be Fake / Stubbed First

- real external LLM provider calls
- advanced tool set
- non-CLI channels
- memory consolidation
- subagents
- server business endpoints
- service extraction

---

## Ordered Implementation Plan

## Step 1. Freeze contracts in `src/core`

Why first:

- every later task depends on these modules.

## Step 2. Bootstrap repo tooling

Deliverables:

- root `pyproject.toml`
- scripts
- CI
- developer docs

Why second:

- every later thread needs a consistent bootstrap and verification path.

## Step 3. Create failing smoke tests for the vertical slice

Tests should prove:

- runtime can process a message,
- storage persists it,
- CLI can drive the runtime,
- fake provider can complete a turn.

## Step 4. Implement provider fake and session store

Why here:

- they are low-coupling dependencies for runtime work,
- they make runtime smoke tests meaningful.

## Step 5. Implement tool registry and one safe tool

Why here:

- enables the first tool-call loop without prematurely opening shell/web risk.

## Step 6. Implement runtime loop

Why here:

- now all contract dependencies exist and can be wired together.

## Step 7. Implement CLI MVP

Why here:

- CLI becomes the first executable surface and demo path.

## Step 8. Reserve server/service skeletons

Why here:

- keeps future expansion points visible,
- avoids polluting MVP with server complexity.

---

## First-Batch Must-Implement Modules

- `src/core`
- `src/storage`
- `src/providers`
- `src/tools`
- `src/runtime`
- `src/cli`

Server and services are placeholders only in this pass.

---

## What To Delay On Purpose

- advanced memory
- cron / heartbeat
- non-CLI channels
- real remote providers beyond one adapter seam
- rich policy matrix
- artifact-first workflows
- server APIs beyond a health skeleton

---

## Acceptance For “MVP Skeleton Ready”

The bootstrap pass is sufficient when:

- `docs/execution/*` exists and is internally consistent,
- root developer workflow exists,
- package boundaries exist,
- contracts exist,
- one smoke-tested runtime path exists,
- CLI can execute that path,
- future modules are reserved without premature implementation.
