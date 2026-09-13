# Comparing the current and proposed repository packages

This comparison is a decision aid, not proof that a structure is universally better.

If both conditions contain the same claims and sources and differ only in organization/routing, call it a **structure comparison**. If the proposal adds user-approved intent, canonical skill bytes, new indexes, or new routing—as the bundled demonstrations do—call it a **repository-package comparison**. Do not attribute the result solely to folders.

## Seal tasks before materializing the proposal

Prepare 4–8 read-only tasks for a normal run; use 8–12 for a serious evaluation. Derive them from historical questions, real failure modes, stakeholder-authored questions, and boundary cases. When a bundled fixture defines `matched_read_only_tasks`, use those exact tasks; its separate Gate A assertions grade reference selection/composition and are not A/B prompts. Record prompts, expected evidence, deterministic assertions, prohibited claims, scoring rubric, budgets, and thresholds in `evaluation.json` before writing the stage.

The proposal designer may see task categories and scoring criteria, not holdout answers. For fixture regression tests this separation is imperfect; disclose that prepared fixtures demonstrate the mechanism rather than independently proving causality.

Include a mix of:

- direct lookup;
- cross-document synthesis;
- source-of-truth/authority selection;
- contradiction and stale-document handling;
- absence detection;
- procedure retrieval;
- orientation/read order;
- “where should this update be recorded?”;
- a question the package should refuse to answer.

## Matched read-only runs

Condition A is an immutable copy of the current package. Condition B is the same source bytes plus the staged wiki and its declared read-order instruction. Neither points at the live project.

For every pair keep equal:

- exact model and harness;
- system/task prompts;
- fresh context;
- working-directory depth;
- available read-only tools;
- token, turn, tool-call, and timeout limits;
- network policy, normally off.

Run sequentially in randomized AB/BA order to reduce load and cache bias. Use three repetitions only when cost permits. Capture executor duration if the harness reports it; otherwise store `null`. Never infer tokens or time from answer length.

Read-only means no edit/write tools and no mutating commands. Hash each condition before and after. Any mutation attempt invalidates that run.

If subagents are available, use fresh subagents. Otherwise run fresh non-interactive processes supported by the active harness. Do not run both conditions in the parent session that designed the proposal.

## Results

Save per run:

```json
{
  "task_id": "authority-01",
  "condition": "A",
  "answer": "…",
  "citations": [],
  "duration_ms": null,
  "total_tokens": null,
  "tool_calls": null,
  "pre_hash": "…",
  "post_hash": "…",
  "valid": true,
  "invalid_reason": null
}
```

Grade deterministic assertions separately. Human review is the primary endpoint.

Rubric:

| Dimension | Weight |
| --- | ---: |
| Factual accuracy | 30% |
| Completeness and relevance | 20% |
| Grounding and traceability | 20% |
| Conflict and uncertainty handling | 15% |
| Directness and usability | 15% |

A fabricated fact, invalid citation, unqualified contradiction of authority, or claim that an absent fact was found is a critical error.

Do not combine quality and speed into one score. Show timing coverage, ranges, median paired delta, and caveats only where timing is observed.

Default recommendation for a limited pilot:

- mean paired quality improvement at least 5/100;
- proposed package wins at least 60% of scorable pairs;
- no increase in critical errors;
- no task category regresses by more than 10/100;
- executor-time ratio no worse than 1.20 where timing coverage is adequate.

Missing thresholds means “inconclusive,” not “current wins.”

## Evaluation review

Render `reviews/evaluation-review.html` with `scripts/render_evaluation_review.py`.

The page has three states in one file:

1. **Blind review** — task prompt, Answer A/B, aliased citations and evidence, rubric controls, A/B/tie/unscorable, confidence, leakage flag, comments. Hide condition names, paths, timing, automatic grades, and aggregates.
2. **Reveal** — identify conditions; show human and deterministic grades, disagreements, task/category results, critical errors, timing coverage, exclusions, protocol deviations, model/harness, and digests.
3. **Decision** — `limited pilot`, `revise and rerun`, `retain current`, or `inconclusive`. If limited pilot is selected, show separate unchecked controls for local adoption, project adapter, private publication, direct collaborators, and team creation/invites/repository access. Access controls name exact targets and roles and run only after successful private publication.

A comparison decision never authorizes filesystem or remote changes. Adoption requires a separate approval record matching the stage and operation digests. Blank approves nothing.

## Adoption

Default: place the accepted wiki as a separate sibling checkout/directory. Do not overwrite or move existing documents. A project instruction adapter may link to the wiki only when separately approved and must be wrapped in removable marker comments.

If in-place migration is requested, first show an exact add/move/change/delete manifest, backup path, and reversal command. Apply atomically where possible and verify reversal byte-for-byte.

Private publication is separately approved. Public visibility is never offered as part of setup.
