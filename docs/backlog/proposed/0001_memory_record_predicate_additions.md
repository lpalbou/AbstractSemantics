# Proposed: Registry additions for AbstractMemory typed memory records

## Metadata

- Created: 2026-07-05
- Status: Implemented (registry side, 2026-07-10) — see the final addendum;
  closes when AbstractMemory's 0016 consumes it
- Completed: N/A
- Priority: Medium (blocks part of AbstractMemory's memory_system_v1 wave)

## ADR status

- Governing ADRs: None identified after review
- ADR impact: None (registry data addition under existing governance rules)

## Context

AbstractMemory's memory-record layer (see
`abstractmemory/docs/backlog/proposed/memory_system_v1/0021_memory_records_and_remember_api.md`
and `0016_semantics_vocabulary_validation_and_aliasing_module.md`) encodes
typed memory records (episode, lesson, plan, instruction, decision, claim,
summary, question, answer, probe_report, entity) as subject-rooted triple
clusters using ONLY registry predicates. AbstractMemory is taking a hard
dependency on this package (owner decision 2026-07-05); the registry remains
the single vocabulary authority.

Verified against `src/abstractsemantics/semantics.yaml` (2026-07-05): the
mapping mostly lands on existing terms (`dcterms:isPartOf`, `schema:nextItem`,
`schema:mentions`, `cito:supports`, `cito:disagreesWith`, `cito:extends`,
`cito:usesDataFrom`, `cito:discusses`, `dcterms:title`, `dcterms:abstract`,
`dcterms:description`, `schema:result`, `dcterms:subject`). Five terms are
missing.

## Problem or opportunity

Missing predicates needed by the memory-record layer — all real terms in
their source ontologies, no invented vocabulary:

1. `dcterms:replaces` — revision/supersession links between record versions.
2. `dcterms:requires` — dependency links (plan/instruction prerequisites).
3. `cito:repliesTo` — answer-to-question links.
4. `prov:wasDerivedFrom` — derivation/source-evidence links (lessons derived
   from episodes, summaries from sources). Introduces the PROV-O namespace;
   alternative if a new namespace is unwanted: `dcterms:source`.
5. `dcterms:type` — the record-kind discriminator literal (episode | lesson |
   plan | ...), so kind filtering is an ordinary triple query instead of an
   attributes convention.

Also worth considering in the same batch (raised by AbstractMemory's review,
not blocking): whether `cito:repliesTo`-style Q/A record types justify
`schema:Question`/`schema:Answer` entity types, and whether the runtime's
predicate alias map (`schema:isPartOf → dcterms:isPartOf` etc., currently in
`abstractruntime/src/abstractruntime/integrations/abstractmemory/effect_handlers.py`)
should move into the registry as declared synonyms rather than living in
consumer code.

## Proposed direction

Add the five predicates to `semantics.yaml` with definitions, domains/ranges
consistent with the source ontologies, and inverse declarations where
applicable (`dcterms:replaces` / `dcterms:isReplacedBy`). Decide the
`prov:` namespace question explicitly. Version-bump the registry per its
change process.

## Why it might matter

Without these, AbstractMemory either blocks its record layer or smuggles
package-private vocabulary — which the framework's rules (and AbstractMemory's
own planned item 001) forbid.

## Promotion criteria

Promote when AbstractMemory's `0016`/`0021` items are promoted to planned —
the registry batch should land before or with them.

## Validation ideas

- Registry loads; `predicate_ids()` includes the new terms.
- Definitions/inverses consistent with dcterms/CiTO/PROV-O sources.
- AbstractMemory's vocabulary tests (item 0016) pass against the updated
  registry.

## Non-goals

- No new invented predicate ids.
- No memory-record schema ownership in this package (records live in
  AbstractMemory; vocabulary lives here).

## Guidance for future agents

Cross-check AbstractMemory's items 0016/0021 for the exact final list before
implementing — the record-layer design may have evolved. Keep the "no invented
vocabulary" rule absolute.

## Addendum 2026-07-10 — verified drift against the shipped engine

Verified against abstractmemory `entity-work` @ 15544f5 (the engine that now
runs live entity homes):

1. **No dependency yet**: abstractmemory has zero references to
   abstractsemantics (no import, no pyproject dependency). The hard-dep
   decision (2026-07-05) is not yet reflected in code; vocabulary validation
   (memory item 0016) remains proposed/deferred —
   `records.py` marks relation predicates "NOT vocabulary-validated in v1
   (0016)" explicitly.
2. **The shipped vocabulary differs from this proposal's mapping**: the only
   CURIE in live use is `dcterms:abstract` (record digests). Relation edges
   use plain words: `summarizes`, `mentions`, `written_amid`, `from_session`,
   `reflected_in`, `continues`, `derived_from` (records/consolidation/
   maintenance modules). The original five-CURIE list above is therefore
   stale as a build list.
3. **Append-only constraint on any future validation**: live homes (Castor's)
   already carry engraved edges with the plain-word predicates, and journals
   are append-only — those strings can never be rewritten. When 0016
   promotes, the registry must either admit the shipped plain-word relations
   (as declared terms or aliases of registry CURIEs), or validation applies
   to new writes only. Registry-side declared synonyms are the likely honest
   shape; decide jointly with AbstractMemory.

Ask filed with the memory seat on agora (commons, 2026-07-10) to settle the
final list before promotion.

## Addendum 2026-07-10 — direction SETTLED (supersedes the original five-CURIE list)

Answered by the memory seat (agora commons c184; resolved c190; durable record:
commons store key `decision:0016-vocabulary-direction` and consensus plan v13
"(vocabulary)" row). Option (a):

1. **Plain words are canonical at rest.** The registry admits the seven shipped
   relation predicates as declared terms: `summarizes`, `mentions`,
   `written_amid`, `from_session`, `reflected_in`, `continues`, `derived_from`.
   `dcterms:abstract` remains the digest predicate. Rationale: append-only
   journals make engraved strings permanent, and the engine equality-keys
   predicate strings with no alias resolution at read (e.g. consolidation's
   `CONTEXT_RELATIONS` frozenset guard) — a second spelling would silently
   bypass guards. One spelling per predicate, at rest, forever.
2. **CURIEs demote to registry-side equivalence metadata.** The original five
   CURIEs (and natural pairs like `cito:repliesTo`/`dcterms:replaces` for the
   plain words) become equivalence annotations on the declared terms — useful
   for export/interop, never a second at-rest spelling. Registry format note:
   this needs a small schema extension (e.g. an `equivalent:` list per
   predicate entry, or a dedicated `memory_relations:` section) — design at
   implementation time, coordinated with memory.
3. **Validation applies to NEW writes** when memory's 0016 promotes; the
   registry is the validation source (memory's statement on record).
4. **Bidirectional coordination rule** (e-s 143/145): memory widens no closed
   set without notifying copy-owners; no new predicate engraves before a
   registry declaration is coordinated with this seat.

Promotion remains gated on memory's 0016 promotion (unchanged criterion). The
original five-CURIE section above is retained as history; it no longer
describes the build.

## Addendum 2026-07-10 (later) — registry side IMPLEMENTED

Landed after laurent's plan sign-off lifted the gate (agora commons c226),
registry version 0 → 1, package 0.0.5:

- `semantics.yaml` gains a `memory_relations` section declaring the seven
  plain-word relations with `equivalent` CURIE metadata (prov prefix added);
  deliberately separate from `predicates` (KG-extraction enum) — disjointness
  is test-pinned.
- Loader: `MemoryRelationDef`, `memory_relation_ids()`,
  `memory_record_predicate_ids()` (relations + `MEMORY_DIGEST_PREDICATE =
  "dcterms:abstract"` — the exact validation set for 0016's new-write checks).
- Tests 4 → 8 (declared set pinned append-widen-only; equivalence prefixes
  must be declared; plain-word rule; disjointness). Docs: registry.md, api.md,
  CHANGELOG.

Open with memory (flagged, not blocking): `answers`, `supports`, `part_of`
appear in their `COMPONENT_RELATIONS` as future-facing edge words but are not
engraved as edges today (`answers`/`resolves` ride record ATTRIBUTES, not
edges). Per the widening rule they get declared here before first engraving —
memory says the word, this seat adds the entries.

## Addendum 2026-07-10 (final) — memory fidelity review folded; thread CLOSED

Memory reviewed all seven mappings against the shipped writers (a2a
0012-entity-topology-execution, 074748Z): six confirmed; `written_amid`
unmapped ENDORSED. Two precisions applied to the registry (8/8 green):
`reflected_in` description names the containment rule (only non-private
projections carry the edge); equivalents documented as MANY-TO-ONE and LOSSY
(summarizes/from_session/derived_from all specialize prov:wasDerivedFrom —
never reversible).

Writer census on record (memory, verified in code 2026-07-10): engraved as
edges today = continues/reflected_in/summarizes/from_session (runtime driver),
mentions (dream pass), written_amid (diary projection); `derived_from` is
declared with NO live writer yet (first engraving will come through
remember_many edges — already in-set). NOT edges: answers/resolves are record
attributes; supports/part_of have no shipped writer (routing policy + report
prose only). Bidirectional widening commitment re-stated by both seats.
