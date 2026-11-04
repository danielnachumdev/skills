# Triage Board — Reference

This file is a **worked example** of one triage-board campaign (GitHub repo
hygiene). The skill itself is topic-agnostic — invent JSON fields and UI pages
that match the **current** decision set. Copy the **shape**, not the domain.

Shipped UI: [`ui/`](ui/) (`serve.py`, `index.html`, `rename.html`). Demo-only
JSON: [`ui/examples/`](ui/examples/).

**PII:** examples use fabricated placeholders only (`OWNER`, `demo-api`,
`192.0.2.0/24`-style dummies). Do not commit live decision JSON; do not paste
full live inventories into chat or PRs.

## UI scaffold

Copy `ui/` to a working directory, drop campaign JSON next to `serve.py`, then:

```bash
cd /path/to/triage-ui-work
python3 serve.py
# Decision board: http://127.0.0.1:8765/
# Rename board:   http://127.0.0.1:8765/rename.html
```

```text
<triage-ui-work>/
  serve.py                 # from skill ui/
  index.html
  rename.html
  repos.json               # campaign input (not committed)
  decisions.json           # Phase 2 output (POST /api/submit)
  renames.json             # Phase 3 input
  rename-decisions.json    # Phase 3 output (POST /api/submit-renames)
```

For other campaigns, adapt or replace pages/endpoints so rows and actions match
that schema. `serve.py` currently accepts `repos` lists on
`/api/submit` and `/api/submit-renames`.

---

## Example campaign: GitHub repo hygiene

Use when the large decision set is GitHub repos under an `OWNER`.

### Progress checklist

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
2. Probe each repo lightly: README presence/size, root file count,
   fork/archived/private, description. Prefer `gh api` / sparse checks over
   full clones.
3. Assign **suggested** `target` and `readme` using heuristics below.
4. Write `repos.json` next to `serve.py` in the working copy. Pre-fill
   `target`/`readme` from suggestions; `decided: false`.

#### Heuristics

| Target | When |
|--------|------|
| **delete** | Empty placeholders, unused forks, broken stubs, fully superseded duplicates |
| **archive** | Coursework, interview take-homes, finished one-offs, old utilities |
| **keep** | Active products, published libs, infra, personal apps still used |

- **Before delete:** check if the logic lives elsewhere (another owner/org or a
  successor codebase).
- README: `yes` if thin/missing and keeping or archiving; `no` if already fine;
  `NA` if delete.

### Phase 2 — Decision UI (keep / archive / delete)

1. Ensure `repos.json` is next to `serve.py` in the working copy.
2. Start server → `http://127.0.0.1:8765/`
3. User submits → `decisions.json` via `POST /api/submit`.
4. Execute:

| Decision | Agent action |
|----------|--------------|
| keep + readme yes | Update README (push) |
| archive | Archive via `gh`; if README yes, **unarchive → push README → re-archive** |
| delete | Prefer user deletes manually; if agent deletes, only after Phase 4 extract and explicit OK |

#### Archive mutate rule

Archived repos must be **unarchived → mutate → re-archived** for any rename or
README push.

### Phase 3 — Rename triage

1. Suggest kebab-case clearer names from purpose; fix typos.
2. Company-qualified interview names **only when company is proven**
   (mail/calendar evidence) — otherwise defer + brainstorm.
3. Write `renames.json`. UI shows **only** rows where `suggested ≠ current`.
4. Open `http://127.0.0.1:8765/rename.html`.

#### Rename UI requirements (do not regress)

- Show **only** rows where suggested ≠ current
- No “decided” checkbox — submit means decided
- Always-editable free-text target name
- Free-text **notes**
- Actions: **Rename | Keep current | Defer (brainstorm)**

5. User submits → `rename-decisions.json` via `POST /api/submit-renames`.
6. Handle actions:
   - **Rename** → `gh repo rename -R owner/old new --yes` (if archived:
     unarchive → rename → re-archive)
   - **Keep current** → no-op
   - **Defer** → brainstorm; use the mail-assistant prompt below when useful

### Phase 4 — Extract before delete

If a delete-candidate still has unique useful code:

1. Extract into a **staging folder** in the successor codebase.
2. Add a short README with provenance (source repo URL, date, what was copied).
3. Do **not** wire into production exports until adapted.
4. Only then allow delete (user or agent).

### Campaign preferences

- User may delete repos themselves; agent focuses on archive + README + rename +
  extract
- Never invent company names for interview repos without evidence

---

## Example: `repos.json` (Phase 2 input)

See also [`ui/examples/repos.json`](ui/examples/repos.json).

```json
{
  "repos": [
    {
      "name": "demo-api",
      "url": "https://github.com/OWNER/demo-api",
      "description": "…",
      "private": false,
      "archived": false,
      "fork": false,
      "language": "Python",
      "disk_kb": 120,
      "pushed_at": "2026-11-03",
      "created_at": "2024-01-15",
      "suggested_target": "archive",
      "suggested_readme": "no",
      "target": "archive",
      "readme": "no",
      "decided": false
    }
  ]
}
```

| Field | Values |
|-------|--------|
| `suggested_target` / `target` | `keep` \| `archive` \| `delete` |
| `suggested_readme` / `readme` | `yes` \| `no` \| `NA` (`NA` only for delete) |

---

## Example: `decisions.json` (Phase 2 output)

```json
{
  "submitted_at": "ISO-8601",
  "repos": [
    {
      "name": "demo-api",
      "target": "archive",
      "readme": "no",
      "decided": true,
      "suggested_target": "archive",
      "suggested_readme": "no"
    }
  ]
}
```

```bash
jq -r '.repos[] | select(.target=="archive") | .name' decisions.json
jq -r '.repos[] | select(.target=="delete") | .name' decisions.json
jq -r '.repos[] | select(.readme=="yes") | "\(.name) \(.target)"' decisions.json
```

---

## Example: `renames.json` (Phase 3 input)

See also [`ui/examples/renames.json`](ui/examples/renames.json).

```json
{
  "repos": [
    {
      "name": "OldName",
      "suggested": "clearer-kebab-name",
      "url": "https://github.com/OWNER/OldName",
      "description": "…",
      "archived": true,
      "fork": false,
      "language": "Python"
    }
  ]
}
```

`rename.html` filters to `name !== suggested` client-side. Still OK to include
same-name rows; they are hidden.

---

## Example: `rename-decisions.json` (Phase 3 output)

```json
{
  "submitted_at": "ISO-8601",
  "repos": [
    {
      "current": "OldName",
      "suggested": "clearer-kebab-name",
      "target": "final-name-user-edited",
      "final": "final-name-user-edited",
      "action": "approve",
      "notes": "",
      "will_rename": true,
      "needs_brainstorm": false
    }
  ]
}
```

| `action` | Meaning |
|----------|---------|
| `approve` | Rename to `final` (if ≠ `current`) |
| `keep` | Keep current name |
| `defer` | Brainstorm; `needs_brainstorm: true` |

```bash
jq -r '.repos[] | select(.will_rename) | "\(.current) -> \(.final)"' rename-decisions.json
jq -r '.repos[] | select(.needs_brainstorm) | "\(.current)\t\(.notes)"' rename-decisions.json
```

---

## Example `gh` commands

```bash
gh repo list OWNER --limit 200 \
  --json name,url,description,isPrivate,isArchived,isFork,primaryLanguage,diskUsage,pushedAt,createdAt

gh api "repos/OWNER/REPO/readme" --jq '.size' 2>/dev/null || echo 0

gh repo archive OWNER/REPO --yes
gh api -X PATCH "repos/OWNER/REPO" -f archived=false

gh repo rename -R OWNER/OLD NEW --yes

gh repo delete OWNER/REPO --yes
```

### Archived mutate sequence

```bash
gh api -X PATCH "repos/OWNER/REPO" -f archived=false
# … git push / gh repo rename …
gh repo archive OWNER/REPO --yes
```

If rename also changes the path, re-archive with the **new** name:
`gh repo archive OWNER/NEW --yes`.

---

## Mail-assistant prompt (company discovery)

Use when an interview / take-home repo is **deferred** and a company-qualified
name might help. Only apply a company slug when evidence is solid.

Keep results **PII-minimized**: no full bodies, no address books, no tokens.
Subjects + sender **domain** + approximate date are enough.

```text
Search my mail (and calendar if available) for evidence of which company
owned or assigned the take-home / interview project related to GitHub repo
"REPO_NAME" (also try: KEYWORDS_FROM_README_OR_CODE).

Return:
1. Company name(s) with confidence (high/medium/low)
2. Evidence: message subject, sender domain, approximate date
   (no full PII dumps — no bodies, no raw email lists)
3. Suggested kebab-case repo name if confidence is high
4. If no clear owner: say so — do not guess

Do not invent a company. Prefer deferring over a wrong qualifier.
Do not paste search hits into public PR bodies or committed files.
```

---

## Extract-before-delete pattern

```text
SUCCESSOR_REPO/
  _staging_from_OLDREPO/     # or similar staging path
    README.md                # provenance: source URL, date, intent
    …copied unique files…
```

Staging README should state: source `https://github.com/OWNER/OLDREPO`, what
was unique, and that it is **not** wired into production exports yet.
