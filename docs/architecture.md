# Architecture

> `abstractsemantics` is a small library: a YAML semantics registry plus helper utilities to build a compact JSON Schema. It does not store data, run workflows, or make network calls.

## What exists in this repo

Core files:
- Registry YAML (packaged as data): `abstractsemantics/semantics.yaml` (in this repo: `src/abstractsemantics/semantics.yaml`)
- Loader + dataclasses: `src/abstractsemantics/registry.py`
- JSON Schema helpers: `src/abstractsemantics/schema.py`
- Public exports: `src/abstractsemantics/__init__.py`

## Data flow

1. `load_semantics_registry()` reads YAML (default file or `ABSTRACTSEMANTICS_REGISTRY_PATH`) and returns `SemanticsRegistry`.
2. `build_kg_assertion_schema_v0()` uses the registry ids to build a deterministic JSON Schema dict.
3. Consumers can reference the schema by `$ref` and resolve it via `resolve_schema_ref()`.

## Diagram (components + flow)

```mermaid
flowchart LR
  subgraph Package[abstractsemantics (this package)]
    YAML[src/abstractsemantics/semantics.yaml]
    Loader[registry.load_semantics_registry()]
    Reg[SemanticsRegistry]
    Builder[schema.build_kg_assertion_schema_v0()]
    Ref[schema.resolve_schema_ref()]
  end

  YAML --> Loader --> Reg --> Builder
  Ref --> Builder
  Builder --> JsonSchema[JSON Schema dict]

  subgraph Consumers[Typical consumers (external to this repo)]
    Runtime[Runtime / ingestion validation]
    Flow[UI authoring / dropdowns]
    Memory[Storage / query layers]
  end

  Reg --> Runtime
  Reg --> Flow
  Reg --> Memory
  JsonSchema --> Runtime
  JsonSchema --> Flow
```

## Design notes (grounded in code)

- Registry ids are treated as opaque strings (typically CURIEs). This package does not expand ids into full IRIs; it just loads and exposes them (`SemanticsRegistry.prefixes`, `PredicateDef.id`, `EntityTypeDef.id`).
- Loader is tolerant by design: unknown keys are ignored and invalid items are skipped (see parsing in `registry.load_semantics_registry()`).
- The v0 KG schema is intentionally small and bounded (see the `max_*` args in `schema.build_kg_assertion_schema_v0()`), and it enforces:
  - `predicate` ∈ registry predicate ids (optionally plus a small alias set)
  - `subject_type` / `object_type` ∈ registry entity-type ids
  - short evidence fields (`maxLength` caps)

## See also

- [Getting started](getting-started.md)
- [Registry format](registry.md)
- [KG assertion JSON Schema](schema.md)
- [FAQ](faq.md)
- [API reference](api.md)
