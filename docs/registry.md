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

Naming note: `entity_types` are NER-sense classes for KG extraction (what
kind of thing a knowledge-graph node is). They are unrelated to the
framework's *summoned entities* (named persistent identities with homes and
phases) — that vocabulary lives in the gateway/runtime lanes, and the
preferred term there is "summoned entity" precisely because "named entity"
collides with NER here.

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

- `subject_role` (required): short noun naming the subject endpoint (e.g. `evidence`)
- `object_role` (required): short noun naming the object endpoint (e.g. `claim`)

This vocabulary is the declared edge-relation set for AbstractMemory's typed
memory records. The rules below govern it:

- **Plain words are the canonical spelling at rest.** Memory journals are
  append-only and match predicate strings exactly, with no alias resolution
  at read time, so a recorded word can never be renamed. `equivalent` CURIEs
  are hints for export and interop — never a second spelling at rest.
- **Equivalents are many-to-one and lossy.** Several plain words may share
  one broader CURIE (`summarizes`, `from_session`, and `derived_from` all
  specialize `prov:wasDerivedFrom`). The mapping is not reversible and must
  not be used to import back to plain words.
- **One most-specific equivalent per entry.** `refines` lists
  `prov:wasRevisionOf` alone and not its superproperty `prov:wasDerivedFrom`,
  which a PROV-aware importer infers.
- **Disjoint from `predicates`.** The `predicates` list feeds the
  KG-extraction structured-output enum, and memory relations must never
  appear there. Some `equivalent` CURIEs (`schema:mentions`,
  `schema:previousItem`, `cito:supports`, `dcterms:isPartOf`) do also exist
  as `predicates` ids — that is intentional and safe, because validation
  accepts only plain-word ids and `equivalent` is export-only.
- **Additive only.** Ids are never renamed or removed, because journals
  record them permanently. Declaring a relation grants permission to write
  it: a declared id immediately joins the validation set, so a word is
  declared when its writer ships, not in anticipation.
- **Each description defines the authoritative direction**, and
  `subject_role`/`object_role` carry it in machine-readable form. For
  formation-time writers, the subject is the newly formed record. Writers
  that accept caller-asserted endpoints validate them against the declared
  roles.
- **The validation set** is `SemanticsRegistry.memory_record_predicate_ids()`:
  the declared relation ids plus the digest predicate
  (`MEMORY_DIGEST_PREDICATE = "dcterms:abstract"`). Memory-record writes are
  checked against it.

### Validation

Unlike `predicates` and `entity_types`, this section is validated strictly:
a malformed entry raises instead of being skipped, because a declared
relation is written into append-only storage where a typo cannot be undone.
The load fails when a relation:

- has an id containing a `:` (ids must be plain words);
- has an id that is also a `predicates` id;
- omits `subject_role` or `object_role`;
- is declared more than once.

These rules apply to every registry, including one supplied through
`ABSTRACTSEMANTICS_REGISTRY_PATH`. See [Troubleshooting](troubleshooting.md)
for the exact messages.

### Scope boundary

This registry owns the at-rest **predicate** vocabulary. It deliberately does
not declare closed sets that belong to the packages that write them —
AbstractMemory's record-kind and `diary_type` sets, or the entity phase keys
and mode enums owned by the gateway and runtime. Import those from their
owning package rather than copying them here, so there is only ever one
authority for each set.

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
