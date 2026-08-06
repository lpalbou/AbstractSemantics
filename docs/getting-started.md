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
print(sorted(reg.memory_relation_ids()))
```

## Read the memory-relation vocabulary

`memory_relations` is the plain-word edge vocabulary for memory records. Each entry names the role of both endpoints, so a writer can validate direction without restating the semantics:

```python
for rel in reg.memory_relations:
    print(rel.id, ":", rel.subject_role, "->", rel.object_role)
```

Use `memory_record_predicate_ids()` as the validation set for memory-record writes. It is the declared relations plus the digest predicate:

```python
from abstractsemantics import MEMORY_DIGEST_PREDICATE

allowed = reg.memory_record_predicate_ids()
assert MEMORY_DIGEST_PREDICATE in allowed
```

See [Registry format](registry.md) for the rules this section is validated against.

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

A custom registry is held to the same rules as the shipped one: malformed `predicates`/`entity_types` items are skipped with a warning and at least one valid predicate id is required, while `memory_relations` problems fail the load. See [Registry format](registry.md) for the full list, and [Troubleshooting](troubleshooting.md) if a load fails.

## Normalize predicates at your boundary

If you enable predicate aliases in the schema, normalize what comes back before you persist it, so one predicate has one spelling at rest:

```python
from abstractsemantics import normalize_kg_predicate

normalize_kg_predicate("schema:hasPart", registry=reg)  # 'dcterms:hasPart'
normalize_kg_predicate("dcterms:hasPart", registry=reg)  # 'dcterms:hasPart'
normalize_kg_predicate("something:invented", registry=reg)  # None
```

A `None` result means the predicate is not recognized. Refuse it or label it as unknown; it is never mapped to a guessed meaning. Pass `registry=reg` in a loop — omitting it reloads the YAML from disk on every call.

## Next

- [Architecture](architecture.md)
- [Registry format](registry.md)
- [KG assertion JSON Schema](schema.md)
- [API reference](api.md)
- [FAQ](faq.md)
- [Troubleshooting](troubleshooting.md)
