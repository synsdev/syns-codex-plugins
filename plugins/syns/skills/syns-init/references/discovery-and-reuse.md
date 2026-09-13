# Discovering the work, history, and existing Syns repositories

The proposal should fit what the person or team is organizing/building, not just the Markdown already present. Use the evidence planes that exist before selecting a structure:

1. **Current project** — checked-out code, manifests, schemas, tests, entry points, instructions, specs, work records, and Markdown.
2. **Bounded Git history, when the source is a Git worktree** — why files changed together, recurring work areas, historical decision language, contributors, and repository relationships. A personal folder with no Git history is not deficient; record this plane as unavailable.
3. **Accessible Syns repositories** — structures or knowledge packages the authenticated user already owns or can read, including personal starters and team-accessible repositories returned by `syns repos`.

Run:

```bash
python3 "$SYNS_INIT_SKILL_ROOT/scripts/discover_context.py" <source-root> --output <run>/context-discovery.json
```

This command is read-only. It never starts login. If the user is not authenticated, record Syns discovery as unavailable and continue; lack of authentication must not block local proposal/review. For bundled synthetic fixtures, pass `--without-syns` unless accessible-repository behavior is the explicit subject of that fixture; private account metadata is not test input.

## Current work or personal-life model

Infer a provisional work model from corroborated evidence:

- **What is being built or organized:** for code/team work, product/service/runtime/modules/interfaces; for personal work, the requested life domains, record types, privacy boundaries and desired repository boundary.
- **What repeatedly changes:** Git co-change evidence where present; otherwise existing folders, timestamps and the person's stated workflow, without inventing history.
- **How work is organized:** issues/projects/specifications, or personal notes/tasks/goals/habits/training/food/travel/people, or a neutral shape.
- **Where durable intent currently lives:** current docs/native stores/source, personal app exports/files, or nowhere explicit.
- **Who appears involved:** contributors/CODEOWNERS where relevant, or the owner and explicitly named collaborators/household members. Never infer a participant from file authorship alone.
- **Repository topology:** remotes and submodules plus explicit links. Strip credentials from remote URLs.

Current checked-out files own current behavior. Commit subjects, deleted files, and author lists are historical evidence. Never turn a commit message into a current business rule without corroboration or a human answer. Read no more history than needed; the helper caps its output at 200 commits.

## Existing Syns repositories

`syns repos --limit 100 --offset … --json` lists repositories accessible to the authenticated caller, including owned, collaborator, and team-granted access. Treat metadata as a shortlist only.

Rank candidates using explicit evidence:

- exact `.syns.yaml` identity or links in current files;
- same Git remote/project identifier recorded in repository metadata or content;
- matching entities, lifecycle, native root, and information questions;
- overlap between current file names/concepts and the candidate's declared structure/read order;
- recency and status only as secondary signals.

For the strongest few candidates, pull into `<run>/candidates/<catalog-id>/` (or a collision-safe owner-name slug for a repository outside the catalog) and inspect their `README.md`, `STRUCTURE.md`, agent entry points, native roots, and representative records. Pulling into the private run is read-only with respect to the project and remote. Never merge candidates into each other during discovery.

Private repositories and their metadata stay in the private review artifact. Do not send them to a public search service or disclose them in public fixture output.

## Proposal outcomes

Record exactly one outcome per relevant existing Syns repository:

- **join** — it is already the canonical repository for this project; switch to JOIN rather than building another.
- **extend** — it is canonical and the proposal adds missing modules/files without replacing its authority.
- **derive** — its structure is a useful starting point, but this project needs a separate repository with provenance.
- **link** — it owns a neighboring domain; keep access boundaries and cross-link rather than copy facts.
- **consolidate** — two repositories claim the same domain. This is never automatic: show duplicate/contradictory ownership and ask which repository remains authoritative.
- **ignore** — superficial match or incompatible access/lifecycle; include the reason.

“Merge” is not a default operation. It risks combining different collaborators, visibility, lifecycles, and fact owners. The proposal may recommend consolidation, but actual cross-repository moves require a complete source → destination manifest, access check, backup, reversal plan, and a separate approval.

## Structure review additions

The Gate A page must show:

- provisional understanding of what the person or team is organizing/building and the evidence behind it;
- bounded history inspected and interpretation limits;
- accessible Syns repositories considered, with sensitive details kept local;
- join/extend/derive/link/consolidate/ignore decision and reason for each relevant candidate;
- which facts remain owned elsewhere;
- whether the proposal adds knowledge, changes routing, or only changes organization.

If this evidence changes the proposed paths, evaluation tasks, or authority mapping, it is part of the digest-bound proposal. If discovery changes after Gate A, invalidate approval and render again.
