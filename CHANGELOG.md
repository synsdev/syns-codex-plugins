# Changelog

All notable changes to `syns-codex-plugins` are documented here. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.0] — 2026-09-13

### Changed

- `syns` plugin: `Stop` runs `syns sync --if-repo` instead of `syns push`. It brings in the repository head and publishes the whole folder; where the head moved, it prepares a resolution instead of refusing.
- Only a resolution continues Codex:
  - `Stop` exits `2` with the CLI's instruction.
  - `SessionStart` puts a pending resolution into developer context before new work.
- Synced, no changes and the no-repository skip print nothing. Every other failure answers with a fixed `systemMessage` per exit code (server unreachable, attention required, or refused), because Codex does not show a failed hook's own output.
- Every publication carries published-by provenance: `SYNS_INTEGRATION=codex`, `SYNS_RUN` (the session id) and `SYNS_TRIGGER` (`start` or `finish`). Each is a default only: a value set in the environment wins.
- Both hooks remain single command lines in `hooks/hooks.json`.
- **The hook commands changed, so Codex asks for them to be trusted again in `/hooks`.** Until then they do not run.

### Removed

- `SYNS_PUSH_MESSAGE`: `syns sync` takes no commit message.

### Requires

- Syns CLI 0.3.0 or newer.

## [0.2.1]

### Added

- `syns-init` skill in the `syns` plugin: the byte-identical hosted/Claude/Codex setup package, with digest-bound local review and evaluation before adoption or private publication.
- `plan-sharing` plugin: the Codex port of the Claude plan-sharing plugin.
  Because Codex has no `ExitPlanMode` tool, it hooks `Stop` and captures the
  `<proposed_plan>` block the agent produces in Plan Mode — keyed off the block
  itself (not `permission_mode`, which is the approval mode at `Stop`), with a
  `transcript_path` fallback because `last_assistant_message` is usually `null`
  in Plan Mode. The plan is saved into the current Syns repo's
  `plans/codex-<session>.md` (pull → write → push). If other agents' plans exist
  in `plans/`, it emits `{"decision":"block","reason":…}` so Codex continues the
  turn and the agent — which reads the peer files itself — checks for conflicts
  before implementing; the message lists peer filenames only (no plan bodies), to
  keep the user-facing prompt clean. `stop_hook_active` is honored to warn only
  once (no loop). Fails open and stays silent outside Plan Mode or a Syns repo.

## [0.1.0] — 2026-06-02

First release. Codex port of `syns-claude-plugins`. One plugin, two hooks.

### Added

- `syns` plugin with `SessionStart` and `Stop` hooks that invoke `syns pull --if-repo` and `syns push --if-repo`. Outside a Syns repo every hook is a silent no-op; inside a Syns repo every Codex turn becomes one commit on the server.
- First-session bootstrap in the `SessionStart` hook: if `syns` isn't on the user's `PATH`, runs `curl -fsSL https://install.syns.dev/install.sh | sh` to install it.
- `Stop` hook reads the commit message from `$SYNS_PUSH_MESSAGE` and falls back to `codex cli session` when the variable is unset.

### Codex-specific adaptations (vs. the Claude plugin)

- **Manifest at `.codex-plugin/plugin.json`** and marketplace at `.agents/plugins/marketplace.json`, with Codex's richer entry shape (`source`, `policy`, `category`) and an `interface` presentation block.
- **Install + pull combined into one inline `SessionStart` command.** Codex launches hooks in a group concurrently, so chaining install and pull in a single command (instead of two entries) preserves the install-then-pull ordering. Both hooks are inline; no wrapper scripts.
- **`SessionStart` matcher `startup|resume`** (avoids pulling on mid-session `clear`/`compact`).
- **`Stop` stdout sent to `/dev/null`** so an exit-0 push emits no output, satisfying Codex's "JSON-or-empty on exit 0" rule for `Stop`. Exit-code behavior is unchanged: `syns push --if-repo` cannot exit `2` (the only continuation-trigger), so the turn never loops, and genuine failures still surface as hook errors.
- **Installer output suppressed** so it isn't injected as Codex "developer context."
- Plugin-bundled hooks require trust review via `/hooks` before they run.

### Known limitations

- macOS and Linux only. Windows users can install the CLI manually via Scoop; the hook commands themselves don't yet run under PowerShell.
- First-run install activates from the next session (install.sh edits the shell rc, not the running process `PATH`).

[0.3.0]: https://github.com/synsdev/syns-codex-plugins/releases/tag/v0.3.0
[0.1.0]: https://github.com/synsdev/syns-codex-plugins/releases/tag/v0.1.0
