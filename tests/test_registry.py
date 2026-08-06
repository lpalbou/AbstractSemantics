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


# --- loader robustness (production-readiness wave, 2026-07-13) ---------------


def test_loader_names_the_file_on_yaml_syntax_error(tmp_path):
    """A hand-editing operator's first typo must produce an error naming the
    FILE — bare PyYAML reports '<unicode string>', which names nothing."""
    import pytest

    bad = tmp_path / "broken.yaml"
    bad.write_text("predicates:\n\t- id: x\n", encoding="utf-8")
    with pytest.raises(ValueError, match="broken.yaml"):
        load_semantics_registry(bad)


def test_loader_enforces_memory_relation_invariants(tmp_path):
    """memory_relations feed append-only journal writers (declaration IS
    permission) — structural typos in a custom/override registry must fail
    LOUD at load, never engrave. Predicates/entity_types keep item-skip
    leniency (they feed enums and fail soft); this section does not."""
    import pytest

    base = (
        "version: 1\n"
        "predicates:\n"
        '  - id: "dcterms:title"\n'
        "entity_types:\n"
        '  - id: "schema:Thing"\n'
    )

    curie = tmp_path / "curie.yaml"
    curie.write_text(
        base + 'memory_relations:\n  - id: "prov:used"\n    subject_role: a\n    object_role: b\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="plain word"):
        load_semantics_registry(curie)

    collide = tmp_path / "collide.yaml"
    collide.write_text(
        base + 'memory_relations:\n  - id: "title"\n    subject_role: a\n    object_role: b\n'.replace(
            '"title"', '"dcterms:title"'
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError):
        load_semantics_registry(collide)

    no_roles = tmp_path / "noroles.yaml"
    no_roles.write_text(base + 'memory_relations:\n  - id: "summarizes"\n', encoding="utf-8")
    with pytest.raises(ValueError, match="subject_role and object_role"):
        load_semantics_registry(no_roles)


# --- loader diagnostics batch (backlog 0003, 2026-07-20) ----------------------
# Four "silent degradation an operator would want a sound for" classes. Valid
# files keep byte-identical behavior (no new warnings on the shipped registry —
# pinned by test_shipped_registry_loads_clean below).

_BASE = (
    "version: 1\n"
    "predicates:\n"
    '  - id: "dcterms:title"\n'
    "entity_types:\n"
    '  - id: "schema:Thing"\n'
)


def test_duplicate_top_level_key_refuses_loudly(tmp_path):
    """Item 1: PyYAML last-wins on duplicate keys — a stray pasted second
    `predicates:` block could replace the whole vocabulary silently. The
    strict loader refuses, naming the file and the line."""
    import pytest

    dup = tmp_path / "dup.yaml"
    dup.write_text(
        _BASE + 'predicates:\n  - id: "schema:name"\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate mapping key"):
        load_semantics_registry(dup)
    with pytest.raises(ValueError, match="dup.yaml"):
        load_semantics_registry(dup)


def test_malformed_items_warn_once_per_section_and_load_succeeds(tmp_path):
    """Item 2: a wrong-indent typo that turns an item into a non-dict used to
    vanish silently (first symptom: a distant extractor enum). One warning
    per section naming path + count; the load still succeeds (leniency is
    deliberate — these sections feed enums and fail soft)."""
    import pytest

    f = tmp_path / "skips.yaml"
    f.write_text(
        "version: 1\n"
        "predicates:\n"
        '  - id: "dcterms:title"\n'
        "  - just-a-string\n"
        '  - {label: "no id"}\n'
        "entity_types:\n"
        '  - id: "schema:Thing"\n',
        encoding="utf-8",
    )
    with pytest.warns(UserWarning, match=r"skipped 2 malformed item\(s\) in 'predicates'"):
        reg = load_semantics_registry(f)
    assert reg.predicate_ids() == {"dcterms:title"}


def test_unparseable_version_warns_and_reads_zero(tmp_path):
    """Item 3: `version: "abc"` used to coerce to 0 silently, conflating
    absent with corrupt. Corruption now gets a sound; absent stays quiet."""
    import pytest
    import warnings as _w

    bad = tmp_path / "vbad.yaml"
    bad.write_text(_BASE.replace("version: 1", 'version: "abc"'), encoding="utf-8")
    with pytest.warns(UserWarning, match="unparseable version"):
        reg = load_semantics_registry(bad)
    assert reg.version == 0

    absent = tmp_path / "vnone.yaml"
    absent.write_text(_BASE.replace("version: 1\n", ""), encoding="utf-8")
    with _w.catch_warnings():
        _w.simplefilter("error")  # absent version must NOT warn
        reg2 = load_semantics_registry(absent)
    assert reg2.version == 0


def test_duplicate_ids_within_section_keep_first_and_warn(tmp_path):
    """Item 4: duplicate ids in one section were both kept — set consumers
    safe, iterating consumers (enums, dropdowns) saw both and label-wins was
    consumer-dependent. Keep-first + one warning makes it deterministic."""
    import pytest

    f = tmp_path / "dupid.yaml"
    f.write_text(
        "version: 1\n"
        "predicates:\n"
        '  - id: "dcterms:title"\n'
        '    label: "first wins"\n'
        '  - id: "dcterms:title"\n'
        '    label: "second loses"\n'
        "entity_types:\n"
        '  - id: "schema:Thing"\n',
        encoding="utf-8",
    )
    with pytest.warns(UserWarning, match=r"duplicate id\(s\) in 'predicates'"):
        reg = load_semantics_registry(f)
    kept = [pdef for pdef in reg.predicates if pdef.id == "dcterms:title"]
    assert len(kept) == 1
    assert kept[0].label == "first wins"


def test_duplicate_memory_relation_ids_are_fatal(tmp_path):
    """Item 4, memory_relations divergence: this section is load-fatal by
    doctrine — keep-first would silently pick which of two conflicting role
    declarations is authoritative, and a broken SECOND copy would demote a
    hard failure to a warning (adversarial finding 2). Duplicates refuse."""
    import pytest

    f = tmp_path / "duprel.yaml"
    f.write_text(
        _BASE
        + "memory_relations:\n"
        '  - id: "summarizes"\n'
        "    subject_role: summary\n"
        "    object_role: source\n"
        '  - id: "summarizes"\n',
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate memory relation id"):
        load_semantics_registry(f)


def test_merge_keys_still_load(tmp_path):
    """Regression pin (adversarial finding 1): YAML merge keys (`<<:`) are
    valid SafeLoader YAML the strict dup scan must not refuse — the merge-tag
    key node has no SafeConstructor and is flattened later by
    construct_mapping, so the scan skips it."""
    f = tmp_path / "merge.yaml"
    f.write_text(
        "version: 1\n"
        "_shared: &common\n"
        '  label: "shared label"\n'
        "predicates:\n"
        '  - id: "dcterms:title"\n'
        "    <<: *common\n"
        "entity_types:\n"
        '  - id: "schema:Thing"\n',
        encoding="utf-8",
    )
    reg = load_semantics_registry(f)
    assert [(pd.id, pd.label) for pd in reg.predicates] == [("dcterms:title", "shared label")]


def test_explicit_null_version_is_absent_shaped(tmp_path):
    """A bare `version:` (explicit null) is a common hand-edit intermediate —
    absent-shaped, quiet, reads 0 (adversarial finding 5)."""
    import warnings as _w

    f = tmp_path / "vnull.yaml"
    f.write_text(_BASE.replace("version: 1", "version:"), encoding="utf-8")
    with _w.catch_warnings():
        _w.simplefilter("error")
        reg = load_semantics_registry(f)
    assert reg.version == 0


def test_shipped_registry_loads_clean():
    """No-behavior-change-for-valid-files, made checkable: the shipped
    registry must load with ZERO warnings under the new diagnostics."""
    import warnings as _w

    with _w.catch_warnings():
        _w.simplefilter("error")
        reg = load_semantics_registry()
    assert reg.version >= 2

