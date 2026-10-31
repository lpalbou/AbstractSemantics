# 0004-semantics: [TASK] Review Koine general-purpose vocabulary and modeling contract

> Package: abstractsemantics
> Type: task
> Created: 2026-10-31
> Status: proposed
> Priority: P2
> Labels: decision-gate, awaiting-user-confirmation, koine, vocabulary, knowledge-graph
> Work-item id: abstractsemantics-0004
> Owner: semantics

## Summary

OPERATOR DECISION GATE (never assignable): review the operator-supplied Koine general-purpose
recommendation against the current semantics registry and its consumers. The PDF has been copied
into this repository as requested. **Review/adoption/implementation requires explicit operator
confirmation; copying and backlog intake do not approve a vocabulary migration.**

## Source and reason

Laurent-Philippe Albou, *Koine — Recommended minimal vocabulary set for interoperable knowledge
graphs (general purpose)*, October 2026, three pages.
Repository copy: [koine_general.pdf](../../research/koine/koine_general.pdf).
Original: `/Users/albou/Downloads/koine_general.pdf`, copied byte-for-byte on 2026-10-31.
SHA-256: `1219bae3391340b815af41390dec45be28cf91baf9b5ac4ee15d4a4b3999ef78` (45,209 bytes).

The operator asked for this review while considering controlled tool-evidence assertions and
session collections. The document recommends schema.org defaults, SKOS, a minimal PROV-O set,
SOSA measurements, selected DCMI terms and optional modules, plus canonical modeling patterns,
qualifiers, certainty/absence values and stable query paths. Its reported research results are
claims of the supplied document; independently verify evidence before using them to justify changes.

## Current code reality

- `src/abstractsemantics/semantics.yaml` declares CURIE predicates/entity types and separate
  plain-word memory_relations with direction roles and export-only ontology equivalences.
- `registry.py` loads and validates these sets; `schema.py` builds controlled assertion schemas.
- Existing memory relations include derived_from, refines and supports (evidence → claim).
  Their at-rest spellings and directionality are consumed by append-only Memory revisions.
- `docs/backlog/proposed/0001_memory_record_predicate_additions.md` records the earlier vocabulary
  decisions and their history. Do not treat Koine as automatic permission to rename live edges.
- AbstractMemory ADR 0003 owns graph/revision/ownership semantics; Runtime ADR 0011 owns source
  reconstruction. Vocabulary recommendations alone do not replace those package contracts.

## Proposed review and expected outcome

Compare each recommended vocabulary/term and modeling pattern against current support, usage and
query paths: present/equivalent/missing/conflicting/deferred. Include attributed/hedged claims,
measurements versus general observations, negation versus absence, qualifiers/time, provenance
versus evidentiary support, canonical identifiers and literal/code handling. Identify what belongs
in the registry, extraction guidance, schema validation, Memory contract or consuming application.

The PDF references a Koine agent skill, companion article and detailed experiments that were NOT
supplied. Record those evidence gaps; do not invent their contents or claim a completed scientific
review from this three-page recommendation alone. Decide whether the operator should supply them.

Produce a compatibility matrix, concrete before/after fixtures, retained/deferred recommendations,
consumer blast radius and proposed ADR/migration work. Consult primary vocabulary definitions as
needed. Keep research and a possible registry change as separate approval decisions.

## Acceptance criteria

- [ ] Operator confirms undertaking the review before work begins.
- [ ] Repository PDF hash/size match the supplied document; citation and evidence gaps retained.
- [ ] Review covers both vocabulary choices and canonical modeling/query contracts.
- [ ] Existing memory predicate strings, aliases and direction roles remain traceable.
- [ ] Missing terms/patterns have exact definitions, ownership and consumer impact, not invented IRIs.
- [ ] Examples cover scoped tool evidence, inference, qualified absence/negation and measurements.
- [ ] Any proposed migration/adoption is separately presented for operator confirmation.

## Testing

On later approved implementation: `python -m pytest tests/test_registry.py tests/test_schema.py`.
For the review, validate fixtures against current and candidate schemas; include Memory consumer
compatibility and round-trip/query checks. No registry or schema change is authorized by intake.

## Promotion and ADR state

Await explicit user confirmation. Review existing vocabulary governance and Memory ADR 0003 before
recommending changes. A changed cross-package modeling contract needs ADR review before adoption;
this item is planning memory, not accepted policy. Related framework proposals:
[accumulated evidence track](../../../../docs/backlog/proposed/accumulated-evidence/README.md)
in the framework checkout.

## Receipts

- PDF copied and title/pages/hash inspected on 2026-10-31; no scientific claims independently validated.
- Hub unavailable (`[Errno 61] Connection refused`); mirror/thread intake remains pending.
