# AGENTS.md — danielnachumdev/skills

Maintainer / coding-agent guide for **this** repo. Consumer overview: [`README.md`](README.md).

---

## Orientation

| Item | Detail |
| ---- | ------ |
| Role | Personal Cursor / Agent Skills library (markdown skills at repo root) |
| Skills today | `async/`, `triage-board/`, `writing-python/` — each is `<dir>/SKILL.md` |
| Toolchain | Validator lives in [`danielnachumdev/actions`](https://github.com/danielnachumdev/actions) (`scripts/validate_skills.*` + `validate-skills.yml`) |
| CI | Thin `.github/workflows/ci.yml` → actions hygiene + reusable validate-skills |
| Permissions | Thin CI needs `id-token: write` (umbrella nests Terraform; GitHub requires OIDC allow even when that lane is skipped) |
| Semver / CD | Omitted — no published artifacts |
| Owners | `.github/CODEOWNERS` → `@danielnachumdev` |

```text
.
├── .github/
│   ├── CODEOWNERS
│   ├── dependabot.yml          # github-actions weekly
│   └── workflows/
│       └── ci.yml              # thin: CI + Validate skills + Dependabot auto-merge
├── async/SKILL.md
├── triage-board/
│   ├── SKILL.md
│   ├── scripts/            # example board: serve.py + index.html
│   └── references/         # write-up + fabricated examples/ (for the AI)
├── writing-python/SKILL.md
├── README.md
└── AGENTS.md
```

Do **not** nest skills under a `skills/` subdirectory — discovery looks at **repo-root** directories that contain `SKILL.md` (skips `.git`, `.github`, `scripts`, venvs, etc. in the hub validator).

---

## Validate locally

Clone or use a checkout of [`danielnachumdev/actions`](https://github.com/danielnachumdev/actions). Requires [uv](https://docs.astral.sh/uv/) and network once to fetch the pinned skills-ref.

```bash
/path/to/actions/scripts/validate_skills.sh /path/to/skills
```

Exit non-zero if any skill fails. CI runs the same script via the reusable workflow; logs and `$GITHUB_STEP_SUMMARY` list per-skill `PASS` / `FAIL`.

The skills-ref pin lives in the actions hub (`SKILLS_REF_SHA` in `scripts/validate_skills.sh`) — bump there, not in this repo.

---

## CI check names

Prefer required status checks:

| Check | Source |
| ----- | ------ |
| **`CI / CI`** | Reusable `danielnachumdev/actions` (`allow-empty: true`) |
| **`Validate skills / Validate skills`** | `validate-skills.yml` via job `name: Validate skills` |

Dependabot auto-merge `needs: [ci, validate-skills]`.

Pin `validate-skills.yml@latest` (floating tag moved by actions CD).

---

## Frontmatter: Spec vs Cursor

**Agent Skills Spec** (what skills-ref enforces): required `name`, `description`; optional `license`, `compatibility`, `metadata`, `allowed-tools`. Unknown keys fail validation.

**Cursor extensions** (top-level in `SKILL.md`, not in the Spec allowlist):

| Field | Notes |
| ----- | ----- |
| `disable-model-invocation` | Cursor-documented; keep top-level. |
| `paths`, `icon`, `color` | Also allowlisted in the hub validator for the same reason |

The hub strips **only** that Cursor allowlist into a temp copy before calling skills-ref. Source files keep the Cursor fields.

`async` uses `disable-model-invocation: true`. `writing-python` omits it so the agent can auto-apply from ambient Python work.

---

## Adding or changing a skill

1. Add or edit `<name>/SKILL.md` at repo root (`name` must match the directory).
2. Write a third-person `description` with what + when (trigger terms).
3. Run the hub `validate_skills.sh` against this repo until green.
4. Branch off `main`; PR into `main`. Both CI checks above should pass.
5. Docs-only / CI-only changes: still keep validate green; no semver labels (none configured).

Validator / allowlist / skills-ref pin changes belong in `danielnachumdev/actions`, not here.
