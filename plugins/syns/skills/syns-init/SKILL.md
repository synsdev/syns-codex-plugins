---
name: syns-init
description: >
  Sets up, extends, or joins a Syns repository containing the markdown a person's or team's agents need before they work and update as they work. Use when asked to run syns-init, set up Syns for a personal wiki, second brain, codebase or team, turn existing notes/tasks/goals/habits/workouts/food logs/travel plans/contacts/memory/specs/tickets/skills/process docs into a structured agent-readable repository, compare a proposed wiki with current files, reuse or compose pinned category starters, reuse or consolidate an existing Syns repository, or join an existing owner/name repository. Mines current files, relevant code and bounded Git history when present, and accessible Syns repositories before proposing; asks only questions that change information ownership or repository/privacy boundaries; proposes from thirteen pinned references or an existing repository; renders local structure and evaluation review pages; stages and evaluates without touching the source; and adopts, privately publishes, or grants access only after explicit approval.
---

# syns-init

Build the knowledge package before asking the person or team to trust it.

A Syns wiki is a separate, versioned repository of deliberate artifacts: constraints, business reasons, specifications, plans, decisions, work state, operating instructions, skills, and retrospectives. Syns carries and versions the files. It does not infer business intent, enforce invariants, run workflows, inspect code, or prove that an agent followed instructions.

This skill has two routes:

- **JOIN** — pull an existing `owner/name` into an empty local directory and tell the agent what to read.
- **BUILD** — mine existing code and markdown, propose a repository, show it locally, compare it read-only with the current package, and only then adopt/publish what the user approves.

## Non-negotiable behavior

- Treat installation, authentication, pull, and push as implementation details. Do not ask whether to pull or push, and do not introduce Syns vocabulary when the question is about the user's work.
- Ask only for information no available file can establish and whose answer changes the proposed structure or its source of truth. At most three content questions in one block.
- Do not write into the source project, create a remote repository, or edit project instructions before approval.
- Preserve the old package unchanged in a snapshot. Build the proposal in a separate private temporary area.
- Use two local review pages: structure first; matched read-only comparison second.
- Approval to evaluate is not approval to adopt. Approval to adopt is not approval to publish.
- Default publication is private. Public visibility is never part of setup.
- Do not configure lifecycle hooks. Claude Code, Codex, and Pi integrations already own session-start pull and lifecycle-end push when installed.
- Never use `syns push --force`.
- Do not claim realtime synchronization, automatic merge, invariant enforcement, process enforcement, cross-machine dashboards, read heat, repair, or any health capability.

## Resolve the skill root

Set `SYNS_INIT_SKILL_ROOT` to the directory containing this file. All bundled references, scripts, assets, fixtures, and the catalog resolve relative to it.

A hosted invocation may initially fetch only this file. If `references/` and `scripts/` are absent, download the sibling `package/checksums.json`, fetch every listed `package/<path>` into a private temporary directory with redirects enabled (`curl -fsSL`), verify each SHA-256, and set the root there. Cloudflare Pages may redirect `.html` asset URLs to extensionless paths; following the redirect is required. If the package is unavailable or a checksum fails, stop with the failing URL; do not improvise the approval/evaluation protocol from this summary.

## Read as needed

- BUILD source mining, question policy, manifests, structure review, and staging: [references/build.md](references/build.md)
- Project/Git-history understanding and existing Syns repository reuse: [references/discovery-and-reuse.md](references/discovery-and-reuse.md)
- Pinned examples and composition rules: [references/catalog.md](references/catalog.md) and [catalog.json](catalog.json)
- Matched read-only evaluation, blind review, adoption: [references/evaluate.md](references/evaluate.md)
- CLI, private push, harness boundaries, JOIN, second-person demo: [references/publish-and-join.md](references/publish-and-join.md)

Read the referenced file before entering that phase. Do not load all of them when routing to JOIN.

## Output discipline

Keep chat/terminal output short. Show facts, paths, counts, and the local review URL. Do not narrate command execution or print stage banners. The HTML pages carry explanations and choices.

Exceptions that need the user's eyes:

- authentication URL/code;
- one block of content questions;
- structure review URL;
- evaluation review URL;
- an operational ambiguity/failure that cannot be decided from files.

Never hide a failure behind reassuring prose.

## Route before side effects

Check in order:

1. An explicit `owner/name` in the invocation → **JOIN**.
2. Exactly one valid `.syns.yaml` at the declared wiki root → **JOIN** that identity.
3. More than one identity in scope → show paths/identities and ask which repository is intended; do nothing else.
4. Otherwise → **BUILD**.

Do not install the CLI or log in before routing. A public JOIN can work without authentication; BUILD can produce both review pages without Syns credentials.

## JOIN

Read [references/publish-and-join.md](references/publish-and-join.md), then:

1. Resolve an empty destination. Default to `./<repository-name>` unless the user named a path.
2. Refuse to merge into a non-empty destination.
3. Attempt `syns pull <owner>/<name> <destination>` without login.
4. If access to a private repository requires authentication, run the device-login flow and retry once.
5. Verify `.syns.yaml`, `STRUCTURE.md` when present, and the first two or three files in declared read order.
6. Report repository, local path, file count, read order, and whether a lifecycle integration was detected.
7. Stop. Do not redesign a team repository during JOIN.

Only add a marker-delimited adapter to a sibling code project when the user explicitly asks and approves the exact edit.

## BUILD state machine

```text
inventory → mine current files/history/Syns repos → select/reuse/compose → ask → propose → structure review
  → approve evaluation → stage → validate → matched read-only runs
  → blind review/reveal → decision → approve exact adoption/publication
  → adopt locally → optional private push → receipt
```

### 1. Create an immutable run

Create `${TMPDIR:-/tmp}/syns-init/<run-id>/` with mode `0700`. Put snapshots, evidence, manifests, staged files, review pages, and approvals there. Never put secrets in the run.

Snapshot the current markdown/instruction package and record a digest before interpretation. Record a digest of the source project so later checks can prove it was not changed during proposal/evaluation.

Seal evaluation tasks and scoring criteria before materializing the proposal. Prepared fixture tasks are regression evidence, not independent causal proof; say so on the review page.

### 2. Inventory and understand the work

Read [references/build.md](references/build.md) and [references/discovery-and-reuse.md](references/discovery-and-reuse.md).

Inventory all existing markdown, agent entry files, process/memory files, skills, specs, plans, tickets, decisions, native stores, symlinks, and identities. Inspect manifests, module roots, schemas, tests, and operational entry points to understand what the user is building. Then read bodies in a narrowing order: agent entry points → authoritative/referenced markdown → native config → source and tests needed to verify claims.

Use bounded Git history to identify recurring areas, files that change together, historical decision language, contributors, and repository topology. Current files own current behavior; commit subjects are historical evidence, not automatically current truth. Do not infer current team membership or dispatcher count from authors.

If `syns whoami --json` already succeeds, list all accessible repositories with paginated `syns repos --json`. Shortlist likely matches from metadata, then privately pull and inspect only the strongest candidates. Decide whether to join, extend, derive, link, propose consolidation, or ignore each relevant repository. Similar names never authorize a merge. If unauthenticated, record this discovery plane as unavailable and continue without starting login.

For every existing document decide:

- which single question it answers;
- who/what treats it as authoritative;
- how agents reach it;
- whether it overlaps, contradicts, or has gone stale relative to another source;
- keep/map/archive/omit in the proposal.

Every source-behavior claim needs `path:line` plus digest. Human intent points to the answer that established it. Label inference and unknowns.

### 3. Select, reuse, and compose

Read [references/catalog.md](references/catalog.md).

First decide whether an inspected Syns repository is already canonical or provides a closer structure than the public shelf. Prefer extending or linking an existing source of truth over inventing a second owner. Consolidation is a proposal—not an automatic merge—and requires an authority decision plus later move/reversal approval.

Detect Spec Kit/OpenSpec before shape selection. Preserve an existing native store rather than translating it. If both are present and authority is unclear, spend one content question on which owns specification truth.

Compare the work/life model with the relevant compact descriptors and inspected Syns candidates. Use `scope` and `domain` in `catalog.json` to narrow obvious non-matches, but compare every plausible candidate. Adopt at most one branded base for an overlapping domain. Personal category-native starters may be composed when their domains do not overlap, subject to an explicit one-repository-versus-linked-repositories decision; rewrite colliding paths and read order deliberately rather than overlaying trees. Record why every plausible shelf and relevant Syns candidate was selected, composed, reused, linked, consolidated or rejected. An honest zero-match is valid.

Do not describe the shelf as customer-proven. It is Syns-authored and internally checked. Personal
category-native pins are direct-Markdown source trees: reuse their information model and agent rules,
not fake personal content, and never add repository scripts/tests/generated views/JSON merely for a
future interface.

### 4. Ask up to three content questions

Ask them together after mining. Every question names the ambiguity, cites the conflicting/missing sources, and says which proposed file or authority rule its answer changes.

Do not automatically ask “what has an agent got wrong?” if existing files already answer it. Do not ask broad project-description questions files can answer. Blank means unknown, never permission to guess.

Operational approvals, authentication, path choice, repository name, and publication are separate controls and do not consume this budget.

### 5. Propose as data, not files

Before materialization, create an exact proposal manifest containing:

- provisional description of what the person or team is organizing/building, with current-file and bounded-history evidence where history exists;
- selected reference/mode and pinned commit, plus join/extend/derive/link/consolidate/ignore decisions for relevant accessible Syns repositories;
- proposed paths in read order;
- one question, owner, update trigger, readers, origin, and exact materialization (`exact-content`, `copy`, `exact-patch`, or `empty-directory-slot`) per path;
- evidence per established claim;
- complete old → proposed mapping;
- omitted and unresolved material;
- canonical owner for each fact;
- generated versus source-owned files;
- validation checks;
- sealed evaluation protocol and thresholds. Bundled fixture evals may define separate Gate A assertions and matched read-only tasks; do not reuse proposal-selection questions as the A/B tasks.

A proposal that adds approved intent, routing, or canonical skill content is a **repository-package proposal**, not a structure-only rewrite.

### 6. Render structure review and wait

Use the bundled renderer/template to write `reviews/structure-review.html`; serve it on localhost and open it. The page is adapted from the Air wiki-structure tree template and must show the understood work/life model, current/history evidence where available, relevant accessible Syns repositories and reuse decisions, full tree, source lineage, old-to-proposed disposition, every plausible shelf decision, unknowns, validation, and evaluation plan.

Its choices are:

- approve exact proposal for isolated staging and read-only evaluation;
- request changes;
- reject.

The page states that approval permits no project edit and no remote repository. Wait for an approval record matching the snapshot, proposal, catalog, mapping, and evaluation digests. Silence and blank forms approve nothing.

### 7. Materialize and validate the isolated stage

Only after valid structure approval, write the exact proposal under the run's `stage/`. It is private local staging, not the team's wiki.

Validate manifest paths, links, evidence, enums, and native roots with their original CLI where available. Validate materialized generated projections only if the approved non-personal schema genuinely owns them. A personal category-native stage must contain no scripts, tests, generated views/JSON, caches or interface code. Re-hash the source project; any mutation aborts the evaluation.

### 8. Run a matched read-only comparison

Read [references/evaluate.md](references/evaluate.md).

Run fresh agents on the sealed tasks against:

- A: immutable current package;
- B: the same source bytes plus the staged wiki and declared read order.

Use the same model, harness, prompts, limits, tools, working-depth, and network policy. Expose no write/edit tools or mutating commands. Run sequential AB/BA in randomized order; hash before and after. Record time/tokens/tool calls only when the harness genuinely reports them; otherwise `null`.

### 9. Render evaluation review and wait

Write `reviews/evaluation-review.html` with:

1. blind A/B answer scoring;
2. identity reveal with quality, assertions, critical errors, timing coverage, exclusions, and caveats;
3. decision: limited pilot, revise, retain current, or inconclusive.

If limited pilot is chosen, show separate unchecked approvals for:

- local adoption;
- project adapter;
- private Syns publication;
- direct collaborator access and role;
- creating/selecting a team, inviting members, and granting that team repository access.

Bind approval to the stage and exact operation manifest. Evaluation interpretation alone changes nothing.

### 10. Adopt only approved operations

Default adoption places the accepted wiki in a separate directory/sibling checkout and leaves all old files byte-identical. An in-place migration requires an exact move/change/delete manifest, backup, and reversal approval.

A project adapter is separately approved, marker-delimited, and removable. Do not install hooks.

Verify the adopted tree. If validation fails, reverse local operations and preserve the stage/reports.

### 11. Publish privately and hand off only when approved

Read [references/publish-and-join.md](references/publish-and-join.md).

Authenticate now if necessary. Get the owner from `syns whoami`. Check the proposed name. Ensure `.syns.yaml` is absent, then first-push the exact accepted wiki with explicit private visibility. Verify status before adding/pushing provenance.

After the repository exists, offer an operational handoff block: finish without sharing; add named collaborators with `read`, `write`, or `admin`; or create/select a team, invite members, and grant the team repository access. Show exact people/emails, roles, team, and commands, and require explicit approval before mutating access. Do not claim the next person is ready until an existing user was added or an invitation was created. Return the exact `owner/name` sentence the next person gives their agent.

If the push or access operation fails, keep the local wiki and report the partial state. Do not force, silently rename, or claim publication/invitation. Public visibility is a later user action.

### 12. Receipt

Report only:

- current package decision;
- adopted local path, if any;
- private repository URL, if any;
- collaborator/team grants and pending invitations actually created, if any;
- a copyable next-person JOIN sentence using the exact `owner/name`;
- files/read order;
- evaluation result and limitations;
- integration detected and the condition for a teammate to see updates: successful push followed by successful pull;
- structure/evaluation report paths;
- reversal path if local operations were applied.

## Demonstration fixtures

Three internal fixtures test the path without exposing real people or prospects:

- `fixtures/payout-intent/` — an eroded `memory.md`, conflicting old spec/current issue/source behavior, and a human-approved beneficiary-ownership rule. The proposal must distinguish intent from implementation and must not claim enforcement.
- `fixtures/agent-practice/` — divergent skill copies across synthetic laptop/server and Claude/Codex, plus an unreferenced `process.md`. The proposal must centralize project-owned bytes and routing while leaving personal global files untouched; it must not claim fleet visibility or process enforcement.
- `fixtures/personal-composition/` — an empty-history request for one private tasks/goals plus habits/routines repository. The proposal must select both pinned category-native schemas, make the one-repository boundary explicit, map path/schema collisions, keep direct source Markdown, and add no scripts, tests, generated views/JSON, caches or interface code.

Rendered company-fixture labels use Northstar Labs and Relay only. The personal fixture is explicitly synthetic and names no person.

## Never

- Ask whether to pull, push, or install lifecycle hooks.
- Push before structure and evaluation approval.
- Publish publicly during setup.
- Merge JOIN into a non-empty directory.
- Add `.syns.yaml` before a first push.
- Use `syns --version` or `syns push --force`.
- Invent a low-confidence answer and write it as current truth.
- Mix two branded shape-only schemas for the same domain.
- Overlay category trees with colliding paths instead of choosing boundaries and an explicit mapping.
- Add scripts, tests, generated views/JSON, caches or interface code to a personal category-native wiki.
- Modify parser-owned native artifacts with Syns frontmatter.
- Claim a synthetic package comparison proves universal superiority.
- Say real-time, instant, prevents conflicts, enforces invariants/process, or shows which skill version runs across a fleet.
