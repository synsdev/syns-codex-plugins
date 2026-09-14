# `syns` plugin (Codex)

Two lifecycle hooks and one setup skill.

| Surface | Action |
|:--|:--|
| `SessionStart` | Installs `syns` if it is missing, then `syns pull --if-repo`. Matches `startup` and `resume`. |
| `Stop` | `syns sync --if-repo` — brings in the repository head and publishes everything written in the folder, once per turn. |
| `syns-init` skill | Mines an existing project, proposes an agent-readable repository for local HTML review, runs a matched read-only comparison after approval, and adopts or privately publishes only explicitly approved operations. An `owner/name` invocation joins instead. |

The setup skill is packaged from the same canonical source as the hosted and Claude copies. `checksums.json` verifies its skill, references, review assets, renderers, and fixtures.

The setup skill does not install lifecycle hooks. Codex runs the hooks below only after they are trusted.

## What the hooks do with the result

Each hook is one command line in `hooks/hooks.json`, with no script behind it. It runs the command a person would run, and only turns the CLI's exit code into Codex's hook answer:

| `syns` exits | `SessionStart` | `Stop` |
|:--|:--|:--|
| `0`: synced, no changes, or not a Syns folder | nothing | nothing |
| `4`: resolution required | the CLI's instruction becomes developer context, asking Codex to finish the resolution before new work | exit `2`: the turn continues with the CLI's instruction |
| `3`: server unreachable | a warning that the next hook retries | the same warning |
| `5`: attention required | a warning to see `syns status` and `syns resolution show` | the same warning |
| anything else: a credential, permission or validation refusal | a warning to run `syns pull` and see why | a warning to run `syns sync` and see why |

Codex does not show a failed hook's own output, so failures are answered with a fixed warning (`systemMessage`) for each exit code. The exit code alone doesn't tell a credential refusal from a validation one; rerunning the command shows the CLI's own line.

Nothing publishes past a moved head until Codex runs `syns resolution continue`. Stop continues the turn once per turn. If Codex stops again in the same turn with the resolution unfinished, the hook warns you instead of continuing it again, and your next prompt starts over.

## Provenance

Every publication records who published it. The hooks set `SYNS_INTEGRATION=codex`, `SYNS_RUN` (the session id) and `SYNS_TRIGGER` (`start` or `finish`). Each is only a default: a value you set in your environment always wins. `SYNS_TASK`, if you set it, is sent alongside.

Codex gives hooks no way to set the agent's own environment. A `syns resolution continue` that Codex runs itself therefore carries only the values your environment sets.

## Trust the hooks

Codex skips plugin-bundled hooks until you review and trust them. After enabling or updating the plugin, run `/hooks` in Codex to review and trust the `SessionStart` and `Stop` hooks. A hook whose command changed must be trusted again, or it silently stops running. For one-off automation you can instead start Codex with `--dangerously-bypass-hook-trust`. Disable all hooks globally with `[features] hooks = false` in `config.toml`.

## Requirements

- Syns CLI 0.3.0 or newer (`syns upgrade`).
- macOS and Linux. The hook lines are POSIX shell, run through `$SHELL -lc`.

## Behavior contract

- **Outside Syns repos: silent no-op.** No output, exit 0.
- **A successful pull or sync prints nothing.**
- **Only a resolution continues the turn.** Every other failure is a warning, and the turn ends normally.
- **Stop is per-turn.** Each turn publishes what the folder holds at that moment, edits from other writers included; a turn that changed nothing publishes nothing.
- **`SYNS_PUSH_MESSAGE` is no longer read.** `syns sync` takes no commit message.

## Known limitations

- **First-run install activates next session.** `install.syns.dev/install.sh` edits your shell rc rather than the running process environment. A freshly installed `syns` is therefore not on `PATH` within the same session: the first session's hooks silently no-op, and `syns` works from the next session onward.
- Codex launches a group's hooks concurrently, so `SessionStart` installs and pulls in one command to keep that order.
