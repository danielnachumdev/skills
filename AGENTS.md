# AGENTS.md — danielnachumdev/skills

Maintainer / coding-agent guide for **this** repo. Consumer overview: [`README.md`](README.md).

---

## Orientation

| Item | Detail |
| ---- | ------ |
| Role | Personal Cursor / Agent Skills library (markdown skills at repo root) |
| Skills today | `async/`, `writing-python/` — each is `<dir>/SKILL.md` |
| Toolchain | `uv` + pinned [skills-ref](https://github.com/agentskills/agentskills/tree/main/skills-ref) (see `scripts/validate_skills.sh`) |
| CI | Thin `.github/workflows/ci.yml` → actions hygiene + local validate job |
| Semver / CD | Omitted — no published artifacts |
| Dogfood | Validate script lives here first; later extract into `danielnachumdev/actions` |
| Owners | `.github/CODEOWNERS` → `@danielnachumdev` |

```text
.
├── .github/
│   ├── CODEOWNERS
│   ├── dependabot.yml          # github-actions weekly
│   └── workflows/
│       └── ci.yml              # thin: CI + Validate skills + Dependabot auto-merge
├── async/SKILL.md
├── writing-python/SKILL.md
├── scripts/
│   ├── validate_skills.sh      # uv launcher; pins agentskills SHA
│   └── validate_skills.py      # discover skills; strip Cursor extensions; skills-ref
├── README.md
└── AGENTS.md
```

Do **not** nest skills under a `skills/` subdirectory — discovery looks at **repo-root** directories that contain `SKILL.md` (skips `.git`, `.github`, `scripts`, venvs, etc.).

---

## Validate locally

Requires [uv](https://docs.astral.sh/uv/) and network once to fetch the pinned skills-ref.

```bash
./scripts/validate_skills.sh
```

Exit non-zero if any skill fails. In GitHub Actions the same command runs under job **`Validate skills`**; logs and `$GITHUB_STEP_SUMMARY` list per-skill `PASS` / `FAIL`.

Pin: `SKILLS_REF_SHA` in `scripts/validate_skills.sh` (do not float on `@main`). Bump deliberately when upgrading skills-ref.

---

## CI check names

Prefer required status checks:

| Check | Source |
| ----- | ------ |
| **`CI / CI`** | Reusable `danielnachumdev/actions` (`allow-empty: true`) |
| **`Validate skills`** | Job `validate-skills` (`name: Validate skills`) in this repo’s `ci.yml` |

Dependabot auto-merge `needs: [ci, validate-skills]`.

---

## Frontmatter: Spec vs Cursor

**Agent Skills Spec** (what skills-ref enforces): required `name`, `description`; optional `license`, `compatibility`, `metadata`, `allowed-tools`. Unknown keys fail validation.

**Cursor extensions** (top-level in `SKILL.md`, not in the Spec allowlist):

| Field | Notes |
| ----- | ----- |
| `disable-model-invocation` | Cursor-documented; default `true` in create-skill guidance so the skill loads only when named. Keep top-level — do not bury under `metadata:` if Cursor expects the top-level key. |
| `paths`, `icon`, `color` | Also allowlisted in the validator wrapper for the same reason |

`scripts/validate_skills.py` strips **only** that Cursor allowlist into a temp copy before calling skills-ref. Source files keep the Cursor fields. Do not widen the allowlist casually — real Spec violations must still fail CI.

`async` uses `disable-model-invocation: true`. `writing-python` omits it so the agent can auto-apply from ambient Python work.

---

## Adding or changing a skill

1. Add or edit `<name>/SKILL.md` at repo root (`name` must match the directory).
2. Write a third-person `description` with what + when (trigger terms).
3. Run `./scripts/validate_skills.sh` until green.
4. Branch off `main`; PR into `main`. Both CI checks above should pass.
5. Docs-only / CI-only changes: still keep validate green; no semver labels (none configured).

When changing discovery rules, the Cursor allowlist, or the skills-ref pin, update this file and the README “Add a skill” / CI sections together.

---

## Extraction note (later)

Portable unit for `danielnachumdev/actions`: `scripts/validate_skills.{sh,py}` + the `validate-skills` job shape. Keep the dogfood path in this repo until the reusable workflow exists; then thin this `ci.yml` to call the hub.
