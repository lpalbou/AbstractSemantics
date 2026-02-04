# FAQ

## What is `abstractsemantics`?

`abstractsemantics` is a small Python package that:

- ships a YAML semantics registry (`predicates` + `entity_types`)
- provides helpers to build a compact JSON Schema dict for knowledge-graph (KG) assertion structured outputs

Start with [Getting started](getting-started.md).

## Does this package store/query a knowledge graph?

No. It only provides **definitions** (allowlists and prefixes) and helper utilities. Storage, indexing, and querying belong in downstream systems.

See [Architecture](architecture.md).

## Where is the default semantics registry? How is it loaded?

The default registry is packaged next to the module as `abstractsemantics/semantics.yaml` (in this repo: `src/abstractsemantics/semantics.yaml`).

The loader resolves it via `resolve_semantics_registry_path()` in `src/abstractsemantics/registry.py`:
- if `ABSTRACTSEMANTICS_REGISTRY_PATH` is set, it loads that path
- otherwise it loads `semantics.yaml` next to `registry.py`

See [Registry format](registry.md).

## How do I use a custom registry file?

Option A: environment variable:

```bash
export ABSTRACTSEMANTICS_REGISTRY_PATH=/absolute/path/to/semantics.yaml
```

Option B: pass an explicit `path`:

```python
from pathlib import Path
from abstractsemantics import load_semantics_registry

reg = load_semantics_registry(Path("/absolute/path/to/semantics.yaml"))
```

See [Getting started](getting-started.md).

## What does the registry loader validate?

`load_semantics_registry()` is intentionally permissive (see `src/abstractsemantics/registry.py`):

- invalid items are skipped (e.g. non-dicts, missing/blank `id`)
- it requires **at least one** valid predicate id (otherwise it raises `ValueError`)
- it does **not** enforce uniqueness or validate cross-references (`inverse`, `parent`)
- it does **not** expand CURIEs into full IRIs (prefixes are loaded but not applied)

See [Registry format](registry.md).

## Why does `build_kg_assertion_schema_v0()` raise “no entity type ids”?

`build_kg_assertion_schema_v0()` requires both:

- at least one predicate id (`predicates[*].id`)
- at least one entity-type id (`entity_types[*].id`)

If your registry has an empty or missing `entity_types` list, the schema builder raises `ValueError` (see `src/abstractsemantics/schema.py`).

See [KG assertion JSON Schema](schema.md).

## What are “predicate aliases” and should I enable them?

`src/abstractsemantics/schema.py` defines a small alias list (`KG_PREDICATE_ALIASES_V0`) for predicate strings that LLMs often emit by default.

- aliases are **not** part of the canonical registry YAML
- enabling aliases (`include_predicate_aliases=True`) makes the schema accept those additional strings
- downstream ingestion/normalization is still the right place to map aliases to canonical ids

See [KG assertion JSON Schema](schema.md).

## Why doesn’t `$ref` resolution include predicate aliases?

`resolve_schema_ref()` resolves `KG_ASSERTION_SCHEMA_REF_V0` by calling `build_kg_assertion_schema_v0()` with default arguments, where `include_predicate_aliases` defaults to `False`.

If you need aliases or custom bounds, build the schema directly.

See [Getting started](getting-started.md) and [KG assertion JSON Schema](schema.md).

## How do I tune schema limits (max assertions, evidence length)?

Use the builder arguments in `build_kg_assertion_schema_v0()`:

```python
from abstractsemantics import build_kg_assertion_schema_v0

schema = build_kg_assertion_schema_v0(
    max_assertions=20,
    min_assertions_when_nonempty=1,
    max_evidence_quote_len=200,
    max_original_context_len=400,
)
```

See [KG assertion JSON Schema](schema.md).

## How do I quickly validate a custom registry in CI?

One simple check is to load the registry and build the KG schema:

```python
from pathlib import Path
from abstractsemantics import load_semantics_registry, build_kg_assertion_schema_v0

reg = load_semantics_registry(Path("path/to/semantics.yaml"))
build_kg_assertion_schema_v0(registry=reg)
```

This will fail fast if required ids are missing.

## Why does `pytest` fail with `ModuleNotFoundError: abstractsemantics`?

If you’re running tests against the source tree, install the package in your environment first:

```bash
pip install -e ".[dev]"
pytest
```

See [Development](development.md).

## How do I regenerate `llms-full.txt`?

`llms-full.txt` is generated from the repo files list in `scripts/generate_llms_full.py`:

```bash
python scripts/generate_llms_full.py
```

See [Development](development.md).

## Where should I report security vulnerabilities?

Please follow the responsible disclosure guidance in [`SECURITY.md`](../SECURITY.md).
