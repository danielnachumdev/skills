---
name: async
description: >-
  Offload the current user task to a background Task subagent so the main chat
  stays free. Use when the user invokes /async, asks to run something in a
  background subagent, or says not to block the main prompt.
disable-model-invocation: true
---

# async

Run the **current task** in a background subagent. Do not do the work in the parent agent.

## Steps

1. **Extract the task** from the user message (everything after `/async`, or the attached/current prompt). If the task is empty or ambiguous, ask one clarifying question in the parent and stop.
2. **Worktree for code changes**: if the task will mutate a git checkout, **prefer / infer an isolated git worktree** (recommended). Create it **usually under `/tmp/...`**. Do **not** place it by going `../` out of the current working directory (e.g. a sibling of the repo under the projects tree)—that clutters checkouts and collides with other work. If unsure whether a worktree is appropriate, **ask the user and get confirmation in the parent** before launching (or before the subagent mutates the tree). When confirmed or clearly appropriate, put worktree setup and the worktree path in the subagent prompt.
3. **Launch** `Task` with:
   - `run_in_background: true`
   - `subagent_type`: `generalPurpose` unless the user named another type
   - `description`: short 3–5 word title for the UI
   - `prompt`: full, self-contained instructions (repo path, goal, constraints, verify steps). The subagent has **no** parent chat history — include all needed context.
4. **Reply briefly** in the parent only: confirm it started and link the agent as `[label](agent-id)`. Do not poll, await, or restate the task at length.
5. **On completion notification**: follow the system’s subagent-notification rules (no regurgitation; follow-ups only if needed).

## Prompt must include

- Absolute workspace/repo path when relevant (worktree path when using an isolated worktree)
- Explicit success criteria (e.g. `npm test` green)
- “Do not commit unless asked” unless the user requested a commit
- Any user constraints verbatim

## Do not

- Implement the task in the parent “while” the subagent runs
- Use `run_in_background: false`
- Block on `Await` / polling unless the user later asks for status
- Launch code-mutating work on a contested checkout when a worktree was recommended but not confirmed
