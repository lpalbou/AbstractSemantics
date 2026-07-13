# Changelog

All notable changes to this package are documented in this file.

## [0.0.5] - 2026-07-10 (amended 2026-07-12)

### Added

- Declared the AbstractMemory typed-record edge vocabulary as a new
  `memory_relations` registry section (`summarizes`, `mentions`,
  `written_amid`, `from_session`, `reflected_in`, `continues`,
  `derived_from`) per decision `0016-vocabulary-direction` (2026-07-10):
  plain words are the canonical at-rest spelling; standard-ontology CURIEs
  ride each entry's `equivalent` list as export/interop metadata only.
- New `MemoryRelationDef` dataclass, `SemanticsRegistry.memory_relation_ids()`,
  `SemanticsRegistry.memory_record_predicate_ids()` (the AbstractMemory
  validation set: declared relations + digest predicate), and the
  `MEMORY_DIGEST_PREDICATE` constant (`"dcterms:abstract"`).
- Declared the `prov` prefix (PROV-O) for equivalence metadata.
- Registry `version` bumped to 1.
- **Widening batch (2026-07-12, coordinated with the memory seat per the
  standing rule)**: four relations join `memory_relations` — `refines`
  (`prov:wasRevisionOf`; live writer: world-model revision chains),
  `answers` (`cito:repliesTo`; the edge form — distinct from the
  `attributes.answers` reference on diary entries), `supports`
  (`cito:supports`; subject = the evidence, object = the claim supported),
  and `part_of` (`dcterms:isPartOf`). The latter three gained a writer path
  through memory's disposal surface (`confirm_relation`). Registry `version`
  bumped to 2. `resolves` is deliberately NOT declared (reader-only today;
  declaration IS permission in this design — it follows the widening rule
  when memory ships its writer).
- **Machine-readable direction (2026-07-12, memory's ask)**: every
  `memory_relations` entry now declares `subject_role`/`object_role` (short
  role nouns, e.g. `supports`: evidence → claim), carried on
  `MemoryRelationDef`. Writers with caller-asserted endpoints (disposal
  `confirm_relation`) validate direction against these instead of
  hardcoding a second copy of the semantics. Test-pinned: every entry must
  carry both roles.

### Notes

- `memory_relations` is deliberately disjoint from `predicates` (test-pinned):
  the `predicates` list feeds the KG-extraction structured-output enum, and
  memory plain words must never surface there.
- Widening rule (both directions, on record with the memory seat): no new
  relation engraves in AbstractMemory before it is declared here; nothing is
  added here without coordinating with the memory seat. Ids are never renamed
  or removed (append-only journals engrave them permanently).
- Direction convention revised (2026-07-12): each entry's description defines
  the authoritative direction; subject-is-the-new-record stays structural for
  formation writers, while disposal-confirmed edges carry caller-asserted
  endpoints (per-relation enforcement is memory's lane, flagged on the hub).
- Equivalence policy recorded: one MOST-SPECIFIC term per entry (`refines`
  lists `prov:wasRevisionOf` alone — a PROV-aware importer infers the broader
  `prov:wasDerivedFrom`; double-emitting adds nothing). The known overlap
  between `equivalent` CURIEs and KG predicate ids (`schema:mentions`,
  `schema:previousItem`, `cito:supports`, `dcterms:isPartOf`) is declared and
  test-pinned so a new instance is a decision, not drift.
- Release-lineage note: no released artifact ever served registry version 1
  (0.0.4 served version 0); the released jump is 0 → 2 in one package
  version. Version 1 is kept distinct in the records because durable
  decision-store and backlog entries cite "version 1 = seven relations".

## [0.0.4] - 2026-05-08

### Added

- Added GitHub Actions CI for Python 3.10 through 3.12 with pytest and package
  build checks.
- Added a trusted-publishing release workflow for tagged or manually dispatched
  releases, including version/changelog validation, distribution artifacts,
  PyPI publication, and GitHub Release creation.
- Added an AbstractSemantics GitHub bug report template.
- Added a `test` optional dependency extra for CI and release validation.

## 0.0.3 - 2026-05-08

### Added

- Added install-profile compatibility extras:
  `abstractsemantics[apple]`, `abstractsemantics[gpu]`,
  `abstractsemantics[all-apple]`, and `abstractsemantics[all-gpu]`.

### Notes

- These extras are intentionally no-op aliases. Semantics has no hardware
  runtime dependencies, but exposing the shared profile names keeps
  higher-level aggregate installs composable.

## 0.0.2 - 2026-02-04

### Added

- A complete, user-facing documentation set under `docs/` (entrypoint: `docs/getting-started.md`).
- `llms.txt` and a generated `llms-full.txt` snapshot for agentic/LLM tooling (generator: `scripts/generate_llms_full.py`).
- Repository policies and project docs: `CONTRIBUTING.md`, `SECURITY.md`, `ACKNOWLEDMENTS.md`, and `LICENSE`.

### Changed

- Packaging metadata: SPDX-style license metadata and explicit `license-files` in `pyproject.toml`.

### Notes

- No runtime API changes: registry loading and schema helpers are unchanged.

## 0.0.1

- Initial release of the semantics registry loader and KG assertion JSON Schema helpers.
