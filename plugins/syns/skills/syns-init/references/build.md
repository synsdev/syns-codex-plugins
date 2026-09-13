# Building a proposed wiki

## Safety boundary

Before the structure review is approved:

- read the source;
- write only inside a private run directory;
- do not change the source project;
- do not create a Syns repository;
- do not edit project instruction files or install hooks.

Use `${TMPDIR:-/tmp}/syns-init/<run-id>/` and set it to mode `0700`. Keep:

```text
run/
  source-snapshot/       immutable snapshot of the original markdown package
  evidence.json          claims and their sources
  context-discovery.json bounded Git history and accessible Syns repository metadata
  proposal.json          exact proposed tree and mappings
  questions.json         questions asked and answers received
  evaluation.json        sealed tasks, rubric, limits, and thresholds
  stage/                 materialized only after structure approval
  reviews/
    structure-review.html
    evaluation-review.html
  approvals/
```

Hash the source snapshot, proposal, evaluation plan, and later the stage. An approval applies only to those bytes. If they change, ask again.

## Source inventory

Exclude dependency, cache, generated, credential, and binary trees unless the user explicitly made one the subject. At minimum exclude `.git`, `node_modules`, `dist`, `build`, `target`, `.next`, `.nuxt`, `.venv`, `.tox`, `.cache`, credentials, and dotenv values.

Inventory before interpretation:

- all markdown and text instruction files;
- `AGENTS.md`, `CLAUDE.md`, memory files, process files, skills, specifications, plans, tickets, decisions, and indexes;
- native `openspec/`, `.specify/`, and `specs/NNN-*` roots;
- code manifests, module roots, schemas, tests, and operational entry points;
- symlinks and their resolved targets;
- existing `.syns.yaml` identities and whether more than one is in scope;
- bounded Git history: current root/head, credential-redacted remotes, submodules, authors, recent commit subjects, and frequently changed paths;
- already accessible Syns repositories, when `syns whoami --json` succeeds without starting authentication.

For every existing markdown file record:

- path and digest;
- the one question it currently answers, if any;
- apparent authority and readers;
- links/references that make it reachable;
- overlaps, contradictions, staleness signals, or orphan state;
- proposed disposition: keep, map, archive, or omit.

Do not turn an inference into a fact. Label evidence as:

- `source` with `path:line` and digest;
- `human` with question ID;
- `inference` with confidence and basis;
- `unknown`.

## Targeted mining

Read bodies after inventory, in narrowing passes:

1. Agent entry files and their referenced read order.
2. Existing markdown with high inbound references or obvious authority.
3. Native configuration and schema files.
4. Manifests, module roots, schemas, code entry points, and tests that reveal what is being built.
5. Bounded Git commits around relevant files to recover historical rationale and co-change patterns.
6. Source lines needed to verify claims the wiki may state.
7. Tests and issue/spec artifacts needed to distinguish behavior from intent.
8. Privately pulled representative files from the strongest accessible Syns repository candidates.

Every statement about source behavior carries `path:line`. Human-approved business intent cites the answer that established it. Historical files and commit subjects remain historical; do not silently promote them to current authority. Repository metadata is a discovery clue, not proof that two repositories should be merged.

## Content questions

Ask no more than three in one block, after mining. A question is eligible only when its answer changes a required file, source-of-truth rule, lifecycle, read order, integration boundary, or approved constraint.

Good forms:

- “These files disagree about who receives a sponsored payout. Which statement is the rule future work must preserve?”
- “`process.md` exists but neither agent entry file points to it. Should project process outrank personal style instructions?”
- “Both OpenSpec and Spec Kit are present. Which one owns current product behavior?”

Do not ask:

- what the code or existing docs already answer;
- whether the user wants pull/push;
- whether the wiki should be public;
- a broad “what is this project?” when manifests and docs answer it;
- implementation preferences unrelated to information ownership.

Blank means unknown. Record it in the private run's `questions.json`; do not fill it with a guess presented as truth. Propose an `OPEN_QUESTIONS.md` only when the selected schema permits that source record and the unknown must remain visible after adoption. Personal category-native schemas forbid extra files unless their composed root contract explicitly adds one.

## Proposed repository

The proposal is a manifest before it is a directory. For every path include:

```yaml
path: constraints/payout-ownership.md
question: "What payout-ownership rule must future work preserve?"
origin: source-required
sources: [Q-001, src/settle.ts:41-48, issues/184-sponsored-gas.md:12-19]
required: true
readers: [engineering-agent, reviewer]
updates_when: "the business rule or payout model changes"
materialization:
  kind: exact-content       # exact-content · copy · exact-patch · empty-directory-slot
  content_sha256: "…"       # and content in the private proposal payload, or source+exact patch
```

Gate A binds exact materialization, not only a section outline. Every `tree` row must carry one
materialization kind (`exact-content`, `copy`, `exact-patch`, or `empty-directory-slot`); every file
kind carries a lowercase 64-hex `content_sha256`. The structure renderer rejects any missing/invalid
kind or digest by default. Every new/adapted document's complete bytes—or an exact source copy/patch
that deterministically produces them—must be inside the private proposal payload and covered by the
proposal digest before review. If wording changes after Gate A,
invalidate approval and render again.

The manifest also records:

- provisional work or personal-life model and its current/history evidence where available;
- selected reference(s) and pinned commit(s), repository-boundary decision, or honest zero-match;
- reason each reference was selected/rejected;
- relevant accessible Syns repositories and their join/extend/derive/link/consolidate/ignore decisions;
- complete old → proposed mapping;
- omitted material and why;
- canonical owners of each fact;
- source/derived status for every path;
- proposed read order;
- one canonical fact owner per domain and every derived in-memory/materialized view;
- unresolved questions and omitted material as separate lists;
- validation checks and expected result;
- exact evaluation tasks and success thresholds.

## Structure review

Render `reviews/structure-review.html` with `scripts/render_structure_review.py`. It is based on `assets/structure-review-template.html`, derived from the Air wiki-structure visual language.

The page shows, conclusion first:

- what is proposed and why;
- what approval permits: **local staging and read-only comparison only**;
- old snapshot and proposal digests;
- detected sources and exclusions;
- what the agent understands the person or team is organizing/building, with available history evidence and limits;
- all relevant accessible Syns repositories considered and whether to join, extend, derive, link, consolidate, or ignore;
- every plausible shelf candidate with selection/composition/rejection reasons; non-matches may be grouped by scope/domain;
- proposed tree, one question per file, source lineage, and exact materialization kind;
- fact owners and source-versus-derived disposition;
- every old file's disposition;
- questions and unknowns, separately from omissions;
- validation checks and expected results;
- evaluation tasks, rubric, limits, and thresholds;
- a form for `approve for staging and evaluation`, `request changes`, or `reject`, plus free text.

Serve it locally through `scripts/review_server.py`, open the localhost URL, and wait for the decision file. If a browser cannot open, give the localhost/file path and stop for the user's review. Do not infer approval from silence.

## Stage after approval

Only an approval matching all Gate A digests permits materialization. Write the exact proposal under `stage/`, then validate:

- paths match the manifest;
- established claims resolve to their evidence;
- links resolve;
- enums and hierarchy are valid;
- generated views are current only where the approved non-personal schema owns materialized derivatives;
- a personal category-native stage has no scripts, tests, generated views/JSON, caches or interface code;
- native roots validate through their original CLI when available;
- the source project hash is unchanged.

The stage is not canonical and is not published.
