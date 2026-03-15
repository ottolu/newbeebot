# Dev Branch Naming

Use small, module-scoped development branches.

## Format

- `dev/<area>-<task>`

## Examples

- `dev/runtime-policy`
- `dev/tools-safe-builtins`
- `dev/observability-metrics`

## Rules

- keep one primary concern per branch
- prefer module-local scope over cross-cutting scope
- if a change must touch shared contracts, call that out in the branch description and in
  `docs/execution/`
