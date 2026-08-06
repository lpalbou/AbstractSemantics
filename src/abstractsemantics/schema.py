from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from .registry import SemanticsRegistry, load_semantics_registry

# Stable reference strings for flow-authored schemas.
#
# Visual flows may reference these via a `json_schema` literal like:
#   {"$ref": "abstractsemantics:kg_assertion_schema_v0"}
# The runtime resolves them into a concrete JSON Schema dict at execution time.
KG_ASSERTION_SCHEMA_REF_V0 = "abstractsemantics:kg_assertion_schema_v0"


# Alias -> canonical normalization map for predicates that LLMs tend to emit
# by default (backlog 0002, built 2026-07-13).
#
# These aliases are *not* part of the canonical semantics registry. Prefer
# keeping structured-output enums canonical (so the model is forced to pick
# from the agreed semantics). When aliases ARE offered
# (`include_predicate_aliases=True`), the ingestion boundary normalizes them
# via `normalize_kg_predicate()` before anything persists — one spelling per
# predicate at rest (the same rule the memory-relations vocabulary enforces).
#
# Design rules (the accept-vs-offer split, decision:workitem-type-enum):
# - The OFFER set (`KG_PREDICATE_ALIASES_V0`, derived from this map's keys)
#   contains ONLY aliases with a DETERMINATE canonical mapping. Earlier alias
#   spellings without one (schema:hasParent — broader vs isPartOf is
#   context-dependent; schema:hasMember — no member predicate in the
#   registry; schema:recognizedAs — lossy vs sameAs; schema:hasMemorySource —
#   invented term with unclear intent) were REMOVED from the offer: offering
#   a spelling the boundary cannot normalize invites un-normalizable data.
# - The ACCEPT side (`normalize_kg_predicate`) passes canonical ids through,
#   maps known aliases, and returns None for everything else — the caller
#   labels or refuses; nothing is ever silently coerced to a guessed meaning.
# - The map's RANGE is canonical registry predicate ids only, and its keys
#   are never themselves registry ids (both test-pinned).
#
# Keep this map intentionally small to protect model context + reduce confusion.
KG_PREDICATE_ALIAS_MAP_V0: Dict[str, str] = {
    # schema.org twins of declared dcterms ids (same meaning, one spelling at rest)
    "schema:description": "dcterms:description",
    "schema:creator": "dcterms:creator",
    "schema:hasPart": "dcterms:hasPart",
    "schema:isPartOf": "dcterms:isPartOf",
    # snake_case spelling variants that do not exist in dcterms
    "dcterms:has_part": "dcterms:hasPart",
    "dcterms:is_part_of": "dcterms:isPartOf",
}

# The alias OFFER set, derived from the map's keys (never maintained by hand —
# a second copy would drift; the map is the single source).
KG_PREDICATE_ALIASES_V0: Sequence[str] = tuple(KG_PREDICATE_ALIAS_MAP_V0)


def normalize_kg_predicate(
    predicate: object,
    registry: Optional[SemanticsRegistry] = None,
) -> Optional[str]:
    """Normalize a predicate string to its canonical registry id.

    The ingestion-boundary half of the alias design: call this on every
    extractor-emitted predicate before persisting. The parameter is typed
    `object` deliberately — sanitizing raw LLM output IS the contract, so
    non-string input returns None instead of raising.

    Matching contract: input is whitespace-stripped, then matched EXACTLY
    (case-sensitive — CURIEs are case-sensitive and case-folding would be
    guessing). The returned id is the stripped form.

    Perf note: `registry=None` loads the registry YAML from disk on EVERY
    call — in a per-assertion loop, load once and pass it in.

    Returns:
    - the (stripped) id when it already is a canonical registry predicate id;
    - the canonical id when the input is a known alias
      (`KG_PREDICATE_ALIAS_MAP_V0`);
    - None otherwise — the caller decides (refuse loudly or label unknown);
      unknown strings are never coerced to a guessed canonical id.
    """
    if not isinstance(predicate, str):
        return None
    p = predicate.strip()
    if not p:
        return None
    reg = registry or load_semantics_registry()
    if p in reg.predicate_ids():
        return p
    canonical = KG_PREDICATE_ALIAS_MAP_V0.get(p)
    if canonical is not None and canonical in reg.predicate_ids():
        return canonical
    return None


def _dedup_preserve_order(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for v in values:
        if not isinstance(v, str):
            continue
        v2 = v.strip()
        if not v2 or v2 in seen:
            continue
        seen.add(v2)
        out.append(v2)
    return out


def build_kg_assertion_schema_v0(
    registry: Optional[SemanticsRegistry] = None,
    *,
    include_predicate_aliases: bool = False,
    max_assertions: int = 12,
    min_assertions_when_nonempty: int = 3,
    max_evidence_quote_len: int = 160,
    max_original_context_len: int = 280,
) -> Dict[str, Any]:
    """Build the structured-output JSON Schema used by the KG extractor workflows.

    This schema is deliberately small and meant to be stable:
    - `predicate` is restricted to the semantics registry (+ optional aliases;
      only aliases whose canonical target exists in the registry are offered).
    - `subject_type` / `object_type` are restricted to the registry entity types.
    - Evidence fields are bounded (short verbatim snippets).

    Bounds: `max_assertions=0` means unbounded (no `maxItems`); negative
    bounds are rejected — a negative cap silently becoming "no cap" is the
    dangerous coercion direction.
    """
    reg = registry or load_semantics_registry()

    if int(max_assertions) < 0 or int(min_assertions_when_nonempty) < 0:
        raise ValueError("max_assertions and min_assertions_when_nonempty must be >= 0")
    if int(max_evidence_quote_len) < 0 or int(max_original_context_len) < 0:
        raise ValueError("evidence length bounds must be >= 0")

    predicate_ids: List[str] = [p.id for p in reg.predicates if isinstance(p.id, str) and p.id.strip()]
    if include_predicate_aliases:
        # Offer ONLY aliases whose canonical target exists in THIS registry —
        # offering a spelling the boundary cannot normalize invites
        # un-normalizable data (custom/env-override registries may lack some
        # canonical targets; the accept-side guard in normalize_kg_predicate
        # has the same check).
        have = set(predicate_ids)
        predicate_ids = list(predicate_ids) + [
            alias for alias, canonical in KG_PREDICATE_ALIAS_MAP_V0.items() if canonical in have
        ]
    predicate_ids = _dedup_preserve_order(predicate_ids)

    entity_type_ids: List[str] = [t.id for t in reg.entity_types if isinstance(t.id, str) and t.id.strip()]
    entity_type_ids = _dedup_preserve_order(entity_type_ids)

    if not predicate_ids:
        raise ValueError("Semantics registry provided no predicate ids")
    if not entity_type_ids:
        raise ValueError("Semantics registry provided no entity type ids")

    max_assertions2 = max(0, int(max_assertions))
    min_nonempty2 = max(0, int(min_assertions_when_nonempty))
    if max_assertions2 and min_nonempty2 and min_nonempty2 > max_assertions2:
        min_nonempty2 = max_assertions2

    assertions_schema: Dict[str, Any] = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "subject": {"type": "string"},
                "predicate": {"type": "string", "enum": predicate_ids},
                "object": {"type": "string"},
                "confidence": {"type": ["number", "null"], "minimum": 0, "maximum": 1},
                "valid_from": {"type": ["string", "null"]},
                "valid_until": {"type": ["string", "null"]},
                "provenance": {"type": ["object", "null"]},
                "attributes": {
                    "type": "object",
                    "properties": {
                        "subject_type": {"type": "string", "enum": entity_type_ids},
                        "object_type": {"type": "string", "enum": entity_type_ids},
                        "evidence_quote": {"type": "string", "maxLength": int(max_evidence_quote_len)},
                        "original_context": {"type": "string", "maxLength": int(max_original_context_len)},
                    },
                    "required": ["evidence_quote"],
                },
            },
            "required": ["subject", "predicate", "object", "attributes"],
        },
    }

    if max_assertions2:
        assertions_schema["maxItems"] = max_assertions2
    if min_nonempty2:
        # Either:
        # - empty list (no facts), OR
        # - at least N assertions (avoid low-signal singletons that “technically” validate).
        assertions_schema["anyOf"] = [{"maxItems": 0}, {"minItems": min_nonempty2}]

    return {
        "type": "object",
        "properties": {
            "assertions": assertions_schema
        },
        "required": ["assertions"],
    }


def resolve_schema_ref(schema: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Resolve a schema reference dict to a concrete JSON Schema (if supported)."""
    ref = schema.get("$ref")
    if isinstance(ref, str) and ref.strip():
        if ref.strip() == KG_ASSERTION_SCHEMA_REF_V0:
            return build_kg_assertion_schema_v0()
    return None
