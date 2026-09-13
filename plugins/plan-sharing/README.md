# `plan-sharing` plugin (Codex)

Coordinate concurrent Codex agents at plan time. When a turn produces a Plan
Mode plan, the plugin saves it into the current Syns repo's `plans/` folder and,
if other agents have plans there, asks the agent to check for conflicts before
implementing.

Plans live in the repo they belong to, so they are version-controlled alongside
everything else and never mixed across projects. Outside a Syns repo, or when no
plan was produced, the plugin does nothing.

| Event  | Action                                                                                                            |
|:-------|:----------------------------------------------------------------------------------------------------------------|
| `Stop` | If the turn produced a `<proposed_plan>`: pull → write `plans/codex-<session>.md` → push → if peers exist, warn. |

## How it works

Codex has **no `ExitPlanMode` tool**. The Plan Mode plan is emitted as assistant
text — a `<proposed_plan>…</proposed_plan>` block — so the plugin hooks `Stop`.

1. **Capture.** Extracts the `<proposed_plan>` block. In Plan Mode
   `last_assistant_message` is usually `null`, so it falls back to reading the
   last assistant message from `transcript_path`. No block → no-op. (It keys off
   the block, not `permission_mode`, which at `Stop` is the approval mode, not the
   plan/collaboration mode.)
2. **Share.** Resolves the repo root via `.syns.yaml`, then `syns pull --if-repo`,
   writes the plan to `plans/codex-<session>.md` (one stable file per session),
   and `syns push --if-repo` (one retry on a head-mismatch).
3. **Warn.** If other `plans/*.md` exist, emits `{"decision":"block","reason":…}`.
   Codex turns this into a continuation, so the agent stays in Plan Mode. The
   message lists the **peer plan filenames** and asks the agent to read them and
   check its plan doesn't edit the same files, duplicate work, or contradict them
   — revise or report if so. The agent does the comparison by reading the files;
   plan bodies are deliberately **not** inlined into the message, to keep the
   user-facing prompt clean.

`stop_hook_active` is honored: the plugin publishes on every plan turn but
**warns only once**, so it never loops.

## Behavior contract

- **No `<proposed_plan>` / not a Syns repo / `syns` or `jq` missing → silent
  no-op** (exit 0, no stdout — `Stop` requires JSON-or-empty).
- **Fail open.** Any infrastructure error ends silently and never wedges the turn.
- **Enforcement is a continuation, not a veto.** `Stop` cannot inject
  `additionalContext`; the warning arrives as a continuation that keeps the agent
  in Plan Mode to act on it.

## Requirements & setup

- `syns` CLI on `PATH`, authenticated, with access to the repo. `jq`.
- **Trust the hook:** Codex skips plugin-bundled hooks until reviewed. Run
  `/hooks` to trust this plugin's `Stop` hook (or `--dangerously-bypass-hook-trust`
  for a one-off). Disable all hooks with `[features] hooks = false`.

Pairs naturally with the [`syns`](../syns) plugin (pull on start, push on stop).
