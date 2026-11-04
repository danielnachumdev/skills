---
name: triage-board
description: >-
  Batch many user decisions through a local web UI instead of chat tables.
  Use when the user must choose among a large set of items on any topic,
  asks for a triage board or decision board, or needs local batched approvals.
---

# Triage Board

When the user must **decide about a lot of things** — **regardless of topic** —
do **not** dump huge decision tables in chat. Run a local decision board:

**inventory → suggest → local web UI → parse JSON → execute.**

## When to use

- Dozens (or more) of items need an explicit choice
- Chat walls of tables would be unusable
- The topic does not matter — only the need for batched human decisions

## Roles

| Actor | Does |
|-------|------|
| Agent | Inventory, suggest defaults, **adapt** the board UI/JSON to the data, serve UI, parse submitted JSON, execute approved actions |
| User | Reviews and submits decisions in the local UI |

## Core loop

1. **Clarify the schema** from the user’s decision type: what is a row, which
   fields, which actions (not every campaign is rename/keep/defer).
2. **Inventory** the items; probe lightly; assign **suggested** values.
3. **Adapt the board** — start from [`scripts/`](scripts/) (`serve.py` +
   `index.html`), then change columns, labels, actions, filters, and JSON
   shape to match **this** campaign. Do not force unrelated data into the
   example rename UX.
4. Copy the adapted UI to a working directory; write campaign `items.json`
   next to `serve.py`; start the server; point the user at the board — never
   paste the full table into chat.
5. **Parse** submitted `decisions.json` (`jq`).
6. **Execute** only what the UI approved. Destructive actions need clear UI
   intent (and often an explicit extra OK from the user).

### Progress checklist

```
- [ ] Schema matched to the user’s decision type
- [ ] Board UI adapted (not a blind copy of the example)
- [ ] Inventory + suggestions loaded
- [ ] Decision UI live; user submits
- [ ] Execute approved actions
```

## Example material

| Path | Role |
|------|------|
| [`scripts/serve.py`](scripts/serve.py) | Tiny localhost server (`POST /api/submit` → `decisions.json`) |
| [`scripts/index.html`](scripts/index.html) | **Example** single board (rename / keep / defer) — adjust freely |
| [`references/`](references/) | Worked write-up + fabricated demo `items.json` |

The shipped `index.html` is a **starting template**, not the product. If the
user is deciding keep/drop, classify, approve/reject, pick owners, etc., change
the actions and fields accordingly. See [`references/reference.md`](references/reference.md).

**Run (after adapting):**

```bash
cp -R /path/to/triage-board/scripts /tmp/triage-ui-work
cd /tmp/triage-ui-work
# write or copy items.json for this campaign (see references/examples/)
python3 serve.py
# → http://127.0.0.1:8765/
```

Do **not** commit live `items.json` or `decisions.json`.

## PII / data safety

- **Fabricate dummy data** in examples, fixtures, PR bodies, and chat summaries
  (`demo-item`, `ops@example.com`, `192.0.2.0/24`). Never paste live
  inventories, real hostnames, tokens, cookies, private paths, or customer data
  into chat or committed files.
- Decision JSON may sit on the operator’s machine — **do not commit** it;
  **do not** echo full boards into chat or PR descriptions.
- When summarizing UI results, report **counts and action tallies** — not full
  row dumps with real identifiers unless the user asks for a specific item.
- Side-channel lookups (mail, calendar, etc.): minimal evidence pointers only —
  **no** full bodies, raw address lists, or token dumps.

## Hard preferences

- Batched approval via **local web UI** — not chat walls of tables
- **Adapt the board to the data** — example rename UX is illustrative only
- Do not commit triage JSON or skill changes unless asked
- Prefer user-driven irreversible ops when they want that control
