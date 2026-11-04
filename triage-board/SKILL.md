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

## Decision model (default)

For **any** topic, the agent proposes a suggestion per row. The user generally:

| Action | Meaning |
|--------|---------|
| **Accept** | Apply the suggestion **or the user-edited value** |
| **Decline** | Reject the suggestion; keep the **current / status quo** (not a second proposal) |
| **Defer** | Not ready to decide; come back later (usually with notes) |

The UI should make it easy to:

- **Edit the suggested value** before accepting (free-text or a constrained editor)
- **Add notes on deferral** (why deferred, brainstorm seeds, questions)

### Nuances

- **Accept ≠ raw suggestion.** Edited accepts are first-class; execute from
  `final` / `target` (or equivalent), not blindly from the original
  `suggested`.
- **Decline is status quo.** Do not invent a competing “counter-suggestion”
  action. If the campaign is “pick among A/B/C,” keep one suggested default and
  let the user **accept after editing** (or use a constrained editor) — still
  accept / decline / defer.
- **Defer is unfinished work.** After submit, summarize **counts**; then chase
  `needs_followup` (or equivalent) + notes. Submit does **not** mean every row
  is settled.
- **One board is enough** when every row is “react to a suggestion.” Add another
  board only for a *different* decision type on a filtered subset — not by
  default.
- **Domain labels are cosmetics.** “Rename” / “Archive” / etc. may appear in the
  UI if they help; the contract stays accept / decline / defer so agents do not
  invent one-off verbs per topic.

## When to use

- Dozens (or more) of items need an explicit choice
- Chat walls of tables would be unusable
- The topic does not matter — only the need for batched human decisions

## Roles

| Actor | Does |
|-------|------|
| Agent | Inventory, suggest defaults, **adapt** the board UI/JSON to the data, serve UI, parse submitted JSON, execute accepted actions |
| User | Accepts, declines, or defers each suggestion in the local UI |

## Core loop

1. **Clarify the row** from the user’s decision type: identity fields, what a
   “suggestion” is, and any extra columns — keep **accept / decline / defer**
   as the default actions unless the campaign truly needs different ones.
2. **Inventory** the items; probe lightly; assign **suggested** values.
3. **Adapt the board** — start from [`scripts/`](scripts/) (`serve.py` +
   `index.html`). Keep editable suggestion + deferral notes; reshape columns
   and wording to match **this** campaign’s data.
4. Copy the adapted UI to a working directory; write campaign `items.json`
   next to `serve.py`; start the server; point the user at the board — never
   paste the full table into chat.
5. **Parse** submitted `decisions.json` (`jq`).
6. **Execute** only accepted rows using the **final** values. Destructive
   actions need clear UI intent (and often an explicit extra OK). Declined rows
   are no-ops; deferred rows stay open for follow-up from notes.

### Progress checklist

```
- [ ] Schema matched to the user’s decision type
- [ ] Board supports accept / decline / defer (+ edit suggestion, defer notes)
- [ ] Inventory + suggestions loaded
- [ ] Decision UI live; user submits
- [ ] Execute accepted actions; track deferrals
```

## Example material

| Path | Role |
|------|------|
| [`scripts/serve.py`](scripts/serve.py) | Tiny localhost server (`POST /api/submit` → `decisions.json`) |
| [`scripts/index.html`](scripts/index.html) | **Example** board (accept / decline / defer + editable suggestion + notes) |
| [`references/`](references/) | Worked write-up + fabricated demo `items.json` |

The shipped `index.html` is a **starting template**. Change field labels and
extra columns for the campaign; keep the accept / decline / defer pattern
unless the user needs a different action set. Details:
[`references/reference.md`](references/reference.md).

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
- Default actions: **accept / decline / defer**; editable suggestion + defer notes
- Execute accepts from **final** values; treat deferrals as open work
- Adapt columns/wording to the data; do not invent a one-off action model without reason
- Prefer a **single** board unless a second decision type truly needs its own
- Do not commit triage JSON or skill changes unless asked
- Prefer user-driven irreversible ops when they want that control
