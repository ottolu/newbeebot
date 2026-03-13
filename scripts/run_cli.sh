#!/usr/bin/env bash
set -euo pipefail

export PYTHONPATH="src"
uv run python -m cli.main demo --message "hello from bootstrap"
