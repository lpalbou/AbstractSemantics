# Changelog

All notable changes to this package are documented in this file.

## [0.0.5] - 2026-07-10

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

### Notes

- `memory_relations` is deliberately disjoint from `predicates` (test-pinned):
  the `predicates` list feeds the KG-extraction structured-output enum, and
  memory plain words must never surface there.
- Widening rule (both directions, on record with the memory seat): no new
  relation engraves in AbstractMemory before it is declared here; nothing is
  added here without coordinating with the memory seat. Ids are never renamed
  or removed (append-only journals engrave them permanently).

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
