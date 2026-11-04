# Triage Board — Reference

## UI scaffold

Reuse or copy a local triage UI project with this layout (example checkout:
`/home/daniel/dev/projects/repo-triage/`):

```text
<triage-ui>/
  serve.py          # 127.0.0.1:8765
  index.html        # keep/archive/delete + README
  rename.html       # rename / keep / defer
  repos.json        # Phase 2 input
  decisions.json    # Phase 2 output (POST /api/submit)
  renames.json      # Phase 3 input
  rename-decisions.json  # Phase 3 output (POST /api/submit-renames)
```

Start:

```bash
cd /path/to/triage-ui   # e.g. a local repo-triage checkout
python3 serve.py
# Keep/archive/delete: http://127.0.0.1:8765/
# Rename triage:       http://127.0.0.1:8765/rename.html
```

---

## `repos.json` (Phase 2 input)

```json
{
  "repos": [
    {
      "name": "example-repo",
      "url": "https://github.com/OWNER/example-repo",
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

## `decisions.json` (Phase 2 output)

```json
{
  "submitted_at": "ISO-8601",
  "repos": [
    {
      "name": "example-repo",
      "target": "archive",
      "readme": "no",
      "decided": true,
      "suggested_target": "archive",
      "suggested_readme": "no"
    }
  ]
}
```

Parse with `jq`, e.g.:

```bash
jq -r '.repos[] | select(.target=="archive") | .name' decisions.json
jq -r '.repos[] | select(.target=="delete") | .name' decisions.json
jq -r '.repos[] | select(.readme=="yes") | "\(.name) \(.target)"' decisions.json
```

---

## `renames.json` (Phase 3 input)

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

`rename.html` filters to `name !== suggested` client-side. Still OK to include same-name rows; they are hidden.

---

## `rename-decisions.json` (Phase 3 output)

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
# Inventory
gh repo list OWNER --limit 200 \
  --json name,url,description,isPrivate,isArchived,isFork,primaryLanguage,diskUsage,pushedAt,createdAt

# README probe (bytes; empty/missing → consider readme yes)
gh api "repos/OWNER/REPO/readme" --jq '.size' 2>/dev/null || echo 0

# Archive / unarchive
gh repo archive OWNER/REPO --yes
gh api -X PATCH "repos/OWNER/REPO" -f archived=false

# Rename (non-interactive)
gh repo rename -R OWNER/OLD NEW --yes

# Delete (prefer user; only with explicit OK after extract)
gh repo delete OWNER/REPO --yes
```

### Archived mutate sequence

For README push or rename on an archived repo:

```bash
gh api -X PATCH "repos/OWNER/REPO" -f archived=false
# … git push / gh repo rename …
gh repo archive OWNER/REPO --yes
```

If rename also changes the path, re-archive with the **new** name: `gh repo archive OWNER/NEW --yes`.

---

## Mail-assistant prompt (company discovery)

Use when an interview / take-home repo is **deferred** and a company-qualified name might help. Only apply a company slug when evidence is solid.

```text
Search my mail (and calendar if available) for evidence of which company
owned or assigned the take-home / interview project related to GitHub repo
"REPO_NAME" (also try: KEYWORDS_FROM_README_OR_CODE).

Return:
1. Company name(s) with confidence (high/medium/low)
2. Evidence: message subject, sender domain, approximate date (no full PII dumps)
3. Suggested kebab-case repo name if confidence is high
4. If no clear owner: say so — do not guess

Do not invent a company. Prefer deferring over a wrong qualifier.
```

---

## Extract-before-delete pattern

```text
SUCCESSOR_REPO/
  _staging_from_OLDREPO/     # or similar staging path
    README.md                # provenance: source URL, date, intent
    …copied unique files…
```

Staging README should state: source `https://github.com/OWNER/OLDREPO`, what was unique, and that it is **not** wired into production exports yet.
