# KG assertion JSON Schema (v0)

> `abstractsemantics` includes a small helper to build a compact JSON Schema dict intended for LLM structured outputs in knowledge-extraction workflows (knowledge-graph “assertions”).

## Stable schema reference (`$ref`)

`src/abstractsemantics/schema.py` defines a stable reference string:

- `KG_ASSERTION_SCHEMA_REF_V0 = "abstractsemantics:kg_assertion_schema_v0"`

`resolve_schema_ref()` accepts a dict like `{"$ref": KG_ASSERTION_SCHEMA_REF_V0}` and returns the concrete JSON Schema dict (or `None` if unsupported).

Note: `resolve_schema_ref()` resolves to `build_kg_assertion_schema_v0()` with its **default arguments** (so predicate aliases are disabled unless you build the schema directly).

## Building the schema directly

```python
from abstractsemantics import build_kg_assertion_schema_v0, load_semantics_registry

reg = load_semantics_registry()
schema = build_kg_assertion_schema_v0(registry=reg, include_predicate_aliases=True)
```

## Tuning output constraints

The schema is designed to be bounded by default. You can tune limits via function arguments:

```python
from abstractsemantics import build_kg_assertion_schema_v0

schema = build_kg_assertion_schema_v0(
    include_predicate_aliases=False,
    max_assertions=20,
    min_assertions_when_nonempty=1,
    max_evidence_quote_len=200,
    max_original_context_len=400,
)
```

### What it enforces (grounded in code)

`build_kg_assertion_schema_v0()`:

- restricts `predicate` to `registry.predicates[*].id` (and optionally a small alias list: `KG_PREDICATE_ALIASES_V0`)
- restricts `attributes.subject_type` and `attributes.object_type` to `registry.entity_types[*].id`
- requires each assertion to include:
  - `subject`, `predicate`, `object`
  - `attributes.evidence_quote` (short verbatim snippet)
- bounds evidence fields with `maxLength` (see `max_evidence_quote_len` and `max_original_context_len`)
- optionally bounds the number of assertions:
  - `max_assertions` via `maxItems`
  - if `min_assertions_when_nonempty > 0`, the schema allows either an empty list OR at least N assertions (an `anyOf` guard)

If the registry has no predicate ids or no entity-type ids, it raises `ValueError`.

## Schema shape (high level)

The returned object schema has the shape:

- `{ "assertions": [ { subject, predicate, object, confidence?, valid_from?, ... , attributes: {...} } ] }`

See `src/abstractsemantics/schema.py` for the authoritative dict.

## Related docs

- [Getting started](getting-started.md)
- [Registry format](registry.md)
- [API reference](api.md)
