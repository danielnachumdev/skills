# skills

Personal [Cursor](https://cursor.com) / [Agent Skills](https://agentskills.io) library for [danielnachumdev](https://github.com/danielnachumdev).

Each skill is a directory at the repo root with a `SKILL.md` (YAML frontmatter + instructions). Install into `~/.cursor/skills/` so Cursor can load them across projects.

## Skills

| Skill | Purpose |
| ----- | ------- |
| [`async`](async/) | Offload the current task to a background Task subagent so the main chat stays free |
| [`triage-board`](triage-board/) | Batch many decisions via a local web UI (`scripts/` example board; `references/` write-up) |
| [`writing-python`](writing-python/) | Conventions for writing and refactoring Python (SRP, strategy/gateway layout, clean imports) |

## Install

Symlink or copy each skill folder into your personal skills directory (do **not** use `~/.cursor/skills-cursor/` — that is Cursor’s built-in skills tree):

```bash
mkdir -p ~/.cursor/skills
ln -sfn /path/to/skills/async ~/.cursor/skills/async
ln -sfn /path/to/skills/triage-board ~/.cursor/skills/triage-board
ln -sfn /path/to/skills/writing-python ~/.cursor/skills/writing-python
```

Or copy instead of symlink if you prefer a snapshot. Restart or refresh the agent session if a newly linked skill does not appear.

## CI

Thin [`.github/workflows/ci.yml`](.github/workflows/ci.yml):

1. **`CI / CI`** — `danielnachumdev/actions` hygiene (`allow-empty: true`; markdown-only repo)
2. **`Validate skills / Validate skills`** — reusable [`validate-skills.yml`](https://github.com/danielnachumdev/actions/blob/main/.github/workflows/validate-skills.yml) (skills-ref + Cursor frontmatter allowlist)

Dependabot auto-merge waits on both. Semver / CD are omitted (no versioned artifacts).

## Add a skill

1. Create `<name>/SKILL.md` at the repo root (`name` = directory name).
2. Required frontmatter: `name` (lowercase, hyphens OK, max 64) and `description` (max 1024; what + when).
3. Optional Agent Skills Spec fields: `license`, `compatibility`, `metadata`, `allowed-tools`.
4. Cursor-only extensions (kept in source; stripped only for skills-ref in CI): `disable-model-invocation`, `paths`, `icon`, `color`. Prefer `disable-model-invocation: true` when the skill should load only when named explicitly.
5. Validate locally from an [actions](https://github.com/danielnachumdev/actions) checkout: `./scripts/validate_skills.sh /path/to/skills`
6. Open a PR; both required checks should pass.

Maintainer / agent details: [`AGENTS.md`](AGENTS.md).
