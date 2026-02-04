# Documentation

> This folder documents the `abstractsemantics` Python package: what it is, how the registry works, and how to use the v0 JSON Schema helpers.

## Start here

- [Project README](../README.md): install + quickstart
- [Getting started](getting-started.md): install, load registry, build schema, `$ref` resolution
- [Architecture](architecture.md): components, data flow, and diagrams
- [Registry format](registry.md): YAML shape and loader behavior
- [KG assertion JSON Schema](schema.md): schema builder and `$ref` resolver
- [API reference](api.md): public API surface (what `abstractsemantics.__init__` exports)
- [Development](development.md): tests, builds, release checklist

## Source of truth (code)

- Default registry: [`src/abstractsemantics/semantics.yaml`](../src/abstractsemantics/semantics.yaml)
- Loader implementation: [`src/abstractsemantics/registry.py`](../src/abstractsemantics/registry.py)
- Schema builder: [`src/abstractsemantics/schema.py`](../src/abstractsemantics/schema.py)
