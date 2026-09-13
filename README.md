# syns-codex-plugins

A [Codex CLI](https://developers.openai.com/codex) plugin marketplace for
the [Syns](https://syns.dev) multi-agent development platform.

This is the Codex port of [`syns-claude-plugins`](https://github.com/synsdev/syns-claude-plugins) —
same behavior, adapted to Codex's hook contract.

## What's in here

| Plugin                                   | Description                                                                                 |
|:-----------------------------------------|:--------------------------------------------------------------------------------------------|
| [`syns`](./plugins/syns)                 | `syns-init` builds or joins an agent-readable repository; lifecycle hooks pull on start and sync on Stop. |
| [`plan-sharing`](./plugins/plan-sharing) | Captures the Plan Mode plan into the current Syns repo and warns when it overlaps another agent's plan. |

## Install

```bash
codex plugin marketplace add synsdev/syns-codex-plugins
```

Then enable the `syns` plugin from the plugin directory and restart Codex. Codex
skips plugin-bundled hooks until you trust them. Run `/hooks` to review and trust
the plugin's `SessionStart` and `Stop` hooks, and do it again after an update that
changes them. The `syns` plugin needs the Syns CLI 0.3.0 or newer. See the
[plugin README](./plugins/syns) for the full behavior contract.

## Development

```bash
node --test "test/*.test.mjs"
```

The tests run each hook line from `plugins/syns/hooks/hooks.json` through every POSIX shell on the machine against a stand-in `syns`.

## License

MIT. See [LICENSE](./LICENSE).
