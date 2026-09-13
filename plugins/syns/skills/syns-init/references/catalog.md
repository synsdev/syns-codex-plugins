# The pinned structure shelf

The setup skill reads this compact catalog before pulling full examples. These are **Syns-authored,
internally checked references**, not customer-proven templates and not a marketplace. A pin is the
reviewed version; never silently replace it with remote head.

## Team and development references

| Reference | Commit | Mode | Adopt when | Do not claim |
| --- | --- | --- | --- | --- |
| `bartsoj/ticks-engineering-work` | `000dfbef291d50cde86aa942697909352f3dfd05` | shape-only | Small engineering queues where dependency waves, waiting, review and explicit blockers are central | `tk` compatibility or native ticks operation |
| `bartsoj/linear-engineering-work` | `e54bb495634698f6485a8e884277cf855552d070` | shape-only | Engineering delivery organized as issues → projects → initiatives, with milestones, cycles, updates and documents | Linear import/sync, realtime UI, permissions, notifications, automations, integrations or analytics |
| `bartsoj/notion-workspace` | `b18f2ed4ebacabe5e5671113d75667a70f9e196e` | shape-only | Cross-functional pages and typed databases with relations, templates and multiple views | Notion compatibility, editor behavior, formulas, permissions, notifications, automations, AI or integrations |
| `bartsoj/attio-crm` | `e27bd7325d852bbb3d221db556052e8973176ed5` | shape-only | Relationship work where durable people/company/deal facts participate in process-specific lists | Attio import/sync, enrichment, communications, permissions, automations, integrations or analytics |
| `bartsoj/spec-kit-feature-specs` | `b3ffce8761fade4ac2cf6dca4e79ac0e8f29ed72` | native transport | The source already contains Spec Kit, or the user chooses constitution plus feature packets | That Syns runs Spec Kit, inspects code, implements tasks or should sync `.specify/feature.json` |
| `bartsoj/openspec-codebase-specs` | `386589ffba465d721124fce1205043ac222b0227` | native transport | The source already contains OpenSpec, or the user chooses current capability truth plus proposed deltas and archives | That Syns authors, applies, verifies, synchronizes or archives OpenSpec changes |

## Personal category-native starters

These are neutral use-case schemas synthesized from several apps and standards. They are **direct
Markdown trees**: agents edit source records; a later external interface may parse the same
frontmatter/body and compute presentation in memory. They intentionally contain no repository
scripts, tests, generated views/JSON, caches or interface code.

| Reference | Commit | Adopt when | Keep outside / do not claim |
| --- | --- | --- | --- |
| `bartsoj/personal-notes` | `f7566f04ae91e9db79952cd5aad4ae000364d6fe` | Free-form notes, collections, tags, links, attachments, daily notes or clippings | Sync, OCR, reminders, collaboration, semantic search; never rewrite supplied note text unless asked |
| `bartsoj/personal-tasks-goals` | `7e8b450ce9d831a42f161a42a42ff1981cf33a2c` | Inbox, tasks, projects, areas, goals, recurrence and reviews | Notification delivery, geofencing, calendar invitations and background recurrence execution |
| `bartsoj/personal-exercise` | `97f5016fd112007415fddf3a02f81a368543ec62` | Strength/endurance/mobility plans, workouts, sessions, measurements and progress | GPS/wearable streams, timers, diagnosis, automatic programming or personalized medical advice |
| `bartsoj/personal-habits-routines` | `467fcf8eb67d13413a38e1e610e33ca9923b2b41` | Habit definitions, routines/steps, check-ins, schedule revisions, experiments and reviews | Reminder delivery, sensor completion, gamification; medication belongs elsewhere |
| `bartsoj/personal-food-nutrition` | `0363e22839bbc48f223d448cbc44eb8c5a0959d4` | Foods, recipes, meals, diary entries, nutrient snapshots, targets and reviews | Global food search, barcode/photo capture, adaptive advice; missing nutrients are unknown, not zero |
| `bartsoj/personal-travel` | `1541897cd3fe854844af3069f7db98f78c3c409b` | Trips, places, itinerary, reservations, decisions, checklists, expenses and memories | Live availability/status, route optimization, booking execution, secrets or live location |
| `bartsoj/personal-people` | `2a618c7682763deb6f58482b867bed0c0690bd08` | Contacts, typed relationships, groups, interactions, dates, commitments and follow-up | Message ingestion, enrichment, ranking/relationship scores, inferred sensitive attributes |

## Selection

1. Prefer an inspected repository that is already canonical over every shelf reference.
2. Detect native Spec Kit/OpenSpec roots before considering translated shapes. Preserve a selected
   native root without translation.
3. Choose by entities, relationships, lifecycle and information questions—not name similarity.
4. For an exact personal-category request, derive from that category-native pin. Preserve its source
   folder/frontmatter semantics and direct-edit agent rules; adapt only what source evidence requires.
5. A request spanning several personal categories requires a repository-boundary decision:
   - default to separate linked repositories when privacy, lifecycle or overlapping paths differ;
   - if the user explicitly wants one repository, compose the selected categories under clear
     namespaces, rewrite paths/read order deliberately, and show every collision and adaptation.
6. At most one branded shape-only base may own one overlapping domain. Several non-overlapping
   category-native modules may be composed; do not copy the same fact into two modules.
7. It is valid for no pin to fit. Say so and compose a neutral structure from source evidence.

Recognizability breaks a tie; it never overrides information fit.

## Reading a reference

Pull a candidate at its pinned commit into the run's private temporary area:

```bash
syns pull <owner/name> <run>/candidates/<id> --version <pinned-commit>
```

Verify the resolved commit against `catalog.json`. Read `README.md`, `STRUCTURE.md`, `AGENTS.md`, and
`FIELD_MAP.md`/`FIELD-MAP.md` first, then only representative source records needed to understand the
slots. Never silently substitute remote head.

For a category-native starter:

- reuse schema and agent behavior, not another person's content;
- keep instructional starter records only if they remain true onboarding for this repository;
- do not turn exercise/reference libraries into personal history;
- strip `.syns.yaml` from a staged derivative before first publication;
- preserve source attribution and the pin in proposal provenance;
- scope each adopted module's “nothing else belongs here” rule to that module;
- resolve duplicate root `README`/`STRUCTURE`/`FIELD_MAP`/agent instructions with one repository router
  and namespaced module copies;
- qualify same-named `type` values by module/path where schemas differ;
- map colliding folders such as `reviews/` or similar check-in names explicitly rather than overlaying
  their files.

## Composition rules

Each proposed path records one origin:

- `kept` — an existing file retained unchanged;
- `adopted` — a slot adapted from a selected reference;
- `native` — a parser-owned native artifact preserved in place;
- `neutral` — a general-purpose module source evidence requires;
- `source-required` — a new file whose need came from source evidence or a human answer;
- `generated` — navigation derived from canonical files, only when the chosen non-personal package
  truly requires a materialized derivative;
- `omitted` — an existing or candidate slot deliberately left out, with a reason.

A fact has one owner. Hierarchy points upward. Filterable/sortable state belongs in typed frontmatter.
Native artifacts keep their parser's syntax. **Personal category-native proposals stay source-Markdown
only:** no scripts, tests, generated/materialized views, JSON projections, caches or interface code.
An agent or external interface computes backlinks, counts, charts, Today, overdue, progress and similar
views in memory whenever it reads the source records.
