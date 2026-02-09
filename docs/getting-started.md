# Getting started

> `abstractsemantics` provides (1) a YAML semantics registry and (2) helpers to turn that registry into a compact JSON Schema for knowledge-graph (KG) assertion structured outputs.

## Install

```bash
pip install abstractsemantics
```

For local development/tests:

```bash
pip install -e ".[dev]"
```

## Load the registry

The default registry is shipped inside the package (next to the Python module). In this repo it lives at `src/abstractsemantics/semantics.yaml` and is resolved by `resolve_semantics_registry_path()` in `src/abstractsemantics/registry.py`.

```python
from abstractsemantics import load_semantics_registry

reg = load_semantics_registry()
print(len(reg.predicates), len(reg.entity_types))
```

List the allowed ids:

```python
print(sorted(reg.predicate_ids())[:10])
print(sorted(reg.entity_type_ids())[:10])
```

## Build the v0 “KG assertion” JSON Schema

`build_kg_assertion_schema_v0()` (in `src/abstractsemantics/schema.py`) returns a plain Python `dict` containing a JSON Schema for structured outputs.

```python
from abstractsemantics import build_kg_assertion_schema_v0, load_semantics_registry

reg = load_semantics_registry()
schema = build_kg_assertion_schema_v0(registry=reg, include_predicate_aliases=True)
```

Notes (defaults are in code):
- `predicate` is restricted to registry predicate ids (optionally plus a small alias list).
- `attributes.subject_type` / `attributes.object_type` are restricted to registry entity-type ids.
- The default schema caps output size and avoids low-signal singletons: it allows either `[]` or at least 3 assertions.

You can tune these bounds via arguments (see `build_kg_assertion_schema_v0()` in `src/abstractsemantics/schema.py`):

```python
schema = build_kg_assertion_schema_v0(max_assertions=25, min_assertions_when_nonempty=1)
```

See [KG assertion JSON Schema](schema.md) for details.

## Use `$ref` and resolve it

Workflows can reference the schema by a stable `$ref` string and resolve it at runtime:

```python
from abstractsemantics import KG_ASSERTION_SCHEMA_REF_V0, resolve_schema_ref

resolved = resolve_schema_ref({"$ref": KG_ASSERTION_SCHEMA_REF_V0})
assert isinstance(resolved, dict)
```

`resolve_schema_ref()` resolves the schema with default builder arguments. If you need non-default bounds or predicate aliases, call `build_kg_assertion_schema_v0(...)` directly.

### AbstractFramework note

In the AbstractFramework ecosystem, downstream systems (for example a runtime at the ingestion boundary) can store a compact schema reference like `{"$ref": "abstractsemantics:kg_assertion_schema_v0"}` and call `resolve_schema_ref()` to materialize the concrete JSON Schema dict.

This package only provides the resolver and the builder (`src/abstractsemantics/schema.py`); it does not automatically wire this into any particular runtime.

## Use a custom registry file

You can point the loader (and therefore the schema builder) at a custom YAML file.

Option A: environment variable (checked by `resolve_semantics_registry_path()`):

```bash
export ABSTRACTSEMANTICS_REGISTRY_PATH=/absolute/path/to/semantics.yaml
```

Option B: explicit path argument:

```python
from pathlib import Path
from abstractsemantics import load_semantics_registry

reg = load_semantics_registry(Path("/absolute/path/to/semantics.yaml"))
```

If you pass an explicit `path`, the environment variable is ignored (`load_semantics_registry()` uses `path or resolve_semantics_registry_path()`).

The loader is tolerant (skips invalid items) but requires at least one valid predicate id; see [Registry format](registry.md).

## Next

- [Architecture](architecture.md)
- [Registry format](registry.md)
- [KG assertion JSON Schema](schema.md)
- [FAQ](faq.md)
- [API reference](api.md)
