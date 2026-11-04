---
name: triage-board
description: >-
  Batch many user decisions through a local web UI instead of chat tables.
  Use when the user must choose among a large set of items on any topic
  (keep/drop/rename/defer/classify/etc.), asks for a triage board or decision
  board, or needs local batched approvals — including but not limited to
  GitHub repo hygiene.
---

# Triage Board

When the user must **decide about a lot of things** — **regardless of topic** —
do **not** dump huge decision tables in chat. Run a local decision board:

**inventory → suggest → local web UI → parse JSON → execute.**

GitHub keep/archive/delete/rename is one worked example below, not the skill’s
purpose.

## When to use

- Dozens (or more) of items need an explicit choice
- Chat walls of tables would be unusable
- Any domain: repos, files, renames, inbox items, config flags, migrations,
  naming, classify/keep/drop campaigns, etc.

## Roles

| Actor | Does |
|-------|------|
| Agent | Inventory, suggest defaults, adapt/serve UI, parse submitted JSON, execute approved actions |
| User | Reviews and submits decisions in the local UI |

## Core loop

1. **Clarify the schema** with the user if needed: what is a row, which
   fields/options (e.g. keep \| drop \| defer, free-text rename, notes).
2. **Inventory** the items; probe lightly; assign **suggested** values.
3. **Write JSON** next to the UI scaffold; start the local server; point the
   user at the board — never paste the full table into chat for approval.
4. **Parse** the submitted decisions JSON (`jq`).
5. **Execute** only what the UI approved. Destructive actions need clear UI
   intent (and often an explicit extra OK from the user).

### Progress checklist (generic)

```
- [ ] Schema + inventory + suggestions
- [ ] Decision UI live; user submits
- [ ] Execute approved actions
- [ ] Optional follow-on boards (e.g. renames) if the campaign needs them
```

## UI scaffold

Reuse or copy a local triage UI project (static HTML + tiny Python server)
with `serve.py`, decision HTML, and JSON drop-ins. Adapt pages/fields to the
campaign schema. Details and example JSON in [reference.md](reference.md).

Typical start:

```bash
cd /path/to/triage-ui
python3 serve.py
# → http://127.0.0.1:8765/
```

## PII / data safety

- **Fabricate dummy data** in skill examples, fixtures, PR bodies, and chat
  summaries (`demo-api`, `ops@example.com`, `192.0.2.0/24`, `OWNER` /
  `example-repo`). Never paste live operator inventory, real hostnames, tokens,
  cookies, private paths, or customer data into chat or committed files.
- Decision JSON may sit on the operator’s machine for the campaign — **do not
  commit** it; **do not** echo full boards into chat or PR descriptions.
- When summarizing UI results, report **counts and action tallies** (e.g. “12
  archive, 3 delete”) — not full row dumps with real names/URLs unless the
  user asks for a specific item.
- Mail/calendar lookups (if used): return company + confidence + minimal
  evidence pointers — **no** full message bodies, raw addresses lists, or
  token dumps. Prefer deferring over inventing identity.

## Hard preferences

- Batched approval via **local web UI** — not chat walls of tables
- Schema is **topic-agnostic**; invent fitting JSON/fields per campaign
- Do not commit triage JSON or skill changes unless asked
- Prefer user-driven deletes / irreversible ops when they want that control

---

## Example campaign: GitHub repo hygiene

Use this section when the large decision set is GitHub repos under an `OWNER`.
Same core loop; concrete phases and heuristics follow.

### Progress checklist (repos)

```
- [ ] Phase 1 — Inventory + suggestions
- [ ] Phase 2 — Decision UI (keep/archive/delete + README)
- [ ] Phase 2b — Execute archives / README updates (user deletes)
- [ ] Phase 3 — Rename triage UI + execute
- [ ] Phase 4 — Extract unique code before any delete
```

### Phase 1 — Inventory

1. List repos:
   ```bash
   gh repo list OWNER --limit 200 \
     --json name,url,description,isPrivate,isArchived,isFork,primaryLanguage,diskUsage,pushedAt,createdAt
   ```
2. Probe each repo lightly: README presence/size, root file count, fork/archived/private, description. Prefer `gh api` / sparse checks over full clones.
3. Assign **suggested** `target` and `readme` using heuristics below.
4. Write `repos.json` for the decision UI (schema in [reference.md](reference.md)). Pre-fill `target`/`readme` from suggestions; `decided: false`.

#### Heuristics

| Target | When |
|--------|------|
| **delete** | Empty placeholders, unused forks, broken stubs, fully superseded duplicates |
| **archive** | Coursework, interview take-homes, finished one-offs, old utilities |
| **keep** | Active products, published libs, infra, personal apps still used |

- **Before delete:** check if the logic lives elsewhere (another owner/org or a successor codebase).
- README: `yes` if thin/missing and keeping or archiving; `no` if already fine; `NA` if delete.

### Phase 2 — Decision UI (keep / archive / delete)

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

#### Archive mutate rule

Archived repos must be **unarchived → mutate → re-archived** for any rename or README push. See [reference.md](reference.md).

### Phase 3 — Rename triage

Run after keep/archive decisions (or on the surviving set).

1. Suggest kebab-case clearer names from purpose; fix typos.
2. Company-qualified interview assignment names **only when company is proven** (mail/calendar evidence) — otherwise defer + brainstorm.
3. Write `renames.json` (all candidates). UI shows **only** rows where `suggested ≠ current`.
4. Open `http://127.0.0.1:8765/rename.html`.

#### Rename UI requirements (do not regress)

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

### Phase 4 — Extract before delete

If a delete-candidate still has unique useful code:

1. Extract into a **staging folder** in the successor codebase.
2. Add a short README with provenance (source repo URL, date, what was copied).
3. Do **not** wire into production exports until adapted.
4. Only then allow delete (user or agent).

### Repo-campaign preferences

- User may delete repos themselves; agent focuses on archive + README + rename + extract
- Never invent company names for interview repos without evidence
