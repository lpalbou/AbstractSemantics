# API reference

> Prefer importing from `abstractsemantics` (re-exported from `src/abstractsemantics/__init__.py`). Direct submodule imports may change.

## Registry

- `SemanticsRegistry`: frozen dataclass with fields `version`, `prefixes`, `predicates`, `entity_types`
  - `predicate_ids() -> set[str]`
  - `entity_type_ids() -> set[str]`
- `resolve_semantics_registry_path() -> pathlib.Path`
  - default: `abstractsemantics/semantics.yaml` (in this repo: `src/abstractsemantics/semantics.yaml`)
  - override: `ABSTRACTSEMANTICS_REGISTRY_PATH`
- `load_semantics_registry(path: pathlib.Path | None = None) -> SemanticsRegistry`

### Registry entry shapes (returned objects)

While only `SemanticsRegistry` is re-exported at top-level, the registry loader returns immutable dataclass instances for entries too (defined in `src/abstractsemantics/registry.py`):

- `PredicateDef`: `id`, `label?`, `inverse?`, `description?`
- `EntityTypeDef`: `id`, `label?`, `parent?`, `description?`

These entry classes are not part of the explicitly re-exported top-level API. For compatibility, prefer treating them as simple records and rely on the documented fields (especially `id`).

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
