# `syns` plugin (Codex)

Two lifecycle hooks and one setup skill.

| Surface | Action |
|:--|:--|
| `SessionStart` | Installs `syns` on first run if missing, then `syns pull --if-repo` — pulls if the session's working tree resolves to a Syns repo, no-op otherwise. Matches `startup` and `resume`. |
| `Stop` | `syns push --if-repo -m "<your message>"` — pushes the working tree as a single commit, once per turn. |
| `syns-init` skill | Mines an existing project, proposes an agent-readable repository for local HTML review, runs a matched read-only comparison after approval, and adopts or privately publishes only explicitly approved operations. An `owner/name` invocation joins instead. |

The setup skill is packaged from the same canonical source as the hosted and Claude copies. `checksums.json` verifies its skill, references, review assets, renderers, and fixtures.

The setup skill does not install lifecycle hooks. Codex runs the hooks below only after they are trusted.

## Configuration

The `syns push` in the `Stop` hook reads `$SYNS_PUSH_MESSAGE` for the commit message, falling back to `codex cli session` if unset. Set the variable to customize.

## Trust the hooks

Codex skips plugin-bundled hooks until you review and trust them. After enabling the plugin, run `/hooks` in Codex to review and trust the `SessionStart` and `Stop` hooks. For one-off automation you can instead start Codex with `--dangerously-bypass-hook-trust`. Disable all hooks globally with `[features] hooks = false` in `config.toml`.

## Behavior contract

- **Outside Syns repos: silent no-op.** The `--if-repo` flag exits 0 with no output.
- **Stop never blocks or loops.** `syns push --if-repo` cannot exit `2`, which is the only exit code Codex treats as "continue the turn." Genuine push failures (network, auth, server) exit non-zero and surface as a hook error — the turn still ends normally.
- **Stop is per-turn.** A session with N model turns produces up to N commits (empty turns push nothing).
- **No `Stop` stdout noise.** The push success banner is sent to `/dev/null` so an exit-0 push produces no output, satisfying Codex's "JSON-or-empty on exit 0" rule for `Stop`. The `>/dev/null` does not change any exit-code behavior; `stderr` is left intact so real errors stay visible.
- **Clean session context.** The first-run installer's output is suppressed so it isn't injected as Codex "developer context."

## Known limitations

- macOS and Linux only. Windows users can install the CLI manually via Scoop; the hook commands themselves don't yet run under PowerShell.
- **First-run install activates next session.** `install.syns.dev/install.sh` edits your shell rc rather than the running process environment, so a freshly installed `syns` is not on `PATH` within the same session — the first session's pull silently no-ops, and `syns` becomes usable from the next session onward.

## Implementation notes

- Both hooks are one-line inline commands in `hooks/hooks.json`; there are no wrapper scripts.
- The `SessionStart` command combines install + pull into a single command (`… ; syns pull --if-repo`). Codex launches multiple command hooks in a group concurrently, so two separate entries would race and `pull` could run before `syns` exists; chaining them in one command preserves the install-then-pull ordering.
