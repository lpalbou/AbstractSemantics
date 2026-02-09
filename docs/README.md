# Documentation

> This folder documents the `abstractsemantics` Python package: what it is, how the registry works, and how to use the v0 JSON Schema helpers.

## Quick links

- [Project README](../README.md): install + quickstart
- [Getting started](getting-started.md): install, load registry, build schema, `$ref` resolution
- [API reference](api.md): public API surface (what `abstractsemantics.__init__` exports)
- [Architecture](architecture.md): components, data flow, and diagrams
- [Registry format](registry.md): YAML shape and loader behavior
- [KG assertion JSON Schema](schema.md): schema builder and `$ref` resolver
- [FAQ](faq.md): common questions and troubleshooting
- [Development](development.md): tests, builds, release checklist

## I want to…

- **Load the default registry** or override it with `ABSTRACTSEMANTICS_REGISTRY_PATH`: see [Getting started](getting-started.md).
- **Edit/extend the YAML registry** (ids, labels, inverses, parents): see [Registry format](registry.md).
- **Build a bounded “KG assertion” JSON Schema** for structured outputs: see [KG assertion JSON Schema](schema.md).
- **Resolve a stable `$ref`** like `abstractsemantics:kg_assertion_schema_v0`: see [Getting started](getting-started.md) and [KG assertion JSON Schema](schema.md).
- **Understand how this fits in AbstractFramework** (and what it does *not* do): see [Architecture](architecture.md).

## AbstractFramework ecosystem

`abstractsemantics` is designed to be a small, reusable component within AbstractFramework:

- AbstractFramework: https://github.com/lpalbou/AbstractFramework
- AbstractCore: https://github.com/lpalbou/abstractcore
- AbstractRuntime: https://github.com/lpalbou/abstractruntime

This repo ships the definitions (registry ids) and a schema helper; integration happens in downstream systems (runtimes, UIs, ingestion pipelines).

## Project docs

- [Changelog](../CHANGELOG.md)
- [Contributing](../CONTRIBUTING.md)
- [Security policy](../SECURITY.md)
- [Acknowledgments](../ACKNOWLEDMENTS.md)
- [License](../LICENSE)

## Source of truth (code)

- Default registry: [`src/abstractsemantics/semantics.yaml`](../src/abstractsemantics/semantics.yaml)
- Loader implementation: [`src/abstractsemantics/registry.py`](../src/abstractsemantics/registry.py)
- Schema builder: [`src/abstractsemantics/schema.py`](../src/abstractsemantics/schema.py)
