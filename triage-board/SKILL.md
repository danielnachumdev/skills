---
name: triage-board
description: >-
  Run a batch local-web-UI decision board for keep/archive/delete/rename-style
  triage (primary use: GitHub repo cleanup and hygiene). Use when cleaning up a
  GitHub account or org, deciding which repos to keep/archive/delete, renaming
  repos for hygiene, running a repo triage campaign, or when the user mentions
  repo cleanup, archive-delete-rename, GitHub repo hygiene, triage board, or a
  local decision UI for batched approvals.
---

# Triage Board

Batch decision workflow via a **local web UI** — do **not** dump huge decision
tables in chat. The primary use is cleaning up GitHub repos under an owner
(`OWNER`); the same pattern (inventory → suggest → UI approve → execute) can
apply to other batch keep/archive/delete/rename campaigns.

**Working UI scaffold:** reuse or copy a local triage UI project that serves
`serve.py`, `index.html`, and `rename.html` (example checkout:
`/home/daniel/dev/projects/repo-triage/`). Details in [reference.md](reference.md).

## Roles

| Actor | Does |
|-------|------|
| Agent | Inventory, suggest targets/names, serve UI, parse JSON, archive, update READMEs, rename, extract code |
| User | Approves via web UI; **may delete repos themselves** when they prefer |

## Progress checklist

```
- [ ] Phase 1 — Inventory + suggestions
- [ ] Phase 2 — Decision UI (keep/archive/delete + README)
- [ ] Phase 2b — Execute archives / README updates (user deletes)
- [ ] Phase 3 — Rename triage UI + execute
- [ ] Phase 4 — Extract unique code before any delete
```

---

## Phase 1 — Inventory

1. List repos:
   ```bash
   gh repo list OWNER --limit 200 \
     --json name,url,description,isPrivate,isArchived,isFork,primaryLanguage,diskUsage,pushedAt,createdAt
   ```
2. Probe each repo lightly: README presence/size, root file count, fork/archived/private, description. Prefer `gh api` / sparse checks over full clones.
3. Assign **suggested** `target` and `readme` using heuristics below.
4. Write `repos.json` for the decision UI (schema in [reference.md](reference.md)). Pre-fill `target`/`readme` from suggestions; `decided: false`.

### Heuristics

| Target | When |
|--------|------|
| **delete** | Empty placeholders, unused forks, broken stubs, fully superseded duplicates |
| **archive** | Coursework, interview take-homes, finished one-offs, old utilities |
| **keep** | Active products, published libs, infra, personal apps still used |

- **Before delete:** check if the logic lives elsewhere (another owner/org or a successor codebase).
- README: `yes` if thin/missing and keeping or archiving; `no` if already fine; `NA` if delete.

Never paste the full proposed table into chat for approval. Point the user at the local UI.

---

## Phase 2 — Decision UI (keep / archive / delete)

1. Ensure a local triage UI scaffold exists (reuse or copy; see [reference.md](reference.md)).
2. Place `repos.json` next to `serve.py`.
3. Start server: `python3 serve.py` → `http://127.0.0.1:8765/`
4. User reviews keep/archive/delete + README yes/no/NA, then submits → `decisions.json` via `POST /api/submit`.
5. Parse `decisions.json` and execute:

| Decision | Agent action |
|----------|--------------|
| keep + readme yes | Update README (push) |
| archive | Archive via `gh`; if README yes, **unarchive → push README → re-archive** |
| delete | Prefer user deletes manually; if agent deletes, only after Phase 4 extract and explicit OK |

### Archive mutate rule

Archived repos must be **unarchived → mutate → re-archived** for any rename or README push. See [reference.md](reference.md).

---

## Phase 3 — Rename triage

Run after keep/archive decisions (or on the surviving set).

1. Suggest kebab-case clearer names from purpose; fix typos.
2. Company-qualified interview assignment names **only when company is proven** (mail/calendar evidence) — otherwise defer + brainstorm.
3. Write `renames.json` (all candidates). UI shows **only** rows where `suggested ≠ current`.
4. Open `http://127.0.0.1:8765/rename.html`.

### Rename UI requirements (do not regress)

- Show **only** rows where suggested ≠ current
- No “decided” checkbox — submit means decided
- Always-editable free-text target name
- Free-text **notes**
- Actions: **Rename | Keep current | Defer (brainstorm)**

5. User submits → `rename-decisions.json` via `POST /api/submit-renames`.
6. Handle actions:
   - **Rename** → `gh repo rename -R owner/old new --yes` (if archived: unarchive → rename → re-archive)
   - **Keep current** → no-op
   - **Defer** → brainstorm with user; for interview repos, use the mail-assistant prompt in [reference.md](reference.md) to find company owners before naming

---

## Phase 4 — Extract before delete

If a delete-candidate still has unique useful code:

1. Extract into a **staging folder** in the successor codebase.
2. Add a short README with provenance (source repo URL, date, what was copied).
3. Do **not** wire into production exports until adapted.
4. Only then allow delete (user or agent).

---

## Hard preferences

- Batched approval via local web UI — not chat walls of tables
- User may delete repos themselves; agent focuses on archive + README + rename + extract
- Never invent company names for interview repos without evidence
- Do not commit triage JSON or skill changes unless asked
