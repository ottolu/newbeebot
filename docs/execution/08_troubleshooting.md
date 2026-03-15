# Troubleshooting

Updated: 2026-03-15

## First checks

Run the standard repository verification:

```bash
./scripts/check.sh
```

Run runtime diagnostics:

```bash
uv run python -m cli doctor
```

## Common issues

### OpenAI provider requests fail

- confirm `NEWBEEBOT_PROVIDER_API_KEY` is set
- confirm `provider = "openai"` in the selected TOML config
- confirm `base_url` points at a valid Responses API endpoint

### Session state looks wrong

- inspect the saved sessions with `uv run python -m cli sessions list`
- inspect one session with `uv run python -m cli sessions show <session_id>`
- remove corrupted local state under `.newbeebot/state/` only if you intend to reset local history

### Tool execution is blocked

- run `uv run python -m cli doctor` and inspect `allowed_tools`
- inspect the `[policy]` section in your config file
- check whether `max_tool_input_chars` is too low for the requested tool input

### A change passes locally but should not be merged

- confirm branch-local scope against `docs/execution/02_module_ownership.md`
- confirm any contract changes are reflected in `docs/execution/03_interface_freeze_plan.md`
- use the pull request template and include exact verification output
