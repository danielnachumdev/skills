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
| **Decline** | Reject the *suggested value as written* — not “ignore this row” |
| **Defer** | Not ready to lock the suggested action; notes are the primary artifact |

The UI should make it easy to:

- **Edit the suggested value** before accepting (multi-line free-text for long
  locks / design text; constrained editor only when the value set is small)
- **Add notes on any row** (accept / decline / defer) — alternate intent, why
  declined, brainstorm seeds, open questions

### Nuances

- **Always read notes** on every submitted row (accept / decline / defer)
  before executing or opening follow-ups. Notes are first-class intent, not
  optional color.
- **Accept ≠ raw suggestion.** Edited accepts are first-class; execute from
  `final` / `target` (or equivalent), not blindly from the original
  `suggested`.
- **Decline ≠ discard notes.** Decline rejects only the suggested value. If
  notes describe an alternate decision or preferred design, treat that as the
  user’s intent for plan updates / locks. Do not invent a competing
  “counter-suggestion” action verb — prefer Accept-after-edit next time when
  the UI fits — but **never** re-ask a question the notes already answered.
- **Defer notes are primary.** After submit, summarize **counts**; then use
  defer notes for follow-up. Do not re-prompt topics those notes already
  settled. Submit does **not** mean every row is settled.
- **Long suggested values need multi-line editors.** Design locks, paragraphs,
  and other long `suggested` text must use a full-width auto-sizing
  `<textarea>` (`white-space: pre-wrap`), **never** a single-line
  `<input type="text">`. Stack the card (id + badges → description → proposed
  lock → notes → actions) at a readable max-width (~820px). Escape textarea
  content; autosize on input/render.
- **Show all items by default.** Do **not** hide rows where
  `name === suggested` unless the campaign opts into rename-style filtering
  (short labels with nothing to decide). Design-lock campaigns must show every
  row.
- **Follow-up boards = genuine gaps only.** Include rows where the user said
  they don’t understand, or notes leave an unresolved fork. Never re-ask
  locks already present in notes (including decline/defer notes).
- **One board is enough** when every row is “react to a suggestion.” Add
  another board only for a *different* decision type on a filtered subset —
  or for true gaps above — not by default.
- **Domain labels are cosmetics.** “Rename” / “Archive” / etc. may appear in
  the UI if they help; the contract stays accept / decline / defer so agents
  do not invent one-off verbs per topic.

## When to use

- Dozens (or more) of items need an explicit choice
- Chat walls of tables would be unusable
- The topic does not matter — only the need for batched human decisions

## Roles

| Actor | Does |
|-------|------|
| Agent | Inventory, suggest defaults, **adapt** the board UI/JSON to the data, serve UI, parse submitted JSON, execute accepts, incorporate all notes |
| User | Accepts, declines, or defers each suggestion in the local UI; may leave notes on any action |

## Core loop

1. **Clarify the row** from the user’s decision type: identity fields, what a
   “suggestion” is, and any extra columns — keep **accept / decline / defer**
   as the default actions unless the campaign truly needs different ones.
2. **Inventory** the items; probe lightly; assign **suggested** values.
3. **Adapt the board** — start from [`scripts/`](scripts/) (`serve.py` +
   `index.html`). Keep multi-line editable suggestion + notes on every action;
   reshape columns and wording to match **this** campaign’s data. Never demote
   long locks to a one-liner.
4. Copy the adapted UI to a working directory; write campaign `items.json`
   next to `serve.py`; start the server; point the user at the board — never
   paste the full table into chat.
5. **Parse** submitted `decisions.json` (`jq`). **Read notes on every row.**
6. **Execute** accepted rows from **final** values. Incorporate decline/defer
   **notes** into the plan/locks. Only board remaining genuine gaps.
   Destructive actions need clear UI intent (and often an explicit extra OK).

### Progress checklist

```
- [ ] Schema matched to the user’s decision type
- [ ] Board supports accept / decline / defer (+ multi-line edit, notes)
- [ ] Inventory + suggestions loaded
- [ ] Decision UI live; user submits
- [ ] Read all notes; execute accepts; lock note intent; board only gaps
```

## Example material

| Path | Role |
|------|------|
| [`scripts/serve.py`](scripts/serve.py) | Tiny localhost server (`POST /api/submit` → `decisions.json`) |
| [`scripts/index.html`](scripts/index.html) | **Example** board (stacked cards; multi-line proposed lock + notes) |
| [`references/`](references/) | Worked write-up + fabricated demo `items.json` |

The shipped `index.html` is a **starting template**: stacked readable cards,
full-width auto-sizing textarea for proposed locks, notes textarea, and
accept / decline / defer. Change field labels and extra columns for the
campaign; keep that action model unless the user needs a different set.
Details: [`references/reference.md`](references/reference.md).

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
- Default actions: **accept / decline / defer**; multi-line editable suggestion
  + notes on every action
- Long locks / design text → multi-line editors; never a single-line textbox
- Show all items by default; optional rename-style `name === suggested` filter
  only when opted in
- Execute accepts from **final** values; read notes on all rows; incorporate
  decline/defer notes into plan/locks; follow-up boards only for genuine gaps
- Adapt columns/wording to the data; do not invent a one-off action model without reason
- Prefer a **single** board unless a second decision type (or true gaps) needs its own
- Do not commit triage JSON or skill changes unless asked
- Prefer user-driven irreversible ops when they want that control
