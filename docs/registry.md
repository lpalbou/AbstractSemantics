# Semantics registry format (`semantics.yaml`)

> The semantics registry is a YAML file that defines the predicate ids and entity-type ids that upstream systems are allowed to emit/ingest.

## Where it lives

- Default, packaged registry: `src/abstractsemantics/semantics.yaml`
- Override location at runtime: environment variable `ABSTRACTSEMANTICS_REGISTRY_PATH` (implemented by `resolve_semantics_registry_path()` in `src/abstractsemantics/registry.py`)

If `ABSTRACTSEMANTICS_REGISTRY_PATH` is set and points to a non-existent file, `resolve_semantics_registry_path()` raises `FileNotFoundError`.

## Top-level keys

`load_semantics_registry()` (in `src/abstractsemantics/registry.py`) loads YAML via `yaml.safe_load()` and accepts these top-level keys:

- `version`: integer-ish (casts via `int()`; defaults to `0`)
- `prefixes`: mapping `prefix -> namespace_iri` (strings only)
- `predicates`: list of predicate definitions (must contain at least 1 valid entry)
- `entity_types`: list of entity-type definitions (may be empty, but some workflows require it)

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

## Related docs

- [Getting started](getting-started.md)
- [Architecture](architecture.md)
- [KG assertion JSON Schema](schema.md)
- [Semantic triple prompt (guide)](guide/semantics/semantic-triple-prompt-v4-optimized.md)
