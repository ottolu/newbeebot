# CONTRIBUTING

## Workflow

1. Read the relevant design and execution documents.
2. Confirm the target module ownership in `docs/execution/02_module_ownership.md`.
3. Start a feature branch for normal development work and keep `main` for coordinated integration.
4. Add or update tests before implementation when changing behavior.
5. Keep changes inside the assigned module boundary whenever possible.
6. Run `./scripts/check.sh` before handoff.

## Pull request expectations

- state which execution task or prompt you implemented
- list the files and module boundaries touched
- call out any contract changes explicitly
- include verification commands and results

## Branch guidance

- preferred branch naming is `dev/<topic>`
- use small, module-local branches whenever possible
- direct pushes to `main` are reserved for explicit coordination or release decisions
- branch examples and rules live in `docs/templates/dev_branch_naming.md`

## Conflict handling

If the implementation requirement conflicts with repository documents:

1. record the conflict in `docs/execution/`
2. propose the smallest safe resolution
3. avoid silently rewriting shared architecture

## Troubleshooting

- start with `docs/execution/08_troubleshooting.md`
