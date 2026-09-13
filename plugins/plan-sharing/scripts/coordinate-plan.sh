#!/usr/bin/env bash
# Stop hook: when a Codex Plan Mode turn proposes a plan, save it into the
# current Syns repo's plans/ folder; if other agents have plans there, ask the
# agent to check for conflicts before implementing. No-op outside a Syns repo or
# when no <proposed_plan> was produced. Fails open and silent (Stop needs
# JSON-or-empty on stdout).
set -uo pipefail

command -v syns >/dev/null 2>&1 || exit 0
command -v jq   >/dev/null 2>&1 || exit 0

INPUT="$(cat)"
MSG="$(jq -r '.last_assistant_message // empty' <<<"$INPUT")"
CWD="$(jq -r '.cwd // empty'                     <<<"$INPUT")"
SESSION="$(jq -r '.session_id // empty'          <<<"$INPUT")"
ACTIVE="$(jq -r '.stop_hook_active // false'     <<<"$INPUT")"
TXPATH="$(jq -r '.transcript_path // empty'      <<<"$INPUT")"
[ -n "$CWD" ] || CWD="$PWD"
[ -n "$SESSION" ] || SESSION="nosession"

# Pull a <proposed_plan>…</proposed_plan> block out of text on stdin.
extract() { awk '/<proposed_plan>/{f=1;next} /<\/proposed_plan>/{f=0} f'; }

PLAN="$(printf '%s\n' "$MSG" | extract)"
# In Plan Mode last_assistant_message is usually null; recover from the transcript.
if [ -z "$PLAN" ] && [ -f "$TXPATH" ]; then
  PLAN="$(jq -rs '[.[] | .. | objects | select(.type? == "output_text") | .text? // empty] | last // empty' "$TXPATH" 2>/dev/null | extract)"
fi
[ -n "$PLAN" ] || exit 0

# Must be inside a Syns repo; resolve its root (so plans land in one place).
ROOT="$(cd "$CWD" 2>/dev/null && pwd)" || exit 0
while [ "$ROOT" != "/" ] && [ ! -f "$ROOT/.syns.yaml" ]; do ROOT="$(dirname "$ROOT")"; done
[ -f "$ROOT/.syns.yaml" ] || exit 0
cd "$ROOT" || exit 0

SLUG="$(printf '%s' "$SESSION" | tr '[:upper:]' '[:lower:]' \
        | sed -E 's#[^a-z0-9._-]+#-#g; s#^-+##; s#-+$##' | cut -c1-80)"
[ -n "$SLUG" ] || SLUG="session"
REL="plans/codex-${SLUG}.md"

save() { mkdir -p plans && printf '%s\n' "$PLAN" >"$REL"; }

# pull (before) -> write -> push (after), retrying once on a head-mismatch.
syns pull --if-repo >/dev/null 2>&1 || true
save || exit 0
if ! syns push --if-repo -m "plan: codex ${SLUG}" >/dev/null 2>&1; then
  syns pull --if-repo >/dev/null 2>&1 || true
  save
  syns push --if-repo -m "plan: codex ${SLUG}" >/dev/null 2>&1 || true
fi

# List peer plans (filenames only — keep the user-facing message clean).
PEERS=""; count=0
while IFS= read -r f; do
  [ "$f" = "$REL" ] && continue
  PEERS="${PEERS}
- $(basename "$f")"
  count=$((count + 1))
done < <(find plans -maxdepth 1 -type f -name '*.md' 2>/dev/null)
[ "$count" -gt 0 ] || exit 0          # no peers -> nothing to warn about
[ "$ACTIVE" = "true" ] && exit 0      # already a continuation -> warn only once

jq -n --arg r "Other agents have active plans in this repo's plans/ folder:${PEERS}

Before exiting Plan Mode, read those files and check your plan does not edit the same files, duplicate work, or contradict them. If it conflicts, revise your plan or report the conflict to the user; otherwise proceed." \
  '{decision:"block",reason:$r}'
