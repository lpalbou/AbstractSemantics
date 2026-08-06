# Architecture

> `abstractsemantics` is a small library: a YAML semantics registry plus helper utilities to build a compact JSON Schema. It does not store data, run workflows, or make network calls.

## Position in AbstractFramework

AbstractFramework is a multi-repo ecosystem. In that ecosystem:

- **AbstractCore** defines shared primitives/contracts used across components.
- **AbstractRuntime** is typically the place where workflows execute and ingestion validation happens.
- **abstractsemantics** (this repo) provides the shared *allowed ids* (predicates, entity types, and memory relations) plus a small JSON Schema helper for structured outputs.

Links:
- AbstractFramework: https://github.com/lpalbou/AbstractFramework
- AbstractCore: https://github.com/lpalbou/abstractcore
- AbstractRuntime: https://github.com/lpalbou/abstractruntime

## What exists in this repo

Core files:
- Registry YAML (packaged as data): `abstractsemantics/semantics.yaml` (in this repo: `src/abstractsemantics/semantics.yaml`)
- Loader + dataclasses: `src/abstractsemantics/registry.py`
- JSON Schema helpers: `src/abstractsemantics/schema.py`
- Public exports: `src/abstractsemantics/__init__.py`

## The three vocabularies

The registry declares three separate id sets, and the distinction is the main thing to understand about this package:

| Section | Spelling | Feeds |
| --- | --- | --- |
| `predicates` | CURIEs (`dcterms:hasPart`) | the KG-extraction structured-output enum |
| `entity_types` | CURIEs (`schema:Person`) | the `subject_type`/`object_type` enums in the same schema |
| `memory_relations` | plain words (`derived_from`) | the validation set for memory-record edge writes |

`predicates` and `memory_relations` are kept disjoint on purpose. The first list is shown to an extraction model, and two spellings of one relation in front of a model is the confusion the split avoids. Standard-ontology CURIEs for a memory relation live in its `equivalent` list as export metadata, never as a second spelling at rest.

`entity_types` here are NER-sense classes for KG nodes. They are unrelated to the framework's *summoned entities*, which are named persistent identities owned by the gateway and runtime lanes.

## Data flow

1. `load_semantics_registry()` reads YAML (default file or `ABSTRACTSEMANTICS_REGISTRY_PATH`) and returns `SemanticsRegistry`.
2. `build_kg_assertion_schema_v0()` uses the registry ids to build a deterministic JSON Schema dict.
3. Consumers can reference the schema by `$ref` and resolve it via `resolve_schema_ref()`.
4. `normalize_kg_predicate()` maps an extractor-emitted predicate back to a canonical registry id at the ingestion boundary.
5. Memory-record writers validate edge predicates against `memory_record_predicate_ids()` and edge direction against each relation's `subject_role`/`object_role`.

## Diagram (components + flow)

```mermaid
flowchart LR
  subgraph Package[abstractsemantics (this package)]
    YAML[src/abstractsemantics/semantics.yaml]
    Loader[registry.load_semantics_registry()]
    Reg[SemanticsRegistry]
    Builder[schema.build_kg_assertion_schema_v0()]
    Ref[schema.resolve_schema_ref()]
    Norm[schema.normalize_kg_predicate()]
  end

  YAML --> Loader --> Reg --> Builder
  Ref --> Builder
  Reg --> Norm
  Builder --> JsonSchema[JSON Schema dict]

  subgraph Consumers[Typical consumers (external)]
    Runtime[AbstractRuntime / ingestion validation]
    Memory[Memory-record writers]
    Other[Other tools (UIs, pipelines, storage layers)]
  end

  Reg --> Runtime
  Reg --> Memory
  Reg --> Other
  Norm --> Runtime
  JsonSchema --> Runtime
  JsonSchema --> Other
```

## Validation model

The loader applies two different standards, chosen by what each section feeds.

```mermaid
flowchart TD
  Load[load_semantics_registry()] --> Parse{Section}
  Parse -->|predicates / entity_types| Soft[Lenient: skip malformed items, warn once per section, keep first duplicate id]
  Parse -->|memory_relations| Hard[Strict: raise on CURIE-shaped id, predicate collision, missing direction role, or duplicate id]
  Soft --> Enum[Structured-output enums fail soft]
  Hard --> Journal[Append-only journal writers must never engrave a typo]
```

`predicates` and `entity_types` feed model-facing enums, where a missing id degrades a result. `memory_relations` feeds writers that record edges permanently, where a wrong id is unrecoverable — so load is the last cheap place to fail. Structural failures apply to every registry, including one supplied through `ABSTRACTSEMANTICS_REGISTRY_PATH`.

## Design notes (grounded in code)

- Registry ids are treated as opaque strings (typically CURIEs). This package does not expand ids into full IRIs; it just loads and exposes them (`SemanticsRegistry.prefixes`, `PredicateDef.id`, `EntityTypeDef.id`).
- Unknown top-level keys are ignored, so a registry can carry extra sections without breaking the loader.
- The v0 KG schema is intentionally small and bounded (see the `max_*` args in `schema.build_kg_assertion_schema_v0()`), and it enforces:
  - `predicate` ∈ registry predicate ids (optionally plus a small alias set)
  - `subject_type` / `object_type` ∈ registry entity-type ids
  - short evidence fields (`maxLength` caps)
- Alias handling is split: `build_kg_assertion_schema_v0(include_predicate_aliases=True)` decides what is *offered* to a model, and `normalize_kg_predicate()` decides what is *accepted* at the boundary. Both check the same registry, so every offered spelling normalizes.

## See also

- [Getting started](getting-started.md)
- [Registry format](registry.md)
- [KG assertion JSON Schema](schema.md)
- [API reference](api.md)
- [FAQ](faq.md)
- [Troubleshooting](troubleshooting.md)
