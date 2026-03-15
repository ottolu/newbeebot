# newbeebot

`newbeebot` is a contract-first Python repository for building the MVP described in
`docs/system-design/`, `docs/blueprint/`, and `docs/implementation/`.

The current repository state is an implemented MVP and V1 baseline:

- execution planning lives in `docs/execution/`
- interfaces are defined before feature work
- the runnable closure includes fake and OpenAI-backed CLI flows
- module boundaries are reserved inside the root `src/` tree for parallel Codex work
- remaining work is enhancement backlog

## Repository shape

```text
src/
  channels/
  cli/
  core/
  observability/
  providers/
  runtime/
  server/
  storage/
  tools/
services/
  prompts/
  policies/
  observability/
tests/
```

## Local development

```bash
uv sync --extra dev
uv run ruff check .
uv run mypy src tests
uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=85
```

Run the CLI smoke flow:

```bash
./scripts/run_cli.sh
```

## MVP demo paths

Run the local fake-provider flow:

```bash
uv run python -m cli run --message "hello local"
```

Run the interactive local chat flow:

```bash
uv run python -m cli chat
```

Run a quick local diagnostics check:

```bash
uv run python -m cli doctor
```

Run against the OpenAI Responses API:

```toml
# newbeebot.toml
[runtime]
provider = "openai"

[provider]
model = "gpt-4.1-mini"
base_url = "https://api.openai.com/v1"
```

```bash
export NEWBEEBOT_PROVIDER_API_KEY="your-api-key"
uv run python -m cli run --config newbeebot.toml --message "hello from newbeebot"
```

Inspect saved sessions:

```bash
uv run python -m cli sessions list
uv run python -m cli sessions show <session_id>
```

## Working rules

- Treat `docs/system-design/`, `docs/blueprint/`, and `docs/implementation/` as source of truth.
- Treat `docs/execution/` as the current execution contract for parallel implementation.
- Freeze core contracts before expanding implementations across modules.
- Prefer adding new files over editing shared core files during parallel work.
- Default to branch-based development for all follow-on work; direct pushes to `main` should be
  treated as exceptional release/coordination actions.

## Troubleshooting

- runtime/operator checks: `docs/execution/08_troubleshooting.md`
- branch naming guide: `docs/templates/dev_branch_naming.md`
