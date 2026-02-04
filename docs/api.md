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

## JSON Schema helpers

- `KG_ASSERTION_SCHEMA_REF_V0: str`
- `build_kg_assertion_schema_v0(...) -> dict`
  - important args: `include_predicate_aliases`, `max_assertions`, `min_assertions_when_nonempty`
- `resolve_schema_ref(schema: dict) -> dict | None`

## Related docs

- [Getting started](getting-started.md)
- [Architecture](architecture.md)
- [Registry format](registry.md)
- [KG assertion JSON Schema](schema.md)
- [FAQ](faq.md)
