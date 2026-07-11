# Semantics registry format (`semantics.yaml`)

> The semantics registry is a YAML file that defines the predicate ids and entity-type ids that upstream systems are allowed to emit/ingest.

## Where it lives

- Default, packaged registry: `abstractsemantics/semantics.yaml` (in this repo: `src/abstractsemantics/semantics.yaml`)
- Override location at runtime: environment variable `ABSTRACTSEMANTICS_REGISTRY_PATH` (implemented by `resolve_semantics_registry_path()` in `src/abstractsemantics/registry.py`)

If `ABSTRACTSEMANTICS_REGISTRY_PATH` is set and points to a non-existent file, `resolve_semantics_registry_path()` raises `FileNotFoundError`.

## Top-level keys

`load_semantics_registry()` (in `src/abstractsemantics/registry.py`) loads YAML via `yaml.safe_load()` and accepts these top-level keys:

- `version`: integer-ish (casts via `int()`; defaults to `0`)
- `prefixes`: mapping `prefix -> namespace_iri` (strings only)
- `predicates`: list of predicate definitions (must contain at least 1 valid entry)
- `entity_types`: list of entity-type definitions (may be empty, but some workflows require it)
- `memory_relations`: list of memory-record edge relations (plain-word ids; see below)

Unknown keys are ignored.

## Loader behavior (what is and is not validated)

The loader is intentionally permissive (see `src/abstractsemantics/registry.py`):

- It does **not** expand CURIEs into IRIs (prefixes are loaded but not applied).
- It does **not** validate cross-references:
  - `PredicateDef.inverse` is not checked to exist in `predicates`.
  - `EntityTypeDef.parent` is not checked to exist in `entity_types`.
- It preserves list order and does not deduplicate entries (use `predicate_ids()` / `entity_type_ids()` if you only need the unique ids).

## Predicate definitions

Each item under `predicates` becomes a `PredicateDef` dataclass instance with:

- `id` (required): string, typically a CURIE like `dcterms:isPartOf` or `rdf:type`
- `label` (optional): string
- `inverse` (optional): string (points to another predicate id)
- `description` (optional): string

Invalid items are skipped. If no valid predicates remain, `load_semantics_registry()` raises `ValueError`.

## Entity-type definitions

Each item under `entity_types` becomes an `EntityTypeDef` dataclass instance with:

- `id` (required): string, typically a CURIE like `schema:Person`
- `label` (optional): string
- `parent` (optional): string (points to another type id)
- `description` (optional): string

Invalid items are skipped. The registry loader does not currently require entity types to be present; however, `build_kg_assertion_schema_v0()` raises `ValueError` if the provided registry has no entity types.

## Memory-relation definitions

Each item under `memory_relations` becomes a `MemoryRelationDef` dataclass instance with:

- `id` (required): a **plain word** (e.g. `summarizes`, `written_amid`) — deliberately NOT a CURIE
- `label` (optional): string
- `description` (optional): string
- `equivalent` (optional): list of standard-ontology CURIEs (equal-or-broader terms) carried as export/interop metadata only

This vocabulary is the declared edge-relation set for AbstractMemory's typed
memory records (decision `0016-vocabulary-direction`, 2026-07-10). Design
rules, in force:

- **Plain words are the canonical at-rest spelling.** Memory journals are
  append-only and equality-key predicate strings with no alias resolution at
  read, so an engraved word can never be renamed. `equivalent` CURIEs are
  hints for export/interop — never a second at-rest spelling.
- **Equivalents are many-to-one and lossy.** Several plain words may share
  one broader CURIE (`summarizes`/`from_session`/`derived_from` all
  specialize `prov:wasDerivedFrom`); the mapping is never reversible and
  must never drive an import back to plain words (memory fidelity review,
  2026-07-10).
- **Disjoint from `predicates`.** The `predicates` list feeds the
  KG-extraction structured-output enum; memory relations must never appear
  there (test-pinned).
- **Append-widen only, coordinated.** No new relation is engraved by
  AbstractMemory before it is declared here, and nothing is added here
  without coordinating with the memory seat. Ids are never renamed or
  removed.
- **Validation set.** `SemanticsRegistry.memory_record_predicate_ids()`
  returns the declared relation ids plus the digest predicate
  (`MEMORY_DIGEST_PREDICATE = "dcterms:abstract"`) — the set AbstractMemory's
  vocabulary validation checks NEW record writes against.
- **Authority boundary (settled with the memory seat, 2026-07-10).** The
  registry owns AT-REST PREDICATE vocabulary (this section, per the 0016
  ruling). Engine validation vocabularies — AbstractMemory's record-kind set
  and `diary_type` closed set — stay engine-owned and are package-root
  exports of `abstractmemory` (`MEMORY_RECORD_KINDS`, `DIARY_TYPES`,
  `KIND_RANKS`): consumers import the owning set rather than copying it. A
  registry declaration of those sets would create a second authority that
  could disagree with the refusing code — the drift class one level up.

## Minimal example

```yaml
version: 0
prefixes:
  schema: "https://schema.org/"
predicates:
  - id: "schema:name"
    label: "name"
entity_types:
  - id: "schema:Thing"
    label: "Thing"
```

## Working with the registry in Python

```python
from abstractsemantics import load_semantics_registry

reg = load_semantics_registry()
print(sorted(reg.predicate_ids())[:5])
print(sorted(reg.entity_type_ids())[:5])
```

## Practical editing guidelines

When updating `semantics.yaml`:

- Prefer stable, explicit ids (typically CURIEs) and keep them consistent over time.
- Add `label`/`description` for human-facing tooling (UIs, review, curation).
- Use `inverse` (predicates) and `parent` (entity types) as navigational hints; the loader does not validate that references exist.
- After changes, run `pytest` and (if applicable) regenerate `llms-full.txt` so agent manifests stay in sync.

## Related docs

- [Getting started](getting-started.md)
- [Architecture](architecture.md)
- [KG assertion JSON Schema](schema.md)
- [FAQ](faq.md)
- [Semantic triple prompt (guide)](guide/semantics/semantic-triple-prompt-v4-optimized.md)
