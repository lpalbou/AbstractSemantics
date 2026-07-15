# Proposed: Canonical normalization map for KG predicate aliases

## Metadata

- Created: 2026-07-10
- Status: Implemented (2026-07-13 — see addendum)
- Completed: 2026-07-13
- Priority: Low (no consumer currently enables aliases; gap was latent)

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

## Addendum 2026-07-13 — IMPLEMENTED (idle-bar cycle, commons c1369)

Built under the operator's idle directive; one fable5 adversary attacked the
built code (findings folded — see below). What shipped:

- `KG_PREDICATE_ALIAS_MAP_V0: dict[str, str]` — alias → canonical registry
  id; `KG_PREDICATE_ALIASES_V0` now DERIVES from its keys (derive-never-copy;
  test-pinned equality).
- `normalize_kg_predicate(predicate, registry=None) -> str | None` — the
  ingestion-boundary verb: canonical ids pass through; known aliases map;
  everything else returns None (caller refuses or labels-unknown; never
  guesses). Both exported at package top level.
- The OFFER set was NARROWED per the accept-vs-offer split (the second
  option the original item named — "whether aliases belong in the ENUM at
  all" — resolved per-alias): four indeterminate aliases were REMOVED from
  the offer (`schema:hasParent` — broader-vs-isPartOf is context-dependent;
  `schema:hasMember` — no member predicate in the registry;
  `schema:recognizedAs` — lossy vs sameAs; `schema:hasMemorySource` —
  invented term). Offering a spelling the boundary cannot normalize invites
  un-normalizable data; those spellings now return None at the boundary.
  Kept (determinate): schema:description→dcterms:description,
  schema:creator→dcterms:creator, schema:hasPart→dcterms:hasPart,
  schema:isPartOf→dcterms:isPartOf, dcterms:has_part→dcterms:hasPart,
  dcterms:is_part_of→dcterms:isPartOf.
- Consumer check re-verified at build time: no consumer anywhere in the
  framework enables `include_predicate_aliases=True` (rg across all package
  src trees) — the offer-set narrowing has zero blast radius.
- Tests 10 → 17: map range ⊆ registry ids; keys ∩ registry ids = ∅; derived
  offer set; canonical pass-through; EVERY offered enum spelling normalizes
  (the round-trip promise); unknown/indeterminate → None; dropped aliases
  absent from offer and map. Docs: schema.md (normalization section),
  faq.md, api.md, CHANGELOG.

The "design the map with the KG-consuming seats" caveat was honored by
subtraction: every mapping shipped is a same-meaning spelling variant
(schema.org twin or snake_case slip), not a semantic judgment call; the
judgment-call aliases were dropped rather than decided unilaterally. If a
consuming seat later wants one of the dropped spellings offered, it comes
back through the standing vocabulary route with that seat's use case.

Adversary folds (same-session): perf note + docstring matching contract
(strip-then-exact, case-sensitive, registry=None reloads per call — pass it
in loops; the doc example loads once); memory-relations disjointness PIN on
the map keys plus the every-memory-word-returns-None belt (the leak the
range check alone would miss); CHANGELOG folded into 0.0.5 as a dated
amendment (matching the file's own convention — 0.0.5 is itself unreleased,
and a stranded [Unreleased] above it would produce wrong notes at tag time);
`predicate` parameter typed `object` (sanitizing raw LLM output IS the
contract). Honest scope correction from the adversary, recorded: the kept
six are the OLD OFFER minus the indeterminate entries, not a fresh
derivation of "LLM-common" — four determinate twins of declared ids
(schema:dateCreated→dcterms:created, schema:dateModified→dcterms:modified,
schema:identifier→dcterms:identifier, schema:publisher→dcterms:publisher,
arguably schema:author→dcterms:creator) are candidates for a future _V0
widening through the standing route when a consuming seat brings the use
case. Also observed by the adversary, pre-existing and out of this item's
scope: the registry itself declares near-synonym canonical pairs
(dcterms:subject vs schema:about; dcterms:title vs schema:name) — the
one-spelling-at-rest tension lives in the KG predicate list too; filed as a
future registry-review note, not acted on here.
