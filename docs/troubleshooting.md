# Troubleshooting

> Symptoms you may hit when loading a registry, building the KG assertion schema, or normalizing predicates — with the cause and the fix for each.

Most failures here come from a hand-edited registry YAML. The loader names the file it was reading in every error message, so start by opening the path in the message.

## Import and installation

### `ImportError: cannot import name 'MEMORY_DIGEST_PREDICATE' from 'abstractsemantics'`

The same import error appears for `MemoryRelationDef`, `KG_PREDICATE_ALIAS_MAP_V0`, and `normalize_kg_predicate`.

An older `abstractsemantics` is installed in the active environment and shadows the version you expect. This is common in a source checkout, where `site-packages` wins over `src/`.

Check which copy is being imported and what version it is:

```bash
python -c "import abstractsemantics, importlib.metadata as m; print(abstractsemantics.__file__, m.version('abstractsemantics'))"
```

Install the checkout in editable mode, or upgrade the dependency:

```bash
pip install -e ".[dev]"
```

These names require `0.0.5` or later. See [Getting started](getting-started.md) for setup.

### Type checker reports `Any` for registry objects

Upgrade to `0.0.5` or later. Earlier versions shipped without a `py.typed` marker, so the annotations were not visible to consumers.

## Registry loading

### `FileNotFoundError: ABSTRACTSEMANTICS_REGISTRY_PATH does not exist: <path>`

The environment variable is set to a path that is not there. The message shows the resolved absolute path — relative values resolve against the current working directory, so a value that works from the repo root will not work from a subdirectory. Use an absolute path.

### `FileNotFoundError: ABSTRACTSEMANTICS_REGISTRY_PATH is not a file: <path>`

The variable points at a directory. Point it at the YAML file itself, not the folder holding it.

### `ValueError: Invalid YAML in semantics registry <path>: duplicate mapping key 'predicates' (line N)`

The file declares the same key twice at one level. This usually happens after pasting a second section into the file. Only one of the two blocks would have taken effect, so the loader refuses instead of silently discarding a vocabulary. Merge the two blocks into one and reload.

YAML merge keys (`<<:`) are unaffected and remain valid.

### `ValueError: Invalid YAML in semantics registry <path>: <parser error>`

A syntax error such as a bad indent or an unclosed quote. The message includes the line and column reported by the YAML parser.

### `ValueError: Semantics registry has no predicates: <path>`

No `predicates` entry survived parsing. Either the section is missing or empty, or every item was skipped as malformed — check for a `UserWarning` naming the skip count just before the error. Each item must be a mapping with a non-empty string `id`:

```yaml
predicates:
  - id: "dcterms:hasPart"
    label: "has part"
```

## Memory-relation declarations

These failures raise on load rather than degrading, because a declared relation immediately joins `memory_record_predicate_ids()` and its consumers write edges into append-only journals. See [Registry format](registry.md) for the section's full rules.

### `ValueError: ... memory relation id '<id>' must be a plain word (no CURIE prefix)`

A `memory_relations` id contains a `:`. Plain words are the canonical spelling at rest for this vocabulary. Put the standard-ontology term in `equivalent` instead:

```yaml
memory_relations:
  - id: "derived_from"
    equivalent: ["prov:wasDerivedFrom"]
    subject_role: "derived record"
    object_role: "source"
```

### `ValueError: ... memory relation id '<id>' collides with a KG predicate id`

The same plain word is declared as both a `predicates` id and a `memory_relations` id. The two vocabularies must stay disjoint, because `predicates` is what an extraction model is shown. Rename the memory relation, or drop the entry from whichever section should not own it.

A CURIE-shaped id trips the plain-word rule above first, so you will see this message only when a `predicates` entry itself uses a plain word.

A CURIE appearing in an `equivalent` list *may* also be a `predicates` id — that is expected and does not trigger this error.

### `ValueError: ... memory relation '<id>' must declare both subject_role and object_role`

Every entry needs both role fields. They are short nouns naming each endpoint, and writers use them to validate direction:

```yaml
  - id: "supports"
    subject_role: "evidence"
    object_role: "claim"
```

### `ValueError: ... duplicate memory relation id(s) ['<id>'] — this section is load-fatal`

The same relation is declared twice. Unlike `predicates`, this section does not keep the first occurrence, because that would silently pick which of two conflicting direction declarations wins. Remove the duplicate.

## Load warnings

A valid registry loads with no warnings. If you want them to fail your test suite:

```python
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("error")
    reg = load_semantics_registry()
```

### `skipped N malformed item(s) in '<section>'`

`N` items in `predicates` or `entity_types` were not mappings with a non-empty string `id`, and were dropped. The load succeeded without them, so the usual symptom is a downstream enum missing a value you expected. A wrong indent level is the common cause.

### `unparseable version '<value>' — reading as 0`

The `version` key is not an integer. The registry still loads with version `0`. An absent or explicitly null `version` is treated as `0` without a warning.

### `duplicate id(s) in '<section>' — keeping the first occurrence`

The same id appears more than once in `predicates` or `entity_types`. The first wins, so every consumer resolves the same entry. Remove the later duplicates, keeping the definition you want.

## Schema building

### `ValueError: Semantics registry provided no entity type ids`

`build_kg_assertion_schema_v0()` needs both predicates and entity types, even though `load_semantics_registry()` only requires predicates. Add an `entity_types` section to the registry you passed.

### `ValueError: Semantics registry provided no predicate ids`

The registry reached the builder with an empty predicate list. If you built `SemanticsRegistry` yourself rather than loading it, populate `predicates`.

### `ValueError: max_assertions and min_assertions_when_nonempty must be >= 0`

A negative bound was passed. Use `max_assertions=0` for "no maximum" — negative values are rejected rather than silently treated as unbounded.

### `ValueError: evidence length bounds must be >= 0`

`max_evidence_quote_len` or `max_original_context_len` was negative, which is not valid `maxLength` in JSON Schema.

### `resolve_schema_ref()` returns `None`

The `$ref` string did not match a known reference. The only supported value is `KG_ASSERTION_SCHEMA_REF_V0` (`"abstractsemantics:kg_assertion_schema_v0"`); check for a typo or surrounding whitespace.

`resolve_schema_ref()` also always builds with default arguments and the default registry. If you need custom bounds, aliases, or a custom registry, call `build_kg_assertion_schema_v0()` directly. See [KG assertion JSON Schema](schema.md).

## Predicate normalization

### `normalize_kg_predicate()` returns `None` for a predicate you expected to work

Three causes, in order of likelihood:

1. **Case or spelling.** Matching is exact and case-sensitive, because CURIEs are case-sensitive. `Dcterms:hasPart` does not match `dcterms:hasPart`. Leading and trailing whitespace is stripped for you.
2. **Not an alias.** Only aliases in `KG_PREDICATE_ALIAS_MAP_V0` are mapped. Print it to see the current set. Aliases without a single determinate canonical target are deliberately absent, so an unrecognized spelling is returned as `None` rather than guessed.
3. **Custom registry.** The canonical target must exist in the registry you passed. An alias whose target is missing from a custom registry returns `None`.

`None` is a normal result, not an error. Refuse the assertion or label it unknown — see [FAQ](faq.md).

### A spelling the schema offered is then rejected at the boundary

This should not happen: `build_kg_assertion_schema_v0(include_predicate_aliases=True)` only offers aliases whose canonical target exists in the registry passed to it. Verify both calls use the *same* registry object. Building the schema with a custom registry while normalizing against the default one (by omitting `registry=`) will produce this mismatch.

### Normalization is slow in a per-assertion loop

`normalize_kg_predicate(predicate)` with no `registry` argument reloads the YAML from disk on every call. Load once and pass it in:

```python
reg = load_semantics_registry()
for a in assertions:
    canonical = normalize_kg_predicate(a["predicate"], registry=reg)
```

## Still stuck

- [Registry format](registry.md) — the YAML shape and every validation rule
- [API reference](api.md) — the public surface
- [FAQ](faq.md) — conceptual questions and design boundaries
- [Contributing](../CONTRIBUTING.md) — how to report an issue
