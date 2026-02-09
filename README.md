# AbstractSemantics (`abstractsemantics`)

Central, editable semantics registry (predicates + entity types) for AbstractFramework, with helpers to build a compact JSON Schema for knowledge-graph (KG) assertion structured outputs.

This package intentionally contains **definitions**, not storage:
- prefix mappings (CURIE namespaces)
- predicate allowlists (optional inverse pointers)
- entity-type allowlists

## AbstractFramework ecosystem

`abstractsemantics` is a small, standalone building block within the wider AbstractFramework ecosystem:

- **AbstractFramework** (umbrella): https://github.com/lpalbou/AbstractFramework
- **AbstractCore** (core primitives/contracts): https://github.com/lpalbou/abstractcore
- **AbstractRuntime** (execution + ingestion boundary): https://github.com/lpalbou/abstractruntime

In practice, this repo provides the shared **allowed ids** (predicates and entity types) and a small JSON Schema helper that downstream components (including runtimes) can use for validation and structured outputs.

## Status

Small, dependency-light package (only PyYAML) with a tiny public API:
- the default registry is shipped as package data (`abstractsemantics/semantics.yaml`; in this repo: `src/abstractsemantics/semantics.yaml`)
- the loader returns immutable dataclasses (`SemanticsRegistry`)
- the v0 schema builder produces a deterministic JSON Schema dict

This package makes no network calls and does not store/query data (see `src/abstractsemantics/registry.py` and `src/abstractsemantics/schema.py`).

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

Resolve a stable `$ref` (useful when a downstream system stores schema references rather than full dicts):

```python
from abstractsemantics import KG_ASSERTION_SCHEMA_REF_V0, resolve_schema_ref

schema = resolve_schema_ref({"$ref": KG_ASSERTION_SCHEMA_REF_V0})
assert isinstance(schema, dict)
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

## Diagram (registry → schema → consumers)

```mermaid
flowchart LR
  YAML[src/abstractsemantics/semantics.yaml] --> Loader[load_semantics_registry()]
  Loader --> Reg[SemanticsRegistry]
  Reg --> Builder[build_kg_assertion_schema_v0()]
  Builder --> Schema[JSON Schema dict]
  Schema --> Consumers[AbstractRuntime / other consumers]
```

## Intended consumers (external)

Typical consumers include:
- AbstractRuntime (ingestion-boundary validation and structured-output contracts)
- authoring tools/UIs (dropdowns and semantic pickers backed by the registry)
- ingestion pipelines and storage/query layers that want a shared, explicit allowlist of ids

## Documentation

Start with:
- `docs/getting-started.md` (recommended entrypoint)
- `docs/README.md` (documentation index)
- `docs/architecture.md` (what exists in this repo, with diagrams)
- `docs/registry.md` (registry YAML format)
- `docs/schema.md` (KG assertion JSON Schema + `$ref`)
- `docs/faq.md` (common questions and troubleshooting)

## Project

- Changelog: `CHANGELOG.md`
- Contributing: `CONTRIBUTING.md`
- Security: `SECURITY.md`
- Acknowledgments: `ACKNOWLEDMENTS.md`

## License

MIT (see `LICENSE`).
