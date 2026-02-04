# Semantic triple prompt (v4, optimized)

> Prompt template for LLM-based extraction workflows that need to emit facts aligned to the `abstractsemantics` registry. This file is guidance for humans/agents; it is not used by the `abstractsemantics` Python package at runtime.

## Inputs

- Registry (source of truth): `src/abstractsemantics/semantics.yaml`
- Suggested structured-output schema: `abstractsemantics:kg_assertion_schema_v0` (see `docs/schema.md`)

## Prompt template

System / developer message:

> You extract knowledge-graph assertions from the provided text. Output **only** JSON that conforms to the JSON Schema. Use only predicate ids and entity-type ids from the provided semantics registry. Every assertion must include an `attributes.evidence_quote` copied verbatim from the text.
>
> If you cannot extract any high-confidence facts, output `{"assertions": []}`. Otherwise, output **at least 3** assertions.
>
> Keep `attributes.evidence_quote` short (ideally one sentence fragment) and include `attributes.original_context` only when needed.

User message (example):

> Registry: (attach `semantics.yaml`)
>
> Schema: `{"$ref": "abstractsemantics:kg_assertion_schema_v0"}`
>
> Text:
> (paste text here)

## Output guidelines (aligned to the v0 schema)

- `subject`, `predicate`, `object`: required strings
- `attributes.evidence_quote`: required string (verbatim from text)
- `attributes.subject_type` / `attributes.object_type`: include when you can map to a registry type id
- `confidence`: number in `[0, 1]` or `null`
- Prefer fewer, higher-signal assertions over many weak ones (the schema caps list size by default)

## Related docs

- [Registry format](../../registry.md)
- [KG assertion JSON Schema](../../schema.md)
