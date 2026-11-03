#!/usr/bin/env bash
# Validate Agent Skills at repo root with pinned skills-ref.
# Thin launcher so this can later move into danielnachumdev/actions unchanged.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# Pin agentskills/skills-ref for reproducible CI (do not float on @main).
# SHA from https://github.com/agentskills/agentskills @ main when added.
SKILLS_REF_SHA="69ef37e9424c0a7ea9dd2293b559e43ec8176379"
SKILLS_REF_SPEC="git+https://github.com/agentskills/agentskills.git@${SKILLS_REF_SHA}#subdirectory=skills-ref"

if ! command -v uv >/dev/null 2>&1; then
  echo "uv is required (https://docs.astral.sh/uv/). Install it or use astral-sh/setup-uv in CI." >&2
  exit 1
fi

# Python >=3.11 required by skills-ref; pyyaml rebuilds frontmatter after
# stripping Cursor-only keys (see validate_skills.py).
exec uv run --python 3.13 --with "$SKILLS_REF_SPEC" --with "pyyaml>=6" \
  python "$ROOT/scripts/validate_skills.py" "$@"
