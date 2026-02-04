# AbstractSemantics (`abstractsemantics`)

Central, editable semantics registry (predicates + entity types) for AbstractFramework, with helpers to build a compact JSON Schema for knowledge-graph (KG) assertion structured outputs.

This package intentionally contains **definitions**, not storage:
- prefix mappings (CURIE namespaces)
- predicate allowlists (optional inverse pointers)
- entity-type allowlists

## Status

Small, dependency-light package (only PyYAML) with a tiny public API:
- the default registry is shipped as package data (`abstractsemantics/semantics.yaml`; in this repo: `src/abstractsemantics/semantics.yaml`)
- the loader returns immutable dataclasses (`SemanticsRegistry`)
- the v0 schema builder produces a deterministic JSON Schema dict

## Install

From PyPI:

```bash
pip install abstractsemantics
```

From source (editable, with test deps):

```bash
pip install -e ".[dev]"
```

Requires Python `>=3.10` (see `pyproject.toml`).

## Quickstart

Load the default registry and build the v0 structured-output schema:

```python
from abstractsemantics import load_semantics_registry, build_kg_assertion_schema_v0

reg = load_semantics_registry()
print(len(reg.predicates), len(reg.entity_types))

schema = build_kg_assertion_schema_v0(registry=reg, include_predicate_aliases=True)
```

Use a custom registry YAML (must exist on disk):

```bash
export ABSTRACTSEMANTICS_REGISTRY_PATH=/absolute/path/to/semantics.yaml
```

```python
from abstractsemantics import load_semantics_registry

reg = load_semantics_registry()  # loads from ABSTRACTSEMANTICS_REGISTRY_PATH if set
```

Note: `load_semantics_registry()` only requires at least 1 predicate, but `build_kg_assertion_schema_v0()` requires both predicate ids **and** entity-type ids (it raises `ValueError` if `entity_types` is empty).

## Intended consumers (external)

This package is designed to be consumed by:
- AbstractRuntime (validation at ingestion boundary)
- AbstractFlow (UI dropdowns + authoring support)
- AbstractMemory (storage/query on top of validated semantics)

## Documentation

Start with:
- `docs/getting-started.md` (recommended entrypoint)
- `docs/README.md` (documentation index)
- `docs/architecture.md` (what exists in this repo, with diagrams)
- `docs/registry.md` (registry YAML format)
- `docs/schema.md` (KG assertion JSON Schema + `$ref`)

## License

MIT (see `LICENSE`).
