from __future__ import annotations

from abstractsemantics import (
    KG_ASSERTION_SCHEMA_REF_V0,
    KG_PREDICATE_ALIAS_MAP_V0,
    KG_PREDICATE_ALIASES_V0,
    build_kg_assertion_schema_v0,
    load_semantics_registry,
    normalize_kg_predicate,
    resolve_schema_ref,
)


def test_build_kg_assertion_schema_v0_tracks_registry_predicates_and_types() -> None:
    reg = load_semantics_registry()
    schema = build_kg_assertion_schema_v0(registry=reg, include_predicate_aliases=True)

    pred_enum = schema["properties"]["assertions"]["items"]["properties"]["predicate"]["enum"]
    assert isinstance(pred_enum, list) and pred_enum
    for pid in reg.predicate_ids():
        assert pid in pred_enum

    type_enum = schema["properties"]["assertions"]["items"]["properties"]["attributes"]["properties"]["subject_type"]["enum"]
    assert isinstance(type_enum, list) and type_enum
    for tid in reg.entity_type_ids():
        assert tid in type_enum


def test_build_kg_assertion_schema_v0_can_disable_aliases() -> None:
    reg = load_semantics_registry()
    schema = build_kg_assertion_schema_v0(registry=reg, include_predicate_aliases=False)
    pred_enum = schema["properties"]["assertions"]["items"]["properties"]["predicate"]["enum"]
    assert "schema:creator" not in pred_enum
    assert "schema:description" not in pred_enum


def test_resolve_schema_ref_returns_concrete_schema() -> None:
    resolved = resolve_schema_ref({"$ref": KG_ASSERTION_SCHEMA_REF_V0})
    assert isinstance(resolved, dict)
    assert resolved.get("type") == "object"
    assert "assertions" in resolved.get("properties", {})


# --- alias -> canonical normalization (backlog 0002) -------------------------


def test_alias_map_range_is_canonical_registry_ids_only() -> None:
    """The map's RANGE must be canonical registry predicate ids — normalizing
    to a non-registry string would just mint a third spelling."""
    reg = load_semantics_registry()
    ids = reg.predicate_ids()
    for alias, canonical in KG_PREDICATE_ALIAS_MAP_V0.items():
        assert canonical in ids, f"alias {alias!r} maps outside the registry: {canonical!r}"


def test_alias_map_keys_are_never_registry_ids() -> None:
    """An alias that IS a registry id would make normalization ambiguous
    (pass-through vs mapping) — keys and registry ids stay disjoint."""
    reg = load_semantics_registry()
    ids = reg.predicate_ids()
    for alias in KG_PREDICATE_ALIAS_MAP_V0:
        assert alias not in ids, f"alias {alias!r} is itself a registry id"


def test_alias_offer_set_is_derived_from_the_map() -> None:
    """One source: the offered alias tuple derives from the map's keys — a
    hand-maintained second copy is the drift class (derive-never-copy)."""
    assert tuple(KG_PREDICATE_ALIAS_MAP_V0) == tuple(KG_PREDICATE_ALIASES_V0)


def test_normalize_passes_canonical_ids_through() -> None:
    reg = load_semantics_registry()
    for pid in sorted(reg.predicate_ids()):
        assert normalize_kg_predicate(pid, reg) == pid


def test_normalize_maps_every_offered_alias() -> None:
    """Round-trip promise: everything the alias-enabled enum can offer, the
    boundary can normalize — no offered spelling is un-normalizable."""
    reg = load_semantics_registry()
    schema = build_kg_assertion_schema_v0(registry=reg, include_predicate_aliases=True)
    pred_enum = schema["properties"]["assertions"]["items"]["properties"]["predicate"]["enum"]
    for offered in pred_enum:
        normalized = normalize_kg_predicate(offered, reg)
        assert normalized is not None, f"offered spelling {offered!r} cannot be normalized"
        assert normalized in reg.predicate_ids()


def test_normalize_returns_none_for_unknown_never_guesses() -> None:
    reg = load_semantics_registry()
    for unknown in ("schema:hasParent", "schema:hasMemorySource", "made:up", "", "   ", None, 42):
        assert normalize_kg_predicate(unknown, reg) is None


def test_offer_side_filters_aliases_whose_canonical_is_absent(tmp_path) -> None:
    """Custom registries may lack an alias's canonical target — offering a
    spelling the boundary cannot normalize invites un-normalizable data, so
    the enum offers only aliases whose canonical exists in THIS registry
    (the offer-side twin of normalize's accept-side guard)."""
    custom = tmp_path / "custom.yaml"
    custom.write_text(
        "version: 1\n"
        "predicates:\n"
        '  - id: "dcterms:creator"\n'
        "entity_types:\n"
        '  - id: "schema:Thing"\n',
        encoding="utf-8",
    )
    reg = load_semantics_registry(custom)
    schema = build_kg_assertion_schema_v0(registry=reg, include_predicate_aliases=True)
    enum = schema["properties"]["assertions"]["items"]["properties"]["predicate"]["enum"]
    assert "schema:creator" in enum  # canonical dcterms:creator present
    assert "schema:hasPart" not in enum  # canonical dcterms:hasPart absent
    for offered in enum:
        assert normalize_kg_predicate(offered, reg) is not None


def test_negative_bounds_are_rejected() -> None:
    """A negative cap silently becoming 'no cap' is the dangerous coercion
    direction; negative maxLength is invalid JSON Schema."""
    import pytest

    with pytest.raises(ValueError):
        build_kg_assertion_schema_v0(max_assertions=-1)
    with pytest.raises(ValueError):
        build_kg_assertion_schema_v0(max_evidence_quote_len=-7)


def test_alias_map_stays_disjoint_from_memory_relations() -> None:
    """Memory-relation plain words must never enter the KG alias vocabulary
    (semantics.yaml: memory words never surface in the KG enum) — a future
    map entry like "summarizes": "dcterms:abstract" would pass the range
    check while leaking the vocabulary; this pin makes it a decision, not
    drift. Belt: every memory word returns None from the normalizer."""
    reg = load_semantics_registry()
    assert set(KG_PREDICATE_ALIAS_MAP_V0) & reg.memory_relation_ids() == set()
    for word in sorted(reg.memory_relation_ids()):
        assert normalize_kg_predicate(word, reg) is None


def test_indeterminate_aliases_are_not_offered() -> None:
    """Aliases without a determinate canonical mapping were deliberately
    removed from the offer set (offering what the boundary cannot normalize
    invites un-normalizable data at rest)."""
    for dropped in ("schema:hasParent", "schema:hasMember", "schema:recognizedAs", "schema:hasMemorySource"):
        assert dropped not in KG_PREDICATE_ALIASES_V0
        assert dropped not in KG_PREDICATE_ALIAS_MAP_V0

