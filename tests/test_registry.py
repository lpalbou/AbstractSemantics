from __future__ import annotations

from abstractsemantics import (
    MEMORY_DIGEST_PREDICATE,
    load_semantics_registry,
)

# The plain-word memory-record relations declared per
# decision:0016-vocabulary-direction (2026-07-10, seven relations) plus the
# 2026-07-12 widening batch (refines live via world-model revision chains;
# answers/supports/part_of disposal-writable via confirm_relation). Engraved
# append-only — this set may WIDEN (coordinated with the memory seat) but an
# id must never be renamed or removed.
DECLARED_MEMORY_RELATIONS = {
    "summarizes",
    "mentions",
    "written_amid",
    "from_session",
    "reflected_in",
    "continues",
    "derived_from",
    "refines",
    "answers",
    "supports",
    "part_of",
}


def test_load_semantics_registry_has_predicates():
    reg = load_semantics_registry()
    ids = reg.predicate_ids()
    assert "rdf:type" in ids
    assert "dcterms:isPartOf" in ids


def test_memory_relations_declared_plain_words():
    reg = load_semantics_registry()
    ids = reg.memory_relation_ids()
    assert DECLARED_MEMORY_RELATIONS <= ids
    # Plain words are the canonical at-rest spelling: no prefixed/CURIE ids
    # may ever appear in this vocabulary (one spelling per predicate).
    assert all(":" not in rid for rid in ids)


def test_memory_record_predicate_ids_is_relations_plus_digest():
    reg = load_semantics_registry()
    validation_set = reg.memory_record_predicate_ids()
    assert validation_set == reg.memory_relation_ids() | {MEMORY_DIGEST_PREDICATE}
    assert MEMORY_DIGEST_PREDICATE == "dcterms:abstract"


def test_memory_relation_equivalents_are_prefixed_registry_style():
    """Equivalence metadata carries standard CURIEs only (interop hints), and
    every CURIE prefix must be declared in the registry prefixes map — the
    no-invented-vocabulary rule made checkable."""
    reg = load_semantics_registry()
    for rel in reg.memory_relations:
        for eq in rel.equivalent:
            assert ":" in eq, f"{rel.id}: equivalent {eq!r} is not a CURIE"
            prefix = eq.split(":", 1)[0]
            assert prefix in reg.prefixes, (
                f"{rel.id}: equivalent {eq!r} uses undeclared prefix {prefix!r}"
            )


def test_memory_relations_never_leak_into_kg_predicates():
    """The KG-extraction predicate list and the memory-relation vocabulary are
    disjoint by design: memory plain words must never surface in the
    structured-output enum fed to extractors."""
    reg = load_semantics_registry()
    assert not (reg.predicate_ids() & reg.memory_relation_ids())


def test_memory_relations_carry_direction_roles():
    """Every memory relation declares subject_role/object_role — the
    machine-readable direction carrier (2026-07-12) that writers with
    caller-asserted endpoints (memory's disposal confirm_relation) validate
    against, instead of hardcoding a second copy of the semantics."""
    reg = load_semantics_registry()
    for rel in reg.memory_relations:
        assert rel.subject_role and rel.subject_role.strip(), f"{rel.id}: missing subject_role"
        assert rel.object_role and rel.object_role.strip(), f"{rel.id}: missing object_role"


def test_equivalent_overlap_with_kg_predicates_is_the_declared_set():
    """Some memory-relation `equivalent` CURIEs legitimately coincide with ids
    in the KG predicate list (export-only metadata; memory validation refuses
    CURIE-spelled edges, so no at-rest collision can arise). The overlap is
    DECLARED — a new instance must be a decision, never drift."""
    reg = load_semantics_registry()
    equivalents = {eq for rel in reg.memory_relations for eq in rel.equivalent}
    assert equivalents & reg.predicate_ids() == {
        "schema:mentions",
        "schema:previousItem",
        "cito:supports",
        "dcterms:isPartOf",
    }

