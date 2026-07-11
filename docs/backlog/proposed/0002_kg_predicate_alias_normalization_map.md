# Proposed: Canonical normalization map for KG predicate aliases

## Metadata

- Created: 2026-07-10
- Status: Proposed
- Completed: N/A
- Priority: Low (no consumer currently enables aliases; gap is latent)

## ADR status

- Governing ADRs: None identified
- ADR impact: None (additive API; no behavior change to defaults)

## Context

`schema.py` ships `KG_PREDICATE_ALIASES_V0` — "predicates that LLMs tend to
emit by default" — and `build_kg_assertion_schema_v0(include_predicate_aliases=True)`
adds them to the structured-output enum. The module comment says "Alias
handling belongs at the ingestion boundary", but the package provides no
alias → canonical mapping, so an ingestion boundary CANNOT normalize: with
aliases enabled, an extractor may emit `schema:hasMemorySource` (not a real
schema.org term) or `dcterms:has_part` (snake_case variant that does not
exist in dcterms) and the string lands in KG stores un-normalized — invented
or non-canonical vocabulary at rest, the exact failure class the registry
exists to prevent.

Mitigating fact (verified 2026-07-10): `include_predicate_aliases` defaults
to False and `resolve_schema_ref()` uses the default, so the shipped
KG-extraction path exposes canonical ids only. The gap fires only when a
consumer explicitly enables aliases.

## Proposed direction

Add `KG_PREDICATE_ALIAS_MAP_V0: dict[str, str]` (alias → canonical registry
id) beside the tuple, keep the tuple derived from its keys, and document that
ingestion boundaries normalize via the map before persisting. Mapping choices
need care (e.g. `schema:hasParent` → `skos:broader` vs `dcterms:isPartOf` is
context-dependent; `schema:recognizedAs` → `schema:sameAs` is lossy) — design
the map with the KG-consuming seats, not unilaterally.

Also worth deciding: whether aliases belong in the ENUM at all (letting the
model emit an alias the boundary must catch) vs prompt-side hints with a
canonical-only enum. The second is stricter and may obsolete the map.

## Why it might matter

Same principle as the memory-relations ruling (one spelling per predicate at
rest): two spellings of one predicate in stores makes equality-keyed queries
silently incomplete.

## Promotion criteria

Promote when any consumer enables `include_predicate_aliases=True`, or when
KG ingestion normalization is built anywhere in the framework.

## Validation ideas

- Every alias maps to a canonical id present in the registry.
- Normalization round-trip: schema built with aliases, assertion emitted with
  an alias, boundary normalizes, store carries canonical only.

## Non-goals

- No change to `include_predicate_aliases=False` default behavior.
- No new invented vocabulary — the map's RANGE is registry ids only.
