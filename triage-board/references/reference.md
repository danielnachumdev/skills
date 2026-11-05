# Triage Board — Reference

Example material for the agent. Default decision model (any topic): the AI
suggests a value per row; the user **accepts**, **declines**, or **defers**.
The UI should allow **editing the suggestion** before accept and **notes on
any action**. Accept applies **final** (edited) values; decline rejects the
suggested value as written (still read notes — they may carry alternate
intent); defer is unfinished work whose **notes are primary**. Always read
notes before executing or opening follow-ups; never re-ask locks already in
notes. Follow-up boards only for genuine gaps. One board is enough for
“react to a suggestion”; domain labels are cosmetic. Adapt
[`scripts/index.html`](../scripts/index.html) columns/JSON to the campaign —
keep that action model unless the campaign truly needs other actions. See
**Nuances** in [`SKILL.md`](../SKILL.md).

**PII:** placeholders only (`OWNER`, `demo-api`, …). Do not commit live
`items.json` / `decisions.json`; do not paste full live inventories into chat
or PRs.

## Layout

```text
triage-board/
  SKILL.md
  scripts/
    serve.py       # POST /api/submit → decisions.json
    index.html     # example board — customize per campaign
  references/
    reference.md   # this file
    examples/
      items.json   # fabricated demo input
```

## Adapt before you serve

Copy `scripts/` to a working directory, then reshape fields to the data while
keeping accept / decline / defer (+ editable suggestion, notes on any action):

| Campaign flavor | Typical tweaks |
|-----------------|----------------|
| Renames / labels | Example is already close; “suggested” = proposed name |
| Keep vs drop vs archive | Suggestion = proposed target; accept applies it |
| Classify / tag / assign | Suggestion = class/owner; maybe constrain the editor |
| Approve content changes | Suggestion = proposed text/path; decline = reject that proposal (read notes for alternate intent) |

## Run the example board

```bash
cp -R /path/to/triage-board/scripts /tmp/triage-ui-work
cd /tmp/triage-ui-work
cp /path/to/triage-board/references/examples/items.json ./items.json
python3 serve.py
# → http://127.0.0.1:8765/
```

Example UI behavior (as shipped):

- Loads `items.json` (`items` array)
- Hides rows where `name === suggested` (nothing to decide)
- Actions: **Accept | Decline | Defer**
- Editable suggested value + notes (on any action; especially useful for defer)
- `POST /api/submit` writes `decisions.json`

---

## Example campaign: suggested renames

Fabricated rows — only to show the template.

### Input — `items.json`

See [`examples/items.json`](examples/items.json).

```json
{
  "items": [
    {
      "name": "OldHelper",
      "suggested": "old-helper",
      "url": "https://github.com/OWNER/OldHelper",
      "description": "…",
      "archived": true,
      "fork": false,
      "language": "Python"
    }
  ]
}
```

### Output — `decisions.json`

```json
{
  "submitted_at": "ISO-8601",
  "items": [
    {
      "current": "OldHelper",
      "suggested": "old-helper",
      "target": "old-helper",
      "final": "old-helper",
      "action": "accept",
      "notes": "",
      "accepted": true,
      "applied": true,
      "needs_followup": false
    }
  ]
}
```

| `action` | Meaning |
|----------|---------|
| `accept` | Apply `final` (edited suggestion or original suggestion); still read `notes` |
| `decline` | Reject suggested value as written; **read `notes`** for alternate intent — do not treat as “unset” |
| `defer` | Follow up later; **`notes` are primary** (`needs_followup: true`); do not re-ask what notes already answered |

```bash
jq -r '.items[] | select(.accepted) | "\(.current) -> \(.final)"' decisions.json
jq -r '.items[] | "\(.action)\t\(.current)\t\(.notes)"' decisions.json
jq -r '.items[] | select(.needs_followup) | "\(.current)\t\(.notes)"' decisions.json
```

After submit: execute accepts from `final`; fold decline/defer note intent into
plan/locks; open a follow-up board only for genuine gaps (unresolved forks /
user said they don’t understand) — never re-ask settled notes.

### Optional follow-through (rename-style accept)

```bash
gh repo rename -R OWNER/OLD NEW --yes
# If archived: unarchive → rename → re-archive
gh api -X PATCH "repos/OWNER/REPO" -f archived=false
gh repo archive OWNER/NEW --yes
```

### Mail-assistant prompt (defer + company naming)

PII-minimized: subjects + sender **domain** + approximate date only — no
bodies, address books, or tokens.

```text
Search my mail (and calendar if available) for evidence of which company
owned or assigned the take-home / interview project related to GitHub repo
"REPO_NAME" (also try: KEYWORDS_FROM_README_OR_CODE).

Return:
1. Company name(s) with confidence (high/medium/low)
2. Evidence: message subject, sender domain, approximate date
3. Suggested kebab-case name if confidence is high
4. If no clear owner: say so — do not guess

Do not invent a company. Do not paste hits into PR bodies or commits.
```
