# API reference

> Prefer importing from `abstractsemantics` (re-exported from `src/abstractsemantics/__init__.py`). Direct submodule imports may change.

## Registry

- `SemanticsRegistry`: frozen dataclass with fields `version`, `prefixes`, `predicates`, `entity_types`, `memory_relations`
  - `predicate_ids() -> set[str]`
  - `entity_type_ids() -> set[str]`
  - `memory_relation_ids() -> set[str]`
  - `memory_record_predicate_ids() -> set[str]` — declared memory relations plus `MEMORY_DIGEST_PREDICATE`; the validation set for AbstractMemory record writes
- `MEMORY_DIGEST_PREDICATE: str` — `"dcterms:abstract"`, the digest predicate for memory records
- `resolve_semantics_registry_path() -> pathlib.Path`
  - default: `abstractsemantics/semantics.yaml` (in this repo: `src/abstractsemantics/semantics.yaml`)
  - override: `ABSTRACTSEMANTICS_REGISTRY_PATH`
- `load_semantics_registry(path: pathlib.Path | None = None) -> SemanticsRegistry`

### Registry entry shapes (returned objects)

While `SemanticsRegistry` and `MemoryRelationDef` are re-exported at top-level, the registry loader returns immutable dataclass instances for the other entries too (defined in `src/abstractsemantics/registry.py`):

- `PredicateDef`: `id`, `label?`, `inverse?`, `description?`
- `EntityTypeDef`: `id`, `label?`, `parent?`, `description?`
- `MemoryRelationDef`: `id` (plain word), `label?`, `description?`, `equivalent` (tuple of standard CURIEs, interop metadata only), `subject_role?`/`object_role?` (machine-readable edge direction — short role nouns, e.g. `supports`: subject_role `evidence`, object_role `claim`; direction-validating writers consume these instead of hardcoding semantics)

`PredicateDef`/`EntityTypeDef` are not part of the explicitly re-exported top-level API. For compatibility, prefer treating them as simple records and rely on the documented fields (especially `id`).

You can treat these as simple, frozen objects with attributes:

```python
from abstractsemantics import load_semantics_registry

reg = load_semantics_registry()
first = reg.predicates[0]
print(first.id, first.label)
```

## JSON Schema helpers

- `KG_ASSERTION_SCHEMA_REF_V0: str`
- `build_kg_assertion_schema_v0(...) -> dict`
  - important args: `include_predicate_aliases`, `max_assertions`, `min_assertions_when_nonempty`
- `normalize_kg_predicate(predicate, registry=None) -> str | None`: ingestion-boundary normalization — canonical ids pass through, known aliases map to canonical (`KG_PREDICATE_ALIAS_MAP_V0`), anything else returns `None` (caller refuses or labels; never guesses)
- `KG_PREDICATE_ALIAS_MAP_V0: dict[str, str]`: alias → canonical registry id (single source; the offered `KG_PREDICATE_ALIASES_V0` tuple derives from its keys)
- `resolve_schema_ref(schema: dict) -> dict | None`

### Evidence (tests)

For concrete, executable examples that anchor expected behavior:

- Registry loading: `tests/test_registry.py`
- Schema construction and `$ref` resolution: `tests/test_schema.py`

## Related docs

- [Getting started](getting-started.md)
- [Architecture](architecture.md)
- [Registry format](registry.md)
- [KG assertion JSON Schema](schema.md)
- [FAQ](faq.md)
