// Tests for the one-line hooks in hooks.json. Each hook runs through the real
// shells present on the machine against a stand-in `syns` that answers with a
// chosen exit code and output, the way `syns pull` and `syns sync` answer.
//
//   node --test "test/*.test.mjs"

import assert from "node:assert/strict";
import { spawnSync } from "node:child_process";
import { chmodSync, existsSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import test from "node:test";

const HOST = {
  hooksFile: "../plugins/syns/hooks/hooks.json",
  start: "SessionStart",
  finish: "Stop",
  integration: "codex",
  // the variable the host exports with the session id; null where it arrives on stdin alone
  sessionEnv: null,
  // "stderr": a failure exits 1 with the CLI's line on stderr; "json": exits 0 with a systemMessage
  failures: "json",
  // whether the start hook writes the agent's defaults to CLAUDE_ENV_FILE
  envFile: false,
};

const hooks = JSON.parse(readFileSync(new URL(HOST.hooksFile, import.meta.url), "utf8")).hooks;
const START = hooks[HOST.start][0].hooks[0].command;
const FINISH = hooks[HOST.finish][0].hooks[0].command;
const SHELLS = ["/bin/sh", "/bin/bash", "/bin/zsh"].filter((shell) => existsSync(shell));

const INSTRUCTION = [
  "The repository alice/proj advanced while this working copy held local work. Your local work is preserved: nothing was published and nothing was discarded.",
  "",
  "Recovery id: rec-1",
  "3. In every collision path delete each marker block's `<<<<<<< local` lines — keep \"both\" sides",
  "",
  "Publish it with: syns resolution continue — continuing is what publishes; nothing is published until it runs.",
].join("\n");

const SILENT = { code: 0, stdout: "", stderr: "" };

function sandbox() {
  const root = mkdtempSync(join(tmpdir(), "syns-hooks-"));
  const withCli = join(root, "bin");
  const withoutCli = join(root, "bare");
  const script = (dir, name, lines) => {
    mkdirSync(dir, { recursive: true });
    writeFileSync(join(dir, name), ["#!/bin/sh", ...lines, ""].join("\n"));
    chmodSync(join(dir, name), 0o755);
  };
  script(withCli, "syns", [
    `printf 'args=%s\\nintegration=%s\\nrun=%s\\ntrigger=%s\\n' "$*" "$SYNS_INTEGRATION" "$SYNS_RUN" "$SYNS_TRIGGER" > '${root}/call'`,
    `cat '${root}/stdout'`,
    `cat '${root}/stderr' >&2`,
    `exit "$(cat '${root}/code')"`,
  ]);
  // a start hook with no CLI must never reach the real installer
  for (const dir of [withCli, withoutCli]) script(dir, "curl", ["exit 1"]);

  return {
    root,
    answer(code, stdout = "", stderr = "") {
      writeFileSync(join(root, "code"), String(code));
      writeFileSync(join(root, "stdout"), stdout);
      writeFileSync(join(root, "stderr"), stderr);
    },
    call() {
      return Object.fromEntries(readFileSync(join(root, "call"), "utf8").trim().split("\n").map((line) => {
        const at = line.indexOf("=");
        return [line.slice(0, at), line.slice(at + 1)];
      }));
    },
    run(command, { shell, env = {}, cli = true }) {
      const base = { PATH: `${cli ? withCli : withoutCli}:/usr/bin:/bin`, HOME: root };
      if (HOST.sessionEnv) base[HOST.sessionEnv] = "sess-1";
      const result = spawnSync(shell, ["-c", command], {
        cwd: root,
        input: JSON.stringify({ session_id: "sess-1", cwd: root, hook_event_name: "hook" }),
        env: { ...base, ...env },
        encoding: "utf8",
      });
      return { code: result.status, stdout: result.stdout, stderr: result.stderr };
    },
  };
}

/** The report a failure leaves for the person, asserting it does not continue the agent. */
function reportedWithoutContinuing(result) {
  if (HOST.failures === "stderr") {
    assert.equal(result.code, 1, result.stderr);
    assert.equal(result.stdout, "");
    return result.stderr.trim();
  }
  assert.equal(result.code, 0, result.stderr);
  assert.equal(result.stderr, "");
  const reply = JSON.parse(result.stdout);
  assert.deepEqual(Object.keys(reply), ["systemMessage"]);
  return reply.systemMessage;
}

for (const shell of SHELLS) {
  const name = (text) => `${text} (${shell})`;

  test(name("a finish that lands writes nothing to either stream and exits 0"), () => {
    const box = sandbox();
    box.answer(0, "Synced alice/proj: published 1a2b3c4d (version 2)\n", "  downloaded: notes.md\n");
    assert.deepEqual(box.run(FINISH, { shell }), SILENT);
    assert.equal(box.call().args, "sync --if-repo");
    box.answer(0, "No changes — alice/proj is up to date\n");
    assert.deepEqual(box.run(FINISH, { shell }), SILENT);
    box.answer(0); // the no-repository skip
    assert.deepEqual(box.run(FINISH, { shell }), SILENT);
  });

  test(name("a start that lands or skips writes nothing to either stream and exits 0"), () => {
    const box = sandbox();
    box.answer(0, "Pulled alice/proj: 1 downloaded, 2 unchanged, 0 deleted\n", "  downloaded: notes.md\n");
    assert.deepEqual(box.run(START, { shell }), SILENT);
    assert.equal(box.call().args, "pull --if-repo");
    box.answer(0);
    assert.deepEqual(box.run(START, { shell }), SILENT);
  });

  test(name("resolution required at finish continues the agent with the CLI's instruction"), () => {
    const box = sandbox();
    box.answer(4, `${INSTRUCTION}\n`, "error: resolution required for alice/proj (recovery id rec-1)\n");
    const result = box.run(FINISH, { shell });
    assert.equal(result.code, 2);
    assert.equal(result.stdout, "");
    assert.ok(result.stderr.includes(INSTRUCTION), result.stderr);
  });

  test(name("a resolution pending at start is handed to the agent before new work"), () => {
    const box = sandbox();
    box.answer(4, `${INSTRUCTION}\n`, "error: resolution required for alice/proj (recovery id rec-1)\n");
    const result = box.run(START, { shell });
    assert.equal(result.code, 0);
    assert.equal(result.stderr, "");
    assert.ok(result.stdout.startsWith("A Syns resolution is pending in this folder. Finish it before new work.\n\n"), result.stdout);
    assert.ok(result.stdout.includes(INSTRUCTION), result.stdout);
  });

  test(name("each failure is reported to the person and never continues the agent"), () => {
    const box = sandbox();
    const failures = {
      credential: [1, "error: authentication required — run 'syns login' first"],
      retryable: [3, "error: could not reach server at http://127.0.0.1:8099/api/v1/repos/alice/proj/tree"],
      validation: [1, "error: server error (422): validation_error"],
      attention: [5, "error: attention required for alice/proj: the repository kept moving past every continuation round"],
    };
    const reports = {};
    for (const [kind, [code, line]] of Object.entries(failures)) {
      box.answer(code, "", `${line}\n`);
      reports[kind] = reportedWithoutContinuing(box.run(FINISH, { shell }));
      if (HOST.failures === "stderr") assert.equal(reports[kind], line);
    }
    box.answer(3, "", `${failures.retryable[1]}\n`);
    reportedWithoutContinuing(box.run(START, { shell }));

    if (HOST.failures === "stderr") {
      assert.equal(new Set(Object.values(reports)).size, 4);
    } else {
      // an exit code alone cannot tell a credential refusal from a validation one
      assert.equal(reports.credential, reports.validation);
      assert.equal(new Set([reports.credential, reports.retryable, reports.attention]).size, 3);
    }
  });

  test(name("each run carries the host's provenance defaults"), () => {
    const box = sandbox();
    box.answer(0);
    box.run(START, { shell });
    assert.deepEqual(box.call(), { args: "pull --if-repo", integration: HOST.integration, run: "sess-1", trigger: "start" });
    box.run(FINISH, { shell });
    assert.deepEqual(box.call(), { args: "sync --if-repo", integration: HOST.integration, run: "sess-1", trigger: "finish" });
  });

  test(name("provenance the person set in the environment wins over the defaults"), () => {
    const box = sandbox();
    const env = { SYNS_INTEGRATION: "my-rig", SYNS_RUN: "nightly-7", SYNS_TRIGGER: "cron" };
    for (const [command, args] of [[START, "pull --if-repo"], [FINISH, "sync --if-repo"]]) {
      box.answer(0);
      box.run(command, { shell, env });
      assert.deepEqual(box.call(), { args, integration: "my-rig", run: "nightly-7", trigger: "cron" });
    }
  });

  test(name("without the CLI both hooks stay silent"), () => {
    const box = sandbox();
    assert.deepEqual(box.run(START, { shell, cli: false }), SILENT);
    assert.deepEqual(box.run(FINISH, { shell, cli: false }), SILENT);
  });

  if (HOST.envFile) {
    test(name("start gives the agent's own shell the same defaults, and the person's values still win"), () => {
      const box = sandbox();
      const envFile = join(box.root, "claude-env");
      box.answer(0);
      assert.deepEqual(box.run(START, { shell, env: { CLAUDE_ENV_FILE: envFile } }), SILENT);
      const read = (env) => spawnSync(shell, ["-c", `. '${envFile}'; printf '%s %s %s' "$SYNS_INTEGRATION" "$SYNS_RUN" "$SYNS_TRIGGER"`], {
        env: { PATH: "/usr/bin:/bin", ...env },
        encoding: "utf8",
      }).stdout;
      assert.equal(read({}), "claude-code sess-1 agent");
      assert.equal(read({ SYNS_TRIGGER: "manual", SYNS_INTEGRATION: "my-rig" }), "my-rig sess-1 manual");
    });
  }
}
