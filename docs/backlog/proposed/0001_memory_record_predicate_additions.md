# Proposed: Registry additions for AbstractMemory typed memory records

## Metadata

- Created: 2026-07-05
- Status: Proposed
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
