# Changelog

All notable changes to this package are documented in this file.

## [0.0.5] - 2026-08-06

### Added

- **`memory_relations` registry section.** A third vocabulary alongside
  `predicates` and `entity_types`, describing the edge relations used by
  AbstractMemory's typed memory records: `summarizes`, `mentions`,
  `written_amid`, `from_session`, `reflected_in`, `continues`,
  `derived_from`, `refines`, `answers`, `supports`, and `part_of`. Ids are
  plain words, which are the canonical spelling at rest. Each entry carries
  an optional `equivalent` list of standard-ontology CURIEs for export and
  interop, and `subject_role`/`object_role` naming each endpoint so writers
  can validate edge direction from the registry instead of duplicating the
  semantics.
- **New public API**: `MemoryRelationDef`, the `SemanticsRegistry.memory_relations`
  field, `SemanticsRegistry.memory_relation_ids()`,
  `SemanticsRegistry.memory_record_predicate_ids()` (declared relations plus
  the digest predicate — the validation set for memory-record writes), and
  the `MEMORY_DIGEST_PREDICATE` constant (`"dcterms:abstract"`).
- **`normalize_kg_predicate()` and `KG_PREDICATE_ALIAS_MAP_V0`.** Call
  `normalize_kg_predicate()` at your ingestion boundary to map an
  extractor-emitted predicate to its canonical registry id. Canonical ids
  pass through, known aliases map to canonical, and anything else returns
  `None` so you can refuse or label it — nothing is coerced to a guessed
  meaning. Both are exported at package top level.
- **`prov` prefix** (PROV-O), used by `equivalent` metadata.
- **`py.typed` marker.** The package is fully annotated and its types are now
  visible to type checkers in consumer projects.

### Changed

- Registry `version` is now `2`.
- `KG_PREDICATE_ALIASES_V0` is derived from `KG_PREDICATE_ALIAS_MAP_V0` and
  now offers only aliases with a single determinate canonical target.
  `schema:hasParent`, `schema:hasMember`, `schema:recognizedAs`, and
  `schema:hasMemorySource` are no longer offered. This affects you only if
  you build schemas with `include_predicate_aliases=True` and rely on those
  four spellings being accepted; use a canonical predicate id instead.
- `build_kg_assertion_schema_v0(include_predicate_aliases=True)` offers an
  alias only when its canonical target exists in the registry you passed, so
  custom registries are never offered a spelling the boundary would reject.
- Loader errors name the registry file, including YAML syntax errors.
- `build_kg_assertion_schema_v0()` raises `ValueError` for negative bounds
  rather than treating them as unbounded.
- `ABSTRACTSEMANTICS_REGISTRY_PATH` pointing at a directory raises a message
  that says so.

### Registry validation

`predicates` and `entity_types` remain lenient — malformed items are skipped
and the load succeeds — because they feed structured-output enums. Problems
that used to pass silently now report:

- Duplicate YAML mapping keys fail the load. A stray second `predicates:`
  block previously replaced the whole vocabulary without a warning.
- Malformed items emit one warning per section, naming the file and the
  number skipped.
- An unparseable `version` warns and reads as `0`. An absent or explicitly
  null `version` stays quiet.
- Duplicate ids in `predicates`/`entity_types` warn and keep the first
  occurrence, so every consumer resolves the same winner.

`memory_relations` is validated strictly, because a declared relation
immediately joins `memory_record_predicate_ids()` and its consumer writes to
append-only journals. The load fails when a relation id contains a CURIE
prefix, collides with a KG predicate id, omits `subject_role` or
`object_role`, or is declared twice.

A valid registry loads with no warnings.

### Compatibility

- `memory_relations` is disjoint from `predicates`. The `predicates` list
  feeds the KG-extraction structured-output enum; memory-record plain words
  never appear there.
- Relation ids are additive: they are never renamed or removed, because
  append-only journals record them permanently.
- Some `equivalent` CURIEs (`schema:mentions`, `schema:previousItem`,
  `cito:supports`, `dcterms:isPartOf`) also exist as `predicates` ids. This
  is intentional and safe: memory-record validation accepts only plain-word
  ids, and `equivalent` is export metadata.
- `equivalent` mappings are many-to-one and lossy — several plain words can
  share one broader CURIE — so they must not be used to import back to plain
  words.
- Registry version `1` was never published. Version `0.0.4` served registry
  version `0`, so upgrading from `0.0.4` moves the registry from `0` to `2`.

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
