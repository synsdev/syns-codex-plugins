# Implementation plan — `syns-codex-plugins`

A Codex CLI port of the `syns-claude-plugins` plugin. Goal: **identical behavior** —
auto-pull on session start, auto-push on every turn-stop, silent no-op outside a
Syns repo — adapted to Codex's hook contract.

---

## 1. What the Claude Code plugin does (reference behavior)

Repo `syns-claude-plugins` is a one-plugin marketplace:

```
syns-claude-plugins/
  .claude-plugin/marketplace.json     # marketplace catalog
  plugins/syns/
    .claude-plugin/plugin.json        # plugin manifest
    hooks/hooks.json                  # the two hooks
    README.md
  README.md  CHANGELOG.md  LICENSE  .gitignore
```

The entire plugin is **two hooks** (`plugins/syns/hooks/hooks.json`):

| Event          | Commands (in order)                                                                 |
|:---------------|:------------------------------------------------------------------------------------|
| `SessionStart` | 1. `if ! command -v syns …; then curl -fsSL https://install.syns.dev/install.sh \| sh; fi`  (bootstrap install) <br> 2. `syns pull --if-repo` |
| `Stop`         | `syns push --if-repo -m "${SYNS_PUSH_MESSAGE:-claude code session}"`                 |

Behavior contract (from the plugin README):
- **Outside a Syns repo → silent no-op, exit 0.** Delivered by the CLI's `--if-repo` flag.
- **Hooks never block the agent.**
- **Stop is per-turn** → a session with N model turns produces up to N commits (empty turns push nothing).
- Commit message comes from `$SYNS_PUSH_MESSAGE`, default `claude code session`.
- macOS/Linux only; Windows install is manual (Scoop).

CLI facts confirmed against the installed `syns` binary and CLI_IA.md:
- `syns pull --if-repo` / `syns push --if-repo -m <msg>` — `--if-repo` = "exit 0 silently unless `.syns.yaml` provided the repository identity."
- Repo identity resolves from cwd (`--name` flag → `.syns.yaml` → git `origin` last segment).

---

## 2. Codex vs. Claude: what is the same, what changes

### Same
- Hook event **names** `SessionStart` and `Stop` exist in Codex.
- Hook **config shape** is identical: `event → matcher group → handlers`, `{"type":"command","command":"…"}`.
- Default plugin hook file location is the **same**: `hooks/hooks.json` at plugin root.
- Hooks run with the **session `cwd`** as working directory — so `--if-repo` resolution works exactly as on Claude.
- `Stop` runs at **turn scope** → "one commit per turn" is preserved.
- `$SYNS_PUSH_MESSAGE` env expansion works identically.

### Changes (the substance of the port)

1. **Manifest dir + marketplace path.** Codex uses `.codex-plugin/plugin.json` (not `.claude-plugin/`). Marketplace is `.agents/plugins/marketplace.json` (Codex also reads a legacy `.claude-plugin/marketplace.json`). We ship the Codex-native `.agents/plugins/marketplace.json`.

2. **Marketplace entry format is richer.** Codex needs `source` as an object (or local string) plus **`policy.installation`, `policy.authentication`, `category`** per entry, and `interface.displayName` for the catalog title. Presentation metadata lives in the plugin manifest's `interface` object.

3. **Concurrency: hooks in one group run *concurrently* in Codex.** "Multiple matching command hooks for the same event are launched concurrently." The Claude `SessionStart` group relies on install-then-pull **ordering**. On Codex two separate command entries would race and `pull` could run before `syns` exists. **Fix:** chain install + pull into a **single inline command** (`if … fi; syns pull --if-repo`) so they run sequentially in one shell. (This is the one place we can't keep Claude's two-entry shape; the command stays inline — no wrapper script.)

4. **`SessionStart` matcher.** Codex matcher values: `startup`, `resume`, `clear`, `compact`. Use **`startup|resume`** (pull at the start of real sessions; avoid `clear`/`compact`, which are mid-session and could clobber the working tree).

5. **Trust review (no Claude analog).** Plugin-bundled hooks are non-managed; Codex **skips them until the user reviews and trusts** them via `/hooks` (or `--dangerously-bypass-hook-trust` for one-off). Documented in the README.

6. **`Stop` output contract — handled minimally, NOT wrapped.** See §3 verification below: the raw Claude-style command is safe. We keep it as a one-line inline command (matching Claude), changing only the default message and adding a `>/dev/null` on stdout to silence the success banner.

7. **stdout → "developer context" on SessionStart.** See §4. The installer is the only noisy stdout source; we suppress it inline in the SessionStart command.

8. **Default commit message** → `codex cli session`.

9. **`timeout` units = seconds** (default 600). Leave default.

10. **`PLUGIN_ROOT` env var.** Codex exports `PLUGIN_ROOT`/`PLUGIN_DATA` to plugin hooks for referencing bundled files. Not used here — both hooks are inline and reference no plugin files — but available if a future hook needs a bundled script or data dir.

### Pre-existing caveat to mirror, not fix
**PATH after first-run install.** `install.sh` edits the shell rc, not the current process env, so a freshly installed `syns` is not on PATH within the same session — the first session's pull silently no-ops and the binary becomes usable from the *next* session. The Claude plugin has this exact behavior. Mirror it; note it in the README.

---

## 3. The `Stop` hook is safe as-is — verification (your request #1)

**Question:** can we keep the raw Claude-style Stop hook (no continuation-control wrapper, and let it exit non-zero on real push failures)?

**Answer: yes, it's safe.** The only Codex behavior to avoid is an unintended *turn continuation*, which Codex triggers **only** on `Stop` `exit 2` or `decision:"block"`. So the whole safety question reduces to: *can `syns push --if-repo -m "…"` ever exit `2`?*

`syns push` exit codes (CLI_IA.md § `syns push` → Failure matrix):

| Condition | Exit |
|---|---|
| success (commit created, or nothing changed) | `0` |
| no repo identity resolves (the hook-in-a-non-Syns-dir case) | `0` **because `--if-repo` converts the identity-failure → silent skip** |
| empty local collection (everything excluded) | `6` |
| network failure / `--strict` partial | `3` |
| auth / api / io / config (invalid flag value) | `1` |
| repo-identity failure **without `--if-repo`** | `2` ← **the only exit-2 path, and `--if-repo` removes it** |

Our invocation passes only `--if-repo` and `-m <string>` — both always-valid — so no clap usage error is reachable either. **Conclusion: `syns push --if-repo -m "…"` cannot return exit `2`.** Therefore:

- **No continuation loop is possible.** ✓
- **Real failures (network=3, auth/api=1, push-empty=6) exit non-zero** → Codex surfaces a hook error and the turn ends normally. This is exactly the behavior you asked for: a genuine push problem is visible, not swallowed.
- **No-repo / non-Syns directory** → exit `0`, silent. ✓

**One cosmetic detail.** On a *successful* in-repo push, non-JSON `syns push` prints a success banner to **stdout**. Codex's `Stop` event wants "JSON-or-empty on exit 0"; a plain-text banner triggers a harmless per-turn "invalid Stop output" notice (not a loop). A single `>/dev/null` on stdout removes that with **zero** change to exit-code behavior. We keep `stderr` intact so real error/warning text stays visible.

So the Stop hook stays a one-line inline command, just like Claude:
```
syns push --if-repo -m "${SYNS_PUSH_MESSAGE:-codex cli session}" >/dev/null
```
(If you'd rather be byte-for-byte identical to Claude, drop the `>/dev/null`; the only consequence is the cosmetic per-push notice. No wrapper script, no `{"continue":true}` — your call was right.)

---

## 4. "Developer context" and why we suppress it on SessionStart (your request #2)

**What it is.** A model conversation has roles: *system*, *developer*, *user*, *assistant*. The **developer** role carries tooling/harness instructions that sit above the user's prompt — effectively a secondary system prompt the model reads as authoritative context. When a `SessionStart` (or `UserPromptSubmit`) hook prints **plain text to stdout**, Codex injects that text into the conversation **as a developer-role message** ("Plain text on stdout is added as extra developer context"; the structured equivalent is `hookSpecificOutput.additionalContext`). The model then "sees" it at the top of the session.

**Why suppress it here.** Our SessionStart command does two things whose output is irrelevant — even harmful — as model context:
- The **installer** (`curl … | sh`) can dump verbose install logs to stdout. Injecting that as developer context is pure noise and a (low) prompt-injection surface.
- `syns pull` prints a summary like `Pulled bartsoj/syns: 0 downloaded, 1519 unchanged, 0 deleted`. Per CLI_IA.md the pull summary goes to **stderr** and its **stdout is empty in non-JSON mode** — so *pull itself doesn't pollute context*. The installer is the only real stdout polluter.

Pulling is an infrastructure side effect; the model should not reason about download counts or installer output. So we keep developer context clean.

**How to suppress.** Two mechanisms exist:
- **Redirect stdout** in the command (`… >/dev/null`). Deterministic and robust. ← we use this for the installer.
- Return JSON with `suppressOutput: true` — **unreliable**: the docs say `suppressOutput` is "parsed today but not yet implemented," so it currently does nothing. Don't depend on it.

Because pull's stdout is already empty, suppressing the installer's stdout is sufficient to guarantee no developer context is injected. (Optional: redirect the installer to `${PLUGIN_DATA}/install.log` instead of `/dev/null` to keep Codex clean while preserving a debug trail.)

---

## 5. Target repo layout

```
syns-codex-plugins/
  .agents/plugins/marketplace.json         # Codex-native marketplace catalog
  plugins/syns/
    .codex-plugin/plugin.json              # Codex plugin manifest (complete)
    hooks/hooks.json                        # the two hooks (both inline)
    README.md
  README.md
  CHANGELOG.md
  LICENSE                                   # MIT, copy from claude repo
  .gitignore                                # copy from claude repo
```

No wrapper scripts. Both hooks are one-line inline commands in `hooks.json`, matching the Claude plugin's "just hooks.json" shape. The only Codex-forced change is joining Claude's two `SessionStart` entries into one chained command (Codex runs group entries concurrently, so they can't stay split).

---

## 6. Concrete file contents

### `plugins/syns/hooks/hooks.json`
```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|resume",
        "hooks": [
          {
            "type": "command",
            "command": "if ! command -v syns >/dev/null 2>&1; then curl -fsSL https://install.syns.dev/install.sh | sh >/dev/null 2>&1 || true; fi; syns pull --if-repo",
            "statusMessage": "Syns: pulling repository"
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "syns push --if-repo -m \"${SYNS_PUSH_MESSAGE:-codex cli session}\" >/dev/null",
            "statusMessage": "Syns: pushing session"
          }
        ]
      }
    ]
  }
}
```

The `SessionStart` command is the inline equivalent of Claude's two-step bootstrap,
chained into one command:
- `if ! command -v syns …; then curl … | sh …; fi` installs the CLI on first run (installer
  stdout suppressed so it isn't injected as Codex "developer context").
- `; syns pull --if-repo` then pulls. Codex runs the command string through a shell, so
  `if/then/fi`, the pipe, and the redirect work directly — no `sh -c` wrapper needed. `syns pull`
  writes its summary to stderr and keeps non-JSON stdout empty, so its real errors stay visible
  without polluting context. The body has no single/double quotes, so it inlines into JSON with
  zero escaping.

### `plugins/syns/.codex-plugin/plugin.json` (complete manifest)
```json
{
  "name": "syns",
  "version": "0.1.0",
  "description": "Auto-pull on Codex session start and auto-push on every turn-stop, scoped to directories containing a .syns.yaml.",
  "author": {
    "name": "Bartosz Sojka",
    "email": "bartsoj@gmail.com",
    "url": "https://syns.dev"
  },
  "homepage": "https://syns.dev",
  "repository": "https://github.com/synsdev/syns-codex-plugins",
  "license": "MIT",
  "keywords": ["syns", "version-control", "multi-agent", "automation", "hooks", "auto-commit"],
  "hooks": "./hooks/hooks.json",
  "interface": {
    "displayName": "Syns",
    "shortDescription": "Auto-pull on start, auto-push on every turn.",
    "longDescription": "Pulls a Syns repository when a Codex session starts and pushes the working tree as one commit on every turn-stop. Silent no-op outside a Syns repo (a directory with a .syns.yaml). Installs the syns CLI on first run if it is missing. Set SYNS_PUSH_MESSAGE to customize the commit message.",
    "developerName": "Syns",
    "category": "Productivity",
    "capabilities": ["Read", "Write"],
    "websiteURL": "https://syns.dev",
    "brandColor": "#5e6ad2",
    "composerIcon": "./assets/icon.png",
    "logo": "./assets/logo.png"
  }
}
```

Sources for the metadata: `author`/`homepage`/`license`/`keywords` from the existing
Claude `plugin.json`; `brandColor` `#5e6ad2` is **Brand Indigo** from DESIGN.md § 2
("Brand & Accent"); `repository` is the new sibling repo.

Notes / TODO before publishing:
- `hooks` is optional (Codex auto-detects `hooks/hooks.json`); kept for explicitness.
- `composerIcon`/`logo` require real files under `plugins/syns/assets/` — **add the assets or drop these two keys** (don't ship dangling paths).
- `privacyPolicyURL`/`termsOfServiceURL` deliberately omitted — add only if those pages exist on syns.dev; don't ship 404s.
- `defaultPrompt` omitted on purpose: this plugin ships **no skills**, only lifecycle hooks, so starter prompts are meaningless here.
- `category: "Productivity"` is the value documented in the Codex examples (the Claude marketplace's `"version-control"` is Claude's taxonomy, not Codex's). Switch if Codex documents a better-fitting category.

### `.agents/plugins/marketplace.json` (complete)
```json
{
  "name": "syns-codex-plugins",
  "interface": {
    "displayName": "Syns Codex Plugins"
  },
  "plugins": [
    {
      "name": "syns",
      "source": {
        "source": "local",
        "path": "./plugins/syns"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

`source.path` is resolved relative to the marketplace root (the cloned repo root), so the
same local entry works for git distribution: `codex plugin marketplace add synsdev/syns-codex-plugins`
clones the repo and resolves `./plugins/syns` inside it — mirroring the Claude install flow.

If instead you publish this plugin through a *separate aggregator* marketplace, use the
Git-subdir source form there:
```json
{
  "name": "syns",
  "source": {
    "source": "git-subdir",
    "url": "https://github.com/synsdev/syns-codex-plugins.git",
    "path": "./plugins/syns",
    "ref": "main"
  },
  "policy": { "installation": "AVAILABLE", "authentication": "ON_INSTALL" },
  "category": "Productivity"
}
```

The marketplace entry sticks to Codex's documented fields (`name`, `source`, `policy`,
`category`); all presentation metadata (descriptions, icon, brand color) lives in the
plugin manifest's `interface` object, which is where Codex reads it.

---

## 7. Install & usage (for the README)

```bash
codex plugin marketplace add synsdev/syns-codex-plugins
# enable the `syns` plugin from the plugin directory, then restart Codex
```
- **Trust the hooks:** run `/hooks` in Codex to review and trust the plugin's
  `SessionStart`/`Stop` hooks — Codex skips untrusted plugin hooks. (One-off bypass:
  `--dangerously-bypass-hook-trust`.)
- Customize the commit message via `SYNS_PUSH_MESSAGE` (default `codex cli session`).
- Disable all hooks globally with `[features] hooks = false` in `config.toml`.

---

## 8. Verification checklist (after building)

1. **Outside a Syns repo:** start Codex, run a turn, stop → no commits, no errors, no
   stray developer-context text from SessionStart.
2. **Inside a Syns repo (`.syns.yaml` present):** session start pulls; each turn-stop
   produces exactly one commit on the server; empty turn → no commit; **no per-turn
   "invalid Stop output" notice** (confirms the `>/dev/null` works).
3. **Stop never loops, real errors surface:** force a push failure (e.g., bad `SYNS_URL`/offline)
   → turn still ends cleanly (no runaway continuation, since push can't exit 2) **and** Codex
   shows the push error.
4. **Trust gate:** confirm hooks are listed and require trust in `/hooks` on first run.
5. **First-run install:** on a machine without `syns`, SessionStart installs it; confirm the
   documented "usable next session" PATH behavior.
6. Windows: out of scope for v0.1.0, same as the Claude plugin.

---

## 9. Open decisions for Bart

- **Repo name/location:** assumed `syns-codex-plugins` as a sibling of `syns-claude-plugins`
  under `github.com/synsdev/`. Confirm.
- **Stop `>/dev/null`:** kept (silences the cosmetic per-push notice; no behavioral change).
  Drop it for a byte-for-byte Claude clone.
- **SessionStart matcher:** `startup|resume` proposed. Add `clear`/`compact` only if you want
  a pull on mid-session resets (not recommended — clobber risk).
- **Assets / category:** add `assets/icon.png` + `assets/logo.png` (or drop those manifest
  keys); confirm `category`.
- **Separate repo vs combined:** Codex reads legacy `.claude-plugin/marketplace.json`, but the
  manifest dir (`.codex-plugin/` vs `.claude-plugin/`) and the Stop nuance differ, so a
  **separate repo is cleaner**. Recommend separate.
