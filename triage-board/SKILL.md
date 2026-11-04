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

For a full worked example of one campaign (schemas, UI layout, commands), see
[reference.md](reference.md). Copy the **shape**, not the domain.

## When to use

- Dozens (or more) of items need an explicit choice
- Chat walls of tables would be unusable
- The topic does not matter — only the need for batched human decisions

## Roles

| Actor | Does |
|-------|------|
| Agent | Inventory, suggest defaults, adapt/serve UI, parse submitted JSON, execute approved actions |
| User | Reviews and submits decisions in the local UI |

## Core loop

1. **Clarify the schema** with the user if needed: what is a row, which
   fields/options (actions, free-text, notes, etc.).
2. **Inventory** the items; probe lightly; assign **suggested** values.
3. **Write JSON** next to the UI scaffold; start the local server; point the
   user at the board — never paste the full table into chat for approval.
4. **Parse** the submitted decisions JSON (`jq`).
5. **Execute** only what the UI approved. Destructive actions need clear UI
   intent (and often an explicit extra OK from the user).

### Progress checklist

```
- [ ] Schema + inventory + suggestions
- [ ] Decision UI live; user submits
- [ ] Execute approved actions
- [ ] Optional follow-on boards if the campaign needs them
```

## UI scaffold

Reuse or copy a local triage UI project (static HTML + tiny Python server)
with decision pages and JSON drop-ins. Adapt pages/fields to the campaign
schema. Scaffold layout and example payloads: [reference.md](reference.md).

Typical start:

```bash
cd /path/to/triage-ui
python3 serve.py
# → http://127.0.0.1:8765/
```

## PII / data safety

- **Fabricate dummy data** in skill examples, fixtures, PR bodies, and chat
  summaries (`demo-item`, `ops@example.com`, `192.0.2.0/24`). Never paste live
  inventories, real hostnames, tokens, cookies, private paths, or customer data
  into chat or committed files.
- Decision JSON may sit on the operator’s machine for the campaign — **do not
  commit** it; **do not** echo full boards into chat or PR descriptions.
- When summarizing UI results, report **counts and action tallies** — not full
  row dumps with real identifiers unless the user asks for a specific item.
- Side-channel lookups (mail, calendar, etc.): return minimal evidence
  pointers only — **no** full message bodies, raw address lists, or token
  dumps. Prefer deferring over inventing identity.

## Hard preferences

- Batched approval via **local web UI** — not chat walls of tables
- Schema is **topic-agnostic**; invent fitting JSON/fields per campaign
- Do not commit triage JSON or skill changes unless asked
- Prefer user-driven irreversible ops when they want that control
